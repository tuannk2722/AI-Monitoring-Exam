from __future__ import annotations

import importlib.util
import json
import math
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

ML_AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ("torch", "torchvision"))
if ML_AVAILABLE:
    import torch
    from PIL import Image
    from test_pilot_schema import usable_record
    from torchvision.models import resnet18

    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.training.artifacts import digest_json
    from ai_exam_monitoring.training.config import ExperimentConfig, verify_approval
    from ai_exam_monitoring.training.data import labels, letterbox, select_records
    from ai_exam_monitoring.training.evaluate import validate_protocol
    from ai_exam_monitoring.training.metrics import evaluate_scores, masked_loss
    from ai_exam_monitoring.training.model import FrozenEncoder, SplitFeatures, extract_features
    from ai_exam_monitoring.training.train import run, train_head


def config():
    return ExperimentConfig(
        experiment_id="E001-unit", owner="unit", hypothesis="Synthetic software fixture",
        approval_ref="fixture", dataset="data/fixture", dataset_version="fixture",
        split_version="fixture", encoding_version="pilot-b-targets-v1",
        payload_sha256="a" * 64, weights="fixture.pth", weights_sha256="b" * 64,
        weights_url="https://download.pytorch.org/models/resnet18-f37072fd.pth",
        seed=42, image_size=32, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225],
        fill=[124, 116, 104], extraction_batch_size=2, threads=1,
        learning_rate=0.001, weight_decay=0.0001, max_epochs=8, patience=20,
        min_delta=0.0001, threshold=0.5, model="resnet18_frozen_linear",
        weights_id="IMAGENET1K_V1", device="cpu", optimizer="AdamW", loss="macro_masked_bce",
        transform="rgb_letterbox_bilinear_v1", target_order=["phone_use", "looking_around"],
        run_kind="smoke")


@unittest.skipUnless(ML_AVAILABLE, "Install requirements/classifier-cpu.txt for ML tests")
class TrainingTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)

    def test_config_rejects_unknown_model_invalid_numeric_and_unpinned_weights(self):
        for change in ({"model": "other"}, {"learning_rate": float("nan")},
                       {"max_epochs": True}, {"weights_sha256": "TBD"},
                       {"threshold": 1}, {"std": [0, 1, 1]}):
            with self.subTest(change=change), self.assertRaises(ConfigurationError):
                replace(config(), **change)

    def test_unknown_nan_ignored_and_gradient_is_zero_per_target_normalized(self):
        logits = torch.zeros(3, 2, requires_grad=True)
        values = torch.tensor([[1., float("nan")], [0., 1.], [float("nan"), 0.]])
        mask = torch.tensor([[True, False], [True, True], [False, True]])
        loss = masked_loss(logits, values, mask)
        self.assertAlmostEqual(float(loss.detach()), math.log(2), places=6)
        loss.backward()
        self.assertTrue(torch.equal(logits.grad[~mask], torch.zeros(2)))
        self.assertTrue(torch.allclose(logits.grad[mask], torch.tensor([-.125, .125, -.125, .125])))
        unequal_mask = torch.tensor([[True, True], [False, True], [False, True]])
        logits = torch.zeros(3, 2, requires_grad=True)
        masked_loss(logits, torch.zeros(3, 2), unequal_mask).backward()
        self.assertAlmostEqual(float(logits.grad[0, 0]), 0.25)
        self.assertAlmostEqual(float(logits.grad[0, 1]), 1 / 12)

    def test_missing_target_support_and_nonfinite_scores_fail(self):
        with self.assertRaises(DataContractError):
            masked_loss(torch.zeros(2, 2), torch.zeros(2, 2),
                        torch.tensor([[True, False], [True, False]]))
        with self.assertRaises(DataContractError):
            evaluate_scores(torch.full((2, 2), float("nan")), torch.zeros(2, 2),
                            torch.ones(2, 2, dtype=torch.bool), .5)

    def test_ap_ties_confusion_and_unknown_denominators(self):
        values = torch.tensor([[1., 0.], [0., 1.], [1., 0.]])
        mask = torch.tensor([[True, True], [True, True], [True, False]])
        scores = torch.tensor([[.9, .5], [.8, .5], [.7, .99]])
        result = evaluate_scores(scores, values, mask, .5)
        phone = result["targets"]["phone_use"]
        self.assertAlmostEqual(phone["ap"], 5 / 6)
        self.assertEqual((phone["tp"], phone["fp"], phone["fn"], phone["tn"]), (2, 1, 0, 0))
        looking = result["targets"]["looking_around"]
        self.assertEqual(looking["ap"], .5)
        self.assertEqual(looking["unknown"], 1)
        self.assertAlmostEqual(result["macro_ap"], 2 / 3)

    def test_undefined_metrics_are_null_not_fabricated_zero(self):
        scores, mask = torch.zeros(2, 2), torch.ones(2, 2, dtype=torch.bool)
        result = evaluate_scores(scores, torch.tensor([[1., 0.], [0., 0.]]), mask, .5)
        self.assertIsNone(result["macro_ap"])
        self.assertIsNone(result["targets"]["looking_around"]["ap"])
        self.assertIsNone(result["targets"]["phone_use"]["precision"])
        self.assertEqual(result["targets"]["phone_use"]["recall"], 0)

    def test_train_selection_never_uses_test_or_review_only(self):
        train = usable_record("train")
        val = usable_record("val", split="val")
        test = usable_record("test", split="test")
        self.assertEqual(select_records([test, val, train], "train"), [train])
        with self.assertRaises(DataContractError):
            select_records([test], "test")
        values, mask = labels([train])
        self.assertEqual(values.tolist(), [[1, 0]])
        self.assertEqual(mask.tolist(), [[True, False]])
        self.assertEqual(train.target_values, (1, None))

    def test_letterbox_preserves_both_edges_and_padding(self):
        image = Image.new("RGB", (32, 16), "white")
        image.putpixel((0, 0), (255, 0, 0))
        image.putpixel((31, 15), (0, 0, 255))
        result = letterbox(image, config())
        self.assertEqual(result.size, (32, 32))
        self.assertEqual(result.getpixel((0, 8)), (255, 0, 0))
        self.assertEqual(result.getpixel((31, 23)), (0, 0, 255))
        self.assertEqual(result.getpixel((0, 0)), tuple(config().fill))

    def test_letterbox_odd_geometry_and_color_modes(self):
        current = replace(config(), image_size=224)
        fixtures = [((175, 308), (127, 224), (48, 0)),
                    ((1001, 111), (224, 25), (0, 99)),
                    ((1, 300), (1, 224), (111, 0))]
        for size, resized, offset in fixtures:
            for mode in ["RGB", "L", "RGBA"]:
                with self.subTest(size=size, mode=mode):
                    image = Image.new(mode, size, 7)
                    pixel = image.convert("RGB").getpixel((0, 0))
                    result = letterbox(image, current)
                    self.assertEqual(result.mode, "RGB")
                    self.assertEqual(result.size, (224, 224))
                    self.assertEqual(result.getpixel(offset), pixel)
                    self.assertEqual(result.getpixel((offset[0] + resized[0] - 1,
                                                      offset[1] + resized[1] - 1)), pixel)
                    self.assertEqual(result.getpixel((0, 0)), tuple(current.fill))

    def test_frozen_encoder_keeps_weights_bn_buffers_and_no_grad(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic-unit-only.pth"
            torch.save(resnet18(weights=None).state_dict(), path)
            encoder = FrozenEncoder(path, sha256_file(path))
            before = {k: v.clone() for k, v in encoder.state_dict().items()}
            encoder.train()
            features = encoder(torch.randn(2, 3, 32, 32))
            self.assertEqual(features.shape, (2, 512))
            self.assertFalse(features.requires_grad)
            self.assertFalse(encoder.training)
            self.assertTrue(all(torch.equal(before[k], v) for k, v in encoder.state_dict().items()))
            self.assertTrue(all(not p.requires_grad for p in encoder.parameters()))

    def test_cache_reuse_and_changed_transform_rejected(self):
        class UnitEncoder:
            calls = 0

            def eval(self):
                return self

            def __call__(self, images):
                self.calls += 1
                return torch.zeros(len(images), 512)

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "crops").mkdir()
            row = usable_record()
            path = root / row.crop.crop_relpath
            Image.new("RGB", (8, 8), "red").save(path)
            # Fixture crop hash+review must agree; changing geometry is outside this test.
            from dataclasses import replace as dc_replace

            sha = sha256_file(path)
            review = dc_replace(row.crop.review, crop_sha256=sha)
            row = dc_replace(row, crop=dc_replace(row.crop, crop_sha256=sha, review=review),
                             phone_use=dc_replace(row.phone_use, review=review))
            encoder = UnitEncoder()
            cache = root / "features.pt"
            one = extract_features(encoder, root, [row], config(), cache)
            two = extract_features(encoder, root, [row], config(), cache)
            self.assertTrue(torch.equal(one.features, two.features))
            self.assertEqual(encoder.calls, 1)
            with self.assertRaises(DataContractError):
                extract_features(encoder, root, [row], replace(config(), image_size=64), cache)

    def test_resume_matches_uninterrupted_including_best_and_history(self):
        torch.manual_seed(7)
        features = torch.randn(6, 4)
        values = torch.tensor([[0., 1.], [1., 0.], [0., 0.], [1., 1.], [0., 1.], [1., 0.]])
        data = SplitFeatures([], features, values,
                             torch.ones_like(values, dtype=torch.bool), "unit")
        with tempfile.TemporaryDirectory() as folder:
            full, resumed = Path(folder) / "full", Path(folder) / "resume"
            full.mkdir()
            resumed.mkdir()
            result = train_head(data, data, config(), full, "identity")
            with self.assertRaises(KeyboardInterrupt):
                train_head(data, data, config(), resumed, "identity", interrupt_after=3)
            with self.assertRaises(DataContractError):
                train_head(data, data, config(), resumed, "different", resume=True)
            actual = train_head(data, data, config(), resumed, "identity", resume=True)
            self.assertEqual(result["history"], actual["history"])
            self.assertEqual(result["best_epoch"], actual["best_epoch"])
            self.assertTrue(all(torch.equal(v, actual["head"].state_dict()[k])
                                for k, v in result["head"].state_dict().items()))

    def test_test_protocol_requires_exact_candidate_and_owner(self):
        with tempfile.TemporaryDirectory() as folder:
            checkpoint = Path(folder) / "checkpoint"
            checkpoint.write_bytes(b"synthetic software fixture")
            with self.assertRaises(DataContractError):
                validate_protocol({}, config(), checkpoint, "config", "code")
            protocol = {"status": "approved", "experiment_id": config().experiment_id,
                        "checkpoint_sha256": sha256_file(checkpoint), "config_sha256": "config",
                        "code_sha256": "code", "payload_sha256": config().payload_sha256,
                        "threshold": .5, "split": "test", "candidate_count": 1,
                        "owner": "unit", "decision_ref": "unit"}
            validate_protocol(protocol, config(), checkpoint, "config", "code")
            checkpoint.write_bytes(b"changed")
            with self.assertRaises(DataContractError):
                validate_protocol(protocol, config(), checkpoint, "config", "code")

    def test_approval_rejects_changed_hyperparameter(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            c = config()
            approval = {"status": "approved", "owner": c.owner,
                        "scope": "local_classifier_research",
                        "configs": {c.experiment_id: digest_json(c.to_dict())}}
            (root / c.approval_ref).write_text(json.dumps(approval))
            verify_approval(c, root)
            with self.assertRaises(ConfigurationError):
                verify_approval(replace(c, learning_rate=.01), root)

    def test_failed_preflight_records_failure_and_preserves_existing_output(self):
        import yaml

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            c = config()
            (root / c.approval_ref).write_text(json.dumps({
                "status": "approved", "owner": c.owner, "scope": "local_classifier_research",
                "configs": {c.experiment_id: digest_json(c.to_dict())}}))
            cfg = root / "config.yaml"
            cfg.write_text(yaml.safe_dump(c.to_dict()))
            output = root / "outputs" / c.experiment_id
            with patch("ai_exam_monitoring.training.train.environment", return_value={}):
                with patch("ai_exam_monitoring.training.train.verify_dataset",
                           side_effect=DataContractError("fixture failure")):
                    with self.assertRaises(DataContractError):
                        run(cfg, output, root)
            status = json.loads((output / "run.json").read_text())
            self.assertEqual(status["status"], "FAILED")
            self.assertIn("fixture failure", status["error"])
            self.assertTrue((output / "checksums.json").is_file())
            before = (output / "run.json").read_bytes()
            with self.assertRaises(FileExistsError):
                run(cfg, output, root)
            self.assertEqual(before, (output / "run.json").read_bytes())

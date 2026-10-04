import hashlib
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.review_plan import validate_review_plan
from scripts.audits import roboflow_remaining_qa as renderer


def fixture_plan():
    return {"items": [{"id": "P1", "observation": "Synthetic ambiguous region",
                       "boxes": [], "regions": [[1, 1, 9, 9]], "blockers": ["unclear"]}],
            "approved_image_completeness": [{"id": "P2", "observation": "Synthetic review",
                                             "unresolved": "other labels"}],
            "training_eligible": False, "dataset_accepted": False}


class ReviewPlanTests(unittest.TestCase):
    def test_complete_hold_plan_is_not_a_negative(self):
        validate_review_plan(fixture_plan(), {"P1"}, {"P2"}, {"P1": (10, 10)})

    def test_missing_duplicate_or_acceptance_changes_fail(self):
        for change in ("missing", "duplicate", "acceptance"):
            plan = fixture_plan()
            if change == "missing":
                plan["items"] = []
            elif change == "duplicate":
                plan["items"] *= 2
            else:
                plan["training_eligible"] = True
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_review_plan(plan, {"P1"}, {"P2"}, {"P1": (10, 10)})

    def test_nonfinite_reversed_or_out_of_bounds_rectangles_fail(self):
        for coords in ([0, 0, float("nan"), 9], [0, 0, 11, 9], [8, 2, 3, 9]):
            plan = fixture_plan()
            plan["items"][0]["boxes"] = [coords]
            expected_error = ValueError if coords[2] != coords[2] else DataContractError
            with self.subTest(coords=coords), self.assertRaises(expected_error):
                validate_review_plan(plan, {"P1"}, {"P2"}, {"P1": (10, 10)})

    def test_render_preserves_approval_and_never_emits_empty_yolo_negative(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base, images = root / "outputs/base", root / "outputs/source/images"
            evidence = root / "artifacts/reports/roboflow-20261004"
            for folder in (base, images, evidence):
                folder.mkdir(parents=True)
            queue = []
            for sample_id, status in (("P1", "pending_manual_QA"),
                                      ("P2", "bbox_approved_completeness_pending")):
                path = images / f"{sample_id}.jpg"
                Image.new("RGB", (10, 10), "white").save(path)
                queue.append({"id": sample_id, "disposition": status,
                              "source_image": f"train/images/{sample_id}.jpg",
                              "image_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                              "training_eligible": False})
            renderer.write_json(base / "queue.json", queue)
            # Includes UTF-8 and formatting that must survive byte-for-byte.
            approved = '[{"id":"P2","owner_answer":"Đã duyệt","boxes":[]}]\n'.encode()
            (base / "approved-boxes.json").write_bytes(approved)
            reference = {"outputs_sha256": {p.name: renderer.digest(p) for p in base.iterdir()}}
            renderer.write_json(evidence / "remaining-reviewed-summary.json", reference)
            renderer.write_json(evidence / "remaining-qa-plan.json", fixture_plan())
            # Renderer includes the code file in provenance; provide a synthetic file in temp root.
            code = root / "src/ai_exam_monitoring/data/review_plan.py"
            code.parent.mkdir(parents=True)
            code.write_text("# software fixture only\n", encoding="utf-8")
            output = root / "outputs/new-review"
            with patch.object(renderer, "ROOT", root):
                result = renderer.run(base, images, output)
                self.assertEqual(result["held_images"], 1)
                self.assertEqual((output / "approved-boxes.json").read_bytes(), approved)
                self.assertEqual(list(output.rglob("*.txt")), [])
                self.assertEqual(json.loads((output / "queue.json").read_text())[0]
                                 ["training_eligible"], False)
                before = deepcopy(queue)
                self.assertEqual(json.loads((base / "queue.json").read_text()), before)
                with self.assertRaises(ValueError):
                    renderer.run(base, images, output)
                (images / "P1.jpg").write_bytes(b"tampered")
                with self.assertRaises(ValueError):
                    renderer.run(base, images, root / "outputs/tampered")
                self.assertFalse((root / "outputs/tampered").exists())

class OwnerReviewTests(unittest.TestCase):
    def fixture(self):
        queue = [{"id": str(i), "disposition": "pending_manual_QA",
                  "source_image": f"train/images/{i}.jpg", "image_sha256": str(i),
                  "training_eligible": False} for i in range(3)]
        proposals = [{**r, "boxes": [[1, 1, 5, 5]] if i < 2 else [],
                      "observation": "software fixture", "blockers": ["completeness"]}
                     for i, r in enumerate(queue)]
        decisions = [{"id": str(i), "action": action, "answer_verbatim": "owner fixture"}
                     for i, action in enumerate(
                         ["approve_bbox_only", "keep_pending", "hold_outside_train"])]
        return queue, proposals, decisions

    def test_approval_hold_and_exception_stay_distinct(self):
        from ai_exam_monitoring.data.review_plan import apply_owner_review

        queue, proposals, decisions = self.fixture()
        old = [{"id": "old", "boxes": [{"label": "phone_use", "xyxy": [1, 2, 3, 4]}]}]
        original = deepcopy(queue)
        result, boxes = apply_owner_review(queue, old, proposals, decisions)
        self.assertEqual(queue, original)
        self.assertEqual(boxes[0], old[0])
        self.assertEqual(len(boxes), 2)
        self.assertEqual([r["disposition"] for r in result],
                         ["bbox_approved_completeness_pending", "pending_manual_QA",
                          "held_outside_train_by_owner"])
        self.assertTrue(all(r["training_eligible"] is False for r in result))

    def test_reject_incomplete_duplicate_changed_or_empty_approval(self):
        from ai_exam_monitoring.data.review_plan import apply_owner_review

        for case in ("missing", "duplicate", "identity", "empty", "action", "test"):
            q, p, d = self.fixture()
            if case == "missing":
                d.pop()
            elif case == "duplicate":
                d.append(d[0])
            elif case == "identity":
                p[0]["image_sha256"] = "changed"
            elif case == "empty":
                d[2]["action"] = "approve_bbox_only"
            elif case == "action":
                d[0]["action"] = "accept_dataset"
            else:
                q[0]["source_image"] = p[0]["source_image"] = "test/images/0.jpg"
            with self.subTest(case=case), self.assertRaises(ValueError):
                apply_owner_review(q, [], p, d)

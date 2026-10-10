"""Kiểm attribution metadata, không đọc ảnh thật hoặc sử dụng credentials."""

import argparse
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ai_exam_monitoring.data import public_attribution_audit as audit


def oi_row(landing="https://www.flickr.com/photos/creator/123456/"):
    return {
        "candidate_id": "V7-A-001", "source_original_split": "train",
        "source_image_id": "abcd", "crop_path": "data/interim/draft/crop.png",
        "crop_sha256": "c" * 64, "source_image_sha256": "d" * 64,
        "screening_set": "oi", "screening_id": "V7-OI-SCREEN-001", "xyxy": [0, 0, 5, 5],
        "training_eligible": False, "canonical_mask": [0, 0],
        "canonical_targets": [None, None], "split": None, "usage": "review_only",
        "attribution_metadata": {
            "Subset": "train", "ImageID": "abcd", "Author": "Creator", "Title": "Title",
            "OriginalLandingURL": landing,
            "OriginalURL": "https://farm1.staticflickr.com/1/123456_abcd.jpg",
            "License": audit.CC_BY_2,
        },
    }


class AttributionTests(unittest.TestCase):
    def test_review_html_escapes_credit_and_preserves_local_panels(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            candidate = workspace / "data/interim/draft/candidates.jsonl"
            row = oi_row()
            row["observation"] = "<script>không chạy</script>"
            record = audit.attribution(row, audit.public_seed(row, {}, {}), None)
            record["attribution_draft_text"] = '<script>credit</script> & tác giả'
            document = audit.render_review_html([row], [record], candidate,
                                               workspace / "outputs/review", workspace)
            self.assertNotIn("<script>", document)
            self.assertIn("&lt;script&gt;credit", document)
            self.assertIn("../../data/interim/draft/review/V7-A-001.jpg", document)
            self.assertIn("pending_individual_attribution_and_owner_review", document)

    def test_review_html_rejects_unsafe_candidate_id(self):
        row = oi_row()
        row["candidate_id"] = "../../outside"
        with self.assertRaises(ValueError):
            audit.render_review_html([row], [], Path("data/interim/draft/candidates.jsonl"),
                                     Path("outputs/review"), Path.cwd())

    def test_https_domain_credentials_and_ports(self):
        for url in ["http://flickr.com/photos/c/1", "https://flickr.com.evil.test/a",
                    "https://user:password@flickr.com/a", "https://flickr.com:444/a"]:
            with self.assertRaises(ValueError):
                audit.enforce_flickr_url(url)
        audit.enforce_flickr_url("https://www.flickr.com/photos/c/123456/")

    def test_ids_and_short_url(self):
        self.assertEqual(audit.static_photo_id(
            "https://farm1.static.flickr.com/1/123456_abcd.jpg"), "123456")
        self.assertEqual(audit.landing_photo_id(
            "https://www.flickr.com/photos/c/123456/"), "123456")
        self.assertEqual(audit.short_landing("58"), "https://flic.kr/p/21")
        self.assertIsNone(audit.static_photo_id("https://evil.test/123456_abcd.jpg"))

    def test_bad_landing_blocks_only_record_without_network(self):
        seed = audit.public_seed(oi_row("https://evil.test/123456"), {}, {})
        self.assertIsNone(seed["landing_page_url"])
        self.assertTrue(seed["seed_blockers"])
        self.assertEqual(seed["original_landing_page_url"], "https://evil.test/123456")
        record = audit.attribution(oi_row(), seed, None)
        self.assertTrue(record["rights_review_blockers"])
        self.assertIs(record["training_eligible"], False)

    def test_http_flickr_metadata_normalizes_without_http_request(self):
        seed = audit.public_seed(oi_row("http://www.flickr.com/photos/creator/123456/"), {}, {})
        self.assertEqual(seed["landing_page_url"],
                         "https://www.flickr.com/photos/creator/123456/")
        self.assertFalse(seed["seed_blockers"])

    def test_conflicting_photo_identity_and_nontrain_are_rejected(self):
        seed = audit.public_seed(oi_row("https://www.flickr.com/photos/c/999/"), {}, {})
        self.assertTrue(seed["seed_blockers"])
        self.assertIsNone(seed["landing_page_url"])
        row = oi_row()
        row["attribution_metadata"]["Subset"] = "test"
        with self.assertRaises(ValueError):
            audit.public_seed(row, {}, {})

    def test_missing_credit_and_license_conflict_remain_pending(self):
        row = oi_row()
        row["attribution_metadata"].update(Author="", Title="")
        seed = audit.public_seed(row, {}, {})
        record = audit.attribution(row, seed, None)
        self.assertIn("creator", record["missing_attribution_fields"])
        self.assertIsNone(record["creator"])
        observation = {"status": "public_metadata_observed_not_rights_approval",
                       "public_metadata": {"author_name": "Creator", "title": "Title",
                                           "license_url": "https://creativecommons.org/publicdomain/zero/1.0/"}}
        record = audit.attribution(row, seed, observation)
        self.assertTrue(record["rights_review_blockers"])
        self.assertEqual(record["owner_review"], "PENDING")

    def test_wrong_oembed_identity_is_not_imported(self):
        class Response:
            status = 200
            headers = {"Content-Type": "application/json"}

            def geturl(self):
                return "https://www.flickr.com/photos/creator/123456/"

            def read(self, size):
                return json.dumps({"type": "photo", "web_page":
                                   "https://www.flickr.com/photos/creator/999/",
                                   "author_name": "Wrong author"}).encode()

            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

        with patch.object(audit.urllib.request, "build_opener") as opener:
            opener.return_value.open.return_value = Response()
            result = audit.observe_flickr(audit.public_seed(oi_row(), {}, {}))
        self.assertEqual(result["status"], "unverified_request_failed")
        self.assertNotIn("public_metadata", result)

    def test_candidate_eligibility_rejected_before_output_or_network(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            candidate = workspace / "data/interim/draft/candidates.jsonl"
            candidate.parent.mkdir(parents=True)
            row = oi_row()
            row["split"] = "train"
            candidate.write_text(json.dumps(row) + "\n", encoding="utf8")
            args = argparse.Namespace(workspace=workspace, candidates=candidate,
                                      output=Path("outputs/new"))
            with patch.object(audit, "observe_flickr") as observe:
                with self.assertRaises(ValueError):
                    audit.build(args)
                observe.assert_not_called()
            self.assertFalse((workspace / "outputs/new").exists())

    def test_pinned_cache_with_wrong_photo_or_media_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            candidate = workspace / "data/interim/draft/candidates.jsonl"
            candidate.parent.mkdir(parents=True)
            candidate.write_text(json.dumps(oi_row()) + "\n", encoding="utf8")
            cache = workspace / "outputs/cache.json"
            cache.parent.mkdir()
            observation = {"flickr_photo_id": "123456", "status":
                           "public_metadata_observed_not_rights_approval",
                           "credentials_used": False, "media_downloaded": True,
                           "public_metadata": {"web_page":
                                               "https://www.flickr.com/photos/c/123456/"}}
            cache.write_text(json.dumps([observation]), encoding="utf8")
            args = argparse.Namespace(workspace=workspace, candidates=candidate,
                                      output=Path("outputs/new"), max_network_images=None,
                                      receipt_cache=cache, receipt_cache_sha256=
                                      hashlib.sha256(cache.read_bytes()).hexdigest(),
                                      verify_public=True)
            with patch.object(audit, "observe_flickr") as observe:
                with self.assertRaises(ValueError):
                    audit.build(args)
                observe.assert_not_called()
            self.assertFalse((workspace / "outputs/new").exists())


if __name__ == "__main__":
    unittest.main()

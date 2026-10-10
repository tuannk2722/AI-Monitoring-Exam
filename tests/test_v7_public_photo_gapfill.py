"""Guards cho rights, rate-limit và pin public-photo preparation."""

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import yaml
from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.v7_public_photo_gapfill import (
    discover,
    eligible_pages,
    request,
    screen,
)


class PublicPhotoGuardsTests(unittest.TestCase):
    def test_license_and_dispute_are_evidence_gates(self) -> None:
        page = {"pageid": 1, "title": "File:test.jpg", "discovery_queries": [], "imageinfo": [{
            "mime": "image/jpeg", "width": 1000, "height": 800, "size": 123,
            "url": "https://publisher/image.jpg", "descriptionurl": "https://publisher/page",
            "sha1": "abc", "extmetadata": {"LicenseShortName": {"value": "CC BY 4.0"},
            "LicenseUrl": {"value": "https://creativecommons.org/licenses/by/4.0/"},
            "Artist": {"value": "<a>creator</a>"}}}]}
        config = {"allowed_licenses": ["CC BY 4.0"], "blocked_categories": ["without consent"],
                  "max_image_bytes": 1000, "min_dimension": 600}
        accepted, excluded = eligible_pages({"test": page}, config)
        self.assertEqual(accepted[0]["artist"], "creator")
        self.assertFalse(accepted[0]["training_eligible"])
        self.assertFalse(excluded)
        page["imageinfo"][0]["extmetadata"]["Categories"] = {"value": "Without consent"}
        accepted, excluded = eligible_pages({"test": page}, config)
        self.assertFalse(accepted)
        self.assertEqual(excluded["publisher_rights_dispute_or_no_consent_flag"], 1)

    def test_429_stops_batch_and_preserves_failure_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            metadata = root / "metadata.json"
            metadata.write_text(json.dumps([{"title": f"title{i}", "license": "CC BY 4.0",
                "license_url": "license", "url": "https://publisher/original",
                "thumb_url": "https://publisher/1920px.jpg"} for i in range(3)]), encoding="utf8")
            config = {"metadata": {"path": "metadata.json", "sha256": sha256_file(metadata)},
                "raw_images": "data/raw/new", "output": "data/interim/new", "image_cap": 3,
                "asset_mode": "thumbnail", "prior_screenings": [], "id_offset": 0,
                "allowed_licenses": ["CC BY 4.0"], "max_image_bytes": 1000,
                "max_total_bytes": 3000, "interval_seconds": 0}
            config_path = root / "config.yaml"
            config_path.write_text(yaml.safe_dump(config), encoding="utf8")
            error = HTTPError("https://publisher", 429, "rate limited", {"Retry-After": "60"}, None)
            with patch("ai_exam_monitoring.data.v7_public_photo_gapfill.request",
                       side_effect=error) as http:
                result = screen(config_path, root)
            self.assertEqual(http.call_count, 1)
            self.assertTrue(result["failures"][0]["remaining_batch_deferred"])
            self.assertEqual(result["failures"][0]["retry_after"], "60")
            self.assertTrue((root / "data/raw/new/receipt.json").exists())

    def test_original_sha_mismatch_never_materializes_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            buffer = io.BytesIO()
            Image.new("RGB", (10, 10), "red").save(buffer, "PNG")
            path = root / "metadata.json"
            path.write_text(json.dumps([{"title": "a", "license": "CC BY 4.0",
                "license_url": "license", "url": "https://publisher/original",
                "publisher_sha1": "incorrect"}]), encoding="utf8")
            config = {"metadata": {"path": "metadata.json", "sha256": sha256_file(path)},
                "raw_images": "data/raw/new", "output": "data/interim/new", "image_cap": 1,
                "asset_mode": "original", "prior_screenings": [], "id_offset": 0,
                "allowed_licenses": ["CC BY 4.0"], "max_image_bytes": 1000,
                "max_total_bytes": 3000, "interval_seconds": 0}
            cfg = root / "config.yaml"
            cfg.write_text(yaml.safe_dump(config), encoding="utf8")
            with patch("ai_exam_monitoring.data.v7_public_photo_gapfill.request",
                       return_value=(buffer.getvalue(), {"status": 200})):
                result = screen(cfg, root)
            self.assertEqual(result["records"], 0)
            self.assertIn("SHA1", result["failures"][0]["reason"])

    def test_non_https_request_is_rejected(self) -> None:
        with self.assertRaises(DataContractError):
            request("http://publisher/image.jpg", 1000)

    def test_discovery_rate_limit_defers_queries_and_seeds(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = {"raw_metadata": "data/raw/new", "discovery_output": "artifacts/reports/new",
                "queries": ["classroom phone", "writing"], "seed_titles": ["File:seed.jpg"],
                "limit_per_query": 20, "thumb_width": 1920, "api": "https://publisher/api",
                "interval_seconds": 0, "max_metadata_bytes": 1000, "allowed_licenses": [],
                "blocked_categories": [], "max_image_bytes": 1000, "min_dimension": 600}
            path = root / "config.yaml"
            path.write_text(yaml.safe_dump(config), encoding="utf8")
            error = HTTPError("https://publisher", 429, "rate limited", {}, None)
            with patch("ai_exam_monitoring.data.v7_public_photo_gapfill.request",
                       side_effect=error) as http:
                result = discover(path, root)
            self.assertEqual(http.call_count, 1)
            self.assertEqual(result["queries"][0]["status"], "FAILED_preserved")
            self.assertFalse(result["full_source_exhausted"])


if __name__ == "__main__":
    unittest.main()

"""Guards Range và byte budget cho intake public ZIP subset."""

import unittest
from unittest.mock import MagicMock, patch

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.public_zip_screening import PublicZipReader, fetch_range


class PublicZipTests(unittest.TestCase):
    def test_full_response_does_not_get_read_as_range(self) -> None:
        response = MagicMock()
        response.status = 200
        response.__enter__.return_value = response
        with patch("urllib.request.urlopen", return_value=response):
            with self.assertRaises(DataContractError):
                fetch_range("https://publisher/archive", 5, 10, 20)
        response.read.assert_not_called()

    def test_range_wrong_total_or_short_payload_fails(self) -> None:
        response = MagicMock()
        response.status = 206
        response.__enter__.return_value = response
        response.headers = {"Content-Range": "bytes 5-9/21"}
        response.read.return_value = b"1234"
        with patch("urllib.request.urlopen", return_value=response):
            with self.assertRaises(DataContractError):
                fetch_range("https://publisher/archive", 5, 10, 20)
            response.headers = {"Content-Range": "bytes 5-9/20"}
            with self.assertRaises(DataContractError):
                fetch_range("https://publisher/archive", 5, 10, 20)

    def test_budget_guard_precedes_network(self) -> None:
        reader = PublicZipReader("https://publisher/archive", 1000, 10)
        with patch("ai_exam_monitoring.data.public_zip_screening.fetch_range") as network:
            with self.assertRaises(DataContractError):
                reader.read(11)
            network.assert_not_called()
        with self.assertRaises(DataContractError):
            reader.seek(-1001, 2)

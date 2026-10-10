import tempfile
import unittest
from pathlib import Path

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import ConfigurationError


class ConfigTests(unittest.TestCase):
    def test_tbd_required_value_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.yaml"
            path.write_text("x: TBD_BY_TEAM\n", encoding="utf-8")
            config = load_yaml(path)
            with self.assertRaises(ConfigurationError):
                from ai_exam_monitoring.common.config import require

                require(config, "x")


if __name__ == "__main__":
    unittest.main()

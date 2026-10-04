import tempfile
import unittest
from pathlib import Path

from ai_exam_monitoring.common.config import load_yaml, validate_training_config
from ai_exam_monitoring.common.errors import ConfigurationError


class ConfigTests(unittest.TestCase):
    def test_baseline_config_contract(self) -> None:
        config = load_yaml("configs/baseline.yaml")
        with self.assertRaisesRegex(ConfigurationError, "Formulation B"):
            validate_training_config(config)

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

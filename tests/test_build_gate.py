import unittest

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.build_dataset import build_dataset


class BuildGateTests(unittest.TestCase):
    def test_unreviewed_sources_fail_closed(self) -> None:
        with self.assertRaisesRegex(DataContractError, "Formulation B"):
            build_dataset("configs/datasets/exam_v0.1.yaml")


if __name__ == "__main__":
    unittest.main()

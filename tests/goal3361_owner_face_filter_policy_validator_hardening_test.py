import inspect
from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl import closed_shape_topology


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3361_owner_face_filter_policy_validator_hardening_2026-06-04.md"


class Goal3361OwnerFaceFilterPolicyValidatorHardeningTest(unittest.TestCase):
    def test_validator_checks_topology_face_presence_policy(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        self.assertEqual(
            contract["filter_policy"]["topology_face_presence_columns"],
            "gate_left_and_right_face_ids_when_present",
        )
        source = inspect.getsource(closed_shape_topology.validate_owner_face_priority_pipeline_contract)
        self.assertIn("topology_face_presence_columns", source)
        self.assertIn("gate_left_and_right_face_ids_when_present", source)

    def test_report_records_claude_minor_hardening_note(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3360 Claude", text)
        self.assertIn("topology_face_presence_columns", text)
        self.assertIn("validator", text)
        self.assertIn("does not authorize release", text)


if __name__ == "__main__":
    unittest.main()

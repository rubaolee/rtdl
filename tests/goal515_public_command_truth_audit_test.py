from __future__ import annotations

import unittest

from scripts.goal515_public_command_truth_audit import audit


class Goal515PublicCommandTruthAuditTest(unittest.TestCase):
    def test_public_runnable_commands_are_mechanically_covered(self) -> None:
        payload = audit()

        self.assertTrue(payload["valid"], payload["uncovered"])
        self.assertGreaterEqual(payload["command_count"], 35)
        self.assertIn("goal410_harness_exact", payload["coverage_counts"])
        self.assertIn("goal410_harness_family", payload["coverage_counts"])
        self.assertIn("goal513_front_page_smoke_exact", payload["coverage_counts"])
        self.assertIn("v3_release_facing_partner_command_exact", payload["coverage_counts"])
        self.assertIn("linux_gpu_backend_gated", payload["classification_counts"])
        self.assertIn("optional_native_backend_gated", payload["classification_counts"])
        self.assertIn("portable_python_cpu", payload["classification_counts"])
        commands = {record["normalized"] for record in payload["commands"]}
        self.assertIn(
            "python scripts/rtdl_source_tree_doctor.py",
            commands,
        )
        self.assertIn(
            "python examples/current/getting_started/rtdl_prepared_measurement_demo.py",
            commands,
        )
        self.assertIn(
            "python examples/current/partners/rtdl_partner_anyhit.py --partner numpy --backend embree",
            commands,
        )
        feature_cookbook = [
            record for record in payload["commands"]
            if record["program"] == "examples/current/getting_started/rtdl_feature_quickstart_cookbook.py"
        ]
        self.assertTrue(feature_cookbook)
        self.assertTrue(
            all(record["coverage"] == "goal410_harness_exact" for record in feature_cookbook),
            feature_cookbook,
        )


if __name__ == "__main__":
    unittest.main()

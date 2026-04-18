from __future__ import annotations

import unittest

from scripts.goal515_public_command_truth_audit import audit


class Goal515PublicCommandTruthAuditTest(unittest.TestCase):
    def test_public_runnable_commands_are_mechanically_covered(self) -> None:
        payload = audit()

        self.assertTrue(payload["valid"], payload["uncovered"])
        self.assertGreaterEqual(payload["command_count"], 80)
        self.assertIn("goal410_harness_exact", payload["coverage_counts"])
        self.assertIn("goal410_harness_family", payload["coverage_counts"])
        self.assertIn("postgresql_validation_command", payload["coverage_counts"])
        self.assertIn("linux_gpu_backend_gated", payload["classification_counts"])
        self.assertIn("linux_postgresql_gated", payload["classification_counts"])
        self.assertIn("portable_python_cpu", payload["classification_counts"])
        commands = {record["normalized"] for record in payload["commands"]}
        self.assertIn(
            "python scripts/rtdl_generate_only.py --workload polygon_set_jaccard --dataset authored_polygon_set_jaccard_minimal --backend cpu_python_reference --output-mode rows --artifact-shape handoff_bundle --output build/generated_polygon_set_jaccard_bundle",
            commands,
        )
        feature_cookbook = [
            record for record in payload["commands"]
            if record["program"] == "examples/rtdl_feature_quickstart_cookbook.py"
        ]
        self.assertTrue(feature_cookbook)
        self.assertTrue(
            all(record["coverage"] == "goal410_harness_exact" for record in feature_cookbook),
            feature_cookbook,
        )


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3612_rayjoin_safe_mixed_route_composite.py"
REPORT = ROOT / "docs" / "reports" / "goal3732_rayjoin_composite_lsi_route_label_cleanup_2026-06-07.md"


class Goal3732RayJoinCompositeLsiRouteLabelCleanupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_composite_lsi_metadata_names_intersection_program_route(self):
        self.assertIn(
            '"segment_policy": "device_double_exact_count_during_optix_intersection_program_identity_range"',
            self.script,
        )
        self.assertIn('"segment_pair_count_route": payload["summary"].get("segment_pair_count_route")', self.script)
        self.assertIn("inside the custom intersection program over identity-range primitive records", self.script)
        self.assertIn('["git", "status", "--short", "--untracked-files=no"]', self.script)
        self.assertNotIn("device_double_exact_count_during_optix_anyhit", self.script)
        self.assertNotIn("inside the RT any-hit traversal", self.script)

    def test_report_scopes_this_as_metadata_cleanup(self):
        self.assertIn("updates only the composite script metadata", self.report)
        self.assertIn("does not change native code", self.report)
        self.assertIn("prevents future composite artifacts from carrying stale route language", self.report)


if __name__ == "__main__":
    unittest.main()

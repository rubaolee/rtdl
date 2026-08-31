from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal5768PrePodBundleTest(unittest.TestCase):
    def test_prepare_authority_is_file_backed_not_string_only(self):
        source = (ROOT / "scripts/goal5768_target_prepare.py").read_text(
            encoding="utf-8")
        self.assertIn("--owner-review", source)
        self.assertIn("--review-absorption", source)
        self.assertIn("validate_prepare_authority_files", source)
        self.assertNotIn("len(review) != 64", source)

    def test_prepare_driver_cannot_execute_formal_matrix(self):
        source = (ROOT / "scripts/goal5768_target_prepare.py").read_text(
            encoding="utf-8")
        self.assertNotIn("goal5768_three_way_worker.py", source)
        self.assertNotIn("goal5768_formal_controller.execute", source)
        self.assertIn('"formal_worker_count": 0', source)
        self.assertIn(
            '"formal_execution_requires_second_exact_owner_authority": True',
            source,
        )

    def test_bundle_overlay_is_explicit_and_private_state_is_absent(self):
        source = (ROOT / "scripts/goal5768_build_pre_pod_bundle.py").read_text(
            encoding="utf-8")
        self.assertIn("OVERLAYS = (", source)
        self.assertIn("goal5768_three_way_frontdoors.py", source)
        self.assertIn("goal5768_recount_three_way_raw.py", source)
        self.assertNotIn("C:/Users/", source)
        self.assertNotIn(".codex/rtdl", source)


if __name__ == "__main__":
    unittest.main()

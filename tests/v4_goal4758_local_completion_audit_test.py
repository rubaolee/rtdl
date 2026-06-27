from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4758_local_completion_audit import V4_GOAL4758_DECISION
from rtdsl.v4_goal4758_local_completion_audit import validate_v4_goal4758_local_completion_audit


class V4Goal4758LocalCompletionAuditTest(unittest.TestCase):
    def test_goal4758_audits_the_full_objective_without_authorizing_tag(self) -> None:
        audit = validate_v4_goal4758_local_completion_audit(ROOT)

        self.assertEqual(V4_GOAL4758_DECISION, audit["decision"])
        self.assertEqual(9, audit["requirement_count"])
        self.assertFalse(audit["release_authorized"])
        self.assertFalse(audit["public_tag_authorized"])
        self.assertTrue(audit["external_review_debt_open"])

    def test_goal4758_requires_v2_v3_superset_and_complete_matrix(self) -> None:
        audit = validate_v4_goal4758_local_completion_audit(ROOT)

        self.assertEqual(10, audit["app_compatibility_row_count"])
        self.assertEqual((), audit["app_compatibility_repair_required_apps"])
        self.assertEqual(10, audit["complete_rt_core_app_matrix_app_count"])
        self.assertEqual(30, audit["complete_rt_core_app_matrix_row_count"])
        self.assertEqual((), audit["goal4756_regression_apps"])
        self.assertEqual({"triangle_counting", "barnes_hut"}, set(audit["goal4756_material_candidate_apps"]))

    def test_goal4758_requires_bounded_cupy_and_numba_partner_support(self) -> None:
        audit = validate_v4_goal4758_local_completion_audit(ROOT)

        self.assertEqual(("cupy", "numba", "rtdl_native", "torch"), audit["measured_partners"])
        self.assertIn("cupy", audit["certified_partners"])
        self.assertIn("numba", audit["certified_partners"])
        self.assertGreaterEqual(audit["cupy_certified_surface_count"], 1)
        self.assertGreaterEqual(audit["cupy_measured_surface_count"], 1)
        self.assertGreaterEqual(audit["numba_certified_surface_count"], 1)
        self.assertGreaterEqual(audit["numba_measured_surface_count"], 1)
        self.assertFalse(audit["cupy_performance_claim_authorized"])
        self.assertFalse(audit["tier3_callback_claim_authorized"])

    def test_goal4758_requires_current_tree_package_artifact(self) -> None:
        audit = validate_v4_goal4758_local_completion_audit(ROOT)

        self.assertEqual(
            "dist/goal4758_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl",
            audit["package_wheel"],
        )
        self.assertGreater(audit["package_wheel_size"], 0)
        self.assertEqual(
            "4f349985e0daa8e16cbbfe90cab8663c8517815b1f22c8d6be67901a7da2eed5",
            audit["package_wheel_sha256"],
        )

    def test_goal4758_requires_installed_wheel_frontdoor_smoke(self) -> None:
        audit = validate_v4_goal4758_local_completion_audit(ROOT)

        self.assertEqual(
            "future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/wheel_install_with_deps.log",
            audit["wheel_install_log"],
        )
        self.assertEqual(
            "future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/import_claim_boundary_after_install.log",
            audit["wheel_import_log"],
        )
        self.assertEqual(
            "future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/summary.json",
            audit["wheel_smoke_summary"],
        )

    def test_goal4758_requires_final_review_manifest(self) -> None:
        audit = validate_v4_goal4758_local_completion_audit(ROOT)

        self.assertEqual(
            "future/v4/evidence/v4_goal4759_final_review_evidence_manifest_2026-06-26.json",
            audit["final_review_manifest"],
        )


if __name__ == "__main__":
    unittest.main()

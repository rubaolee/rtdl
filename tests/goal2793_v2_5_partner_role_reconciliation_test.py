from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2793_v2_5_partner_role_reconciliation_2026-05-31.md"
REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2793_gemini_review_partner_role_reconciliation_2026-05-31.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal2793_v2_5_partner_role_reconciliation_consensus_2026-05-31.md"


class Goal2793V25PartnerRoleReconciliationTest(unittest.TestCase):
    def test_protocol_roles_distinguish_numba_fallback_from_cupy_conformance(self) -> None:
        self.assertEqual(rt.V2_5_PRIMARY_PARTNER, "triton")
        self.assertEqual(rt.V2_5_FALLBACK_PARTNER, "numba")
        self.assertEqual(rt.V2_5_CONFORMANCE_PARTNER, "cupy_conformance")
        self.assertIn(rt.V2_5_FALLBACK_PARTNER, rt.V2_5_ALLOWED_PARTNERS)
        self.assertIn(rt.V2_5_CONFORMANCE_PARTNER, rt.V2_5_ALLOWED_PARTNERS)
        self.assertNotEqual(rt.V2_5_FALLBACK_PARTNER, rt.V2_5_CONFORMANCE_PARTNER)

    def test_support_matrix_keeps_cupy_out_of_generic_fallback_slot(self) -> None:
        matrix = rt.v2_5_partner_support_matrix()
        validation = rt.validate_v2_5_partner_support_matrix(matrix)

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(matrix["allowed_partners"], rt.V2_5_ALLOWED_PARTNERS)
        self.assertEqual(matrix["numba_preview_operations"], rt.V2_5_NUMBA_PREVIEW_OPERATIONS)
        self.assertEqual(matrix["cupy_preview_operations"], rt.V2_5_CUPY_PREVIEW_OPERATIONS)

        numba_count = rt.plan_v2_5_partner_support("segmented_count_i64", "numba")
        cupy_count = rt.plan_v2_5_partner_support("segmented_count_i64", "cupy")
        cupy_hit_stream = rt.plan_v2_5_partner_support(
            "hit_stream_grouped_ray_id_primitive_i64",
            "cupy",
        )

        self.assertEqual(numba_count["partner"], "numba")
        self.assertEqual(numba_count["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
        self.assertEqual(cupy_count["partner"], "cupy_conformance")
        self.assertEqual(cupy_count["status"], rt.V2_5_SUPPORT_STATUS_DESCRIPTOR)
        self.assertIn("conformance", cupy_count["notes"])
        self.assertEqual(cupy_hit_stream["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
        self.assertIn("Goals2771-2772", cupy_hit_stream["notes"])

    def test_dbscan_plan_names_cupy_as_app_choice_not_fallback(self) -> None:
        apps = {app["app_id"]: app for app in rt.v2_5_triton_benchmark_app_migration_plan()["apps"]}
        dbscan = apps["rt_dbscan"]
        text = " ".join(
            str(dbscan[field])
            for field in ("current_hot_path_partner", "v2_5_status", "first_port_action", "notes")
        )

        self.assertIn("app_chosen_cupy", dbscan["current_hot_path_partner"])
        self.assertIn("generic_fallback_partner_remains_numba", dbscan["v2_5_status"])
        self.assertIn("explicit app-chosen phase", text)
        self.assertIn("fallback partner is Numba", text)
        self.assertNotIn("legacy_cupy_for_component_continuations", text)

    def test_report_review_and_consensus_are_present(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Goal2793", report)
        self.assertIn("Numba", report)
        self.assertIn("CuPy", report)
        self.assertIn("app-chosen", report)
        self.assertIn("## verdict", review.lower())
        self.assertIn("accept", review.lower())
        self.assertIn("accept-with-boundary", consensus.lower())
        self.assertIn(str(REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt
from scripts import goal947_v1_rtx_app_status_page as goal947


ROOT = Path(__file__).resolve().parents[1]


class Goal1044PublicRtxCloudPolicySyncTest(unittest.TestCase):
    _STATUS_PAGE_SUPERSEDED_POLICY = {
        "graph_analytics": ("Goal1267", "not public speedup wording"),
        "polygon_pair_overlap_area_rows": ("Goal1263", "whole-app polygon-overlap speedup remain outside"),
    }

    _MATURITY_SUPERSEDED_POLICY = {
        "database_analytics": ("Goal1262", "Goal1264", "no positive public DB speedup wording"),
        "graph_analytics": ("Goal1267", "not public speedup wording"),
        "polygon_pair_overlap_area_rows": ("Goal1263", "whole-app polygon-overlap speedup remain outside"),
        "polygon_set_jaccard": ("Goal1262", "positive Jaccard speedup wording"),
    }

    def _assert_legacy_batch_policy(self, text: str) -> None:
        self.assertIn("Goal1048", text)
        self.assertIn("Goal1058", text)
        self.assertIn("Goal1135", text)
        self.assertIn("Goal1136", text)
        self.assertIn("Goal1177", text)

    def test_status_page_records_current_rerun_policy(self) -> None:
        payload = goal947.build_status_page()
        ready_rows = [
            row
            for row in payload["rows"]
            if row["readiness_status"] == "ready_for_rtx_claim_review"
        ]
        self.assertTrue(ready_rows)
        for row in ready_rows:
            with self.subTest(app=row["app"]):
                expected = self._STATUS_PAGE_SUPERSEDED_POLICY.get(row["app"])
                if expected is None:
                    self._assert_legacy_batch_policy(row["cloud_action"])
                    self.assertIn("bounded sub-path", row["cloud_action"])
                else:
                    for phrase in expected:
                        self.assertIn(phrase, row["cloud_action"])
                self.assertNotIn("no readiness pod needed", row["cloud_action"].lower())

    def test_public_docs_do_not_use_stale_no_readiness_pod_policy(self) -> None:
        for relpath in (
            "docs/v1_0_rtx_app_status.md",
            "docs/app_engine_support_matrix.md",
        ):
            text = (ROOT / relpath).read_text(encoding="utf-8")
            with self.subTest(relpath=relpath):
                self.assertIn("Goal1048", text)
                self.assertIn("Goal1058", text)
                self.assertIn("Goal1135", text)
                self.assertIn("Goal1136", text)
                self.assertIn("Goal1177", text)
                self.assertIn("0c79b64d1b71383080f2e8572612488796d1c16c", text)
                self.assertIn("21fa036881bf9a0c806f69c15727d87b482ccfcf", text)
                self.assertIn("oracle parity", text)
                self.assertNotIn("no readiness pod needed", text.lower())

    def test_maturity_policy_keeps_batched_cloud_rule(self) -> None:
        for app, row in rt.rt_core_app_maturity_matrix().items():
            if row.current_status != "rt_core_ready":
                continue
            with self.subTest(app=app):
                self.assertNotIn("restart per app", row.cloud_policy.lower())
                expected = self._MATURITY_SUPERSEDED_POLICY.get(app)
                if expected is None:
                    self._assert_legacy_batch_policy(row.cloud_policy)
                else:
                    for phrase in expected:
                        self.assertIn(phrase, row.cloud_policy)
                    continue
                if app == "facility_knn_assignment":
                    self.assertIn("Goal1146", row.cloud_policy)
                elif app == "robot_collision_screening":
                    self.assertIn("Goal1142", row.cloud_policy)
                    self.assertIn("Goal1126", row.cloud_policy)
                    self.assertIn("normalized per-pose", row.cloud_policy)
                else:
                    self.assertIn("claim-grade", row.cloud_policy)


if __name__ == "__main__":
    unittest.main()

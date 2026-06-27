from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.phoenix_v3_serious_v2x_paired_analysis import EXPECTED_BENCHMARK_APPS, build_payload


class PhoenixV3SeriousV2xPairedAnalysisTest(unittest.TestCase):
    def _write_summary(self, root: Path, tree: str, suite: str, rows: list[dict[str, object]]) -> None:
        path = root / f"{tree}_{suite}"
        path.mkdir(parents=True, exist_ok=True)
        (path / "summary.json").write_text(json.dumps({"rows": rows}), encoding="utf-8")

    def test_builds_same_metric_and_optix_embree_explanation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "status.tsv").write_text(
                "v2_14\tgoal2626_large\t0\tstart\tend\ncurrent\tgoal2626_large\t0\tstart\tend\n",
                encoding="utf-8",
            )
            v2_rows = [
                {
                    "status": "ok",
                    "app_id": "spatial_rayjoin",
                    "comparison_group": "rayjoin_all_backend_query_summary",
                    "backend": "embree",
                    "case_id": "rayjoin_embree",
                    "primary_metric_sec": 2.0,
                },
                {
                    "status": "ok",
                    "app_id": "spatial_rayjoin",
                    "comparison_group": "rayjoin_all_backend_query_summary",
                    "backend": "optix",
                    "case_id": "rayjoin_optix",
                    "primary_metric_sec": 4.0,
                },
            ]
            v3_rows = [
                {
                    "status": "ok",
                    "app_id": "spatial_rayjoin",
                    "comparison_group": "rayjoin_all_backend_query_summary",
                    "backend": "embree",
                    "case_id": "rayjoin_embree",
                    "primary_metric_sec": 1.0,
                },
                {
                    "status": "ok",
                    "app_id": "spatial_rayjoin",
                    "comparison_group": "rayjoin_all_backend_query_summary",
                    "backend": "optix",
                    "case_id": "rayjoin_optix",
                    "primary_metric_sec": 2.0,
                },
            ]
            self._write_summary(root, "v2_14", "goal2626_large", v2_rows)
            self._write_summary(root, "current", "goal2626_large", v3_rows)

            payload = build_payload(root)

        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["release_consideration_eligible"])
        self.assertFalse(payload["release_consideration_bar"]["all_required_suites_finished"])
        self.assertIn("barnes_hut", payload["release_consideration_bar"]["missing_promoted_apps"])
        self.assertEqual(payload["same_metric_comparison_count"], 2)
        self.assertEqual(payload["v3_faster_count_gt_5pct"], 2)
        self.assertEqual(payload["status_tsv_rows"][0]["tree"], "v2_14")
        ratio_rows = payload["optix_vs_embree_ratio_change_rows"]
        self.assertEqual(len(ratio_rows), 1)
        self.assertEqual(ratio_rows[0]["v2_optix_vs_embree"], 0.5)
        self.assertEqual(ratio_rows[0]["v3_optix_vs_embree"], 0.5)
        self.assertIn("OptiX slower than Embree in both", ratio_rows[0]["interpretation"])

    def test_release_consideration_requires_preregistered_bar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status_lines = [
                f"{tree}\t{suite}\t0\tstart\tend"
                for tree in ("v2_14", "current")
                for suite in ("goal2626_large", "goal2636_stress", "goal3828_full")
            ]
            (root / "status.tsv").write_text("\n".join(status_lines) + "\n", encoding="utf-8")
            v2_rows = []
            v3_rows = []
            for index, app in enumerate(EXPECTED_BENCHMARK_APPS):
                v2_rows.append(
                    {
                        "status": "ok",
                        "app_id": app,
                        "comparison_group": "same_contract",
                        "backend": "optix",
                        "case_id": f"{app}_case",
                        "primary_metric_source": "query_sec",
                        "primary_metric_sec": 2.0,
                    }
                )
                v3_rows.append(
                    {
                        "status": "ok",
                        "app_id": app,
                        "comparison_group": "same_contract",
                        "backend": "optix",
                        "case_id": f"{app}_case",
                        "primary_metric_source": "query_sec",
                        "primary_metric_sec": 1.0 if index < 8 else 2.0,
                    }
                )
            self._write_summary(root, "v2_14", "goal2626_large", v2_rows)
            self._write_summary(root, "current", "goal2626_large", v3_rows)

            payload = build_payload(root)

        self.assertTrue(payload["release_consideration_eligible"])
        self.assertFalse(payload["release_authorized"])
        self.assertEqual(payload["release_consideration_bar"]["missing_promoted_apps"], [])
        self.assertGreaterEqual(payload["release_consideration_bar"]["actual_app_geomean_wins_gt_1_05x"], 8)


if __name__ == "__main__":
    unittest.main()

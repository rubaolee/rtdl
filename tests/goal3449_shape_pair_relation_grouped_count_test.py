from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
SCRIPT = ROOT / "scripts" / "goal3449_shape_pair_relation_grouped_count_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3449_shape_pair_relation_grouped_count_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3449_shape_pair_relation_grouped_count_pod_2026-06-05.json"


class Goal3449ShapePairRelationGroupedCountTest(unittest.TestCase):
    def test_runtime_reuses_generic_grouped_count_device_columns(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        for phrase in (
            "def grouped_count_by_id_compact_device_columns(",
            "def grouped_count_by_left_id_compact_device_columns(",
            "def grouped_count_by_right_id_compact_device_columns(",
            "OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_COMPACT_DEVICE_COLUMNS_WITH_CAPACITY_SYMBOL",
            "device_column_grouped_count_i64_compact_columns",
            "id_axis must be 'left' or 'right'",
        ):
            self.assertIn(phrase, runtime)

    def test_app_route_keeps_rayjoin_semantics_out_of_native_runtime(self) -> None:
        app = APP.read_text(encoding="utf-8")

        for phrase in (
            "def run_packed_left_active_relation_grouped_count_by_left(",
            "self.id_capacity",
            "prepared_optix_shape_pair_active_relation_grouped_count_by_left_reuse",
            "active_relation_grouped_count_by_left_sec",
            "group_capacity",
            "grouped_count_sum_matches_active_count",
            "generic active ",
            "relation columns feed the existing generic compact grouped-count",
            "RayJoin interpretation stays in Python",
        ):
            self.assertIn(phrase, app)

    def test_probe_and_report_record_boundaries(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3449.shape_pair_relation_grouped_count.v1",
            "grouped_count_sum",
            "grouped_speedup_vs_host",
            "rayjoin_paper_reproduction_claim_authorized",
        ):
            self.assertIn(phrase, script)
        for phrase in (
            "Goal3449",
            "generic device-column grouped-count reducer",
            "does not authorize",
            "full overlay relation-row",
            "bounded witness/area continuation",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3449 pod artifact pending")
    def test_pod_artifact_grouped_sum_matches_host_count(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3449.shape_pair_relation_grouped_count.v1")
        self.assertEqual(payload["goal"], 3449)
        self.assertTrue(payload["all_counts_match"])
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))
        self.assertEqual(payload["host_counts"], payload["grouped_count_sums"])
        self.assertGreater(payload["grouped_speedup_vs_host"]["median"], 1.0)
        for run in payload["runs"]:
            self.assertTrue(run["counts_match"])
            self.assertTrue(run["grouped_count_metadata"]["device_resident"])
            self.assertEqual(
                run["native_phase_timings"]["mode"],
                "active_relation_device_columns",
            )
            self.assertTrue(all(value is False for value in run["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()

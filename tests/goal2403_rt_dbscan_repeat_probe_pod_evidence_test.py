from __future__ import annotations

import json
import pathlib
import statistics
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2403_rt_dbscan_repeat_probe_pod"
REPORT = ROOT / "docs" / "reports" / "goal2403_rt_dbscan_repeat_probe_pod_evidence_2026-05-19.md"


def _load(dataset: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / f"{dataset}_repeat4.json").read_text(encoding="utf-8"))


def _mode_rows(payload: dict[str, object], mode: str) -> list[dict[str, object]]:
    rows = payload["rows"]
    assert isinstance(rows, list)
    return [row for row in rows if isinstance(row, dict) and row.get("mode") == mode]


def _app_seconds(rows: list[dict[str, object]]) -> list[float]:
    return [float(row["app_elapsed_sec"]) for row in rows]


class Goal2403RtDbscanRepeatProbePodEvidenceTest(unittest.TestCase):
    def test_clean_pod_environment_records_repeat_probe_commit(self) -> None:
        environment = (ARTIFACT_DIR / "environment.txt").read_text(encoding="utf-8")

        self.assertIn("commit=86856bb37f0f2a8d2f03b3677435b3988f646599", environment)
        self.assertIn("NVIDIA RTX A5000, 570.211.01", environment)
        self.assertIn("RTDL_OPTIX_LIBRARY=/root/rtdl_goal2392_pod/build/librtdl_optix.so", environment)

    def test_repeat_probe_records_matching_signatures_and_claim_boundary(self) -> None:
        for dataset in ("clustered3d", "road3d"):
            with self.subTest(dataset=dataset):
                payload = _load(dataset)
                boundary = payload["claim_boundary"]

                self.assertTrue(payload["signatures_match"])
                self.assertEqual(payload["repeat_count"], 4)
                self.assertEqual(payload["point_count"], 4096)
                self.assertTrue(boundary["steady_state_probe_only"])
                self.assertFalse(boundary["paper_dataset_reproduction"])
                self.assertFalse(boundary["paper_speedup_claim_authorized"])
                self.assertFalse(boundary["broad_rt_core_speedup_claim_authorized"])

    def test_warm_runs_are_faster_than_cold_runs_but_cupy_still_leads(self) -> None:
        for dataset in ("clustered3d", "road3d"):
            with self.subTest(dataset=dataset):
                payload = _load(dataset)
                cupy_rows = _mode_rows(payload, "partner_cupy_grid_components_3d")
                bridge_rows = _mode_rows(payload, "optix_core_flags_cupy_grid_components_3d")

                self.assertEqual(len(cupy_rows), 4)
                self.assertEqual(len(bridge_rows), 4)

                cupy_seconds = _app_seconds(cupy_rows)
                bridge_seconds = _app_seconds(bridge_rows)

                self.assertLess(statistics.median(cupy_seconds[1:]), cupy_seconds[0])
                self.assertLess(statistics.median(bridge_seconds[1:]), bridge_seconds[0])
                self.assertLess(statistics.median(cupy_seconds[1:]), statistics.median(bridge_seconds[1:]))

                for row in bridge_rows:
                    self.assertFalse(row["rt_core_accelerated"])
                    self.assertFalse(row["materializes_neighbor_rows"])
                    self.assertIsNotNone(row["optix_core_flag_sec"])
                    self.assertIsNotNone(row["cupy_component_continuation_sec"])

    def test_report_states_boundary_and_next_runtime_gap(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("warm steady-state behavior", report)
        self.assertIn("not a paper-speedup claim", report)
        self.assertIn("rather than RT cores", report)
        self.assertIn("not yet faster than the optimized pure CuPy device-grid", report)
        self.assertIn("device-resident output handoff", report)


if __name__ == "__main__":
    unittest.main()

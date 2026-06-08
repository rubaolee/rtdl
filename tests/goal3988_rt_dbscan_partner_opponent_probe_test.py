import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3988_rt_dbscan_partner_opponent_probe_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3988_rt_dbscan_partner_opponent_probe_2026-06-08"


def _load(name: str) -> dict:
    return json.loads((ARTIFACT / name).read_text(encoding="utf-8"))


def _median(payload: dict) -> float:
    protocol = payload["metadata"].get("prepared_query_repeat_protocol")
    if protocol is None:
        return float(payload["elapsed_sec"])
    if "elapsed_sec_median" in protocol:
        return float(protocol["elapsed_sec_median"])
    return float(protocol["median_elapsed_sec"])


class Goal3988RtDbscanPartnerOpponentProbeTest(unittest.TestCase):
    def test_all_opponent_routes_emit_same_signature(self) -> None:
        payloads = {
            path.name: _load(path.name)
            for path in ARTIFACT.glob("*.stdout.json")
        }
        self.assertEqual(len(payloads), 4)
        signatures = {json.dumps(payload["signature"], sort_keys=True) for payload in payloads.values()}
        self.assertEqual(len(signatures), 1)
        for stdout_name in payloads:
            stderr = ARTIFACT / stdout_name.replace(".stdout.json", ".stderr.log")
            self.assertEqual(stderr.read_text(encoding="utf-8"), "")

    def test_rtdl_optix_grouped_stream_beats_partner_only_opponents(self) -> None:
        grouped = _load("optix_rt_core_grouped_stream_numba_column_signature_3d.stdout.json")
        flags = _load("optix_rt_core_flags_numba_prepared_grid_column_signature_3d.stdout.json")
        numba = _load("partner_numba_prepared_grid_components_3d.stdout.json")
        cupy = _load("partner_cupy_prepared_grid_components_3d.stdout.json")
        grouped_median = _median(grouped)
        self.assertTrue(grouped["metadata"]["rt_core_accelerated"])
        self.assertEqual(grouped["metadata"]["partner"], "numba")
        self.assertLess(grouped_median, _median(flags))
        self.assertLess(grouped_median, _median(numba))
        self.assertLess(grouped_median, _median(cupy))
        self.assertGreater(_median(numba) / grouped_median, 10.0)
        self.assertGreater(_median(cupy) / grouped_median, 50.0)

    def test_report_records_boundary_and_next_runtime_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "RTDL/OptiX grouped stream remains the fastest",
            "primitive-first RTDL/OptiX benchmark row",
            "less parent-workspace atomic contention",
            "does not authorize public speedup wording",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()

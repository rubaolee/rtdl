import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3987_rt_dbscan_blocked_grouped_negative_probe_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3987_rt_dbscan_blocked_grouped_probe_2026-06-08"


def _load(name: str) -> dict:
    return json.loads((ARTIFACT / name).read_text(encoding="utf-8"))


class Goal3987RtDbscanBlockedGroupedNegativeProbeTest(unittest.TestCase):
    def test_all_probe_files_exist_and_stderr_empty(self) -> None:
        expected = {
            "optix_rt_core_grouped_stream_numba_column_signature_3d.stdout.json",
            "optix_rt_core_grouped_stream_numba_column_signature_3d_direct_side_effect.stdout.json",
            "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d_bs2048.stdout.json",
            "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d_bs4096.stdout.json",
            "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d_bs8192.stdout.json",
            "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d_bs16384.stdout.json",
            "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d_bs32768.stdout.json",
        }
        actual = {path.name for path in ARTIFACT.glob("*.stdout.json")}
        self.assertEqual(actual, expected)
        for stdout_name in expected:
            stderr = ARTIFACT / stdout_name.replace(".stdout.json", ".stderr.log")
            self.assertEqual(stderr.read_text(encoding="utf-8"), "")

    def test_blocked_variants_do_not_beat_unblocked(self) -> None:
        baseline = _load("optix_rt_core_grouped_stream_numba_column_signature_3d.stdout.json")
        baseline_median = baseline["metadata"]["prepared_query_repeat_protocol"]["elapsed_sec_median"]
        baseline_signature = baseline["signature"]
        for block_size in (2048, 4096, 8192, 16384, 32768):
            with self.subTest(block_size=block_size):
                payload = _load(
                    f"optix_rt_core_grouped_stream_blocked_numba_column_signature_3d_bs{block_size}.stdout.json"
                )
                self.assertEqual(payload["signature"], baseline_signature)
                self.assertGreater(
                    payload["metadata"]["prepared_query_repeat_protocol"]["elapsed_sec_median"],
                    baseline_median,
                )
                self.assertTrue(payload["metadata"]["grouped_union_query_blocked_candidate"])
                self.assertEqual(payload["metadata"]["grouped_union_query_block_size"], block_size)

    def test_direct_side_effect_is_not_a_material_speedup(self) -> None:
        baseline = _load("optix_rt_core_grouped_stream_numba_column_signature_3d.stdout.json")
        direct = _load("optix_rt_core_grouped_stream_numba_column_signature_3d_direct_side_effect.stdout.json")
        baseline_median = baseline["metadata"]["prepared_query_repeat_protocol"]["elapsed_sec_median"]
        direct_median = direct["metadata"]["prepared_query_repeat_protocol"]["elapsed_sec_median"]
        self.assertEqual(direct["signature"], baseline["signature"])
        self.assertTrue(
            direct["metadata"]["native_grouped_stream_metadata"]["grouped_union_direct_side_effect_enabled"]
        )
        self.assertLess(abs(direct_median - baseline_median), 0.005)

    def test_report_records_next_design_target_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "No existing switch wins",
            "grouped-union atomic pressure",
            "without introducing DBSCAN-specific engine vocabulary",
            "does not authorize release",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()

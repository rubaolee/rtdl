from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4093_partition_summary_non_skip_pair_stream_2026-06-09.md"
BASELINE = ROOT / "docs" / "reports" / "goal4088_partition_summary_build_after_host_aabb_skip_pod.json"
BUILD = ROOT / "docs" / "reports" / "goal4093_partition_summary_non_skip_pair_stream_pod.json"
REUSE = ROOT / "docs" / "reports" / "goal4093_partition_non_skip_reuse_pod.json"


class Goal4093PartitionSummaryNonSkipPairStreamTest(unittest.TestCase):
    def test_source_exposes_explicit_non_skip_device_mode(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        for fragment in [
            "device_count_then_emit_non_skip",
            "emit_status_filter",
            "non_skip_actionable_pairs",
            "safe_skip_pairs_elided",
            "device_exact_active_count",
            "if (emit_non_skip_only != 0u && status == 0u) return;",
        ]:
            self.assertIn(fragment, source)
        self.assertIn("device_count_then_emit_non_skip", app)

    def test_pod_artifact_records_active_pair_stream_reduction(self) -> None:
        import json

        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        build = json.loads(BUILD.read_text(encoding="utf-8"))
        self.assertEqual(build["source_commit"][:8], "28291d11")
        baseline_rows = {row["profile"]: row for row in baseline["rows"]}
        build_rows = {row["profile"]: row for row in build["rows"]}
        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            old = baseline_rows[profile]
            new = build_rows[profile]
            self.assertEqual(new["pair_capacity_source"], "device_exact_active_count")
            self.assertEqual(new["pair_enumeration"], "device_count_then_emit_non_skip")
            self.assertEqual(new["status_counts"]["safe_skip_partition_pairs"], 0)
            self.assertLess(new["pair_count"], old["pair_count"])
            self.assertLess(
                new["partition_summary_build_sec"]["median_sec"],
                old["partition_summary_build_sec"]["median_sec"],
            )
            for sample in new["samples"]:
                self.assertEqual(sample["pair_stream_filter"], "non_skip_actionable_pairs")
                self.assertTrue(sample["safe_skip_pairs_elided"])

    def test_reuse_artifact_keeps_default_route_policy_closed(self) -> None:
        import json

        reuse = json.loads(REUSE.read_text(encoding="utf-8"))
        self.assertEqual(reuse["source_commit"][:8], "28291d11")
        rows = {row["profile"]: row for row in reuse["rows"]}
        self.assertLess(rows["clustered3d"]["amortized"]["break_even_runs_reference"], 8.0)
        self.assertIsNone(rows["road3d"]["amortized"]["break_even_runs_reference"])
        self.assertLess(rows["clustered3d"]["amortized"]["speedup_vs_current_reference_for_n_runs"], 1.0)
        self.assertLess(rows["road3d"]["amortized"]["speedup_vs_current_reference_for_n_runs"], 1.0)
        self.assertFalse(reuse["release_authorized"])
        self.assertFalse(reuse["native_abi_added"])

    def test_report_keeps_non_skip_mode_explicit_and_unpromoted(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "device_count_then_emit_non_skip",
            "non_skip_actionable_pairs",
            "1.795x",
            "2.635x",
            "Do not promote it as the RT-DBSCAN default route",
            "does not promote",
        ]:
            self.assertIn(fragment, report)

    def test_non_skip_mode_preserves_small_component_signature_when_cupy_available(self) -> None:
        try:
            import cupy  # noqa: F401
        except Exception:
            self.skipTest("CuPy is not available in this local environment")

        points = [
            (0.00, 0.00, 0.00),
            (0.01, 0.00, 0.00),
            (0.02, 0.00, 0.00),
            (1.00, 1.00, 1.00),
            (1.01, 1.00, 1.00),
            (4.00, 4.00, 4.00),
        ]
        all_pairs = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
            points,
            radius=0.05,
            cell_factor=0.5,
            pair_enumeration="device_count_then_emit",
            validate_summary_same_contract=False,
            validate_against_component_labels=False,
        )
        non_skip = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
            points,
            radius=0.05,
            cell_factor=0.5,
            pair_enumeration="device_count_then_emit_non_skip",
            validate_summary_same_contract=False,
            validate_against_component_labels=False,
        )
        self.assertEqual(
            tuple(all_pairs["columns"]["component_size_signature"]),
            tuple(non_skip["columns"]["component_size_signature"]),
        )
        self.assertEqual(non_skip["metadata"]["partition_summary_pair_enumeration"], "device_count_then_emit_non_skip")
        self.assertEqual(non_skip["metadata"]["partition_summary_pair_capacity_source"], "device_exact_active_count")
        self.assertEqual(non_skip["metadata"]["partition_summary_pair_stream_filter"], "non_skip_actionable_pairs")
        self.assertTrue(non_skip["metadata"]["partition_summary_safe_skip_pairs_elided"])
        self.assertLess(
            non_skip["metadata"]["partition_summary_pair_count"],
            all_pairs["metadata"]["partition_summary_pair_count"],
        )


if __name__ == "__main__":
    unittest.main()

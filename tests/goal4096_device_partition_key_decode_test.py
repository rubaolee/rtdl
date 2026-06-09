from __future__ import annotations

import pathlib
import unittest
import json

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4096_device_partition_key_decode_2026-06-09.md"
BASELINE = ROOT / "docs" / "reports" / "goal4095_partition_convergence_phase_breakdown_pod.json"
ARTIFACT = ROOT / "docs" / "reports" / "goal4096_device_partition_key_decode_phase_breakdown_pod.json"
STDOUT = ROOT / "docs" / "reports" / "goal4096_device_partition_key_decode_phase_breakdown_pod.stdout.txt"
BUILD_BASELINE = ROOT / "docs" / "reports" / "goal4093_partition_summary_non_skip_pair_stream_pod.json"
BUILD = ROOT / "docs" / "reports" / "goal4096_partition_summary_build_after_device_key_decode_pod.json"
REUSE_BASELINE = ROOT / "docs" / "reports" / "goal4093_partition_non_skip_reuse_pod.json"
REUSE = ROOT / "docs" / "reports" / "goal4096_partition_reuse_after_device_key_decode_pod.json"


class Goal4096DevicePartitionKeyDecodeTest(unittest.TestCase):
    def test_device_pair_kernel_decodes_unique_cells_without_host_key_arrays(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")

        self.assertIn("const long long encoded = unique_cells[left];", source)
        self.assertIn("const long long base_x = encoded / plane;", source)
        self.assertIn("occupied_key_x = (local_key_x + min_kx).astype", source)
        self.assertNotIn("const int* key_x", source)
        self.assertNotIn("const int* key_y", source)
        self.assertNotIn("const int* key_z", source)
        self.assertNotIn("key_rows=key_rows", source)

    def test_non_skip_device_mode_preserves_small_signature_when_cupy_available(self) -> None:
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
        result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
            points,
            radius=0.05,
            cell_factor=0.5,
            pair_enumeration="device_count_then_emit_non_skip",
            validate_summary_same_contract=False,
            validate_against_component_labels=True,
        )
        self.assertEqual(result["metadata"]["status"], "accept")
        self.assertTrue(result["metadata"]["same_contract_against_component_labels"])
        self.assertEqual(tuple(result["columns"]["component_size_signature"]), (1, 2, 3))

    def test_pod_artifact_records_build_speedup_against_goal4095(self) -> None:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["source_commit"][:8], "0619c6e3")
        self.assertFalse(artifact["release_authorized"])
        self.assertFalse(artifact["native_abi_added"])
        old_rows = {row["profile"]: row for row in baseline["rows"]}
        new_rows = {row["profile"]: row for row in artifact["rows"]}
        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            old_build = old_rows[profile]["phase_summary"]["build_total_sec"]["median_sec"]
            new_build = new_rows[profile]["phase_summary"]["build_total_sec"]["median_sec"]
            old_other = old_rows[profile]["phase_summary"]["build_uninstrumented_sec"]["median_sec"]
            new_other = new_rows[profile]["phase_summary"]["build_uninstrumented_sec"]["median_sec"]
            self.assertLess(new_build, old_build, profile)
            self.assertLess(new_other, old_other, profile)
            self.assertEqual(new_rows[profile]["pair_stream_filter"], "non_skip_actionable_pairs")
            self.assertTrue(new_rows[profile]["safe_skip_pairs_elided"])
        ngsim_old = old_rows["ngsim_dense"]["phase_summary"]["build_total_sec"]["median_sec"]
        ngsim_new = new_rows["ngsim_dense"]["phase_summary"]["build_total_sec"]["median_sec"]
        self.assertGreater(ngsim_old / ngsim_new, 1.4)

    def test_build_and_reuse_artifacts_keep_route_unpromoted(self) -> None:
        build_baseline = json.loads(BUILD_BASELINE.read_text(encoding="utf-8"))
        build = json.loads(BUILD.read_text(encoding="utf-8"))
        reuse_baseline = json.loads(REUSE_BASELINE.read_text(encoding="utf-8"))
        reuse = json.loads(REUSE.read_text(encoding="utf-8"))

        self.assertEqual(build["source_commit"][:8], "765a271b")
        self.assertEqual(reuse["source_commit"][:8], "765a271b")
        old_build = {row["profile"]: row for row in build_baseline["rows"]}
        new_build = {row["profile"]: row for row in build["rows"]}
        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            old_sec = old_build[profile]["partition_summary_build_sec"]["median_sec"]
            new_sec = new_build[profile]["partition_summary_build_sec"]["median_sec"]
            self.assertLess(new_sec, old_sec, profile)
        self.assertGreater(
            old_build["ngsim_dense"]["partition_summary_build_sec"]["median_sec"]
            / new_build["ngsim_dense"]["partition_summary_build_sec"]["median_sec"],
            1.4,
        )

        old_reuse = {row["profile"]: row for row in reuse_baseline["rows"]}
        new_reuse = {row["profile"]: row for row in reuse["rows"]}
        self.assertLess(new_reuse["clustered3d"]["prepare_sec"], old_reuse["clustered3d"]["prepare_sec"])
        self.assertLess(new_reuse["road3d"]["prepare_sec"], old_reuse["road3d"]["prepare_sec"])
        self.assertLess(new_reuse["clustered3d"]["amortized"]["speedup_vs_current_reference_for_n_runs"], 1.0)
        self.assertLess(new_reuse["road3d"]["amortized"]["speedup_vs_current_reference_for_n_runs"], 1.0)
        self.assertIsNone(new_reuse["road3d"]["amortized"]["break_even_runs_reference"])
        self.assertFalse(reuse["release_authorized"])
        self.assertFalse(reuse["native_abi_added"])

    def test_stdout_and_report_document_boundary(self) -> None:
        stdout = STDOUT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("PROFILE_PHASE_WARMUP_START clustered3d", stdout)
        self.assertIn("PROFILE_PHASE_SAMPLE", stdout)
        for fragment in [
            "decode",
            "1.479x",
            "2.026x",
            "0.849x",
            "current grouped-stream Numba route remains",
            "generic fused/native fixed-radius",
            "does not promote",
            "authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()

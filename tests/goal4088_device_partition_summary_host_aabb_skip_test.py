from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4088_device_partition_summary_host_aabb_skip_2026-06-09.md"
BASELINE = ROOT / "docs" / "reports" / "goal4085_partition_summary_build_feasibility_pod.json"
BUILD = ROOT / "docs" / "reports" / "goal4088_partition_summary_build_after_host_aabb_skip_pod.json"
REUSE = ROOT / "docs" / "reports" / "goal4088_partition_reuse_after_host_aabb_skip_pod.json"
STDOUT = ROOT / "docs" / "reports" / "goal4088_partition_summary_build_after_host_aabb_skip_pod.stdout.txt"


class Goal4088DevicePartitionSummaryHostAabbSkipTest(unittest.TestCase):
    def test_host_aabb_rebuild_is_limited_to_host_pair_enumeration(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        function = source.split(
            "def build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d",
            1,
        )[1].split(
            "def _skipped_partition_summary_prepare_validation",
            1,
        )[0]
        before_host_branch = function.split('if pair_enumeration == "host":', 1)[0]
        host_branch = function.split('if pair_enumeration == "host":', 1)[1].split("else:", 1)[0]
        self.assertIn("key_rows.append", before_host_branch)
        self.assertNotIn("cupy.asnumpy(point_partition_ids)", before_host_branch)
        self.assertIn("cupy.asnumpy(point_partition_ids)", host_branch)

    def test_build_probe_improves_all_current_profiles_without_changing_counts(self) -> None:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        build = json.loads(BUILD.read_text(encoding="utf-8"))
        self.assertEqual(build["source_commit"][:8], "b5cb7968")
        baseline_rows = {row["profile"]: row for row in baseline["rows"]}
        build_rows = {row["profile"]: row for row in build["rows"]}
        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            old = baseline_rows[profile]
            new = build_rows[profile]
            self.assertEqual(new["pair_count"], old["pair_count"])
            self.assertEqual(new["status_counts"], old["status_counts"])
            self.assertLess(
                new["partition_summary_build_sec"]["median_sec"],
                old["partition_summary_build_sec"]["median_sec"],
            )
            self.assertFalse(new["release_authorized"])
            self.assertFalse(new["native_abi_added"])

    def test_reuse_probe_updates_break_even_but_keeps_default_policy_closed(self) -> None:
        reuse = json.loads(REUSE.read_text(encoding="utf-8"))
        self.assertEqual(reuse["source_commit"][:8], "b5cb7968")
        rows = {row["profile"]: row for row in reuse["rows"]}
        self.assertLess(rows["clustered3d"]["amortized"]["break_even_runs_reference"], 9.0)
        self.assertLess(rows["clustered3d"]["amortized"]["speedup_vs_current_reference_for_n_runs"], 1.0)
        self.assertIsNone(rows["road3d"]["amortized"]["break_even_runs_reference"])
        self.assertLess(rows["road3d"]["amortized"]["speedup_vs_current_reference_for_n_runs"], 1.0)
        self.assertFalse(reuse["release_authorized"])
        self.assertFalse(reuse["native_abi_added"])

    def test_report_and_stdout_capture_boundary_and_progress(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "2.129x",
            "2.289x",
            "1.643x",
            "break-even point drops",
            "should not change the current recommended route",
            "does not promote",
        ]:
            self.assertIn(fragment, report)
        stdout = STDOUT.read_text(encoding="utf-8")
        self.assertIn("PROFILE_MEASURE clustered3d", stdout)
        self.assertIn("PROFILE_MEASURE road3d", stdout)
        self.assertIn("PROFILE_MEASURE ngsim_dense", stdout)


if __name__ == "__main__":
    unittest.main()

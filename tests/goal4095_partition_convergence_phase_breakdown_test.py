from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal4095_partition_convergence_phase_breakdown.py"
REPORT = ROOT / "docs" / "reports" / "goal4095_partition_convergence_phase_breakdown_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4095_partition_convergence_phase_breakdown_pod.json"
STDOUT = ROOT / "docs" / "reports" / "goal4095_partition_convergence_phase_breakdown_pod.stdout.txt"


class Goal4095PartitionConvergencePhaseBreakdownTest(unittest.TestCase):
    def test_runner_instruments_pair_status_and_union_phases(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for fragment in [
            "_timed_partition_pair_status",
            "_timed_partition_union",
            "pair_status_count_probe",
            "pair_status_emit",
            "ambiguous_partition_point_union",
            "device_count_then_emit_non_skip",
        ]:
            self.assertIn(fragment, source)

    def test_pod_artifact_records_phase_breakdown(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual("Goal4095", artifact["goal"])
        self.assertEqual("device_count_then_emit_non_skip", artifact["pair_enumeration"])
        self.assertEqual(artifact["source_commit"][:8], "c56596f8")
        self.assertFalse(artifact["release_authorized"])
        self.assertFalse(artifact["native_abi_added"])
        rows = {row["profile"]: row for row in artifact["rows"]}
        self.assertEqual({"clustered3d", "road3d", "ngsim_dense"}, set(rows))
        for profile, row in rows.items():
            phase = row["phase_summary"]
            build = float(phase["build_total_sec"]["median_sec"])
            count_probe = float(phase["pair_status_count_probe_sec"]["median_sec"])
            emit = float(phase["pair_status_emit_sec"]["median_sec"])
            other = float(phase["build_uninstrumented_sec"]["median_sec"])
            signature = float(phase["signature_total_sec"]["median_sec"])
            ambiguous = float(phase["ambiguous_partition_point_union_sec"]["median_sec"])
            self.assertGreater(build, 0.0, profile)
            self.assertGreater(count_probe, 0.0, profile)
            self.assertGreater(emit, 0.0, profile)
            self.assertGreater(other, 0.0, profile)
            self.assertGreater(signature, ambiguous, profile)
            self.assertEqual("non_skip_actionable_pairs", row["pair_stream_filter"])
            self.assertTrue(row["safe_skip_pairs_elided"])
            self.assertEqual(0, row["status_counts"]["safe_skip_partition_pairs"])
        clustered = rows["clustered3d"]["phase_summary"]
        self.assertGreater(
            clustered["build_uninstrumented_sec"]["median_sec"],
            clustered["pair_status_emit_sec"]["median_sec"],
        )
        ngsim = rows["ngsim_dense"]["phase_summary"]
        self.assertGreater(
            ngsim["pair_status_count_probe_sec"]["median_sec"] + ngsim["pair_status_emit_sec"]["median_sec"],
            ngsim["build_uninstrumented_sec"]["median_sec"],
        )

    def test_stdout_has_progress_lines(self) -> None:
        stdout = STDOUT.read_text(encoding="utf-8")
        for fragment in [
            "PROFILE_PHASE_WARMUP_START clustered3d",
            "PROFILE_PHASE_MEASURE_START road3d",
            "PROFILE_PHASE_SAMPLE",
            "\"profile\": \"ngsim_dense\"",
        ]:
            self.assertIn(fragment, stdout)

    def test_report_points_to_fused_native_producer_without_overclaim(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "43.9%",
            "59.1%",
            "runs a count probe and an emit pass",
            "fixed-radius grouped-union producer",
            "does not promote",
            "authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()

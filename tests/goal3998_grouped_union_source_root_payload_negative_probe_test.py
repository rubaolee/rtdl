from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
BASELINE = ROOT / "docs" / "reports" / "goal3996_grouped_union_extended_telemetry_sweep_pod.json"
ARTIFACT = ROOT / "docs" / "reports" / "goal3998_grouped_union_source_root_payload_sweep_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal3998_grouped_union_source_root_payload_negative_probe_2026-06-08.md"


class Goal3998GroupedUnionSourceRootPayloadNegativeProbeTest(unittest.TestCase):
    def test_failed_source_root_payload_experiment_is_not_promoted(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        grouped_union = core[
            core.index("kFixedRadiusGroupedUnion3DRtKernelSrc"):
            core.index(")CUDA\";", core.index("kFixedRadiusGroupedUnion3DRtKernelSrc"))
        ]
        self.assertNotIn("source_root_payload", grouped_union)
        self.assertNotIn("optixGetPayload_1()", grouped_union)
        self.assertIn("nullptr, 1).release();", workloads)

    def test_pod_artifact_rejects_source_root_payload_for_default_mode(self) -> None:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal3998")
        self.assertEqual(artifact["status"], "pass")
        self.assertFalse(artifact["claim_boundary"]["performance_claim_authorized"])
        for point_count in (4096, 16384, 65536):
            base_row = next(row for row in baseline["rows"] if row["point_count"] == point_count)
            new_row = next(row for row in artifact["rows"] if row["point_count"] == point_count)
            base_default = next(
                variant for variant in base_row["variants"]
                if variant["label"] == "same_root_on_direct_off"
            )
            new_default = next(
                variant for variant in new_row["variants"]
                if variant["label"] == "same_root_on_direct_off"
            )
            self.assertGreater(
                new_default["median_native_elapsed_sec"],
                base_default["median_native_elapsed_sec"],
            )
            self.assertGreater(
                new_default["last_telemetry"][7],
                base_default["last_telemetry"][7],
            )

    def test_report_records_rejection_and_next_generic_direction(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "`reject`",
            "native experiment was reverted",
            "No source-root payload optimization is promoted",
            "too stale for concurrent union-find",
            "convergence-aware or partition-assisted strategy",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()

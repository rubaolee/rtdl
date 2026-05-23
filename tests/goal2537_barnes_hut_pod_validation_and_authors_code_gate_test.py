from pathlib import Path
import json
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2537_barnes_hut_pod_validation_and_authors_code_gate_2026-05-23.md"
)
POD_TIMING = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2537_barnes_hut_pod_rtdl_reference_timing_2026-05-23.json"
)
POD_CPU_BASELINE = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2537_barnes_hut_pod_cpu_baseline_8192_2026-05-23.json"
)
AUTHORS_CONFIGURE_LOG = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2537_barnes_hut_authors_code_cmake_configure_pod_2026-05-23.txt"
)


class Goal2537BarnesHutPodValidationAndAuthorsCodeGateTest(unittest.TestCase):
    def test_report_records_pod_environment_and_validation_boundary(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "ssh root@203.57.40.169 -p 10297 -i ~/.ssh/id_ed25519_rtdl_codex",
            "NVIDIA RTX A5000",
            "35 tests OK",
            "not public speedup evidence",
            "not an RTDL public speedup packet",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_timing_artifact_records_streamed_boundary(self) -> None:
        payload = json.loads(POD_TIMING.read_text())
        self.assertIn("not OptiX timing", payload["claim_boundary"])
        records = {(record["body_count"], record["mode"]): record for record in payload["records"]}
        materialized = records[(8192, "bucketized_force_cpu")]
        streamed = records[(8192, "streamed_force_sum_bucketized_cpu")]
        pressure = records[(8192, "materialization_pressure_bucketized_cpu")]
        self.assertEqual(materialized["vector_sum_summary"]["contribution_row_count"], 1188963)
        self.assertEqual(streamed["vector_sum_summary"]["contribution_row_count"], 1188963)
        self.assertFalse(streamed["vector_sum_summary"]["materialized_contribution_rows"])
        self.assertEqual(
            pressure["materialization_pressure"]["summary"]["recommended_execution"],
            "streamed_or_native_fused",
        )
        self.assertAlmostEqual(materialized["checksum_force_x"], streamed["checksum_force_x"])
        self.assertAlmostEqual(materialized["checksum_force_y"], streamed["checksum_force_y"])

    def test_exact_cpu_baseline_artifact_is_marked_as_non_authors_code(self) -> None:
        payload = json.loads(POD_CPU_BASELINE.read_text())
        metadata = payload["metadata"]
        self.assertFalse(metadata["authors_code_comparison"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["same_contract_as_paper_code"])
        by_threads = {record["threads"]: record["elapsed_ms"] for record in payload["runs"]}
        self.assertIn(1, by_threads)
        self.assertIn(4, by_threads)
        self.assertIn(16, by_threads)
        self.assertGreater(by_threads[1], by_threads[4])
        self.assertGreater(by_threads[4], by_threads[16])

    def test_authors_code_gate_records_missing_optix_sdk(self) -> None:
        report_text = REPORT.read_text()
        log_text = AUTHORS_CONFIGURE_LOG.read_text()
        for phrase in [
            "https://github.com/vani-nag/OWLRayTracing",
            "BarnesHutRT",
            "2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7",
            "samples/cmdline/s01-rtbarneshut",
            "Could NOT find OptiX",
            "OptiX_ROOT_DIR",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("Could NOT find OptiX", log_text)
        self.assertIn("missing: OptiX_ROOT_DIR", log_text)

    def test_report_preserves_fused_generic_next_target(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "generic_aggregate_frontier_weighted_vector_sum_2d_v1",
            "no Python frontier/contribution-row materialization",
            "no Barnes-Hut app name or app-specific ABI",
            "The authors-code comparison should be retried only after OptiX SDK availability",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

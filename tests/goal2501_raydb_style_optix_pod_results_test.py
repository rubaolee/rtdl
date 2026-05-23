import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2501_raydb_style_optix_pod_validation_results_2026-05-22.md"
ENV = ROOT / "docs/reports/goal2501_raydb_style_pod_environment_2026-05-22.txt"
BUILD_LOG = ROOT / "docs/reports/goal2501_make_build_optix_2026-05-22.txt"
SUITE_LOG = ROOT / "docs/reports/goal2501_raydb_style_focused_suite_pod_2026-05-22.txt"
APP_JSON = ROOT / "docs/reports/goal2501_raydb_style_optix_app_pod_2026-05-22.json"
MATRIX_JSON = ROOT / "docs/reports/goal2501_raydb_style_backend_matrix_pod_2026-05-22.json"


class Goal2501RaydbStyleOptixPodResultsTest(unittest.TestCase):
    def test_environment_records_exact_pod_and_dependencies(self) -> None:
        text = ENV.read_text(encoding="utf-8")
        self.assertIn("ssh=root@69.30.85.198 -p 22017 -i ~/.ssh/id_ed25519_rtdl_codex", text)
        self.assertIn("NVIDIA RTX A5000", text)
        self.assertIn("570.211.01", text)
        self.assertIn("Cuda compilation tools, release 12.8", text)
        self.assertIn("#define OPTIX_VERSION 90000", text)
        self.assertIn("a9193856547bf692069955a3dbaf6c3e00c09b1b", text)

    def test_build_and_suite_logs_passed(self) -> None:
        build = BUILD_LOG.read_text(encoding="utf-8")
        suite = SUITE_LOG.read_text(encoding="utf-8")
        self.assertIn("BUILD_RC=0", build)
        self.assertIn("build/librtdl_optix.so", build)
        self.assertIn("Ran 31 tests", suite)
        self.assertIn("OK (skipped=2)", suite)

    def test_optix_app_payload_matches_cpu_reference(self) -> None:
        payload = json.loads(APP_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["backend"], "optix")
        self.assertTrue(payload["all_match_cpu_reference"])
        for mode in ("count", "sum"):
            mode_payload = payload["modes"][mode]
            self.assertTrue(mode_payload["matches_cpu_reference"])
            metadata = mode_payload["metadata"]
            self.assertEqual(metadata["contract"], "columnar_grouped_aggregate_optix_columnar_payload")
            self.assertFalse(metadata["native_abi_added"])
            self.assertTrue(metadata["rt_core_accelerated"])
            self.assertFalse(metadata["lowering_plan"]["true_zero_copy_authorized"])
            self.assertTrue(metadata["lowering_plan"]["uses_compatibility_wrapper"])

    def test_matrix_payload_records_optix_ok(self) -> None:
        payload = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
        optix = payload["cases"]["optix"]
        self.assertEqual(optix["status"], "ok")
        self.assertTrue(optix["all_match_cpu_reference"])
        self.assertTrue(optix["modes"]["count"]["matches_cpu_reference"])
        self.assertTrue(optix["modes"]["sum"]["matches_cpu_reference"])
        self.assertIn("diagnostic", payload["claim_boundary"])
        self.assertIn("do not authorize public speedup", payload["claim_boundary"])

    def test_report_blocks_overclaims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("OptiX runtime parity is validated", text)
        for phrase in (
            "RayDB reproduction",
            "authors-code comparison",
            "SQL engine or DBMS behavior",
            "public speedup wording",
            "true zero-copy wording",
            "whole-app acceleration",
            "min/max/avg native OptiX support",
            "new app-specific native ABI",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

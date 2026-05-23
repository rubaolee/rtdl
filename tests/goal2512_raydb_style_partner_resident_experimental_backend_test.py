from importlib import util
import json
from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
MATRIX_SCRIPT = ROOT / "scripts/goal2500_raydb_style_backend_matrix.py"
POD_SCRIPT = ROOT / "scripts/goal2512_raydb_style_partner_resident_backend_pod.py"
POD_ARTIFACT = ROOT / "docs/reports/goal2512_raydb_style_partner_resident_backend_pod_2026-05-22.json"
REPORT = ROOT / "docs/reports/goal2512_raydb_style_partner_resident_experimental_backend_2026-05-22.md"
README = ROOT / "examples/v2_0/research_benchmarks/raydb_style/README.md"


def _load_matrix():
    spec = util.spec_from_file_location("goal2500_raydb_style_backend_matrix", MATRIX_SCRIPT)
    assert spec is not None
    module = util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal2512RaydbStylePartnerResidentExperimentalBackendTest(unittest.TestCase):
    def test_backend_is_explicit_not_default(self) -> None:
        self.assertEqual(app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND, "optix_partner_resident_experimental")
        self.assertEqual(
            app.OPTIX_PARTNER_RESIDENT_RESULT_MODES,
            ("count", "sum", "min", "max", "avg_as_sum_count"),
        )
        self.assertIn(app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND, app.BACKENDS)
        matrix = _load_matrix()
        self.assertNotIn(app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND, matrix.DEFAULT_BACKENDS)
        self.assertIn(app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND, matrix.AVAILABLE_BACKENDS)

    def test_lowering_plan_records_experimental_partner_resident_boundary(self) -> None:
        plan = rt.plan_columnar_aggregate_lowering(app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND).to_dict()
        self.assertEqual(plan["supported_aggregates"], ["count", "sum", "min", "max", "avg_as_sum_count"])
        self.assertEqual(
            plan["transfer_path"],
            "partner_resident_cuda_column_descriptors_to_experimental_optix_grouped_i64",
        )
        self.assertFalse(plan["materializes_input_rows_for_wrapper"])
        self.assertFalse(plan["true_zero_copy_authorized"])
        self.assertIn("Experimental partner-resident OptiX", plan["claim_boundary"])

    def test_unsupported_aggregate_fails_before_requiring_cuda(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported result mode"):
            app.run_result_mode("not_a_mode", backend=app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND)

    def test_matrix_records_unavailable_experimental_backend_as_skip_or_ok(self) -> None:
        matrix = _load_matrix()
        payload = matrix.run_matrix(backends=(app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND,), repeats=1)
        case = payload["cases"][app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND]
        self.assertIn(case["status"], {"skipped", "ok"})
        if case["status"] == "skipped":
            self.assertRegex(case["reason"], "PyTorch|CUDA|OptiX|librtdl_optix")
        else:
            self.assertEqual(set(case["modes"]), {"count", "sum", "min", "max", "avg_as_sum_count"})
            self.assertTrue(case["all_match_cpu_reference"])

    def test_docs_and_runner_record_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        runner = POD_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("optix_partner_resident_experimental", report)
        self.assertIn("No RayDB reproduction", report)
        self.assertIn("true zero-copy", report)
        self.assertIn("all_match_cpu_reference: true", report)
        self.assertIn("optix_partner_resident_experimental", readme)
        self.assertIn("run_suite", runner)
        self.assertIn("all_match_cpu_reference", runner)

    def test_pod_artifact_records_experimental_backend_parity(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["backend"], app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND)
        self.assertIs(payload["cuda_available"], True)
        self.assertIs(payload["all_match_cpu_reference"], True)
        suite = payload["suite"]
        self.assertIs(suite["all_match_cpu_reference"], True)
        self.assertEqual(suite["modes"]["count"]["metadata"]["group_capacity"], 3)
        self.assertEqual(suite["modes"]["sum"]["metadata"]["group_capacity"], 3)
        self.assertEqual(
            suite["modes"]["count"]["rows"],
            [
                {"count": 2, "region_id": 0},
                {"count": 1, "region_id": 1},
                {"count": 1, "region_id": 2},
            ],
        )
        self.assertEqual(
            suite["modes"]["sum"]["rows"],
            [
                {"region_id": 0, "sum": 190},
                {"region_id": 1, "sum": 200},
                {"region_id": 2, "sum": 80},
            ],
        )
        case = payload["matrix"]["cases"][app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND]
        self.assertEqual(case["status"], "ok")
        self.assertIs(case["all_match_cpu_reference"], True)
        self.assertIn("No RayDB reproduction", payload["claim_boundary"])


if __name__ == "__main__":
    unittest.main()

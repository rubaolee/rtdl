from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MATCHED = ROOT / "experiments" / "goal5796_matched"
SPEC = MATCHED / "semantic_spec.json"
PYOPTIX = ROOT / ".tmp_goal5796_upstream_20260823" / "otk-pyoptix"
OWL = ROOT / ".tmp_goal5796_upstream_20260823" / "OWL"


def load_oracle():
    path = MATCHED / "independent_oracle.py"
    spec = importlib.util.spec_from_file_location("goal5796_independent_oracle", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


class Goal5796MatchedImplementationsTest(unittest.TestCase):
    def test_frozen_spec_and_independent_oracle(self) -> None:
        spec_bytes = SPEC.read_bytes()
        self.assertEqual(
            hashlib.sha256(spec_bytes).hexdigest(),
            "88bc8468c78302ed18cb3176e70a6c1dea65bc8306bf5e747bc18dea1e3fac4b",
        )
        data = json.loads(spec_bytes)
        oracle = load_oracle()
        expected = oracle.build_expected(data)
        self.assertEqual(
            oracle.digest(expected),
            "8f10d4ff7560e5bcabf47a3989a22ab870b302c6fd418243fd56c4ae5becaadb",
        )
        self.assertEqual(expected["triangle"], {"per_ray": [3, 2, 0, 1], "weighted_sum": 16})
        self.assertEqual(len(expected["bounded_relation"]), 4)
        witness = data["tasks"]["CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"][
            "overflow_witness"]
        self.assertEqual(witness["capacity"], 7)
        self.assertEqual(witness["expected_unique_row_count"], 8)

    def test_route_independence_and_public_import_boundary(self) -> None:
        oracle_imports = imported_roots(MATCHED / "independent_oracle.py")
        self.assertTrue({"rtdsl", "optix", "cupy", "cuda"}.isdisjoint(oracle_imports))
        pyoptix_imports = imported_roots(MATCHED / "pyoptix_baseline.py")
        self.assertNotIn("rtdsl", pyoptix_imports)
        rtdl_source = (MATCHED / "rtdl_baseline.py").read_text(encoding="utf-8")
        self.assertIn("from rtdsl.v4 import (", rtdl_source)
        self.assertNotIn("_load_optix_library", rtdl_source)
        self.assertNotIn("v4_prepared_provider", rtdl_source)
        self.assertNotIn("paper_apps", rtdl_source)
        direct = (MATCHED / "direct_optix.cpp").read_text(encoding="utf-8")
        self.assertNotIn("rtdsl", direct.lower())
        self.assertNotIn("pyoptix", direct.lower())
        self.assertNotIn("owl", direct.lower())

    def test_same_device_source_covers_both_geometry_mechanisms(self) -> None:
        source = (MATCHED / "matched_device.cu").read_text(encoding="utf-8")
        for literal in (
            "__intersection__goal5796_relation",
            "__anyhit__goal5796_relation",
            "__anyhit__goal5796_triangle",
            "OPTIX_RAY_FLAG_NONE",
            "atomicExch(params.status",
            "optixIgnoreIntersection()",
        ):
            self.assertIn(literal, source)
        direct = (MATCHED / "direct_optix.cpp").read_text(encoding="utf-8")
        pyoptix = (MATCHED / "pyoptix_baseline.py").read_text(encoding="utf-8")
        self.assertIn("read_file(argv[1])", direct)
        self.assertIn("--device-source", pyoptix)
        self.assertIn("static_assert(sizeof(Params) == 120", direct)
        self.assertIn("PARAM_DTYPE", pyoptix)
        self.assertIn("PARAM_DTYPE.itemsize != 120", pyoptix)
        self.assertNotIn("cp.asarray(indexed)", pyoptix)
        self.assertNotIn("cp.asarray(rays)", pyoptix)

    def test_rtdl_capacity_is_canonical_not_private_event_capacity(self) -> None:
        native = (
            ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
        ).read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        runtime = (
            ROOT / "src/rtdsl/v4_bounded_relation_prepared_runtime.py"
        ).read_text(encoding="utf-8")
        self.assertIn("semantic_capacity", native)
        self.assertIn("2ull * (prepared->semantic_capacity + 1ull)", native)
        self.assertIn("std::unique(host_rows.begin(), host_rows.end()", native)
        self.assertIn("rtdl_optix_v4_execute_prepared_bounded_relation_callback_v2", api)
        self.assertIn("output_raw_event_count", api)
        self.assertIn("output_unique_count", api)
        self.assertIn("callback_v2", runtime)
        self.assertIn("observed_raw_count=int(unique_count.value)", runtime)

    def test_no_performance_measurement_in_functional_arms(self) -> None:
        for name in ("direct_optix.cpp", "pyoptix_baseline.py", "rtdl_baseline.py"):
            text = (MATCHED / name).read_text(encoding="utf-8")
            self.assertIn("registered_performance_timing_count", text)
            self.assertNotIn("perf_counter", text)
            self.assertNotIn("cudaEventElapsedTime", text)
            self.assertNotIn("std::chrono", text)

    def test_closeout_refuses_to_invent_the_missing_pyoptix_denominator(self) -> None:
        result = json.loads((
            ROOT / "history/internal_docs/goal5796_matched_implementation_result_20260823.json"
        ).read_bytes())
        self.assertEqual(
            result["status"],
            "TERMINAL_PARTIAL__A_AND_D_EXACT__C_ANALYSED_ONLY__B_ENVIRONMENT_BLOCKED",
        )
        self.assertFalse(result["goal5796_completion_gate_met"])
        self.assertTrue(result["arm_results"]["A_direct_cuda_optix"]["all_registered_outputs_exact"])
        self.assertTrue(result["arm_results"]["D_rtdl_public"]["all_registered_outputs_exact"])
        pyoptix = result["arm_results"]["B_current_pyoptix"]
        self.assertFalse(pyoptix["correctness_result_exists"])
        self.assertFalse(pyoptix["package_install_attempted"])
        self.assertFalse(pyoptix["optix_context_created"])
        self.assertFalse(pyoptix["substitution_used"])
        self.assertEqual(result["arm_results"]["C_owl"]["status"], "ANALYSED_NOT_IMPLEMENTED")
        self.assertEqual(result["measurement"]["registered_performance_timing_count"], 0)
        self.assertFalse(result["next_gate"]["goal5797_full_entry_authorized"])
        self.assertFalse(result["next_gate"]["goal5798_formal_timing_authorized"])

    def test_pyoptix90_successor_is_explicitly_compatibility_scoped(self) -> None:
        source = (MATCHED / "pyoptix_baseline.py").read_text(encoding="utf-8")
        self.assertIn("--expected-optix-api-version", source)
        self.assertIn("--compatibility-authority", source)
        self.assertIn("stock_current_pyoptix_9_1_claimed", source)
        result = json.loads((
            ROOT / "history/internal_docs/goal5796_pyoptix90_compatibility_successor_result_20260823.json"
        ).read_bytes())
        self.assertTrue(
            result["gates"]["revised_current_source_optix90_compatibility_gate_met"])
        self.assertFalse(
            result["gates"]["original_stock_current_pyoptix_9_1_gate_met"])
        self.assertTrue(
            result["gates"]["goal5797_compatibility_scope_entry_authorized"])
        self.assertFalse(result["gates"]["goal5798_formal_timing_authorized"])
        self.assertFalse(
            result["pyoptix_compatibility_identity"]
            ["stock_current_pyoptix_9_1_claimed"])
        self.assertEqual(result["measurement"]["registered_performance_timing_count"], 0)

    @unittest.skipUnless(PYOPTIX.is_dir() and OWL.is_dir(), "frozen upstream source clones absent")
    def test_three_responsibility_tables_rebuild(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "responsibility.json"
            subprocess.run(
                [
                    sys.executable,
                    str(MATCHED / "build_responsibility.py"),
                    "--root", str(ROOT),
                    "--pyoptix", str(PYOPTIX),
                    "--owl", str(OWL),
                    "--output", str(output),
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            result = json.loads(output.read_bytes())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(len(result["composition_ownership"]), 5)
        self.assertEqual(len(result["protocol_contract_ownership"]), 6)
        self.assertEqual(len(result["device_language_path"]), 2)
        self.assertEqual(len(result["historical_application_table"]), 9)
        exceptions = [
            row for row in result["historical_application_table"]
            if row["historical_native_loader_exception"] is not None
        ]
        self.assertEqual([row["application"] for row in exceptions], ["raydb"])
        self.assertTrue(
            result["historical_application_table_authority"]
            ["raydb_private_loader_exception_visible_in_row"])
        self.assertFalse(
            result["historical_application_table_authority"]
            ["matched_task_or_generalization_evidence"])
        self.assertEqual(result["owl_arm_status"], "ANALYSED_NOT_IMPLEMENTED")
        self.assertFalse(result["owl_performance_claim_allowed"])
        self.assertFalse(result["usability_or_productivity_inference_allowed"])
        self.assertEqual(result["registered_performance_timing_count"], 0)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts import goal5793_x2_structural_friction_v2 as friction
from tests.goal5793_x2_structural_friction_test import _lineage


PYTHON_SOURCE = b"""import rtdsl.v4_semantically_admitted_compiler

def run(x):
    # CUDA_SUCCESS OPTIX_SUCCESS optixAccelBuild are prose and must not count.
    message = "cudaMalloc optixTrace"
    n = len([1, 2])
    print(n)
    d = dict()
    for i in range(3):
        value = str(i).upper()
    return rtdsl.v4_semantically_admitted_compiler.run_semantically_admitted_builtin_triangle(x)
"""

C_SOURCE = b"""#include <optix_stubs.h>
#include <cuda_runtime_api.h>
if (res != CUDA_SUCCESS) return;
if (r != OPTIX_SUCCESS) return;
OPTIX_CHECK(optixAccelBuild(ctx));
cuda_stream_t s;
char *p = "no cuda mention here"; // CUDA optixTrace
optixTrace(h);
cudaMalloc(&p, 4);
"""


class Goal5793X2StructuralFrictionV2Test(unittest.TestCase):
    def test_01_dotted_import_resolves_public_and_builtins_are_not_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "app.py").write_bytes(PYTHON_SOURCE)
            result = friction.measure_lineage(root, _lineage("app.py", PYTHON_SOURCE))
        self.assertEqual(result["metrics"]["public_rtdl_api_call_sites"]["value"], 1)
        self.assertEqual(result["metrics"]["unresolved_rtdl_api_call_sites"]["value"], 0)
        self.assertGreaterEqual(result["metrics"]["non_rtdl_call_sites_excluded_from_api_metric"]["value"], 6)
        self.assertEqual(result["metrics"]["raw_cuda_optix_code_tokens"]["value"], 0)

    def test_02_cuda_optix_prefixes_and_headers_count_code_not_prose(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "app.cu").write_bytes(C_SOURCE)
            result = friction.measure_lineage(root, _lineage("app.cu", C_SOURCE))
        sites = result["details"]["raw_cuda_optix_code_token_sites"]
        tokens = [row["token"] for row in sites]
        for expected in (
            "<optix_stubs.h>", "<cuda_runtime_api.h>", "CUDA_SUCCESS", "OPTIX_SUCCESS",
            "OPTIX_CHECK", "optixAccelBuild", "cuda_stream_t", "optixTrace", "cudaMalloc",
        ):
            self.assertIn(expected, tokens)
        self.assertEqual(len(tokens), 9)
        self.assertNotIn("optix_stubs", tokens)
        self.assertNotIn("cuda_runtime_api", tokens)
        self.assertNotIn("CUDA", tokens)
        self.assertFalse(any(row["line"] == 7 for row in sites))

    def test_03_call_metrics_are_explicitly_not_direct_baseline_comparable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "app.py").write_bytes(PYTHON_SOURCE)
            result = friction.measure_lineage(root, _lineage("app.py", PYTHON_SOURCE))
        definition = result["measurement_definition"]
        self.assertFalse(definition["public_private_unresolved_metrics_comparable_to_direct_cuda_optix_baseline"])
        self.assertTrue(definition["builtins_stdlib_and_other_third_party_calls_excluded_from_unresolved"])
        self.assertFalse(result["supports_easy_productive_simpler_less_code_or_better_than_cuda_claim"])

    def test_04_v2_seal_changes_on_measurement_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "app.py").write_bytes(PYTHON_SOURCE)
            first = friction.measure_lineage(root, _lineage("app.py", PYTHON_SOURCE))
            second = dict(first); second["measurement_sha256"] = ""
            second["metrics"] = dict(first["metrics"])
            second["metrics"]["unresolved_rtdl_api_call_sites"] = dict(first["metrics"]["unresolved_rtdl_api_call_sites"], value=1)
            from scripts.goal5793_x1_canonical import seal_document
            changed = seal_document(second, seal_field="measurement_sha256", domain=friction.MEASUREMENT_DOMAIN, version=2)
        self.assertNotEqual(first["measurement_sha256"], changed)


if __name__ == "__main__":
    unittest.main()

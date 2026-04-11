#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


TEST_GROUPS: dict[str, tuple[str, ...]] = {
    "unit": (
        "tests.baseline_contracts_test",
        "tests.dsl_negative_test",
        "tests.goal10_workloads_test",
        "tests.goal15_compare_test",
        "tests.goal17_prepared_runtime_test",
        "tests.goal18_result_mode_test",
        "tests.goal19_compare_test",
        "tests.goal22_reproduction_test",
        "tests.goal23_reproduction_test",
        "tests.goal28b_staging_test",
        "tests.goal28c_conversion_test",
        "tests.goal28d_execution_test",
        "tests.goal30_precision_abi_test",
        "tests.goal31_lsi_gap_closure_test",
        "tests.goal32_lsi_sort_sweep_test",
        "tests.goal36_performance_test",
        "tests.goal40_native_oracle_test",
        "tests.paper_reproduction_test",
        "tests.report_smoke_test",
        "tests.rtdsl_language_test",
        "tests.rtdsl_py_test",
        "tests.rtdsl_ray_query_test",
        "tests.rtdsl_simulator_test",
        "tests.section_5_6_scalability_test",
        "tests.test_core_quality",
    ),
    "integration": (
        "tests.baseline_integration_test",
        "tests.cpu_embree_parity_test",
        "tests.evaluation_test",
        "tests.goal44_optix_benchmark_test",
        "tests.optix_embree_interop_test",
        "tests.rtdsl_embree_test",
        "tests.rtdsl_vulkan_test",
    ),
    "system": (
        "tests.goal34_performance_test",
        "tests.goal35_blockgroup_waterbodies_test",
        "tests.goal37_lkau_pkau_test",
        "tests.goal38_feasibility_test",
        "tests.goal43_optix_validation_test",
        "tests.goal45_optix_county_zipcode_test",
        "tests.goal47_optix_goal41_large_checks_test",
        "tests.goal50_postgis_ground_truth_test",
        "tests.goal54_lkau_pkau_four_system_test",
    ),
    "v0_2_local": (
        "tests.goal110_baseline_runner_backend_test",
        "tests.goal110_segment_polygon_hitcount_semantics_test",
        "tests.goal111_generate_only_mvp_test",
        "tests.goal113_generate_only_maturation_test",
        "tests.goal116_segment_polygon_backend_audit_test",
        "tests.goal118_segment_polygon_linux_large_perf_test",
        "tests.goal128_segment_polygon_anyhit_postgis_test",
        "tests.goal129_generate_only_second_workload_test",
    ),
    "v0_2_linux": (
        "tests.goal110_segment_polygon_hitcount_closure_test",
        "tests.goal114_segment_polygon_postgis_test",
    ),
}


def build_env() -> dict[str, str]:
    env = os.environ.copy()
    pythonpath_key = next((key for key in env if key.upper() == "PYTHONPATH"), "PYTHONPATH")
    entries = [str(ROOT / "src"), str(ROOT)]
    existing = env.get(pythonpath_key)
    if existing:
        entries.append(existing)
    env[pythonpath_key] = os.pathsep.join(entries)
    return env


def group_modules(name: str) -> tuple[str, ...]:
    if name == "full":
        return TEST_GROUPS["unit"] + TEST_GROUPS["integration"] + TEST_GROUPS["system"]
    if name == "v0_2_full":
        return TEST_GROUPS["v0_2_local"] + TEST_GROUPS["v0_2_linux"]
    return TEST_GROUPS[name]


def run_group(name: str) -> dict[str, object]:
    modules = group_modules(name)
    cp = subprocess.run(
        [sys.executable, "-m", "unittest", *modules],
        cwd=str(ROOT),
        env=build_env(),
        text=True,
        capture_output=True,
        check=False,
    )
    output = cp.stdout
    if cp.stderr:
        output = (output + ("\n" if output else "") + cp.stderr).strip()
    return {
        "group": name,
        "command": sys.executable + " -m unittest " + " ".join(modules),
        "module_count": len(modules),
        "returncode": cp.returncode,
        "ok": cp.returncode == 0,
        "output": output,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the RTDL test matrix by group.")
    parser.add_argument(
        "--group",
        choices=("unit", "integration", "system", "full", "v0_2_local", "v0_2_linux", "v0_2_full"),
        default="full",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run_group(args.group)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

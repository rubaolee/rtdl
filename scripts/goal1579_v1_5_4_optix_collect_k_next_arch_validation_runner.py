#!/usr/bin/env python3
"""Run the Goal1578 next-architecture validation suite for OptiX collect-k.

This runner intentionally keeps the derived carry alias diagnostic gated. It
collects baseline and alias profile artifacts, runs the focused static tests,
and writes a small summary without making any promotion decision.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

FOCUSED_TESTS = [
    "tests.goal1573_v1_5_4_optix_collect_k_derived_carry_alias_diagnostic_test",
    "tests.goal1572_v1_5_4_optix_collect_k_carry_pointer_device_counts_diagnostic_test",
    "tests.goal1571_v1_5_4_optix_collect_k_carry_pointer_diagnostic_test",
    "tests.goal1570_v1_5_4_optix_collect_k_carry_alias_implementation_preflight_test",
]

SWEEP_COUNTS = [7, 8192, 12289, 16385, 20481, 24577, 32769, 45057, 49153, 65536, 65537]
TARGETED_COUNTS = [49153, 65536, 65537]

PROFILE_ENV = {
    "RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT": "1",
    "RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT": "1",
    "RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL": "1",
    "RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE": "1",
    "RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT": "1",
    "RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS": "1",
    "RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS": "1",
    "RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS": "1",
}

CANDIDATE_PRESET_ENV = {
    "RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE": "1",
}


def _run(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def _profile_env(*, enable_alias: bool, ld_library_path: str | None, use_candidate_preset: bool = False) -> dict[str, str]:
    env = os.environ.copy()
    if use_candidate_preset:
        for key in PROFILE_ENV:
            env.pop(key, None)
        env.pop("RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC", None)
        env.pop("RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC", None)
        env.pop("RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DEVICE_COUNTS_DIAGNOSTIC", None)
        env.update(CANDIDATE_PRESET_ENV)
    else:
        env.update(PROFILE_ENV)
    if enable_alias and not use_candidate_preset:
        env["RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC"] = "1"
    elif not use_candidate_preset:
        env.pop("RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC", None)
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"src{os.pathsep}." + (f"{os.pathsep}{existing_pythonpath}" if existing_pythonpath else "")
    if ld_library_path:
        env["LD_LIBRARY_PATH"] = ld_library_path
    return env


def _run_profile(
    *,
    library: Path,
    counts: list[int],
    repeats: int,
    output_prefix: Path,
    label: str,
    enable_alias: bool,
    ld_library_path: str | None,
    use_candidate_preset: bool = False,
) -> Path:
    json_path = output_prefix.with_name(f"{output_prefix.name}_{label}.json")
    md_path = output_prefix.with_name(f"{output_prefix.name}_{label}.md")
    jsonl_path = output_prefix.with_name(f"{output_prefix.name}_{label}.jsonl")
    cmd = [
        sys.executable,
        "scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py",
        "--library",
        str(library),
        "--counts",
        *[str(count) for count in counts],
        "--repeats",
        str(repeats),
        "--profile-jsonl",
        str(jsonl_path),
        "--json-out",
        str(json_path),
        "--md-out",
        str(md_path),
    ]
    _run(
        cmd,
        env=_profile_env(
            enable_alias=enable_alias,
            ld_library_path=ld_library_path,
            use_candidate_preset=use_candidate_preset,
        ),
    )
    return json_path


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _case_by_count(data: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(case["candidate_count"]): case for case in data.get("cases", [])}


def _write_summary(
    *,
    output_prefix: Path,
    baseline_path: Path,
    alias_path: Path,
    targeted_baseline_path: Path | None,
    targeted_alias_path: Path | None,
    candidate_preset_path: Path | None,
) -> None:
    baseline = _load_json(baseline_path)
    alias = _load_json(alias_path)
    baseline_cases = _case_by_count(baseline)
    alias_cases = _case_by_count(alias)

    rows: list[dict[str, Any]] = []
    for count in sorted(baseline_cases):
        base_case = baseline_cases[count]
        alias_case = alias_cases[count]
        base_ms = float(base_case["stage_profile"]["stage_median_ms"]["total_ms"])
        alias_ms = float(alias_case["stage_profile"]["stage_median_ms"]["total_ms"])
        rows.append(
            {
                "candidate_count": count,
                "baseline_total_ms": base_ms,
                "alias_total_ms": alias_ms,
                "delta_ms": alias_ms - base_ms,
                "baseline_payload_copies": int(base_case["stage_profile"]["topology"].get("carry_payload_copies", 0)),
                "alias_payload_copies": int(alias_case["stage_profile"]["topology"].get("carry_payload_copies", 0)),
                "same_candidate_rows": bool(alias_case.get("same_candidate_rows")),
            }
        )

    summary = {
        "status": "goal1579_next_arch_validation_recorded",
        "baseline_accepted": bool(baseline.get("accepted_goal1506_evidence")),
        "alias_accepted": bool(alias.get("accepted_goal1506_evidence")),
        "baseline_parity": bool(baseline.get("all_parity_passed")),
        "alias_parity": bool(alias.get("all_parity_passed")),
        "baseline_topology": bool(baseline.get("all_profile_topologies_match_expected")),
        "alias_topology": bool(alias.get("all_profile_topologies_match_expected")),
        "rows": rows,
        "targeted_baseline_json": str(targeted_baseline_path) if targeted_baseline_path else None,
        "targeted_alias_json": str(targeted_alias_path) if targeted_alias_path else None,
        "candidate_preset_json": str(candidate_preset_path) if candidate_preset_path else None,
    }
    summary_json = output_prefix.with_name(f"{output_prefix.name}_summary.json")
    summary_md = output_prefix.with_name(f"{output_prefix.name}_summary.md")
    summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Goal 1579: Next-Architecture Derived Carry Alias Validation",
        "",
        "## Verdict",
        "",
        "`goal1579_next_arch_validation_recorded`",
        "",
        "## Acceptance",
        "",
        f"- Baseline accepted: `{summary['baseline_accepted']}`",
        f"- Alias accepted: `{summary['alias_accepted']}`",
        f"- Baseline parity: `{summary['baseline_parity']}`",
        f"- Alias parity: `{summary['alias_parity']}`",
        f"- Baseline topology: `{summary['baseline_topology']}`",
        f"- Alias topology: `{summary['alias_topology']}`",
        f"- Candidate preset smoke JSON: `{summary['candidate_preset_json']}`",
        "",
        "## Sweep",
        "",
        "| Count | Baseline ms | Alias ms | Delta ms | Baseline payload copies | Alias payload copies | Parity |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {candidate_count} | {baseline_total_ms:.6f} | {alias_total_ms:.6f} | {delta_ms:.6f} | "
            "{baseline_payload_copies} | {alias_payload_copies} | {same_candidate_rows} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This runner records validation evidence only. It does not authorize public speedup wording, "
            "true zero-copy wording, stable primitive promotion, whole-application claims, or release action.",
            "",
        ]
    )
    summary_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", default="build/librtdl_optix.so", help="Path to librtdl_optix.so")
    parser.add_argument("--output-prefix", default="/tmp/goal1579_next_arch", help="Output artifact prefix")
    parser.add_argument("--repeats", type=int, default=5, help="Sweep repeats")
    parser.add_argument("--targeted-repeats", type=int, default=9, help="Targeted rerun repeats")
    parser.add_argument("--candidate-preset-repeats", type=int, default=5, help="Candidate preset smoke repeats")
    parser.add_argument("--skip-targeted", action="store_true", help="Skip targeted rerun")
    parser.add_argument(
        "--candidate-preset-smoke",
        action="store_true",
        help="Also run a cheap targeted profile with only RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE enabled",
    )
    parser.add_argument("--build", action="store_true", help="Build OptiX library before running")
    parser.add_argument("--optix-prefix", default="/root/vendor/optix-sdk", help="OptiX SDK prefix for --build")
    parser.add_argument(
        "--ld-library-path",
        default=os.environ.get("LD_LIBRARY_PATH"),
        help="LD_LIBRARY_PATH to use while loading CUDA/OptiX runtime libraries",
    )
    args = parser.parse_args()

    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    library = Path(args.library)

    if args.build:
        _run(["make", "build-optix", f"OPTIX_PREFIX={args.optix_prefix}"])

    test_env = os.environ.copy()
    test_env["PYTHONPATH"] = f"src{os.pathsep}."
    _run([sys.executable, "-m", "unittest", *FOCUSED_TESTS], env=test_env)

    baseline_path = _run_profile(
        library=library,
        counts=SWEEP_COUNTS,
        repeats=args.repeats,
        output_prefix=output_prefix,
        label="baseline",
        enable_alias=False,
        ld_library_path=args.ld_library_path,
    )
    alias_path = _run_profile(
        library=library,
        counts=SWEEP_COUNTS,
        repeats=args.repeats,
        output_prefix=output_prefix,
        label="alias",
        enable_alias=True,
        ld_library_path=args.ld_library_path,
    )

    targeted_baseline_path = None
    targeted_alias_path = None
    candidate_preset_path = None
    if not args.skip_targeted:
        targeted_baseline_path = _run_profile(
            library=library,
            counts=TARGETED_COUNTS,
            repeats=args.targeted_repeats,
            output_prefix=output_prefix,
            label="targeted_baseline",
            enable_alias=False,
            ld_library_path=args.ld_library_path,
        )
        targeted_alias_path = _run_profile(
            library=library,
            counts=TARGETED_COUNTS,
            repeats=args.targeted_repeats,
            output_prefix=output_prefix,
            label="targeted_alias",
            enable_alias=True,
            ld_library_path=args.ld_library_path,
        )

    if args.candidate_preset_smoke:
        candidate_preset_path = _run_profile(
            library=library,
            counts=TARGETED_COUNTS,
            repeats=args.candidate_preset_repeats,
            output_prefix=output_prefix,
            label="candidate_preset",
            enable_alias=False,
            ld_library_path=args.ld_library_path,
            use_candidate_preset=True,
        )

    _write_summary(
        output_prefix=output_prefix,
        baseline_path=baseline_path,
        alias_path=alias_path,
        targeted_baseline_path=targeted_baseline_path,
        targeted_alias_path=targeted_alias_path,
        candidate_preset_path=candidate_preset_path,
    )
    print(json.dumps({"status": "goal1579_next_arch_validation_recorded", "output_prefix": str(output_prefix)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

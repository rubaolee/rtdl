from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in (SRC, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from rtdsl.v4_goal4698_specialized_tier3_compile_cache import (
    canonicalize_v4_goal4698_callback_ptx_for_cache,
)
from rtdsl.v4_goal4698_specialized_tier3_compile_cache import plan_v4_goal4698_specialized_tier3_compile
from rtdsl.v4_goal4705_source_ptx_cache_stability import (
    classify_v4_goal4705_source_ptx_cache_stability,
    validate_v4_goal4705_source_ptx_cache_stability_contract,
)
from v4_goal4703_specialized_tier3_reliability_matrix_pod import VARIANT_TO_CONTRACT_SHAPE
from v4_goal4703_specialized_tier3_reliability_matrix_pod import _compile_variant_ptx


def _compile_plan(variant: str, ptx: str, toolchain: dict[str, object]) -> dict[str, object]:
    return plan_v4_goal4698_specialized_tier3_compile(
        callback_shape=VARIANT_TO_CONTRACT_SHAPE[variant],
        callback_language="numba",
        numba_cabi_device_function=True,
        callback_symbol=variant,
        callback_ptx=ptx,
        toolchain_fingerprint=json.dumps(toolchain, sort_keys=True),
        optix_abi="8.0",
        compute_target="sm_86",
    ).as_dict()


def _dry_run_rows() -> list[dict[str, object]]:
    ptx1 = ".common .global .align 8 .u64 _ZN08NumbaEnv33custom_scalar_reduceB2v1B96;\n.visible .func f(){ret;}\n"
    ptx2 = ".common .global .align 8 .u64 _ZN08NumbaEnv33custom_scalar_reduceB2v2B96;\n.visible .func f(){ret;}\n"
    toolchain = {"python": "3.12", "numba": "sample", "cuda": "sample", "optix": "sample"}
    plan1 = _compile_plan("custom_scalar_reduce_weighted_sum", ptx1, toolchain)
    plan2 = _compile_plan("custom_scalar_reduce_weighted_sum", ptx2, toolchain)
    changed_ptx = _compile_plan("custom_scalar_reduce_weighted_sum", ptx2 + "// semantic change\n", toolchain)
    changed_toolchain = _compile_plan(
        "custom_scalar_reduce_weighted_sum",
        ptx2,
        {**toolchain, "numba": "changed"},
    )
    return [
        {
            "variant": "custom_scalar_reduce_weighted_sum",
            "same_source_compile_cache_key_match": plan1["cache_key"] == plan2["cache_key"],
            "changed_ptx_changes_key": changed_ptx["cache_key"] != plan2["cache_key"],
            "changed_toolchain_changes_key": changed_toolchain["cache_key"] != plan2["cache_key"],
            "canonical_ptx_equal": canonicalize_v4_goal4698_callback_ptx_for_cache(ptx1)
            == canonicalize_v4_goal4698_callback_ptx_for_cache(ptx2),
        }
    ]


def _run_probe(dry_run: bool) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": "rtdl.v4.goal4705_source_ptx_cache_stability.v1",
        "status": "dry_run" if dry_run else "unknown",
        "dry_run": dry_run,
        "contract_validation": validate_v4_goal4705_source_ptx_cache_stability_contract(),
        "rows": [],
        "summary": None,
        "tier3_public_support_authorized": False,
        "release_authorized": False,
        "performance_claim_authorized": False,
    }
    if dry_run:
        rows = _dry_run_rows()
        payload["rows"] = rows
        payload["summary"] = classify_v4_goal4705_source_ptx_cache_stability(rows * 4)
        payload["status"] = "dry_run_contract_passed" if payload["contract_validation"]["status"] == "passed" else "dry_run_contract_failed"
        return payload

    toolchain = {"python": sys.version.split()[0]}
    rows: list[dict[str, object]] = []
    for variant in VARIANT_TO_CONTRACT_SHAPE:
        print(f"goal4705 progress compile-pair variant={variant}", file=sys.stderr, flush=True)
        ptx1, meta1 = _compile_variant_ptx(variant)
        ptx2, meta2 = _compile_variant_ptx(variant)
        row: dict[str, object] = {
            "variant": variant,
            "ptx1_status": meta1.get("status"),
            "ptx2_status": meta2.get("status"),
            "same_source_compile_cache_key_match": False,
            "changed_ptx_changes_key": False,
            "changed_toolchain_changes_key": False,
        }
        if ptx1 is None or ptx2 is None:
            row["error"] = "ptx_generation_failed"
            rows.append(row)
            continue
        toolchain = {
            "python": sys.version.split()[0],
            "numba_toolchain_1": meta1.get("numba_toolchain_environment"),
            "numba_toolchain_2": meta2.get("numba_toolchain_environment"),
        }
        plan1 = _compile_plan(variant, ptx1, toolchain)
        plan2 = _compile_plan(variant, ptx2, toolchain)
        changed_ptx = _compile_plan(variant, ptx2 + "\n// rtdl-goal4705-semantic-change\n", toolchain)
        changed_toolchain = _compile_plan(variant, ptx2, {**toolchain, "changed": True})
        row.update(
            {
                "ptx1_raw_sha256": plan1["cache_components"]["callback_ptx_raw_sha256"],
                "ptx2_raw_sha256": plan2["cache_components"]["callback_ptx_raw_sha256"],
                "ptx1_canonical_sha256": plan1["cache_components"]["callback_ptx_sha256"],
                "ptx2_canonical_sha256": plan2["cache_components"]["callback_ptx_sha256"],
                "cache_key_1": plan1["cache_key"],
                "cache_key_2": plan2["cache_key"],
                "same_source_compile_cache_key_match": plan1["cache_key"] == plan2["cache_key"],
                "changed_ptx_key": changed_ptx["cache_key"],
                "changed_ptx_changes_key": changed_ptx["cache_key"] != plan2["cache_key"],
                "changed_toolchain_key": changed_toolchain["cache_key"],
                "changed_toolchain_changes_key": changed_toolchain["cache_key"] != plan2["cache_key"],
                "raw_ptx_hash_equal": plan1["cache_components"]["callback_ptx_raw_sha256"]
                == plan2["cache_components"]["callback_ptx_raw_sha256"],
                "canonical_ptx_hash_equal": plan1["cache_components"]["callback_ptx_sha256"]
                == plan2["cache_components"]["callback_ptx_sha256"],
            }
        )
        rows.append(row)
    payload["rows"] = rows
    payload["summary"] = classify_v4_goal4705_source_ptx_cache_stability(rows)
    payload["status"] = "source_ptx_cache_stability_measured_not_public_support"
    return payload


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    summary = payload.get("summary") or {}
    lines = [
        "# V4 Goal4705 Source-Level PTX Cache Stability",
        "",
        f"- status: `{payload['status']}`",
        f"- classification: `{summary.get('classification')}`",
        f"- rows checked: `{summary.get('rows_checked')}`",
        f"- stable source cache keys: `{summary.get('stable_source_cache_keys')}`",
        "",
        "| variant | raw PTX equal | canonical PTX equal | cache key stable | changed PTX changes key | changed toolchain changes key |",
        "|---|---|---|---|---|---|",
    ]
    for row in payload.get("rows", []):
        lines.append(
            f"| `{row['variant']}` | `{row.get('raw_ptx_hash_equal')}` | `{row.get('canonical_ptx_hash_equal')}` | "
            f"`{row.get('same_source_compile_cache_key_match')}` | `{row.get('changed_ptx_changes_key')}` | "
            f"`{row.get('changed_toolchain_changes_key')}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This gate hardens cache behavior only. It does not authorize public Tier-3 support, release wording, or performance claims.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 Goal4705 source-level PTX cache stability gate.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    payload = _run_probe(bool(args.dry_run))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] in {"dry_run_contract_passed", "source_ptx_cache_stability_measured_not_public_support"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

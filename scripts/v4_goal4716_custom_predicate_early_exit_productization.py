from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rt_v4
from rtdsl import v4_operator_catalog as catalog


def build_goal4716_productization_evidence() -> dict[str, object]:
    measured_rows = catalog.measured_v4_tier2_operator_catalog()
    rows_by_operator = {str(row["operator"]): row for row in measured_rows}
    operator = catalog.V4_TIER2_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT
    row = rows_by_operator.get(operator)
    plan = rt_v4.plan_operator_request_v4(
        operator,
        partner="numba",
        callback_shape="pure_boolean_numba_cabi_device_function",
        numba_device_function=True,
    )
    recognition = rt_v4.recognize_pushdown_request_v4(
        {
            "operator": operator,
            "callback_shape": "pure_boolean_numba_cabi_device_function",
            "numba_device_function": True,
        },
        partner="numba",
    )
    wrong_partner = rt_v4.plan_operator_request_v4(
        operator,
        partner="cupy",
        callback_shape="pure_boolean_numba_cabi_device_function",
        numba_device_function=True,
    )
    unsafe = rt_v4.plan_operator_request_v4(
        operator,
        partner="numba",
        callback_shape="pure_boolean_numba_cabi_device_function",
        numba_device_function=True,
        mutates_shared_state=True,
    )
    boundary = rt_v4.ray_triangle_custom_predicate_early_exit_claim_boundary_v4()
    missing: list[str] = []
    if row is None:
        missing.append("catalog_row")
    else:
        if row.get("api_surface") != rt_v4.V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE:
            missing.append("api_surface")
        if row.get("primary_v3_speedup_geomean") != 3.608025018751732:
            missing.append("goal4715_speedup")
        if row.get("release_claim_authorized") is not False:
            missing.append("release_claim_lock")
        if row.get("arbitrary_callback_authorized") is not False:
            missing.append("arbitrary_callback_lock")
    if plan.status != "tier2_measured_ready" or plan.api_surface is None:
        missing.append("planner_measured_path")
    if recognition.status != "pushdown_recognized_measured_tier2":
        missing.append("recognizer_measured_path")
    if wrong_partner.status != "tier2_declared_unmeasured_partner":
        missing.append("wrong_partner_fail_closed")
    if unsafe.status != "rejected_action_shaped_callback_deferred":
        missing.append("unsafe_callback_fail_closed")
    if boundary["whole_app_speedup_claim_authorized"] is not False:
        missing.append("whole_app_claim_lock")
    return {
        "schema": "rtdl.v4.goal4716_custom_predicate_early_exit_productization.v1",
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "operator": operator,
        "api_surface": rt_v4.V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE,
        "measured_catalog_surface_count": len(measured_rows),
        "catalog_row": row,
        "claim_boundary": boundary,
        "planner_success": plan.as_dict(),
        "recognizer_success": recognition.as_dict(),
        "wrong_partner_rejection": wrong_partner.as_dict(),
        "unsafe_callback_rejection": unsafe.as_dict(),
        "goal4715_evidence": {
            "primary_v2_speedup_geomean": 3.608025018751732,
            "primary_v3_speedup_geomean": 3.608025018751732,
            "min_primary_v3_speedup": 1.9761904761904763,
            "source": "future/v4/evidence/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.json",
        },
        "release_authorized": False,
        "formal_high_performance_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "public_tier3_support_authorized": False,
        "arbitrary_callback_authorized": False,
        "raw_optix_callback_authorized": False,
    }


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    row = payload.get("catalog_row") or {}
    lines = [
        "# V4 Goal4716 Custom Predicate Early-Exit Productization Evidence",
        "",
        f"- status: `{payload['status']}`",
        f"- api surface: `{payload['api_surface']}`",
        f"- measured catalog surface count: `{payload['measured_catalog_surface_count']}`",
        f"- primary V4/V3 focused geomean: `{payload['goal4715_evidence']['primary_v3_speedup_geomean']}`",
        f"- min primary V4/V3 row: `{payload['goal4715_evidence']['min_primary_v3_speedup']}`",
        "",
        "## Catalog Row",
        "",
        f"- operator: `{payload['operator']}`",
        f"- measured partners: `{row.get('measured_partners')}`",
        f"- accepted callback shapes: `{row.get('accepted_callback_shapes')}`",
        f"- accepted actions: `{row.get('accepted_actions')}`",
        f"- comparison class: `{row.get('comparison_class')}`",
        "",
        "## Boundaries",
        "",
        "- release authorized: `False`",
        "- whole-app speedup claim authorized: `False`",
        "- arbitrary callback authorized: `False`",
        "- raw OptiX callback authorized: `False`",
        "",
        "Goal4716 productizes the focused Goal4715 win as a V4 measured operator-pushdown surface. It does not authorize release.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V4 Goal4716 productization evidence.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()
    payload = build_goal4716_productization_evidence()
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

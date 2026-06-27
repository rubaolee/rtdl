from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4718_release_matrix_after_custom_predicate import (  # noqa: E402
    validate_v4_goal4718_release_matrix_after_custom_predicate,
)


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    matrix = payload["matrix"]
    workflow = matrix["new_v4_workflow_rows"][0]
    legacy = matrix["legacy_promoted_app_state"]
    lines = [
        "# V4 Goal4718 Release Matrix After Custom Predicate Early-Exit",
        "",
        f"- validation: `{payload['status']}`",
        f"- decision: `{matrix['decision_label']}`",
        f"- measured surfaces: `{matrix['measured_surface_count']}`",
        f"- V4 Python eDSL release candidate supported: `{matrix['v4_python_edsl_release_candidate_supported']}`",
        f"- operator-pushdown workflow high-performance supported: `{matrix['v4_operator_pushdown_workflow_high_performance_supported']}`",
        f"- legacy all-app high-performance supported: `{matrix['legacy_all_app_high_performance_supported']}`",
        "",
        "## New V4 Workflow Row",
        "",
        f"- workflow: `{workflow['workflow']}`",
        f"- API surface: `{workflow['api_surface']}`",
        f"- claim class: `{workflow['claim_class']}`",
        f"- V4/V2.14 primary geomean: `{workflow['v4_vs_v2_14_primary_geomean']}`",
        f"- V4/V3.0.2 primary geomean: `{workflow['v4_vs_v3_0_2_primary_geomean']}`",
        f"- minimum primary V4/V3.0.2 row: `{workflow['min_primary_v4_vs_v3_0_2']}`",
        f"- correctness all passed: `{workflow['correctness_all_passed']}`",
        f"- denominator: `{workflow['denominator']}`",
        "",
        "This row counts as V4 eDSL/operator-pushdown value. It does not count as",
        "legacy all-app benchmark-suite speedup.",
        "",
        "## Legacy Promoted-App State",
        "",
        f"- decision: `{legacy['decision_label']}`",
        f"- formal high-performance supported: `{legacy['formal_high_performance_v4_supported']}`",
        f"- true V4 candidate app count: `{legacy['true_v4_candidate_app_count']}`",
        f"- contributing app count: `{legacy['contributing_app_count']}`",
        "",
        "## Allowed Claim If Later Gates Pass",
        "",
    ]
    for claim in matrix["allowed_claim_if_goal4719_and_final_review_pass"]:
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "## Forbidden Claims",
            "",
        ]
    )
    for claim in matrix["forbidden_claims"]:
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "## Non-Authorization",
            "",
            "- V4 release is not authorized by Goal4718 alone.",
            "- Public wording is not authorized before Goal4719 docs/examples cleanup.",
            "- Broad all-benchmark speedup remains unauthorized.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit V4 Goal4718 release matrix after custom predicate early-exit.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()
    payload = validate_v4_goal4718_release_matrix_after_custom_predicate()
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

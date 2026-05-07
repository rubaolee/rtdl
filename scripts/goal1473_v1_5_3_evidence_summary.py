from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PARITY_JSON = (
    ROOT
    / "docs"
    / "reports"
    / "goal1467_v1_5_3_typed_host_buffer_pod_results_2026-05-07"
    / "goal1467_typed_host_buffer_parity_required_2026-05-07.json"
)
SWEEP_JSON = ROOT / "docs" / "reports" / "goal1472_v1_5_3_typed_host_reuse_sweep_pod_2026-05-07.json"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / "goal1473_v1_5_3_evidence_summary_2026-05-07.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / "goal1473_v1_5_3_evidence_summary_2026-05-07.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_ratios(sweep_payload: dict[str, Any]) -> dict[str, Any]:
    ratios_by_backend: dict[str, list[float]] = {}
    materialization_deltas_by_backend: dict[str, list[int]] = {}
    for package in sweep_payload["packages"]:
        for row in package["results"]:
            backend = row["backend"]
            ratios_by_backend.setdefault(backend, []).append(float(row["typed_to_baseline_elapsed_ratio"]))
            materialization_deltas_by_backend.setdefault(backend, []).append(
                int(row["input_materialization_count_delta"])
            )
    return {
        backend: {
            "min_typed_to_baseline_elapsed_ratio": min(ratios),
            "max_typed_to_baseline_elapsed_ratio": max(ratios),
            "materialization_deltas": tuple(materialization_deltas_by_backend[backend]),
        }
        for backend, ratios in sorted(ratios_by_backend.items())
    }


def build_summary(parity_payload: dict[str, Any], sweep_payload: dict[str, Any]) -> dict[str, Any]:
    parity_backend_summary = parity_payload["backend_summary"]
    required_backends = tuple(parity_payload["required_backends"])
    parity_accepted = (
        parity_payload["accepted"] is True
        and tuple(parity_payload["skipped_required"]) == ()
        and all(
            parity_backend_summary[backend] == {"fail": 0, "pass": 4, "skipped": 0}
            for backend in required_backends
        )
    )
    sweep_accepted = (
        sweep_payload["accepted"] is True
        and tuple(sweep_payload["failed_packages"]) == ()
        and all(package["accepted"] is True for package in sweep_payload["packages"])
    )
    return {
        "goal": "Goal1473",
        "status": "accepted_diagnostic_evidence_summary" if parity_accepted and sweep_accepted else "not_accepted",
        "accepted": parity_accepted and sweep_accepted,
        "track": "v1.5.3_python_rtdl_reduced_copy",
        "primitive": "COLLECT_K_BOUNDED",
        "surface": "typed_host_input_plus_prepared_host_output",
        "parity": {
            "accepted": parity_accepted,
            "required_backends": required_backends,
            "backend_summary": parity_backend_summary,
            "scope": parity_payload["scope"],
        },
        "diagnostic_sweep": {
            "accepted": sweep_accepted,
            "required_backends": tuple(sweep_payload["required_backends"]),
            "sweep_specs": tuple(tuple(spec) for spec in sweep_payload["sweep_specs"]),
            "ratio_summary_by_backend": summarize_ratios(sweep_payload),
        },
        "evidence_paths": (
            str(PARITY_JSON.relative_to(ROOT)).replace("\\", "/"),
            str(SWEEP_JSON.relative_to(ROOT)).replace("\\", "/"),
            "docs/reports/goal1470_v1_5_3_typed_host_pod_parity_acceptance_2026-05-07.md",
            "docs/reports/goal1472_v1_5_3_typed_host_reuse_sweep_pod_2026-05-07.md",
        ),
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "next_steps": (
            "separate true device zero-copy from current typed host reuse evidence",
            "measure device or partner handoff only when a concrete implementation exists",
            "seek external AI review before any public performance wording",
        ),
        "claim_boundary": (
            "This summary accepts same-contract Embree+OptiX parity and "
            "diagnostic typed-host reuse evidence for the named v1.5.3 subpath "
            "only. It does not authorize true zero-copy, public speedup "
            "wording, whole-app claims, stable primitive promotion, partner "
            "tensor handoff, or release action."
        ),
    }


def write_outputs(payload: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# Goal1473 v1.5.3 Evidence Summary",
        "",
        "## Verdict",
        "",
        "ACCEPTED." if payload["accepted"] else "NOT ACCEPTED.",
        "",
        "## Scope",
        "",
        f"- Track: `{payload['track']}`",
        f"- Primitive: `{payload['primitive']}`",
        f"- Surface: `{payload['surface']}`",
        "",
        "## Parity",
        "",
        f"- Accepted: `{payload['parity']['accepted']}`",
        f"- Required backends: {', '.join(payload['parity']['required_backends'])}",
    ]
    for backend, summary in payload["parity"]["backend_summary"].items():
        lines.append(f"- `{backend}`: pass={summary['pass']} fail={summary['fail']} skipped={summary['skipped']}")
    lines.extend(["", "## Diagnostic Sweep", ""])
    for backend, summary in payload["diagnostic_sweep"]["ratio_summary_by_backend"].items():
        deltas = ", ".join(str(delta) for delta in summary["materialization_deltas"])
        lines.append(
            f"- `{backend}`: ratio_min={summary['min_typed_to_baseline_elapsed_ratio']:.6f} "
            f"ratio_max={summary['max_typed_to_baseline_elapsed_ratio']:.6f} "
            f"materialization_deltas={deltas}"
        )
    lines.extend(["", "## Evidence Paths", ""])
    lines.extend(f"- `{path}`" for path in payload["evidence_paths"])
    lines.extend(["", "## Boundary", "", payload["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_PATH))
    parser.add_argument("--md-out", default=str(DEFAULT_MD_PATH))
    args = parser.parse_args(argv)
    payload = build_summary(load_json(PARITY_JSON), load_json(SWEEP_JSON))
    write_outputs(payload, Path(args.json_out), Path(args.md_out))
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0 if payload["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

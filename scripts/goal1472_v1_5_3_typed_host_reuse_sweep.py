from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scripts.goal1471_v1_5_3_typed_host_reuse_benchmark import run_benchmark_package


REPORT_STEM = "goal1472_v1_5_3_typed_host_reuse_sweep_2026-05-07"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"
DEFAULT_SWEEP_SPECS = (
    (1024, 4, 20),
    (4096, 4, 20),
    (16384, 2, 12),
)


def parse_sweep_specs(raw_specs: list[str] | None) -> tuple[tuple[int, int, int], ...]:
    if not raw_specs:
        return DEFAULT_SWEEP_SPECS
    specs = []
    for raw_spec in raw_specs:
        parts = tuple(int(part) for part in raw_spec.split(":"))
        if len(parts) != 3:
            raise ValueError("sweep specs must use unique_rows:repeats:iterations")
        unique_rows, repeats, iterations = parts
        if unique_rows <= 0 or repeats <= 0 or iterations <= 0:
            raise ValueError("sweep specs require positive unique_rows, repeats, and iterations")
        specs.append((unique_rows, repeats, iterations))
    return tuple(specs)


def run_sweep_package(
    *,
    backends: tuple[str, ...],
    required_backends: tuple[str, ...],
    sweep_specs: tuple[tuple[int, int, int], ...],
) -> dict[str, Any]:
    packages = tuple(
        run_benchmark_package(
            backends=backends,
            required_backends=required_backends,
            unique_rows=unique_rows,
            repeats=repeats,
            iterations=iterations,
        )
        for unique_rows, repeats, iterations in sweep_specs
    )
    accepted = all(package["accepted"] for package in packages)
    failed_packages = tuple(package for package in packages if not package["accepted"])
    return {
        "goal": "Goal1472",
        "status": "accepted" if accepted else "not_accepted",
        "accepted": accepted,
        "scope": "v1.5.3 typed host input reuse diagnostic sweep",
        "primitive": "COLLECT_K_BOUNDED",
        "platform": platform.platform(),
        "python": sys.version,
        "backends": backends,
        "required_backends": required_backends,
        "sweep_specs": sweep_specs,
        "packages": packages,
        "failed_packages": failed_packages,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This sweep records wrapper-level input materialization counts and "
            "diagnostic timing across multiple typed-host benchmark sizes. It "
            "does not authorize true zero-copy, public speedup wording, "
            "whole-app claims, stable primitive promotion, partner tensor "
            "handoff, or release action."
        ),
    }


def summarize_package(package: dict[str, Any]) -> list[str]:
    lines = [
        f"- Case unique_rows={package['unique_rows']} repeats={package['repeats']} "
        f"iterations={package['iterations']} accepted={package['accepted']}"
    ]
    for row in package["results"]:
        if row["status"] != "pass":
            lines.append(f"- `{row['backend']}`: {row['status']} ({row.get('error')})")
            continue
        lines.append(
            f"- `{row['backend']}`: rows={row['candidate_row_count']} "
            f"baseline_materializations={row['baseline_input_materialization_count']} "
            f"typed_materializations={row['typed_input_materialization_count']} "
            f"delta={row['input_materialization_count_delta']} "
            f"baseline_total_s={row['baseline_elapsed_total_s']:.6f} "
            f"typed_total_s={row['typed_elapsed_total_s']:.6f} "
            f"ratio={row['typed_to_baseline_elapsed_ratio']:.6f}"
        )
    return lines


def write_outputs(payload: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# Goal1472 v1.5.3 Typed Host Reuse Sweep",
        "",
        "## Verdict",
        "",
        "ACCEPTED." if payload["accepted"] else "NOT ACCEPTED.",
        "",
        "## Scope",
        "",
        "- Primitive: `COLLECT_K_BOUNDED`",
        "- Surface: typed host input reuse plus prepared host output",
        f"- Backends: {', '.join(payload['backends'])}",
        f"- Required backends: {', '.join(payload['required_backends']) or '(none)'}",
        "",
        "## Results",
        "",
    ]
    for package in payload["packages"]:
        lines.extend(summarize_package(package))
    lines.extend(["", "## Boundary", "", payload["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backends", nargs="+", default=["embree", "optix"])
    parser.add_argument("--required-backends", nargs="*", default=[])
    parser.add_argument(
        "--sweep",
        nargs="*",
        help="One or more unique_rows:repeats:iterations specs.",
    )
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_PATH))
    parser.add_argument("--md-out", default=str(DEFAULT_MD_PATH))
    args = parser.parse_args(argv)
    payload = run_sweep_package(
        backends=tuple(args.backends),
        required_backends=tuple(args.required_backends),
        sweep_specs=parse_sweep_specs(args.sweep),
    )
    write_outputs(payload, Path(args.json_out), Path(args.md_out))
    print(json.dumps(payload["packages"], indent=2, sort_keys=True, default=str))
    return 0 if payload["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

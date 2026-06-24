from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_scope import validate_v4_0_scope_gate
from rtdsl.v4_scope import v4_0_scope_gate


def _write_markdown(path: Path, payload: dict[str, object], validation: dict[str, object]) -> None:
    lines = [
        "# V4.0 Scope Gate",
        "",
        "Status: generated development gate, not a release authorization",
        "",
        f"- gate status: `{payload['status']}`",
        f"- validation status: `{validation['status']}`",
        f"- release authorized: `{payload['release_authorized']}`",
        "",
        "## Included Surfaces",
        "",
    ]
    for surface in payload["included_surfaces"]:
        lines.append(f"- `{surface}`")
    lines.extend(["", "## Deferred To V4.x", ""])
    for item in payload["deferred_capabilities"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocking Reasons", ""])
    for item in payload["blocking_reasons"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Non-Authorization",
            "",
            "This gate does not authorize V4 release, broad V4 speedup wording, Tier-3 callback/PTX support, raw OptiX callbacks, embedding/C-ABI, or app-specific native kernels.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the V4.0 scope gate payload.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    gate = v4_0_scope_gate()
    payload = gate.as_dict()
    validation = validate_v4_0_scope_gate(gate)
    result = {"gate": payload, "validation": validation}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload, validation)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if validation["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())


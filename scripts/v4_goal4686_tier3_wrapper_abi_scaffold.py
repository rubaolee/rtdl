from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4686_tier3_wrapper_abi_scaffold import SEMANTIC_OPTIX_WRAPPER_SOURCE
from rtdsl.v4_goal4686_tier3_wrapper_abi_scaffold import validate_v4_goal4686_tier3_wrapper_abi_scaffold
from rtdsl.v4_goal4686_tier3_wrapper_abi_scaffold import v4_goal4686_tier3_wrapper_abi_scaffold


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    lines = [
        "# V4 Goal4686 Tier-3 Wrapper ABI Scaffold",
        "",
        "Status: local scaffold only, not Tier-3 support and not POD authorization",
        "",
        f"- status: `{payload['status']}`",
        f"- callback symbol: `{payload['callback_symbol']}`",
        f"- semantic entries: `{', '.join(str(item) for item in payload['semantic_entries'])}`",
        f"- old bare PTX success path allowed: `{payload['old_bare_ptx_success_path_allowed']}`",
        f"- pod authorized: `{payload['pod_authorized']}`",
        "",
        "## Boundary",
        "",
        "This dry-run emits the semantic wrapper scaffold that a later compile/link gate must test. It does not compile OptiX, link Numba PTX, launch a pipeline, or authorize Tier-3 support.",
        "",
        "## Non-Authorization",
        "",
        "No release, no Tier-3 public support, no raw OptiX callback support, no broad speedup wording, no whole-app claim, and no app-specific native kernels.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit the V4 Goal4686 Tier-3 semantic OptiX wrapper ABI scaffold.")
    parser.add_argument("--dry-run", action="store_true", help="Required; this scaffold does not compile or run OptiX.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--source-out", type=Path)
    args = parser.parse_args()

    if not args.dry_run:
        raise SystemExit("Goal4686 scaffold supports --dry-run only; compile/link is reserved for a later gate.")

    validation = validate_v4_goal4686_tier3_wrapper_abi_scaffold()
    scaffold = v4_goal4686_tier3_wrapper_abi_scaffold().as_dict(include_source=False)
    payload = {
        **scaffold,
        "schema": "rtdl.v4.goal4686_tier3_wrapper_abi_scaffold.v1",
        "validation_status": validation["status"],
        "missing_or_invalid": validation["missing_or_invalid"],
        "dry_run_only": True,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    if args.source_out:
        args.source_out.parent.mkdir(parents=True, exist_ok=True)
        args.source_out.write_text(SEMANTIC_OPTIX_WRAPPER_SOURCE + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if validation["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

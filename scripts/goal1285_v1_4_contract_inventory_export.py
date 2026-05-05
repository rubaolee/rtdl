from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import rtdsl as rt


def build_inventory_payload() -> dict[str, Any]:
    contracts = rt.validate_v1_4_primitive_contract_inventory()
    active_rows = sorted(
        {
            (contract["app_row"], contract["backend"])
            for contract in contracts
            if contract["active_v1_4_backend"]
        }
    )
    frozen_rows = sorted(
        {
            (contract["app_row"], contract["backend"])
            for contract in contracts
            if contract["backend"] in rt.FROZEN_BEFORE_V2_1_BACKENDS
        }
    )
    return {
        "goal": "1285",
        "status": "valid",
        "public_wording_authorized": False,
        "active_v1_4_backends": ["embree", "optix"],
        "frozen_before_v2_1_backends": list(rt.FROZEN_BEFORE_V2_1_BACKENDS),
        "contract_count": len(contracts),
        "active_contract_count": len(active_rows),
        "frozen_contract_count": len(frozen_rows),
        "contracts": list(contracts),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export the RTDL v1.4 primitive contract inventory.")
    parser.add_argument("--output-json", type=Path, help="Optional path for the JSON inventory artifact.")
    args = parser.parse_args(argv)

    payload = build_inventory_payload()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

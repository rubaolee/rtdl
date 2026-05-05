from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_ACTIVE_BACKENDS = ("embree", "optix")
EXPECTED_FROZEN_BACKENDS = ("vulkan", "hiprt", "apple_rt")
EXPECTED_CONTRACT_COUNT = 20
EXPECTED_ACTIVE_CONTRACT_COUNT = 8
EXPECTED_FROZEN_CONTRACT_COUNT = 12
EXPECTED_APP_ROWS = {
    "graph_analytics.visibility_edges",
    "database_analytics.sales_risk",
    "polygon_pair_overlap_area_rows",
    "polygon_set_jaccard",
}


def _load_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("inventory payload must be a JSON object")
    return payload


def validate_inventory_payload(payload: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []

    if payload.get("status") != "valid":
        failures.append(f"status must be valid, got {payload.get('status')!r}")
    if payload.get("public_wording_authorized") is not False:
        failures.append("public_wording_authorized must remain false")
    if tuple(payload.get("active_v1_4_backends", ())) != EXPECTED_ACTIVE_BACKENDS:
        failures.append("active_v1_4_backends must be ['embree', 'optix']")
    if tuple(payload.get("frozen_before_v2_1_backends", ())) != EXPECTED_FROZEN_BACKENDS:
        failures.append("frozen_before_v2_1_backends must be ['vulkan', 'hiprt', 'apple_rt']")
    if payload.get("contract_count") != EXPECTED_CONTRACT_COUNT:
        failures.append(f"contract_count must be {EXPECTED_CONTRACT_COUNT}")
    if payload.get("active_contract_count") != EXPECTED_ACTIVE_CONTRACT_COUNT:
        failures.append(f"active_contract_count must be {EXPECTED_ACTIVE_CONTRACT_COUNT}")
    if payload.get("frozen_contract_count") != EXPECTED_FROZEN_CONTRACT_COUNT:
        failures.append(f"frozen_contract_count must be {EXPECTED_FROZEN_CONTRACT_COUNT}")

    contracts = payload.get("contracts")
    if not isinstance(contracts, list):
        failures.append("contracts must be a list")
        contracts = []

    app_rows = {contract.get("app_row") for contract in contracts if isinstance(contract, dict)}
    if app_rows != EXPECTED_APP_ROWS:
        failures.append(f"app rows drifted: {sorted(str(row) for row in app_rows)}")

    active_contracts = [
        contract
        for contract in contracts
        if isinstance(contract, dict) and contract.get("active_v1_4_backend") is True
    ]
    active_pairs = {(contract.get("app_row"), contract.get("backend")) for contract in active_contracts}
    expected_active_pairs = {
        (app_row, backend) for app_row in EXPECTED_APP_ROWS for backend in EXPECTED_ACTIVE_BACKENDS
    }
    if active_pairs != expected_active_pairs:
        failures.append("active app/backend pairs must be exactly all app rows on Embree plus OptiX")

    for contract in contracts:
        if not isinstance(contract, dict):
            continue
        backend = contract.get("backend")
        if backend in EXPECTED_FROZEN_BACKENDS:
            if contract.get("active_v1_4_backend") is not False:
                failures.append(f"{contract.get('app_row')}/{backend} must remain inactive")
            if contract.get("backend_contract_role") != "compatibility_or_inactive":
                failures.append(f"{contract.get('app_row')}/{backend} must use compatibility_or_inactive")
        if contract.get("app_row") == "polygon_set_jaccard":
            if contract.get("public_wording_allowed") is not False:
                failures.append("Jaccard public_wording_allowed must remain false")
            if contract.get("migration_status") != "diagnostic_metadata_only":
                failures.append("Jaccard migration_status must remain diagnostic_metadata_only")

    return {
        "valid": not failures,
        "failure_count": len(failures),
        "failures": failures,
        "checked_contract_count": len(contracts),
        "boundary": (
            "This gate validates the v1.4 contract inventory snapshot only. "
            "It does not authorize public RTX wording or backend promotion."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate the RTDL v1.4 contract inventory JSON artifact.")
    parser.add_argument("inventory_json", type=Path)
    parser.add_argument("--output-json", type=Path, help="Optional gate result artifact path.")
    args = parser.parse_args(argv)

    result = validate_inventory_payload(_load_payload(args.inventory_json))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

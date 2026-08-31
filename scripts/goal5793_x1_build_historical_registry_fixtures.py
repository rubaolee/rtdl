"""Create the X1 historical registry, stage pin, and replayable fixtures.

These outputs exercise the candidate-agnostic registry/examiner machinery on
historical positive rows only.  They do not authorize search, selection,
candidate implementation, execution, GPU use, timing, or publication.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Mapping

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "scripts/goal5793_x1_registry_derivation.py"
EXPECTED_REGISTRY_SHA256 = (
    "337b0480109ee0184743b30ccd09dbd6a347b182211119d4765afa76bcab1d0c"
)
OUTPUT_DIR = ROOT / "history/internal_docs"
AUTHORITY_NAME = "goal5793_x1_historical_registry_authority_20260822.json"
PIN_NAME = "goal5793_x1_historical_registry_stage_pin_20260822.json"
FIXTURES_NAME = "goal5793_x1_historical_registry_fixtures_20260822.json"
ENVELOPE_NAME = "goal5793_x1_historical_runner_candidate_envelope_20260822.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_registry():
    resolved = REGISTRY_PATH.resolve(strict=True)
    if _sha256(resolved) != EXPECTED_REGISTRY_SHA256:
        raise RuntimeError("registry_derivation_hash_mismatch")
    name = "_goal5793_x1_historical_fixture_registry"
    spec = importlib.util.spec_from_file_location(name, resolved)
    if spec is None or spec.loader is None:
        raise RuntimeError("registry_derivation_spec_unavailable")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
    if Path(module.__file__).resolve(strict=True) != resolved:
        raise RuntimeError("registry_derivation_origin_mismatch")
    return module


def _json_bytes(value: Mapping[str, object]) -> bytes:
    return canonical_json_bytes(value) + b"\n"


def build_outputs() -> dict[str, bytes]:
    registry = _load_registry()
    authority, stage_pin, trusted_pin = registry.historical_registry_context()
    row_ids = (*registry.POSITIVE_IDS, registry.HELD_OUT_ROW)
    rows: list[dict[str, object]] = []
    first_payload: dict[str, object] | None = None
    first_receipt: dict[str, object] | None = None
    for row_id in row_ids:
        payload, receipt = registry.historical_registered_fixture(row_id)
        verified = registry.verify_registered_input(
            payload,
            receipt,
            registry_authority=authority,
            registry_stage_pin=stage_pin,
            trusted_stage_pin_sha256=trusted_pin,
        )
        if verified["status"] != "EXACT_REGISTERED_TEMPLATE_AND_SEVEN_SLOTS":
            raise RuntimeError(f"historical fixture did not verify: {row_id}")
        payload_bytes = canonical_json_bytes(payload)
        receipt_bytes = canonical_json_bytes(receipt)
        rows.append(
            {
                "row_id": row_id,
                "payload_canonical_bytes": len(payload_bytes),
                "payload_canonical_sha256": hashlib.sha256(payload_bytes).hexdigest(),
                "receipt_canonical_bytes": len(receipt_bytes),
                "receipt_canonical_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
                "payload": payload,
                "registry_receipt": receipt,
                "verification": verified,
            }
        )
        if first_payload is None:
            first_payload = payload
            first_receipt = receipt
    assert first_payload is not None and first_receipt is not None

    fixtures: dict[str, Any] = {
        "schema": "rtdl.goal5793.x1.historical_registry_fixtures.v1",
        "date": "2026-08-22",
        "status": "FORMAL_HISTORICAL_FIXTURES__NOT_FUTURE_GENERALIZATION_EVIDENCE",
        "registry_authority_sha256": authority["authority_sha256"],
        "registry_stage_pin_sha256": stage_pin["stage_pin_sha256"],
        "historical_fixture_count": len(rows),
        "rows": rows,
        "scope": {
            "historical_positive_replay_only": True,
            "future_candidate_authority_issued": False,
            "search_count": 0,
            "entropy_count": 0,
            "selection_count": 0,
            "candidate_implementation_count": 0,
            "execution_count": 0,
            "gpu_pod_ssh_count": 0,
            "registered_timing_count": 0,
            "publication_authorized": False,
        },
        "fixtures_sha256": "",
    }
    fixtures["fixtures_sha256"] = seal_document(
        fixtures,
        seal_field="fixtures_sha256",
        domain="rtdl.goal5793.x1.historical_registry_fixtures",
        version=1,
    )
    envelope = {
        "schema": registry.EXAM_INPUT_SCHEMA.replace(
            "generic_examiner_input", "runner_candidate_envelope"
        ),
        "payload": first_payload,
        "registry_receipt": first_receipt,
    }
    if envelope["schema"] != "rtdl.goal5793.x1.runner_candidate_envelope.v1":
        raise RuntimeError("runner envelope schema derivation mismatch")
    return {
        AUTHORITY_NAME: _json_bytes(authority),
        PIN_NAME: _json_bytes(stage_pin),
        FIXTURES_NAME: _json_bytes(fixtures),
        ENVELOPE_NAME: _json_bytes(envelope),
    }


def summary(outputs: Mapping[str, bytes]) -> dict[str, object]:
    return {
        "status": "DRY_RUN_PASS",
        "outputs": [
            {
                "path": name,
                "bytes": len(outputs[name]),
                "sha256": hashlib.sha256(outputs[name]).hexdigest(),
            }
            for name in (AUTHORITY_NAME, PIN_NAME, FIXTURES_NAME, ENVELOPE_NAME)
        ],
    }


def write_create_only(output_dir: Path, outputs: Mapping[str, bytes]) -> None:
    output_dir = output_dir.resolve()
    paths = [output_dir / name for name in outputs]
    existing = [path for path in paths if path.exists() or path.is_symlink()]
    if existing:
        raise FileExistsError(
            "create-only output exists: " + ", ".join(str(path) for path in existing)
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        with (output_dir / name).open("xb") as handle:
            handle.write(payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--write-create-only", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    result = summary(outputs)
    if args.write_create_only:
        write_create_only(args.output_dir, outputs)
        result["status"] = "CREATE_ONLY_WRITE_PASS"
        result["output_dir"] = str(args.output_dir.resolve())
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

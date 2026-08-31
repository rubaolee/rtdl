"""Fresh-process CLI for one inert Goal5793 X1 generic examination.

The runner is explicitly non-hermetic: the Python interpreter and standard
library remain in the TCB.  It exact-loads the frozen examiner, records the
interpreter/environment boundary, and keeps candidate bytes separate from the
out-of-band registry authority, stage pin, and trusted pin digest.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from typing import Mapping


ROOT = Path(__file__).resolve().parents[1]
GENERIC_EXAMINER_PATH = ROOT / "scripts/goal5793_x1_generic_examiner.py"
EXPECTED_GENERIC_EXAMINER_SHA256 = (
    "ef3d16fcbe0e4e84ea114fa8071ca005dfa3414c9afbc5ca2172a257d1d62489"
)
INPUT_ENVELOPE_SCHEMA = "rtdl.goal5793.x1.runner_candidate_envelope.v1"
RUNNER_RECEIPT_SCHEMA = "rtdl.goal5793.x1.fresh_process_exam_receipt.v1"
_ENVIRONMENT_KEYS = (
    "PYTHONHASHSEED",
    "PYTHONNOUSERSITE",
    "PYTHONPATH",
    "PYTHONSAFEPATH",
    "PYTHONDONTWRITEBYTECODE",
)


class RunnerError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _record(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": _sha256(resolved),
    }


def _load_json(path: Path, context: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RunnerError(f"{context}_json_error:{type(exc).__name__}:{exc}") from exc
    if not isinstance(value, dict):
        raise RunnerError(f"{context}_must_be_object")
    return value


def _load_exact_examiner():
    resolved = GENERIC_EXAMINER_PATH.resolve(strict=True)
    if _sha256(resolved) != EXPECTED_GENERIC_EXAMINER_SHA256:
        raise RunnerError("generic_examiner_hash_mismatch")
    name = "_goal5793_x1_runner_exact_generic_examiner"
    spec = importlib.util.spec_from_file_location(name, resolved)
    if spec is None or spec.loader is None:
        raise RunnerError("generic_examiner_spec_unavailable")
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
        raise RunnerError("generic_examiner_origin_mismatch")
    return module


def run(
    candidate_input_path: Path,
    registry_authority_path: Path,
    registry_stage_pin_path: Path,
    trusted_stage_pin_sha256: str,
) -> dict[str, object]:
    """Run one exam in this CLI process and return a sealed receipt."""

    if Path.cwd().resolve() != ROOT.resolve():
        raise RunnerError("runner_cwd_must_equal_frozen_repository_root")
    envelope = _load_json(candidate_input_path, "candidate_input")
    if set(envelope) != {"schema", "payload", "registry_receipt"}:
        raise RunnerError("candidate_envelope_keyset_mismatch")
    if envelope["schema"] != INPUT_ENVELOPE_SCHEMA:
        raise RunnerError("candidate_envelope_schema_mismatch")
    if not isinstance(envelope["payload"], Mapping) \
            or not isinstance(envelope["registry_receipt"], Mapping):
        raise RunnerError("candidate_payload_or_receipt_not_object")
    authority = _load_json(registry_authority_path, "registry_authority")
    stage_pin = _load_json(registry_stage_pin_path, "registry_stage_pin")
    examiner = _load_exact_examiner()
    result = examiner.examine(
        envelope["payload"],
        envelope["registry_receipt"],
        registry_authority=authority,
        registry_stage_pin=stage_pin,
        trusted_stage_pin_sha256=trusted_stage_pin_sha256,
    )
    executable = Path(sys.executable).resolve(strict=True)
    receipt: dict[str, object] = {
        "schema": RUNNER_RECEIPT_SCHEMA,
        "boundary": {
            "fresh_subprocess_required": True,
            "this_process_is_cli_exam_process": True,
            "hermetic": False,
            "python_interpreter_in_tcb": True,
            "python_standard_library_in_tcb": True,
            "host_os_and_filesystem_in_tcb": True,
            "hostile_sitecustomize_or_interpreter_sandbox_claimed": False,
        },
        "invocation": {
            "repository_root": str(ROOT.resolve()),
            "working_directory": str(Path.cwd().resolve()),
            "sys_executable": str(executable),
            "sys_executable_bytes": executable.stat().st_size,
            "sys_executable_sha256": _sha256(executable),
            "python_version": sys.version,
            "sys_flags": {
                "isolated": sys.flags.isolated,
                "no_site": sys.flags.no_site,
                "safe_path": sys.flags.safe_path,
            },
            "selected_environment": {
                key: os.environ.get(key) for key in _ENVIRONMENT_KEYS
            },
        },
        "inputs": {
            "candidate_envelope": _record(candidate_input_path),
            "registry_authority": _record(registry_authority_path),
            "registry_stage_pin": _record(registry_stage_pin_path),
            "out_of_band_trusted_stage_pin_sha256": trusted_stage_pin_sha256,
        },
        "frozen_runner_dependency": {
            **_record(GENERIC_EXAMINER_PATH),
            "expected_sha256": EXPECTED_GENERIC_EXAMINER_SHA256,
        },
        "examiner_result": result,
        "scope": {
            "search": False,
            "entropy": False,
            "selection": False,
            "candidate_implementation": False,
            "execution": False,
            "gpu": False,
            "pod": False,
            "ssh": False,
            "timing": False,
            "publication": False,
        },
        "receipt_sha256": "",
    }
    receipt["receipt_sha256"] = examiner._seal_document(
        receipt,
        seal_field="receipt_sha256",
        domain="rtdl.goal5793.x1.fresh_process_exam_receipt",
        version=1,
    )
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-input", type=Path, required=True)
    parser.add_argument("--registry-authority", type=Path, required=True)
    parser.add_argument("--registry-stage-pin", type=Path, required=True)
    parser.add_argument("--trusted-stage-pin-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.output.exists():
        raise RunnerError(f"create_only_output_exists:{args.output}")
    receipt = run(
        args.candidate_input,
        args.registry_authority,
        args.registry_stage_pin,
        args.trusted_stage_pin_sha256,
    )
    args.output.write_text(
        json.dumps(
            receipt, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False
        ) + "\n",
        encoding="utf-8",
    )
    return 0 if receipt["examiner_result"]["status"] \
        == "VALID_LAYERED_EXAMINATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Ingest a normalized X-HD external response JSON.

This app-owned helper wraps ``validate_xhd_external_response_intake.py`` and
creates an auditable intake case directory. It does not send requests,
download artifacts, run POD, or change any reproduction claim.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import shutil
import sys
from typing import Any, Dict, List


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
APP_DIR = SCRIPT_DIR.parent
DEFAULT_INCOMING_DIR = APP_DIR / "requests" / "incoming"
VALIDATOR_PATH = SCRIPT_DIR / "validate_xhd_external_response_intake.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_xhd_external_response_intake", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError("failed to load validator module")
    spec.loader.exec_module(module)
    return module


def _load_json(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("top-level response JSON must be an object")
    return data


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-._")
    if not slug:
        raise ValueError("case id must contain at least one safe character")
    return slug[:120]


def _default_case_id(response_json: pathlib.Path, payload: Dict[str, Any]) -> str:
    response_type = str(payload.get("response_type") or "unknown")
    received = ""
    received_from = payload.get("received_from")
    if isinstance(received_from, dict):
        received = str(received_from.get("received_date") or "")
    pieces = [received, response_type, response_json.stem]
    return _safe_slug("-".join(piece for piece in pieces if piece))


def _write_json(path: pathlib.Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_next_action(path: pathlib.Path, validation: Dict[str, Any]) -> None:
    pod_expected = bool(validation.get("pod_expected"))
    next_action = validation.get("next_action")
    valid = bool(validation.get("valid"))
    lines = [
        "# X-HD External Response Intake Next Action",
        "",
        f"valid: `{str(valid).lower()}`",
        f"response_type: `{validation.get('response_type')}`",
        f"next_action: `{next_action}`",
        f"pod_expected: `{str(pod_expected).lower()}`",
        "",
        "## Meaning",
        "",
    ]
    if not valid:
        lines.extend(
            [
                "This response is invalid or incomplete. Keep the affected X-HD",
                "full-paper reproduction scope blocked and request missing",
                "information before running any POD gate.",
                "",
            ]
        )
    elif pod_expected:
        lines.extend(
            [
                "This normalized response is valid and may justify a new",
                "provenance-ingestion goal. Use POD only inside that follow-up",
                "goal and only through `scripts/current_pod_ssh.py`.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "This response is valid but does not provide enough concrete",
                "artifact/provenance material for a POD gate. Keep the relevant",
                "scope blocked or request the missing material.",
                "",
            ]
        )
    lines.extend(
        [
            "## Not Allowed",
            "",
            "- claiming exact paper dataset reproduction from this intake result alone",
            "- claiming Figure 5 reproduction from this intake result alone",
            "- claiming full X-HD paper reproduction from this intake result alone",
            "- claiming author-vs-RTDL performance ratio from this intake result alone",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def ingest_response(
    response_json: pathlib.Path,
    incoming_dir: pathlib.Path = DEFAULT_INCOMING_DIR,
    case_id: str | None = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    response_json = response_json.resolve()
    payload = _load_json(response_json)
    case_slug = _safe_slug(case_id) if case_id else _default_case_id(response_json, payload)
    case_dir = incoming_dir / case_slug
    if case_dir.exists() and not overwrite:
        raise FileExistsError(f"intake case already exists: {case_dir}")
    case_dir.mkdir(parents=True, exist_ok=True)

    response_copy = case_dir / "response.json"
    if response_json != response_copy.resolve():
        shutil.copyfile(response_json, response_copy)

    validator = _load_validator()
    validation = validator.classify_intake(payload)
    validation_path = case_dir / "validation_result.json"
    _write_json(validation_path, validation)

    manifest = {
        "schema": "rtdl.paper_reproduction.xhd.external_response_intake.case_manifest.v1",
        "case_id": case_slug,
        "source_response_path": str(response_json),
        "response_copy": "response.json",
        "validation_result": "validation_result.json",
        "next_action_file": "next_action.md",
        "valid": bool(validation["valid"]),
        "pod_expected": bool(validation["pod_expected"]),
        "next_action": validation["next_action"],
        "sufficient_to_claim_exact_input": False,
        "requires_review_before_claim": True,
        "claim_boundary": validation["claim_boundary"],
        "not_allowed": validation["not_allowed"],
    }
    _write_json(case_dir / "manifest.json", manifest)
    _write_next_action(case_dir / "next_action.md", validation)
    return {
        "case_dir": str(case_dir),
        "manifest": manifest,
        "validation": validation,
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response_json", type=pathlib.Path)
    parser.add_argument("--incoming-dir", type=pathlib.Path, default=DEFAULT_INCOMING_DIR)
    parser.add_argument("--case-id", default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = ingest_response(args.response_json, args.incoming_dir, args.case_id, args.overwrite)
    except FileExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except Exception as exc:
        print(f"ingest failed: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result["manifest"], indent=2, sort_keys=True))
    return 0 if result["validation"]["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

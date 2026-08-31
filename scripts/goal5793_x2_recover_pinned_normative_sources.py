#!/usr/bin/env python3
"""Create-only recovery of the two already-pinned normative NIST source files."""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import ssl
import time
from typing import Any, Callable, Mapping
import urllib.error
import urllib.parse
import urllib.request


DATE = "2026-08-22"
AUTHORITY_DOMAIN = "rtdl.goal5793.x2.normative_source_recovery_work_authority"
CLOSURE_DOMAIN = "rtdl.goal5793.x2.normative_source_recovery_owner_closure"
RECEIPT_DOMAIN = "rtdl.goal5793.x2.normative_source_recovery_receipt"
CANONICALIZATION_NAME = "UTF8_SORTED_KEYS_COMPACT_ENSURE_ASCII_FALSE_ALLOW_NAN_FALSE_NO_TRAILING_NEWLINE_V1"
RETRY_DELAYS = (0, 3, 6, 12, 24, 48)
USER_AGENT = "RTDL-Goal5793-X2-SourceRecovery/1.0"
SOURCES = (
    {
        "source_id": "nist_ir_8213_draft",
        "url": "https://nvlpubs.nist.gov/nistpubs/ir/2019/NIST.IR.8213-draft.pdf",
        "accept": "application/pdf",
        "output_name": "NIST.IR.8213-draft.pdf",
        "bytes": 762001,
        "sha256": "6fee39f6cd82d6c1ab219e29bdec77cbf3e07075324ac3202661d7578ee8f183",
    },
    {
        "source_id": "nist_beacon_2_xsd",
        "url": "https://csrc.nist.gov/csrc/media/Projects/interoperable-randomness-beacons/documents/certificate/beacon-2.0.xsd",
        "accept": "application/xml,text/xml",
        "output_name": "beacon-2.0.xsd",
        "bytes": 19033,
        "sha256": "24c5b5b6508c0c33db2cda1902ea7f3b2009224895ba4e3fe275b7f4511675d6",
    },
)


class RecoveryError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _seal(document: Mapping[str, Any], field: str, domain: str) -> str:
    clone = dict(document); clone.pop(field, None)
    body = {
        "canonicalization": CANONICALIZATION_NAME,
        "domain": domain,
        "projection": f"document_without:{field}",
        "value": clone,
        "version": 1,
    }
    return _sha(_canonical(body))


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    except Exception as exc:
        raise RecoveryError("RECOVERY_AUTHORITY_JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise RecoveryError("RECOVERY_AUTHORITY_JSON_INVALID")
    return value


def _identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(data), "sha256": _sha(data)}


def _validate_https_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username is not None or parsed.password is not None or parsed.fragment:
        raise RecoveryError("RECOVERY_REDIRECT_URL_INVALID")
    return value


def validate_authorities(authority_path: Path, review_path: Path, closure_path: Path) -> dict[str, Any]:
    authority = _load(authority_path)
    if authority.get("schema") != "rtdl.goal5793.x2.normative_source_recovery_work_authority.v2" or authority.get("work_authority_sha256") != _seal(authority, "work_authority_sha256", AUTHORITY_DOMAIN):
        raise RecoveryError("RECOVERY_WORK_AUTHORITY_MISMATCH")
    if authority.get("exact_sources") != list(SOURCES) or authority.get("network_execution_authorized_before_returned_review_and_owner_closure") is not False:
        raise RecoveryError("RECOVERY_WORK_AUTHORITY_MISMATCH")
    tool = _identity(Path(__file__).resolve())
    declared_tool = authority.get("recovery_tool")
    if not isinstance(declared_tool, Mapping) or declared_tool.get("bytes") != tool["bytes"] or declared_tool.get("sha256") != tool["sha256"]:
        raise RecoveryError("RECOVERY_TOOL_IDENTITY_MISMATCH")
    closure = _load(closure_path)
    if closure.get("schema") != "rtdl.goal5793.x2.normative_source_recovery_owner_closure.v1" or closure.get("closure_sha256") != _seal(closure, "closure_sha256", CLOSURE_DOMAIN):
        raise RecoveryError("RECOVERY_OWNER_CLOSURE_MISMATCH")
    bindings = closure.get("bindings")
    expected_bindings = {
        "work_authority": _identity(authority_path.resolve()),
        "returned_review": _identity(review_path.resolve()),
        "recovery_tool": tool,
    }
    if bindings != expected_bindings:
        raise RecoveryError("RECOVERY_OWNER_CLOSURE_BINDING_MISMATCH")
    authorization = closure.get("authorization")
    if not isinstance(authorization, dict) or authorization.get("authorizes_exact_pinned_source_recovery") is not True or any(value is not False for key, value in authorization.items() if key != "authorizes_exact_pinned_source_recovery"):
        raise RecoveryError("RECOVERY_OWNER_CLOSURE_AUTHORIZATION_MISMATCH")
    return {"authority": authority, "closure": closure, "bindings": expected_bindings}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        return None


def _request_once(url: str, accept: str, opener: Any, clock: Callable[[], datetime]) -> tuple[int | None, list[dict[str, str]], bytes, str | None, str, str]:
    started = clock().astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    request = urllib.request.Request(url, method="GET", headers={"Accept": accept, "User-Agent": USER_AGENT})
    try:
        with opener.open(request, timeout=60) as response:
            status = int(response.status)
            headers = [{"name": key, "value": value} for key, value in response.headers.items()]
            body = response.read(2_000_000)
            error = None
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        headers = [{"name": key, "value": value} for key, value in exc.headers.items()]
        body = exc.read(2_000_000)
        error = f"HTTP_{status}"
    except Exception as exc:
        status = None; headers = []; body = b""; error = f"{type(exc).__name__}:{exc}"
    received = clock().astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    return status, headers, body, error, started, received


def recover_sources(
    authority_path: Path,
    review_path: Path,
    closure_path: Path,
    output_dir: Path,
    *,
    opener: Any | None = None,
    sleeper: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> dict[str, Any]:
    validated = validate_authorities(authority_path.resolve(), review_path.resolve(), closure_path.resolve())
    output_dir = output_dir.resolve()
    if output_dir.exists() or output_dir.is_symlink() or not output_dir.parent.is_dir():
        raise RecoveryError("RECOVERY_CREATE_ONLY_TARGET_EXISTS_OR_PARENT_INVALID")
    staging_dir = output_dir.parent / (output_dir.name + ".staging-create-only")
    if staging_dir.exists() or staging_dir.is_symlink():
        raise RecoveryError("RECOVERY_CREATE_ONLY_STAGING_EXISTS")
    targets = [output_dir / source["output_name"] for source in SOURCES]
    receipt_path = output_dir / "goal5793_x2_normative_source_recovery_receipt_20260822.json"
    if opener is None:
        context = ssl.create_default_context()
        opener = urllib.request.build_opener(_NoRedirect(), urllib.request.HTTPSHandler(context=context))
    recovered: list[tuple[Path, bytes]] = []
    source_rows: list[dict[str, Any]] = []
    for source, target in zip(SOURCES, targets):
        attempts: list[dict[str, Any]] = []
        success: bytes | None = None
        for index, delay in enumerate(RETRY_DELAYS):
            if delay:
                sleeper(delay)
            status, headers, body, error, started, received = _request_once(source["url"], source["accept"], opener, clock)
            row = {
                "attempt": index + 1, "scheduled_delay_seconds": delay, "method": "GET", "url": source["url"],
                "request_headers": [{"name": "Accept", "value": source["accept"]}, {"name": "User-Agent", "value": USER_AGENT}],
                "request_started_at_utc": started, "status": status, "response_headers": headers,
                "response_received_at_utc": received, "body_bytes": len(body), "body_sha256": _sha(body),
                "body_base64": base64.b64encode(body).decode("ascii"), "error": error,
            }
            attempts.append(row)
            if status == 200 and error is None:
                if len(body) != source["bytes"] or _sha(body) != source["sha256"]:
                    raise RecoveryError("RECOVERY_SOURCE_DRIFT__NO_ALTERNATE_OR_RETRY")
                success = body
                break
        if success is None:
            raise RecoveryError("RECOVERY_RETRY_EXHAUSTED__NO_PARTIAL_WRITE")
        recovered.append((target, success))
        source_rows.append({"source_id": source["source_id"], "url": source["url"], "output_name": source["output_name"], "bytes": len(success), "sha256": _sha(success), "attempts": attempts})
    receipt: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.normative_source_recovery_receipt.v1", "date": DATE,
        "status": "EXACT_PINNED_NORMATIVE_SOURCE_BYTES_RECOVERED__NOT_X2_CLOSURE__NO_BEACON_OR_SEARCH",
        "authority_bindings": validated["bindings"], "sources": source_rows,
        "activity": {"http_source_recovery_calls": sum(len(row["attempts"]) for row in source_rows), "provider_search_calls": 0, "beacon_calls": 0, "entropy_draws": 0, "candidate_search_calls": 0, "selection_count": 0, "gpu_ssh_pod": 0, "timing_count": 0},
        "authorization": {"normative_verifier_implementation": False, "live_search": False, "beacon": False, "entropy": False, "selection": False, "candidate_work": False, "gpu_ssh_pod": False, "timing": False, "publication": False},
        "receipt_sha256": "",
    }
    receipt["receipt_sha256"] = _seal(receipt, "receipt_sha256", RECEIPT_DOMAIN)
    staging_dir.mkdir()
    for target, data in recovered:
        with (staging_dir / target.name).open("xb") as handle:
            handle.write(data)
    with (staging_dir / receipt_path.name).open("xb") as handle:
        handle.write(_canonical(receipt) + b"\n")
    staging_dir.rename(output_dir)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--returned-review", type=Path, required=True)
    parser.add_argument("--owner-closure", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execute-network-create-only", action="store_true")
    args = parser.parse_args()
    if not args.execute_network_create_only:
        raise SystemExit("NETWORK_EXECUTION_REQUIRES_EXPLICIT_POSTREVIEW_CREATE_ONLY_FLAG")
    receipt = recover_sources(args.authority, args.returned_review, args.owner_closure, args.output_dir)
    print(json.dumps({"status": "PASS", "receipt_sha256": receipt["receipt_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Re-run the bounded Goal5791 Amendment-A1 claim-hygiene enumeration."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re


GOAL = 5791
A1_PATH = "history/internal_docs/goal5791_formal_v4_local_closure_amendment_a1_claim_hygiene_authority_20260821.json"
A1_FILE_SHA256 = "c0128ff5b8949b590352ec3d184d55a501517cc610eeb87590aa4ed0dfe2d7d5"
A1_INTERNAL_SHA256 = "e71be2def61ec7530f274c9dfe6bfa84abc4d99e1c01fe44e7cac2400da77a33"
CLOSURE_PATH = "history/internal_docs/goal5791_formal_v4_local_scientific_closure_20260821.json"
CLOSURE_FILE_SHA256 = "829f199637abcb5632fb47c1996616670e38c3db687c3b9f312442dc4e207302"
SUPERSESSION_PATH = "history/internal_docs/goal5791_terminal_analysis_audit_v1_v2_supersession_authority_20260821.json"
SUPERSESSION_FILE_SHA256 = "ba4d729629fdba0f4606e1e7884ae724803cf214c7c65dd7f29a95b7fbc9759f"
DECISION_PATH = "history/internal_docs/goal5791_formal_v4_analysis_successor_decision_review_20260821.md"
DECISION_FILE_SHA256 = "77e00d1448ed5d9af77381d0b27f1bdf0094304aab1823aa80af79b48ca37068"
TERMINAL_REVIEW_PATH = "history/internal_docs/goal5791_formal_v4_primary_evaluator_terminal_review_20260821.md"
TERMINAL_REVIEW_FILE_SHA256 = "a5974711115e9508715500884f29deaac3fd192743e71f78e591e59bf540be49"
RESULT_PATH = "history/internal_docs/goal5791_formal_v4_analysis_successor_20260821/RESULT.json"
RESULT_FILE_SHA256 = "e8417161e33574bb76d1652a3783bfeae77fbe1777e236bfdb066f149b0c6bc5"
MAIN_REVIEW_PATH = "history/internal_docs/review_goal5791_formal_v4_rtx4000ada_result_20260821.md"
MAIN_REVIEW_FILE_SHA256 = "c97052ee1e75f0098648b2a62309fd4a9b76b1a3e3edda3cc6bdc3d46a687100"
A1_REVIEW_PATH = "history/internal_docs/review_goal5791_formal_v4_rtx4000ada_result_amendment_a1_20260821.md"
A1_REVIEW_FILE_SHA256 = "2ff0652ffcbd80872b5358318ddde865b7c34cd8190fed28ac07361aa9fd6ed0"
A1_CFR_PATH = "history/internal_docs/call_for_review_goal5791_formal_v4_rtx4000ada_result_amendment_a1_20260821.md"
A1_CFR_FILE_SHA256 = "8502292a696b82bc18bb5109a3c31f1fb5bd02aeb1d89de5ab2109921b9f0d2f"
FINAL_SOURCE_PATHS = {
    "evaluator_sha256": "scripts/goal5791_formal_evaluate.py",
    "independent_recount_sha256": "scripts/goal5791_formal_independent_recount.py",
    "regression_fixture_sha256": "tests/goal5791_formal_evaluator_recount_test.py",
}
EXPECTED_MISSING_KEYS = {
    "authorizes_particle_causal_claim",
    "authorizes_replacement_worker",
    "authorizes_universal_fusion_claim",
}


class Goal5791A1ScanError(RuntimeError):
    pass


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _file_sha(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def _object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Goal5791A1ScanError(f"non-object JSON: {path}")
    return value


def _seal(value: dict[str, object], field: str) -> str:
    unsigned = dict(value)
    claimed = unsigned.pop(field, None)
    if not isinstance(claimed, str) or claimed != _digest(unsigned):
        raise Goal5791A1ScanError(f"seal mismatch: {field}")
    return claimed


def scan(repository_root: Path, pointer_path: Path) -> dict[str, object]:
    expected_files = {
        A1_PATH: A1_FILE_SHA256,
        CLOSURE_PATH: CLOSURE_FILE_SHA256,
        SUPERSESSION_PATH: SUPERSESSION_FILE_SHA256,
        DECISION_PATH: DECISION_FILE_SHA256,
        TERMINAL_REVIEW_PATH: TERMINAL_REVIEW_FILE_SHA256,
        RESULT_PATH: RESULT_FILE_SHA256,
        MAIN_REVIEW_PATH: MAIN_REVIEW_FILE_SHA256,
        A1_REVIEW_PATH: A1_REVIEW_FILE_SHA256,
        A1_CFR_PATH: A1_CFR_FILE_SHA256,
    }
    for relative, expected in expected_files.items():
        path = repository_root / relative
        if not path.is_file() or _file_sha(path) != expected:
            raise Goal5791A1ScanError(f"predecessor identity drifted: {relative}")

    a1 = _object(repository_root / A1_PATH)
    closure = _object(repository_root / CLOSURE_PATH)
    supersession = _object(repository_root / SUPERSESSION_PATH)
    result = _object(repository_root / RESULT_PATH)
    if _seal(a1, "amendment_sha256") != A1_INTERNAL_SHA256:
        raise Goal5791A1ScanError("A1 internal identity drifted")
    closure_internal = _seal(closure, "closure_sha256")
    if closure_internal != a1["predecessor_closure"]["closure_sha256"]:
        raise Goal5791A1ScanError("closure internal cross-pin drifted")

    decision_text = (repository_root / DECISION_PATH).read_text(encoding="utf-8")
    terminal_text = (repository_root / TERMINAL_REVIEW_PATH).read_text(
        encoding="utf-8")
    p2_labels = sorted(set(re.findall(r"P2-[1-9][0-9]*", decision_text)))
    if p2_labels != ["P2-1", "P2-2", "P2-3", "P2-4"] \
            or decision_text.count("P2_3") != 1 \
            or closure.get("local_review", {}).get("p2_count") != 4 \
            or a1["corrections"]["decision_review_p2_count"].get(
                "controlling_p2_count") != 4:
        raise Goal5791A1ScanError("P2 enumeration drifted")

    lineage = a1["corrections"]["source_lineage"]
    intermediate = lineage["historical_intermediate_sources"]
    final = lineage["controlling_final_sources"]
    if lineage.get("historical_intermediate_sources_are_controlling") is not False:
        raise Goal5791A1ScanError("intermediate lineage widened")
    result_lineage = result.get("analysis_source_lineage", {})
    expected_result_final = {
        "evaluator_sha256": result_lineage.get("corrected_evaluator_sha256"),
        "independent_recount_sha256": result_lineage.get(
            "corrected_independent_recount_sha256"),
        "regression_fixture_sha256": result_lineage.get(
            "corrected_regression_test_sha256"),
    }
    if final != expected_result_final:
        raise Goal5791A1ScanError("final lineage/result drifted")
    result_bytes = (repository_root / RESULT_PATH).read_bytes()
    for field, value in intermediate.items():
        if not isinstance(value, str) or terminal_text.count(value) != 1 \
                or value.encode("ascii") in result_bytes:
            raise Goal5791A1ScanError(f"intermediate lineage drifted: {field}")
    for field, relative in FINAL_SOURCE_PATHS.items():
        if _file_sha(repository_root / relative) != final[field]:
            raise Goal5791A1ScanError(f"final source bytes drifted: {field}")

    result_auth = result.get("authorization")
    a1_auth = a1.get("authorization")
    closure_auth = closure.get("authorization")
    supersession_auth = supersession.get("authorization")
    if not all(isinstance(value, dict) for value in (
            result_auth, a1_auth, closure_auth, supersession_auth)):
        raise Goal5791A1ScanError("authorization object malformed")
    if len(result_auth) != 12 or set(a1_auth) != set(result_auth) \
            or any(value is not False for value in result_auth.values()) \
            or any(value is not False for value in a1_auth.values()) \
            or set(result_auth) - set(closure_auth) != EXPECTED_MISSING_KEYS \
            or set(result_auth) - set(supersession_auth) != EXPECTED_MISSING_KEYS \
            or set(a1["corrections"]["authorization_schema"][
                "missing_from_predecessor_governance_objects"]) \
                != EXPECTED_MISSING_KEYS:
        raise Goal5791A1ScanError("authorization enumeration drifted")

    pointer = _object(pointer_path)
    pointer_seal = _seal(pointer, "pointer_sha256")
    source_path = Path(__file__).resolve()
    if pointer.get("schema") != "rtdl.goal5791.external_review_entrypoint.v1" \
            or pointer.get("goal") != GOAL \
            or pointer.get("a1_authority", {}).get("path") != A1_PATH \
            or pointer.get("a1_authority", {}).get("file_sha256") \
                != A1_FILE_SHA256 \
            or pointer.get("a1_authority", {}).get("amendment_sha256") \
                != A1_INTERNAL_SHA256 \
            or pointer.get("mechanized_scan", {}).get("script_sha256") \
                != _file_sha(source_path) \
            or any(value is not False for value in pointer.get(
                "authorization", {}).values()):
        raise Goal5791A1ScanError("forward pointer drifted")

    payload: dict[str, object] = {
        "schema": "rtdl.goal5791.claim_hygiene_amendment_a1_scan.v1",
        "goal": GOAL,
        "status": "PASS__A1_ENUMERATION_REPLAYED__FORWARD_POINTER_VERIFIED",
        "a1_authority_file_sha256": A1_FILE_SHA256,
        "a1_authority_sha256": A1_INTERNAL_SHA256,
        "bounded_predecessor_file_count": len(expected_files),
        "bounded_predecessor_files": [
            {"path": path, "sha256": sha}
            for path, sha in sorted(expected_files.items())
        ],
        "p2_labels_rebuilt": p2_labels,
        "p2_header_token_occurrence_count_in_decision_review": 1,
        "controlling_p2_count_rebuilt": 4,
        "intermediate_source_hash_count": len(intermediate),
        "intermediate_sources_present_once_in_historical_review": True,
        "intermediate_sources_absent_from_result": True,
        "final_source_hash_count": len(final),
        "final_sources_equal_result_and_live_bytes": True,
        "result_authorization_key_count": len(result_auth),
        "a1_authorization_exactly_equals_result_and_all_false": True,
        "predecessor_missing_authorization_keys": sorted(EXPECTED_MISSING_KEYS),
        "predecessor_missing_authorization_key_count": len(EXPECTED_MISSING_KEYS),
        "forward_pointer_file_sha256": _file_sha(pointer_path),
        "forward_pointer_sha256": pointer_seal,
        "unclassified_active_risk_count": 0,
        "scientific_artifact_or_result_changed": False,
        "authorization_granted": False,
    }
    payload["scan_sha256"] = _digest(payload)
    return payload


def _write_create_only(path: Path, value: object) -> None:
    data = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)
            + "\n").encode("utf-8")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--pointer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repository_root.resolve()
    _write_create_only(args.output.resolve(), scan(root, args.pointer.resolve()))
    print(args.output.resolve())


if __name__ == "__main__":
    main()

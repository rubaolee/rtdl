from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import tarfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "goal5789_successor_theory_readiness_review_packet_v2"

OUTPUT = ROOT / "history/internal_docs/goal5789_successor_theory_readiness_review_packet_v2_20260821.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5789_successor_theory_readiness_review_packet_v2_twin_20260821.tar.gz"
MANIFEST_OUTPUT = ROOT / "history/internal_docs/goal5789_successor_theory_readiness_review_packet_v2_manifest_20260821.json"

GOAL5789_MANIFEST = (
    "history/internal_docs/goal5789_delivery_manifest_20260816.json",
    13176,
    "523c95139d24a84ad2ad02ff1e0bb3ee60fc87e540cdaca112c8b74870ef7667",
)
GOAL5790_A1_MANIFEST = (
    "history/internal_docs/goal5790_a1_delivery_manifest_20260816.json",
    17351,
    "cc309514aa7e6d96a1431c1ab8e848b89efd143ef82971e798dc6758809041e0",
)
GOAL5792_RESULT = (
    "history/internal_docs/goal5792_local_completion_result_20260820.json",
    9147,
    "cfffddcb47e1af24fa0a8c5e10ee1349bfe753d39c88208700119173ef1a0145",
)

SUCCESSOR_CONTEXT = (
    (
        "history/internal_docs/review_goal5790_a1_home_rejected_program_suite_20260816.md",
        14500,
        "778c996516c85ab185c8e3be23132794348827ad13f54d774e402fc42f09e9d9",
    ),
    (
        "history/internal_docs/goal5790_a1_owner_returned_external_review_absorption_20260817.json",
        11626,
        "e830a626689cc362c8223c70544e28bf97d0aa00086727b901cdcb54677f91eb",
    ),
    (
        "history/internal_docs/goal5790_a1_postreview_claim_clarification_20260817.md",
        8076,
        "9fc25d0b5bb0bf81551a119066b6c0913178d0c56da54747212677354a92cbff",
    ),
    (
        "history/internal_docs/goal5791_assume_guarantee_positioning_and_goal5793_acceptance_challenge_20260819.md",
        6724,
        "672fdb360bd0881c8003143b46847f053c8ebdec65f70d49d473433cdab7681e",
    ),
    (
        "history/internal_docs/goal5791_cgo_theory_positioning_review_absorption_20260819.json",
        7859,
        "f99cbf22646d0ec8893ea694459cdcf66ab4e8e9b8cd217d43b095d3cdc3b92a",
    ),
    (
        "history/internal_docs/review_goal5791_formal_v4_rtx4000ada_result_20260821.md",
        32977,
        "c97052ee1e75f0098648b2a62309fd4a9b76b1a3e3edda3cc6bdc3d46a687100",
    ),
    (
        "history/internal_docs/goal5791_formal_v4_external_review_absorption_and_amendment_a2_20260821.json",
        5619,
        "4303f2ca1c1e3c61c6a056cb38207a0486690304039edfc6df99d2228c5a4a89",
    ),
    (
        "history/internal_docs/goal5791_formal_v4_external_review_absorption_and_amendment_a2_20260821.md",
        1755,
        "04ae367f2f85b0a8af6c5bd903d555fdf20b268975fa21efc8679e030b95f157",
    ),
    (
        "history/internal_docs/goal5792_local_completion_closure_20260820.json",
        3055,
        "0abfdd4c6a02a37202342efae0b25b8c82296a605de7c1ce37a8d9eb6069498a",
    ),
    (
        "history/internal_docs/review_goal5792_local_completion_20260820.md",
        27311,
        "b0b2a083c3060c5e1d990c36eadd6e5057b9b88956b2701db25050d212970382",
    ),
    (
        "history/internal_docs/goal5792_owner_returned_external_review_absorption_20260821.json",
        6852,
        "ead1d6554fe212b87c00e388b8319959abf0232f326ec6b09215bf429e001696",
    ),
    (
        "history/internal_docs/goal5792_owner_returned_external_review_absorption_20260821.md",
        5599,
        "06a3262017c9bbb5f0e37e0e3d74f3a6b643ad9b26d428d5da43d303182166b7",
    ),
    (
        "history/internal_docs/goal5792_postreview_closure_20260821.json",
        3494,
        "25c739935225dcc11239845705c63e7efc0bb539d1795044edefd3094414ff3c",
    ),
    (
        "history/internal_docs/goal5789_successor_review_packet_v1_pre_review_supersession_20260821.json",
        2095,
        "b5656327e1dbcbed6e13e7d84b5f36adb32abb4b01f8e42491621b7dfa968e92",
    ),
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def _safe_relative(path: str) -> str:
    candidate = PurePosixPath(path.replace("\\", "/"))
    if candidate.is_absolute() or not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise RuntimeError(f"unsafe repository-relative path: {path!r}")
    return candidate.as_posix()


def _read_expected(path: str, size: int, sha256: str) -> bytes:
    relative = _safe_relative(path)
    source = ROOT / Path(*PurePosixPath(relative).parts)
    if source.is_symlink() or not source.is_file():
        raise RuntimeError(f"expected regular non-link file: {relative}")
    data = source.read_bytes()
    if len(data) != size or _sha(data) != sha256:
        raise RuntimeError(f"identity mismatch: {relative}")
    return data


def _load_json_expected(identity: tuple[str, int, str]) -> tuple[dict[str, object], bytes]:
    path, size, sha256 = identity
    data = _read_expected(path, size, sha256)
    value = json.loads(data.decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value, data


def _add(entries: dict[str, tuple[bytes, str]], path: str, data: bytes, provenance: str) -> None:
    relative = _safe_relative(path)
    previous = entries.get(relative)
    if previous is not None and previous[0] != data:
        raise RuntimeError(f"conflicting duplicate payload: {relative}")
    entries[relative] = (data, provenance if previous is None else previous[1] + "+" + provenance)


def _collect_manifest_payloads(
    entries: dict[str, tuple[bytes, str]],
    manifest: dict[str, object],
    provenance: str,
) -> None:
    payloads = manifest.get("payloads")
    count_field = "payload_count"
    bytes_field = "payload_bytes"
    if payloads is None:
        payloads = manifest.get("files")
        count_field = "listed_file_count"
        bytes_field = "listed_file_bytes"
    if not isinstance(payloads, list):
        raise RuntimeError(f"{provenance}: payloads must be a list")
    expected_count = manifest.get(count_field)
    expected_bytes = manifest.get(bytes_field)
    if expected_count != len(payloads):
        raise RuntimeError(f"{provenance}: payload count mismatch")
    total = 0
    for row in payloads:
        if not isinstance(row, dict) or not {"path", "sha256", "bytes"}.issubset(row):
            raise RuntimeError(f"{provenance}: malformed payload row")
        path = row["path"]
        size = row["bytes"]
        sha256 = row["sha256"]
        if not isinstance(path, str) or not isinstance(size, int) or isinstance(size, bool) or not isinstance(sha256, str):
            raise RuntimeError(f"{provenance}: invalid payload row types")
        data = _read_expected(path, size, sha256)
        _add(entries, path, data, provenance)
        total += size
    if expected_bytes != total:
        raise RuntimeError(f"{provenance}: payload byte total mismatch")


def _collect_goal5792_pins(entries: dict[str, tuple[bytes, str]], result: dict[str, object]) -> None:
    pins = result.get("pins")
    if not isinstance(pins, dict):
        raise RuntimeError("Goal5792 result pins must be an object")
    for name, row in pins.items():
        if not isinstance(name, str) or not isinstance(row, dict) or set(row) != {"path", "sha256", "bytes"}:
            raise RuntimeError("Goal5792 pin row malformed")
        path = row["path"]
        size = row["bytes"]
        sha256 = row["sha256"]
        if not isinstance(path, str) or not isinstance(size, int) or isinstance(size, bool) or not isinstance(sha256, str):
            raise RuntimeError("Goal5792 pin row types invalid")
        _add(entries, path, _read_expected(path, size, sha256), "goal5792_result_pin")


def _tar_bytes(payloads: dict[str, bytes], manifest_bytes: bytes) -> bytes:
    raw = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as archive:
            all_payloads = dict(payloads)
            all_payloads["PACKET_MANIFEST.json"] = manifest_bytes
            for relative, data in sorted(all_payloads.items()):
                info = tarfile.TarInfo(f"{PREFIX}/{relative}")
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o444
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                archive.addfile(info, io.BytesIO(data))
    return raw.getvalue()


def _write_create_only(path: Path, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    descriptor = os.open(path, flags, 0o444)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def main() -> None:
    entries: dict[str, tuple[bytes, str]] = {}

    goal5789, goal5789_bytes = _load_json_expected(GOAL5789_MANIFEST)
    _collect_manifest_payloads(entries, goal5789, "goal5789_delivery_manifest")
    _add(entries, GOAL5789_MANIFEST[0], goal5789_bytes, "packet_root")

    goal5790, goal5790_bytes = _load_json_expected(GOAL5790_A1_MANIFEST)
    _collect_manifest_payloads(entries, goal5790, "goal5790_a1_delivery_manifest")
    _add(entries, GOAL5790_A1_MANIFEST[0], goal5790_bytes, "packet_root")

    goal5792, goal5792_bytes = _load_json_expected(GOAL5792_RESULT)
    _collect_goal5792_pins(entries, goal5792)
    _add(entries, GOAL5792_RESULT[0], goal5792_bytes, "packet_root")

    for path, size, sha256 in SUCCESSOR_CONTEXT:
        _add(entries, path, _read_expected(path, size, sha256), "successor_context")

    payload_rows = [
        {
            "path": path,
            "bytes": len(data),
            "sha256": _sha(data),
            "provenance": provenance,
        }
        for path, (data, provenance) in sorted(entries.items())
    ]
    payload_set_sha256 = _sha(_canonical(payload_rows))
    manifest = {
        "schema": "rtdl.goal5789.successor_theory_readiness_review_packet.v2",
        "goal": 5789,
        "date": "2026-08-21",
        "status": "FROZEN_EXACT_REVIEW_PACKET__OWNER_SELECTED_EXTERNAL_REVIEW_PENDING",
        "review_scope": "Goal5789 bounded registered-family assume-guarantee compatibility, post-Goal5790-A1 empirical anchor, post-Goal5792 UNKNOWN boundary, and Goal5793 entry decision",
        "root_inputs": {
            "goal5789_delivery_manifest": {
                "path": GOAL5789_MANIFEST[0],
                "bytes": GOAL5789_MANIFEST[1],
                "sha256": GOAL5789_MANIFEST[2],
            },
            "goal5790_a1_delivery_manifest": {
                "path": GOAL5790_A1_MANIFEST[0],
                "bytes": GOAL5790_A1_MANIFEST[1],
                "sha256": GOAL5790_A1_MANIFEST[2],
            },
            "goal5792_local_result": {
                "path": GOAL5792_RESULT[0],
                "bytes": GOAL5792_RESULT[1],
                "sha256": GOAL5792_RESULT[2],
            },
        },
        "payload_count": len(payload_rows),
        "payload_bytes": sum(row["bytes"] for row in payload_rows),
        "payload_set_sha256": payload_set_sha256,
        "payloads": payload_rows,
        "claim_boundary": {
            "goal5789_is_bounded_not_universal": True,
            "authorities_remain_tcb": True,
            "jointly_wrong_consistent_authorities_detected": False,
            "rtxrmq_claimed_checker_calculus_held_out": False,
            "rtxrmq_claimed_no_special_case_replay": True,
            "all_v4_paths_claimed_semantically_gated": False,
            "goal5793_completed_or_preregistered": False,
        },
        "authorization": {
            "authorizes_product_or_native_change": False,
            "authorizes_home_gpu_or_pod": False,
            "authorizes_goal5793_execution": False,
            "authorizes_performance_measurement": False,
            "authorizes_public_release": False,
            "authorizes_publication": False,
            "authorizes_submission": False,
        },
    }
    manifest_bytes = _canonical(manifest)
    payload_bytes = {path: data for path, (data, _) in entries.items()}
    archive = _tar_bytes(payload_bytes, manifest_bytes)
    twin = _tar_bytes(payload_bytes, manifest_bytes)
    if archive != twin:
        raise RuntimeError("deterministic archive twin mismatch")
    if any(path.exists() for path in (OUTPUT, TWIN, MANIFEST_OUTPUT)):
        raise RuntimeError("create-only output already exists")
    _write_create_only(OUTPUT, archive)
    _write_create_only(TWIN, twin)
    _write_create_only(MANIFEST_OUTPUT, manifest_bytes)
    print(
        json.dumps(
            {
                "status": "PASS__DETERMINISTIC_CREATE_ONLY_REVIEW_PACKET",
                "archive_sha256": _sha(archive),
                "archive_bytes": len(archive),
                "manifest_sha256": _sha(manifest_bytes),
                "manifest_bytes": len(manifest_bytes),
                "payload_count": len(payload_rows),
                "payload_bytes": manifest["payload_bytes"],
                "payload_set_sha256": payload_set_sha256,
                "twin_byte_identical": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

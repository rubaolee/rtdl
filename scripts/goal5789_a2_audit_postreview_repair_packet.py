"""Independently audit the Goal5789-A2 postreview repair packet.

This module deliberately imports neither the packet builder nor the source-
custody validator.  It reconstructs the exact 120+17 member contract, checks
claims and authorizations, and runs the unchanged materializer in a fresh
temporary repository.  Formal audit output is create-only; fixture mode is
available only through the Python API for prewrite tests.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "goal5789_a2_postreview_repair_packet_v1"
ARCHIVE = ROOT / "history/internal_docs/goal5789_a2_postreview_repair_packet_v1_20260822.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5789_a2_postreview_repair_packet_v1_twin_20260822.tar.gz"
MANIFEST = ROOT / "history/internal_docs/goal5789_a2_postreview_repair_packet_v1_manifest_20260822.json"
OUTPUT = ROOT / "history/internal_docs/goal5789_a2_postreview_repair_packet_v1_audit_20260822.json"

OLD_PACKET_REL = (
    "history/internal_docs/"
    "goal5789_a2_callback_ir_authority_binding_review_packet_v1_20260821.tar.gz"
)
OLD_PACKET_BYTES = 50_105_014
OLD_PACKET_SHA256 = "2c2711f1a75bc7571b222f8c7175767ade46ea23f15b9068a9aeef0dba317b25"
OLD_PACKET_MANIFEST_BYTES = 34_211
OLD_PACKET_MANIFEST_SHA256 = "62e4024ec444d26c46bc24abb1f08203735ae75cfeb78cdb388a5136ae7a690a"
OLD_PACKET_PAYLOAD_COUNT = 120
OLD_PACKET_PAYLOAD_BYTES = 52_007_905
OLD_PACKET_PAYLOAD_SET_SHA256 = (
    "a94730860617895531f89473cbb367588d2404848b750429f0621f0bb665c487"
)
DELIVERY_REL = "history/internal_docs/goal5789_a2_delivery_manifest_20260821.json"
DELIVERY_BYTES = 34_177
DELIVERY_SHA256 = "5df611467f5e52fceb27010e43b4d9a874479f6ddf93336a1b6005a1925e1664"
DELIVERY_INTERNAL_SHA256 = (
    "221575ab12889e1e2c9d716b45441e4152b07623dc94cd500454478bb4540c8f"
)

SOURCE_ARCHIVE_REL = (
    "history/internal_docs/"
    "goal5783_amendment_a1_external_rehash_supplement_20260814.tar.gz"
)
SOURCE_ARCHIVE_BYTES = 10_818_938
SOURCE_ARCHIVE_SHA256 = "b9eb03b7dd0404b1f5ca46f04122699ab24fe622a62c57b1aa786db82f57a529"
SOURCE_MANIFEST_MEMBER = "GOAL5783_AMENDMENT_A1_MANIFEST.json"
SOURCE_MANIFEST_BYTES = 2_274
SOURCE_MANIFEST_SHA256 = "98ac2cbceb09806643da8552207638ab041d4abc9c712010db1acf2226b64eda"
RTXRMQ_SOURCE_REL = "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py"
RTXRMQ_SOURCE_BYTES = 10_553
RTXRMQ_SOURCE_SHA256 = "0823fdf32e0ade592eebc577b1f43d5c81e4fb1134934f353bbd3e3586a3b0b1"

POSTREVIEW_RESULT_REL = (
    "history/internal_docs/goal5789_a2_postreview_repairs_result_20260821.json"
)
POSTREVIEW_REPORT_REL = (
    "history/internal_docs/"
    "goal5789_a2_owner_returned_external_review_absorption_and_repairs_20260821.md"
)
# Updated only after the owner freezes the final postreview result/report.
POSTREVIEW_RESULT_BYTES = 13_784
POSTREVIEW_RESULT_SHA256 = (
    "e487581106837bc5ccd03407308ef64ed6f21db5bc2a3a376bdac27fc2323b89"
)
POSTREVIEW_RESULT_INTERNAL_SHA256 = (
    "16c320c42bb8d2009572659910162e9dad0cd3a4efaf1c1db6970d91cd7e05cc"
)
POSTREVIEW_REPORT_BYTES = 10_723
POSTREVIEW_REPORT_SHA256 = (
    "0ed7b9c40a53024ebb6a44dc42b397163c685709e19d498ee7e2703a10823307"
)
MATERIALIZER_REL = "scripts/goal5789_a2_materialize_callback_ir_authority.py"
MATERIALIZER_BYTES = 40_040
MATERIALIZER_SHA256 = "facf9273ff5db129b25b5a728c051004fe6802d693e6fed3297aa1cf00a0caef"
AUTHORITY_REL = (
    "history/internal_docs/goal5789_a2_contract_evidence_20260821/"
    "CALLBACK_IR_AUTHORITY.json"
)
AUTHORITY_BYTES = 261_703
AUTHORITY_SHA256 = "16422fc282b834286f3f3c22db15f1663cc642e7d97bf940e7f594b550a5a59a"
AUTHORITY_INTERNAL_SHA256 = (
    "8383367ba43b92ec88b0f719a507ade4944e635e1a9b6d9243695b0623eaad70"
)
PIN_REL = (
    "history/internal_docs/goal5789_a2_contract_evidence_20260821/"
    "CALLBACK_IR_AUTHORITY_PIN.json"
)
PIN_BYTES = 1_787
PIN_SHA256 = "98e2aa6bb258030348dd623ed3609e168143003bae51048230a6dcd665dd1a0d"
PIN_INTERNAL_SHA256 = "2defc4649703f0f5bd26c5d6b122d01655886636e2f6880b34dd5e15b33f70e1"

FIXED_ADDITIONS: dict[str, tuple[int, str, str]] = {
    "history/internal_docs/review_goal5789_a2_callback_ir_authority_binding_and_goal5793_entry_20260821.md": (
        27_657,
        "88e0aff9fcc0579c4721a8a3422517beff9146acfcef7862f9dd7e880da1bd3a",
        "owner_returned_external_review",
    ),
    "history/internal_docs/goal5789_a2_postreview_absorption_work_authority_20260821.json": (
        4_249,
        "96be56ab7f450664fa2d2c27f3df3e9be667eacf9cc45ee0d45725924520e3a0",
        "postreview_work_authority",
    ),
    "scripts/goal5789_a2_adversarial_binding_audit_v2.py": (
        14_907,
        "9d4ea2a61df083a21b5e48c100052683b97eddc4e838f3d6056f396619ea5bad",
        "postreview_p2_1_exact_reason_repair",
    ),
    "tests/goal5789_a2_adversarial_binding_audit_v2_test.py": (
        8_569,
        "4fe0f13827533dda1dddb3d7687bae1856ccf15a08665b735fda8a2ab9bc6b97",
        "postreview_p2_1_exact_reason_repair",
    ),
    "history/internal_docs/goal5789_a2_callback_binding_adversarial_matrix_v2_20260821.json": (
        170_343,
        "3ab1d9380f1988f90eac9615ffb6344ac21b9e1737ec4b28715a06a461334d67",
        "postreview_p2_1_exact_reason_repair",
    ),
    "scripts/goal5789_a2_validate_source_custody_replay.py": (
        35_477,
        "1a70525cebbd96e7fbc560d77e5180b044a03577e6834e84532de7fc50e9a357",
        "postreview_p2_2_source_custody_repair",
    ),
    "tests/goal5789_a2_source_custody_replay_test.py": (
        6_010,
        "4c1bdb627bd8048a00fc512f7a22826d001aafff5e5720f92c50003bf9f87316",
        "postreview_p2_2_source_custody_repair",
    ),
    "history/internal_docs/goal5789_a2_postreview_source_custody_supplement_20260821.json": (
        5_529,
        "5dc1bc9117e12f0c8e022d1da9f5162f7c539c277285a7cf3fa81c756def2d5c",
        "postreview_p2_2_source_custody_repair",
    ),
    "scripts/goal5789_a2_build_packet_audit_supplement.py": (
        14_292,
        "bb2b22b181e675bf73802f759c8d9dc750c660d71b7c822860b46e96f5d2e4b3",
        "postreview_p3_1_packet_audit_reporting_repair",
    ),
    "tests/goal5789_a2_packet_audit_supplement_test.py": (
        3_071,
        "4fcb4c61919c611d529190483d50a22ce76d191a594502098f469492ac3ba1dc",
        "postreview_p3_1_packet_audit_reporting_repair",
    ),
    "history/internal_docs/goal5789_a2_postreview_packet_audit_supplement_20260821.json": (
        3_216,
        "279330079636670552b3a7b1ec9001918ef8bfd305c0d79b4246e316120627e6",
        "postreview_p3_1_packet_audit_reporting_repair",
    ),
}
DYNAMIC_TOOL_ADDITIONS = {
    "scripts/goal5789_a2_build_postreview_repair_packet.py": "postreview_successor_packet_tool",
    "scripts/goal5789_a2_audit_postreview_repair_packet.py": "postreview_successor_packet_tool",
    "tests/goal5789_a2_postreview_repair_packet_test.py": "postreview_successor_packet_tool",
}

HISTORICAL_BOUNDARY = {
    "predecessor_packet_payload_count": 120,
    "predecessor_packet_carried_goal5783_source_archive": True,
    "predecessor_packet_contained_rtxrmq_direct_repository_payload": False,
    "predecessor_packet_alone_materializer_replayable": False,
    "successor_adds_exact_source_from_predecessor_carried_immutable_archive": True,
    "predecessor_packet_relabelled_as_historically_self_contained": False,
}
CLAIM_BOUNDARY = {
    "append_only_postreview_repairs_only": True,
    "predecessor_payloads_byte_unchanged": True,
    "predecessor_payload_count": 120,
    "added_payload_count": 17,
    "successor_payload_count": 137,
    "successor_packet_self_contained_for_exact_materializer_replay": True,
    "materialization_independent_of_submitted_certificate": True,
    "materialization_independent_of_product_ir_implementation": False,
    "authority_producer_and_product_ir_implementation_are_tcb": True,
    "scientific_result_changed": False,
    "hostile_matrix_total_case_count": 159,
    "hostile_matrix_negative_mutation_count": 143,
    "hostile_matrix_baseline_case_count": 15,
    "hostile_matrix_tcb_passing_control_count": 1,
    "hostile_matrix_all_cases_are_negative_or_rejections_claimed": False,
    "goal5793_generalization_evidence_count": 0,
    "semantic_soundness_claimed": False,
    "completeness_claimed": False,
    "generalization_claimed": False,
    "usability_claimed": False,
    "production_claimed": False,
    "hermetic_python_environment_claimed": False,
}
AUTHORIZATION = {
    "authorizes_external_reviewer_contact": False,
    "authorizes_goal5793_s0_authoring": False,
    "authorizes_entropy_or_candidate_selection": False,
    "authorizes_implementation_or_execution": False,
    "authorizes_gpu_home_pod_or_ssh": False,
    "authorizes_worker_or_timing": False,
    "authorizes_product_change": False,
    "authorizes_publication_or_submission": False,
}
FIXTURE_RESULT_SCHEMA = "rtdl.goal5789_a2.postreview_repairs_result.test_fixture.v1"
FIXTURE_RESULT_STATUS = "TEST_FIXTURE_ONLY__NOT_A_FORMAL_RESULT"
FIXTURE_REPAIR_STATUS = {
    "p2_1_exact_reason_matrix_closed": True,
    "p2_2_source_custody_and_materializer_replay_closed": True,
    "p2_3_independence_scope_corrected": True,
    "p3_1_packet_audit_reporting_closed": True,
}
CANONICAL_GZIP_HEADER = bytes.fromhex("1f8b08000000000002ff")
OFFICIAL_RESULT_CLAIM_BOUNDARY = {
    "accepted_scope": "BOUNDED_LOCAL_CALLBACK_IR_AUTHORITY_BINDING",
    "frozen_callback_program_count": 5,
    "executed_leaf_count": 26,
    "semantic_physical_pair_to_program_binding_count": 4,
    "inventory_count": 15,
    "callback_bound_count": 6,
    "compatible_count": 6,
    "callback_unbound_unknown_count": 9,
    "callback_bound_rows_equal_compatible_rows": True,
    "executed_program_identity_and_exact_projection_claimed_for_six_rows": True,
    "semantic_correctness_established_by_callback_binding": False,
    "particle_and_rtxrmq_share_byte_identical_callback_program": True,
    "callback_layer_discriminates_particle_from_rtxrmq": False,
    "authority_producers_external_roots_and_product_ir_implementation_are_tcb": True,
    "jointly_wrong_mutually_consistent_authorities_detected": False,
    "soundness_completeness_false_rejection_rate_generalization_third_family_all_path_gate_or_usability_claimed": False,
    "new_goal5793_exam_count": 0,
    "new_gpu_execution_or_performance_evidence_count": 0,
    "publication_or_submission_ready_claimed": False,
}
OFFICIAL_RESULT_AUTHORIZATION = {
    "authorizes_append_only_closure": False,
    "authorizes_cfr_or_external_reviewer_contact": False,
    "authorizes_goal5793": False,
    "authorizes_goal5793_s0_preregistration_authoring": False,
    "authorizes_entropy_draw": False,
    "authorizes_candidate_selection": False,
    "authorizes_candidate_implementation_or_execution": False,
    "authorizes_product_checker_native_application_registry_rule_or_toolchain_change": False,
    "authorizes_gpu_home_pod_or_ssh": False,
    "authorizes_formal_or_replacement_worker": False,
    "authorizes_registered_or_performance_timing": False,
    "authorizes_successor_packet_creation": False,
    "authorizes_public_release": False,
    "authorizes_publication": False,
    "authorizes_submission": False,
}
OFFICIAL_RESULT_NEXT_GATE = {
    "external_review_p0_p1_gate_satisfied": True,
    "append_only_owner_absorption_completed": True,
    "append_only_owner_closure_completed": False,
    "goal5793_s0_preregistration_authoring_currently_authorized": False,
    "required_next_artifact": "SEPARATE_APPEND_ONLY_OWNER_CLOSURE",
    "closure_may_authorize_goal5793_s0_preregistration_authoring_only": True,
    "entropy_draw_candidate_selection_implementation_or_execution_remain_forbidden": True,
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _pretty(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _safe(relative: str) -> str:
    if type(relative) is not str or not relative or "\\" in relative:
        raise RuntimeError(f"unsafe packet path: {relative!r}")
    try:
        relative.encode("ascii")
    except UnicodeEncodeError as exc:
        raise RuntimeError(f"non-ASCII packet path: {relative!r}") from exc
    path = PurePosixPath(relative)
    if (
        path.is_absolute()
        or path.as_posix() != relative
        or any(
            part in {"", ".", ".."}
            or ":" in part
            or part != part.strip()
            or part.endswith(".")
            for part in path.parts
        )
    ):
        raise RuntimeError(f"noncanonical packet path: {relative!r}")
    return relative


def _alias_key(relative: str) -> str:
    return "/".join(part.casefold() for part in PurePosixPath(_safe(relative)).parts)


def _object(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid JSON: {label}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {label}")
    return value


def _self_seal(value: Mapping[str, Any], field: str, expected: str, label: str) -> None:
    if value.get(field) != expected:
        raise RuntimeError(f"{label} stored seal mismatch")
    if _sha(_canonical({key: item for key, item in value.items() if key != field})) != expected:
        raise RuntimeError(f"{label} canonical seal mismatch")


def _read_archive(archive_bytes: bytes) -> dict[str, bytes]:
    if len(archive_bytes) < 18 or archive_bytes[:10] != CANONICAL_GZIP_HEADER:
        raise RuntimeError("successor gzip header or flags are noncanonical")
    observed: dict[str, bytes] = {}
    aliases: set[str] = set()
    relative_order: list[str] = []
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(archive_bytes), mode="rb") as zipped:
            raw = zipped.read()
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
            if archive.pax_headers:
                raise RuntimeError("successor archive has forbidden global PAX metadata")
            for member in archive.getmembers():
                if not member.isreg() or member.issym() or member.islnk():
                    raise RuntimeError(f"non-regular successor member: {member.name!r}")
                if (
                    member.mode != 0o444
                    or member.uid != 0
                    or member.gid != 0
                    or member.mtime != 0
                    or member.uname != ""
                    or member.gname != ""
                ):
                    raise RuntimeError("successor member metadata is noncanonical")
                if member.pax_headers:
                    raise RuntimeError("successor member has forbidden PAX metadata")
                marker = PREFIX + "/"
                if not member.name.startswith(marker):
                    raise RuntimeError(f"successor member prefix mismatch: {member.name!r}")
                relative = member.name[len(marker) :]
                alias = _alias_key(relative)
                if relative in observed or alias in aliases:
                    raise RuntimeError(f"duplicate or aliased successor member: {relative}")
                aliases.add(alias)
                relative_order.append(relative)
                handle = archive.extractfile(member)
                if handle is None:
                    raise RuntimeError(f"unreadable successor member: {relative}")
                data = handle.read()
                if len(data) != member.size:
                    raise RuntimeError(f"successor member size mismatch: {relative}")
                observed[relative] = data
    except (gzip.BadGzipFile, tarfile.TarError, EOFError) as exc:
        raise RuntimeError("invalid successor archive") from exc
    if relative_order != sorted(relative_order):
        raise RuntimeError("successor member relative-path order is noncanonical")
    return observed


def _validate_rows(manifest: Mapping[str, object]) -> tuple[dict[str, Mapping[str, object]], int, str]:
    rows = manifest.get("payloads")
    if not isinstance(rows, list) or len(rows) != 137:
        raise RuntimeError("successor manifest must contain exactly 137 payload rows")
    expected: dict[str, Mapping[str, object]] = {}
    aliases: set[str] = set()
    digest_rows: list[dict[str, object]] = []
    total = 0
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {
            "path",
            "bytes",
            "sha256",
            "provenance",
        }:
            raise RuntimeError("successor manifest row schema mismatch")
        relative, size, identity = row["path"], row["bytes"], row["sha256"]
        if (
            type(relative) is not str
            or relative in expected
            or type(size) is not int
            or size < 0
            or type(identity) is not str
            or len(identity) != 64
            or any(char not in "0123456789abcdef" for char in identity)
            or type(row["provenance"]) is not str
            or not row["provenance"]
        ):
            raise RuntimeError("successor manifest row type mismatch")
        alias = _alias_key(relative)
        if alias in aliases:
            raise RuntimeError("successor manifest path alias collision")
        aliases.add(alias)
        expected[relative] = row
        total += size
        digest_rows.append({"path": relative, "bytes": size, "sha256": identity})
    if [row["path"] for row in rows] != sorted(expected):
        raise RuntimeError("successor manifest rows are not canonically ordered")
    return expected, total, _sha(_canonical(digest_rows))


def _validate_delivery_and_predecessor(
    payloads: Mapping[str, bytes], rows: Mapping[str, Mapping[str, object]]
) -> set[str]:
    delivery_bytes = payloads.get(DELIVERY_REL)
    if (
        delivery_bytes is None
        or len(delivery_bytes) != DELIVERY_BYTES
        or _sha(delivery_bytes) != DELIVERY_SHA256
    ):
        raise RuntimeError("predecessor delivery-manifest identity mismatch")
    delivery = _object(delivery_bytes, "predecessor delivery manifest")
    _self_seal(
        delivery,
        "delivery_manifest_sha256",
        DELIVERY_INTERNAL_SHA256,
        "predecessor delivery manifest",
    )
    delivery_rows = delivery.get("payloads")
    if (
        delivery.get("schema") != "rtdl.goal5789_a2.delivery_manifest.v1"
        or delivery.get("payload_count") != 119
        or not isinstance(delivery_rows, list)
        or len(delivery_rows) != 119
    ):
        raise RuntimeError("predecessor delivery-manifest controls mismatch")
    predecessor_paths = {DELIVERY_REL}
    digest_rows: list[dict[str, object]] = []
    total = 0
    for item in delivery_rows:
        if not isinstance(item, Mapping) or set(item) != {
            "path",
            "bytes",
            "sha256",
            "provenance",
        }:
            raise RuntimeError("predecessor delivery row schema mismatch")
        relative = item["path"]
        if type(relative) is not str or relative in predecessor_paths:
            raise RuntimeError("predecessor delivery duplicate path")
        _safe(relative)
        predecessor_paths.add(relative)
        data = payloads.get(relative)
        successor_row = rows.get(relative)
        if (
            data is None
            or successor_row is None
            or len(data) != item["bytes"]
            or _sha(data) != item["sha256"]
            or successor_row["bytes"] != item["bytes"]
            or successor_row["sha256"] != item["sha256"]
            or successor_row["provenance"] != item["provenance"]
        ):
            raise RuntimeError(f"predecessor payload was not preserved: {relative}")
    delivery_row = rows.get(DELIVERY_REL)
    if (
        delivery_row is None
        or delivery_row["bytes"] != DELIVERY_BYTES
        or delivery_row["sha256"] != DELIVERY_SHA256
        or delivery_row["provenance"] != "goal5789_a2_delivery_manifest_root"
    ):
        raise RuntimeError("predecessor delivery-root row was not preserved")
    for relative in sorted(predecessor_paths):
        row = rows[relative]
        total += row["bytes"]
        digest_rows.append(
            {"path": relative, "bytes": row["bytes"], "sha256": row["sha256"]}
        )
    if (
        len(predecessor_paths) != OLD_PACKET_PAYLOAD_COUNT
        or total != OLD_PACKET_PAYLOAD_BYTES
        or _sha(_canonical(digest_rows)) != OLD_PACKET_PAYLOAD_SET_SHA256
    ):
        raise RuntimeError("predecessor 120-payload set identity mismatch")
    if RTXRMQ_SOURCE_REL in predecessor_paths:
        raise RuntimeError("historical predecessor unexpectedly contained direct RTXRMQ source")
    return predecessor_paths


def _extract_goal5783_source(archive_bytes: bytes) -> bytes:
    if len(archive_bytes) != SOURCE_ARCHIVE_BYTES or _sha(archive_bytes) != SOURCE_ARCHIVE_SHA256:
        raise RuntimeError("Goal5783-A1 source archive identity mismatch")
    observed: dict[str, bytes] = {}
    aliases: set[str] = set()
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        for member in archive.getmembers():
            if (
                not member.isreg()
                or member.issym()
                or member.islnk()
                or member.mode != 0o644
                or member.uid != 0
                or member.gid != 0
                or member.mtime != 0
            ):
                raise RuntimeError("Goal5783-A1 archive member contract mismatch")
            alias = _alias_key(member.name)
            if member.name in observed or alias in aliases:
                raise RuntimeError("Goal5783-A1 duplicate or aliased member")
            aliases.add(alias)
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError("Goal5783-A1 member unreadable")
            observed[member.name] = handle.read()
    manifest_bytes = observed.pop(SOURCE_MANIFEST_MEMBER, None)
    if (
        manifest_bytes is None
        or len(manifest_bytes) != SOURCE_MANIFEST_BYTES
        or _sha(manifest_bytes) != SOURCE_MANIFEST_SHA256
    ):
        raise RuntimeError("Goal5783-A1 source manifest identity mismatch")
    manifest = _object(manifest_bytes, "Goal5783-A1 source manifest")
    rows = manifest.get("payloads")
    if (
        manifest.get("schema")
        != "rtdl.goal5783.amendment_a1_external_rehash_manifest.v1"
        or manifest.get("payload_count") != 10
        or manifest.get("payload_bytes") != 10_857_936
        or not isinstance(rows, list)
        or len(rows) != 10
    ):
        raise RuntimeError("Goal5783-A1 source manifest controls mismatch")
    expected: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {"path", "size", "sha256"}:
            raise RuntimeError("Goal5783-A1 source row schema mismatch")
        relative = row["path"]
        if type(relative) is not str or relative in expected:
            raise RuntimeError("Goal5783-A1 duplicate source row")
        expected.add(relative)
        data = observed.get(relative)
        if data is None or len(data) != row["size"] or _sha(data) != row["sha256"]:
            raise RuntimeError(f"Goal5783-A1 source payload mismatch: {relative}")
    if set(observed) != expected:
        raise RuntimeError("Goal5783-A1 source payload set mismatch")
    source = observed.get(RTXRMQ_SOURCE_REL)
    if (
        source is None
        or len(source) != RTXRMQ_SOURCE_BYTES
        or _sha(source) != RTXRMQ_SOURCE_SHA256
    ):
        raise RuntimeError("Goal5783-A1 RTXRMQ source mismatch")
    return source


def _fixture_result(report_bytes: bytes) -> dict[str, object]:
    result: dict[str, object] = {
        "schema": FIXTURE_RESULT_SCHEMA,
        "result_sha256": "",
        "goal": "5789-A2-postreview-test-fixture",
        "date": "2026-08-22",
        "status": FIXTURE_RESULT_STATUS,
        "repair_status": dict(FIXTURE_REPAIR_STATUS),
        "postreview_report": {
            "path": POSTREVIEW_REPORT_REL,
            "bytes": len(report_bytes),
            "file_sha256": _sha(report_bytes),
        },
        "historical_boundary": dict(HISTORICAL_BOUNDARY),
        "claim_boundary": dict(CLAIM_BOUNDARY),
        "authorization": dict(AUTHORIZATION),
    }
    result["result_sha256"] = _sha(
        _canonical({key: value for key, value in result.items() if key != "result_sha256"})
    )
    return result


def _validate_result(result_bytes: bytes, report_bytes: bytes, *, fixture_mode: bool) -> dict[str, object]:
    result = _object(result_bytes, "postreview result")
    body = {key: value for key, value in result.items() if key != "result_sha256"}
    if result.get("result_sha256") != _sha(_canonical(body)):
        raise RuntimeError("postreview result internal seal mismatch")
    if fixture_mode:
        if result != _fixture_result(report_bytes):
            raise RuntimeError("temporary postreview result fixture mismatch")
        return result
    if (
        len(result_bytes) != POSTREVIEW_RESULT_BYTES
        or _sha(result_bytes) != POSTREVIEW_RESULT_SHA256
        or len(report_bytes) != POSTREVIEW_REPORT_BYTES
        or _sha(report_bytes) != POSTREVIEW_REPORT_SHA256
        or result.get("result_sha256") != POSTREVIEW_RESULT_INTERNAL_SHA256
        or set(result)
        != {
            "schema",
            "goal",
            "date",
            "status",
            "controlling_returned_review",
            "work_authority",
            "immutable_reviewed_roots",
            "finding_absorption",
            "focused_test_recount",
            "review_text_normalization",
            "claim_boundary",
            "next_gate",
            "authorization",
            "result_sha256",
        }
        or result.get("schema") != "rtdl.goal5789_a2.postreview_repairs_result.v1"
        or result.get("goal") != "5789-A2-postreview"
        or result.get("date") != "2026-08-21"
        or result.get("status")
        != "PASS__RETURNED_REVIEW_P2_COUNT_3_AND_P3_COUNT_1_CLOSED_APPEND_ONLY_AT_LOCAL_POSTREVIEW_REPAIR_SCOPE__REVIEWED_SCIENCE_UNCHANGED__GOAL5793_REMAINS_BLOCKED_PENDING_CLOSURE"
        or result.get("claim_boundary") != OFFICIAL_RESULT_CLAIM_BOUNDARY
        or result.get("authorization") != OFFICIAL_RESULT_AUTHORIZATION
        or result.get("next_gate") != OFFICIAL_RESULT_NEXT_GATE
        or set(result.get("finding_absorption", {}))
        != {
            "p2_1_reason_oracle_specificity",
            "p2_2_rtxrmq_consumer_source_custody_and_replay",
            "p2_3_independence_and_product_ir_tcb",
            "p3_1_packet_audit_checks_reporting",
        }
    ):
        raise RuntimeError("official postreview result/report exact contract mismatch")
    return result


def _validate_fixed_additions(
    payloads: Mapping[str, bytes], rows: Mapping[str, Mapping[str, object]]
) -> None:
    for relative, (size, identity, provenance) in FIXED_ADDITIONS.items():
        data, row = payloads.get(relative), rows.get(relative)
        if (
            data is None
            or row is None
            or len(data) != size
            or _sha(data) != identity
            or row["bytes"] != size
            or row["sha256"] != identity
            or row["provenance"] != provenance
        ):
            raise RuntimeError(f"fixed postreview addition mismatch: {relative}")
    matrix = _object(
        payloads[
            "history/internal_docs/goal5789_a2_callback_binding_adversarial_matrix_v2_20260821.json"
        ],
        "matrix v2",
    )
    _self_seal(
        matrix,
        "matrix_sha256",
        "b82d13d2e051ede3d3940fbc54f22c8bba6a8daf1cfac39742f3c6ebc4735190",
        "matrix v2",
    )
    if (
        matrix.get("schema") != "rtdl.goal5789_a2.callback_binding_adversarial_matrix.v2"
        or matrix.get("case_count") != 159
        or matrix.get("case_accounting", {}).get("certificate_only_exact_reason_set_count")
        != 126
        or matrix.get("case_accounting", {}).get(
            "certificate_only_generic_substring_oracle_count_in_v2"
        )
        != 0
        or any(item is not False for item in matrix.get("authorization", {}).values())
    ):
        raise RuntimeError("matrix-v2 claim or authorization mismatch")
    custody = _object(
        payloads[
            "history/internal_docs/goal5789_a2_postreview_source_custody_supplement_20260821.json"
        ],
        "source-custody supplement",
    )
    _self_seal(
        custody,
        "supplement_sha256",
        "6ee36af1c85ecb5c5fa79656a1074a4a92da8da24618f5dfb595bd3702b641cf",
        "source-custody supplement",
    )
    if (
        custody.get("schema")
        != "rtdl.goal5789_a2.postreview_source_custody_supplement.v1"
        or custody.get("claim_boundary", {}).get("independent_product_ir_verifier_claimed")
        is not False
        or any(item is not False for item in custody.get("authorization", {}).values())
    ):
        raise RuntimeError("source-custody claim or authorization mismatch")
    supplement = _object(
        payloads[
            "history/internal_docs/goal5789_a2_postreview_packet_audit_supplement_20260821.json"
        ],
        "packet-audit supplement",
    )
    _self_seal(
        supplement,
        "supplement_sha256",
        "ee6915edaf68146cadd9392cc9b1512f5e6fc6ffa585c0635baeadc148eff482",
        "packet-audit supplement",
    )
    if (
        supplement.get("schema")
        != "rtdl.goal5789_a2.postreview_packet_audit_supplement.v1"
        or supplement.get("payload_identity_checked_count") != 120
        or supplement.get("payload_identity_mismatch_count") != 0
        or supplement.get("checks", {}).get("payload_identity") is not True
        or supplement.get("checks", {}).get("payload_set_digest") is not True
        or any(item is not False for item in supplement.get("authorization", {}).values())
    ):
        raise RuntimeError("packet-audit supplement claim or authorization mismatch")


def _write_fresh_tree(root: Path, payloads: Mapping[str, bytes]) -> None:
    root = root.resolve()
    for relative, data in sorted(payloads.items()):
        _safe(relative)
        target = root.joinpath(*PurePosixPath(relative).parts)
        parent = target.parent.resolve()
        if parent != root and root not in parent.parents:
            raise RuntimeError(f"payload escaped fresh root: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(data)


def _replay_materializer(payloads: Mapping[str, bytes]) -> Mapping[str, object]:
    stored_authority = payloads.get(AUTHORITY_REL)
    stored_pin = payloads.get(PIN_REL)
    materializer = payloads.get(MATERIALIZER_REL)
    if (
        stored_authority is None
        or len(stored_authority) != AUTHORITY_BYTES
        or _sha(stored_authority) != AUTHORITY_SHA256
        or stored_pin is None
        or len(stored_pin) != PIN_BYTES
        or _sha(stored_pin) != PIN_SHA256
        or materializer is None
        or len(materializer) != MATERIALIZER_BYTES
        or _sha(materializer) != MATERIALIZER_SHA256
    ):
        raise RuntimeError("materializer replay fixed-input identity mismatch")
    authority = _object(stored_authority, "stored Callback-IR authority")
    pin = _object(stored_pin, "stored Callback-IR authority pin")
    _self_seal(authority, "authority_sha256", AUTHORITY_INTERNAL_SHA256, "authority")
    _self_seal(pin, "pin_sha256", PIN_INTERNAL_SHA256, "authority pin")
    with tempfile.TemporaryDirectory(prefix="goal5789_a2_successor_replay_") as temporary:
        fresh = Path(temporary).resolve()
        _write_fresh_tree(fresh, payloads)
        authority_path = fresh.joinpath(*PurePosixPath(AUTHORITY_REL).parts)
        pin_path = fresh.joinpath(*PurePosixPath(PIN_REL).parts)
        authority_path.unlink()
        pin_path.unlink()
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        environment.pop("PYTHONHOME", None)
        environment.pop("PYTHONNOUSERSITE", None)
        completed = subprocess.run(
            [sys.executable, str(fresh.joinpath(*PurePosixPath(MATERIALIZER_REL).parts))],
            cwd=fresh,
            env=environment,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "successor-carried materializer replay failed: "
                f"returncode={completed.returncode}; stdout={completed.stdout!r}; "
                f"stderr={completed.stderr!r}"
            )
        regenerated_authority = authority_path.read_bytes()
        regenerated_pin = pin_path.read_bytes()
    if regenerated_authority != stored_authority or regenerated_pin != stored_pin:
        raise RuntimeError("successor materializer authority or pin is not byte-identical")
    try:
        receipt = json.loads(completed.stdout.strip())
    except json.JSONDecodeError as exc:
        raise RuntimeError("materializer replay receipt is invalid JSON") from exc
    if (
        not isinstance(receipt, Mapping)
        or set(receipt)
        != {
            "authority_file_sha256",
            "authority_sha256",
            "pin_file_sha256",
            "pin_sha256",
            "program_count",
        }
        or receipt.get("authority_file_sha256") != AUTHORITY_SHA256
        or receipt.get("authority_sha256") != AUTHORITY_INTERNAL_SHA256
        or receipt.get("pin_file_sha256") != PIN_SHA256
        or receipt.get("pin_sha256") != PIN_INTERNAL_SHA256
        or receipt.get("program_count") != 5
    ):
        raise RuntimeError("materializer replay receipt contract mismatch")
    return receipt


def audit(
    archive_bytes: bytes,
    twin_bytes: bytes,
    manifest_bytes: bytes,
    *,
    fixture_mode: bool = False,
) -> dict[str, object]:
    if archive_bytes != twin_bytes:
        raise RuntimeError("successor packet twin differs")
    manifest = _object(manifest_bytes, "successor external manifest")
    if set(manifest) != {
        "schema",
        "goal",
        "date",
        "status",
        "predecessor_packet",
        "postreview_result",
        "postreview_report",
        "payload_count",
        "payload_bytes",
        "payload_set_sha256",
        "payloads",
        "historical_boundary",
        "claim_boundary",
        "authorization",
    }:
        raise RuntimeError("successor manifest top-level schema mismatch")
    expected_status = (
        "TEST_FIXTURE__NOT_FORMAL_OUTPUT"
        if fixture_mode
        else "FROZEN_APPEND_ONLY_POSTREVIEW_REPAIR_PACKET__GOAL5793_REMAINS_BLOCKED"
    )
    predecessor_control = {
        "path": OLD_PACKET_REL,
        "bytes": OLD_PACKET_BYTES,
        "file_sha256": OLD_PACKET_SHA256,
        "manifest_bytes": OLD_PACKET_MANIFEST_BYTES,
        "manifest_file_sha256": OLD_PACKET_MANIFEST_SHA256,
        "payload_count": OLD_PACKET_PAYLOAD_COUNT,
        "payload_bytes": OLD_PACKET_PAYLOAD_BYTES,
        "payload_set_sha256": OLD_PACKET_PAYLOAD_SET_SHA256,
    }
    if (
        manifest.get("schema") != "rtdl.goal5789_a2.postreview_repair_packet.v1"
        or manifest.get("goal") != "5789-A2-postreview"
        or manifest.get("date") != "2026-08-22"
        or manifest.get("status") != expected_status
        or manifest.get("predecessor_packet") != predecessor_control
        or manifest.get("payload_count") != 137
        or manifest.get("historical_boundary") != HISTORICAL_BOUNDARY
        or manifest.get("claim_boundary") != CLAIM_BOUNDARY
        or manifest.get("authorization") != AUTHORIZATION
    ):
        raise RuntimeError("successor manifest controls, claims, or authorization mismatch")
    expected, total, set_digest = _validate_rows(manifest)
    if total != manifest.get("payload_bytes") or set_digest != manifest.get("payload_set_sha256"):
        raise RuntimeError("successor manifest payload-set digest mismatch")
    members = _read_archive(archive_bytes)
    embedded = members.pop("PACKET_MANIFEST.json", None)
    if embedded != manifest_bytes or set(members) != set(expected):
        raise RuntimeError("successor embedded manifest or exact member set mismatch")
    for relative, row in expected.items():
        data = members[relative]
        if len(data) != row["bytes"] or _sha(data) != row["sha256"]:
            raise RuntimeError(f"successor payload identity mismatch: {relative}")

    predecessor_paths = _validate_delivery_and_predecessor(members, expected)
    added_paths = set(members) - predecessor_paths
    required_added = (
        set(FIXED_ADDITIONS)
        | set(DYNAMIC_TOOL_ADDITIONS)
        | {RTXRMQ_SOURCE_REL, POSTREVIEW_RESULT_REL, POSTREVIEW_REPORT_REL}
    )
    if added_paths != required_added or len(added_paths) != 17:
        raise RuntimeError("successor exact seventeen-added-payload set mismatch")
    source = _extract_goal5783_source(members[SOURCE_ARCHIVE_REL])
    source_row = expected[RTXRMQ_SOURCE_REL]
    if (
        members[RTXRMQ_SOURCE_REL] != source
        or source_row["bytes"] != RTXRMQ_SOURCE_BYTES
        or source_row["sha256"] != RTXRMQ_SOURCE_SHA256
        or source_row["provenance"]
        != "goal5783_a1_immutable_source_archive_member"
    ):
        raise RuntimeError("direct RTXRMQ source is not exact immutable extraction")
    _validate_fixed_additions(members, expected)
    for relative, provenance in DYNAMIC_TOOL_ADDITIONS.items():
        data, row = members.get(relative), expected.get(relative)
        if (
            data is None
            or not data
            or row is None
            or row["bytes"] != len(data)
            or row["sha256"] != _sha(data)
            or row["provenance"] != provenance
        ):
            raise RuntimeError(f"successor packet tool mismatch: {relative}")

    result_bytes = members[POSTREVIEW_RESULT_REL]
    report_bytes = members[POSTREVIEW_REPORT_REL]
    if not report_bytes:
        raise RuntimeError("postreview report is empty")
    result = _validate_result(result_bytes, report_bytes, fixture_mode=fixture_mode)
    result_control = manifest.get("postreview_result")
    report_control = manifest.get("postreview_report")
    if (
        not isinstance(result_control, Mapping)
        or set(result_control) != {"path", "bytes", "file_sha256", "result_sha256"}
        or result_control.get("path") != POSTREVIEW_RESULT_REL
        or result_control.get("bytes") != len(result_bytes)
        or result_control.get("file_sha256") != _sha(result_bytes)
        or result_control.get("result_sha256") != result["result_sha256"]
        or not isinstance(report_control, Mapping)
        or set(report_control) != {"path", "bytes", "file_sha256"}
        or report_control.get("path") != POSTREVIEW_REPORT_REL
        or report_control.get("bytes") != len(report_bytes)
        or report_control.get("file_sha256") != _sha(report_bytes)
    ):
        raise RuntimeError("postreview result/report manifest crossbind mismatch")

    receipt = _replay_materializer(members)
    output: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.postreview_repair_packet_audit.v1",
        "audit_sha256": "",
        "status": (
            "PASS__TEST_FIXTURE__137_EXACT_PAYLOADS__MATERIALIZER_REPLAY_BYTE_IDENTICAL"
            if fixture_mode
            else "PASS__137_EXACT_PAYLOADS__MATERIALIZER_REPLAY_BYTE_IDENTICAL"
        ),
        "archive": {
            "bytes": len(archive_bytes),
            "file_sha256": _sha(archive_bytes),
        },
        "twin": {
            "bytes": len(twin_bytes),
            "file_sha256": _sha(twin_bytes),
            "byte_identical": True,
        },
        "manifest": {
            "bytes": len(manifest_bytes),
            "file_sha256": _sha(manifest_bytes),
            "payload_count": 137,
            "payload_bytes": total,
            "payload_set_sha256": set_digest,
        },
        "checks": {
            "exact_member_set": True,
            "payload_identity": True,
            "payload_set_digest": True,
            "canonical_paths": True,
            "casefold_alias_free": True,
            "canonical_metadata": True,
            "regular_file_only": True,
            "predecessor_120_payloads_byte_unchanged": True,
            "added_17_payloads_exact": True,
            "direct_rtxrmq_source_matches_nested_immutable_archive": True,
            "fresh_temporary_repository": True,
            "fresh_interpreter": True,
            "callback_authority_byte_identical": True,
            "callback_authority_pin_byte_identical": True,
        },
        "materializer_replay": {
            "materializer_file_sha256": MATERIALIZER_SHA256,
            "callback_authority_file_sha256": AUTHORITY_SHA256,
            "callback_authority_pin_file_sha256": PIN_SHA256,
            "hermetic_python_environment_claimed": False,
            "user_site_third_party_dependencies_permitted": True,
            "receipt": dict(receipt),
        },
        "historical_boundary": dict(HISTORICAL_BOUNDARY),
        "claim_boundary": dict(CLAIM_BOUNDARY),
        "authorization": dict(AUTHORIZATION),
    }
    output["audit_sha256"] = _sha(
        _canonical({key: value for key, value in output.items() if key != "audit_sha256"})
    )
    return output


def verify_stored_audit(
    stored_audit_bytes: bytes,
    archive_bytes: bytes,
    twin_bytes: bytes,
    manifest_bytes: bytes,
    *,
    fixture_mode: bool = False,
) -> dict[str, object]:
    observed = _object(stored_audit_bytes, "stored successor audit")
    if (
        observed.get("archive", {}).get("bytes") != len(archive_bytes)
        or observed.get("archive", {}).get("file_sha256") != _sha(archive_bytes)
        or observed.get("twin", {}).get("bytes") != len(twin_bytes)
        or observed.get("twin", {}).get("file_sha256") != _sha(twin_bytes)
        or observed.get("manifest", {}).get("bytes") != len(manifest_bytes)
        or observed.get("manifest", {}).get("file_sha256") != _sha(manifest_bytes)
    ):
        raise RuntimeError("stored successor audit is stale for supplied packet bytes")
    recomputed = audit(
        archive_bytes, twin_bytes, manifest_bytes, fixture_mode=fixture_mode
    )
    if stored_audit_bytes != _pretty(recomputed) or observed != recomputed:
        raise RuntimeError("stored successor audit is stale or not exact")
    return recomputed


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError("Goal5789-A2 postreview packet audit is create-only")
    result = audit(
        ARCHIVE.read_bytes(),
        TWIN.read_bytes(),
        MANIFEST.read_bytes(),
        fixture_mode=False,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("xb") as handle:
        handle.write(_pretty(result))
    print(
        json.dumps(
            {
                "file_sha256": _sha(OUTPUT.read_bytes()),
                "audit_sha256": result["audit_sha256"],
                "status": result["status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

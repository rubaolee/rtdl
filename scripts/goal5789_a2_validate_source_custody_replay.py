"""Create and validate the Goal5789-A2 P2-2 source-custody supplement.

The externally reviewed A2 packet is immutable. This append-only validator
uses two independent frozen byte roots: the exact reviewed A2 packet and the
exact Goal5783-A1 external-rehash archive. It recovers the missing RTXRMQ
consumer witness from the latter, reconstructs a fresh repository from the
former, runs the unchanged A2 materializer in a fresh interpreter, and
requires both produced files to be byte-identical to the reviewed A2 files.

The live workspace RTXRMQ source is never read. This script can also emit the
small, self-sealed custody JSON used by the successor packet; it does not build
or modify any packet.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
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
from typing import Mapping


ROOT = Path(__file__).resolve().parents[1]

PACKET_REL = (
    "history/internal_docs/"
    "goal5789_a2_callback_ir_authority_binding_review_packet_v1_20260821.tar.gz"
)
PACKET_SHA256 = "2c2711f1a75bc7571b222f8c7175767ade46ea23f15b9068a9aeef0dba317b25"
PACKET_BYTES = 50_105_014
PACKET_PREFIX = "goal5789_a2_callback_ir_authority_binding_review_packet_v1"
PACKET_MANIFEST_SHA256 = "62e4024ec444d26c46bc24abb1f08203735ae75cfeb78cdb388a5136ae7a690a"
PACKET_MANIFEST_BYTES = 34_211
PACKET_PAYLOAD_COUNT = 120
PACKET_PAYLOAD_BYTES = 52_007_905
PACKET_PAYLOAD_SET_SHA256 = "a94730860617895531f89473cbb367588d2404848b750429f0621f0bb665c487"

SOURCE_ARCHIVE_REL = (
    "history/internal_docs/"
    "goal5783_amendment_a1_external_rehash_supplement_20260814.tar.gz"
)
SOURCE_ARCHIVE_SHA256 = "b9eb03b7dd0404b1f5ca46f04122699ab24fe622a62c57b1aa786db82f57a529"
SOURCE_ARCHIVE_BYTES = 10_818_938
SOURCE_MANIFEST_MEMBER = "GOAL5783_AMENDMENT_A1_MANIFEST.json"
SOURCE_MANIFEST_SHA256 = "98ac2cbceb09806643da8552207638ab041d4abc9c712010db1acf2226b64eda"
SOURCE_MANIFEST_BYTES = 2_274
SOURCE_PAYLOAD_COUNT = 10
SOURCE_PAYLOAD_BYTES = 10_857_936
RTXRMQ_SOURCE_REL = "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py"
RTXRMQ_SOURCE_SHA256 = "0823fdf32e0ade592eebc577b1f43d5c81e4fb1134934f353bbd3e3586a3b0b1"
RTXRMQ_SOURCE_BYTES = 10_553
GOAL5783_REVIEW_REL = "history/internal_docs/review_goal5783_postfreeze_held_out_rtxrmq_20260814.md"
GOAL5783_REVIEW_SHA256 = "2dd0864e9db0708f13d48d0c2295419c2bdfe7f80cd93792a85745d0293f006b"
GOAL5783_REVIEW_BYTES = 12_143
GOAL5783_ABSORPTION_REL = (
    "history/internal_docs/goal5783_owner_returned_external_review_absorption_20260814.json"
)
GOAL5783_ABSORPTION_SHA256 = "f539103a43d191c5dc3434653c160dfd0168ca5f30139df3c70ff90bfc99e8d3"
GOAL5783_ABSORPTION_BYTES = 1_058

WORK_AUTHORITY_REL = (
    "history/internal_docs/goal5789_a2_postreview_absorption_work_authority_20260821.json"
)
WORK_AUTHORITY_SHA256 = "96be56ab7f450664fa2d2c27f3df3e9be667eacf9cc45ee0d45725924520e3a0"
WORK_AUTHORITY_BYTES = 4_249
WORK_AUTHORITY_INTERNAL_SHA256 = "d37051d04ff5b3ed99abd11f7469de5fc79bbbac59301ad6fd7b210946961e25"

SUPPLEMENT_REL = (
    "history/internal_docs/"
    "goal5789_a2_postreview_source_custody_supplement_20260821.json"
)
VALIDATOR_REL = "scripts/goal5789_a2_validate_source_custody_replay.py"
TEST_REL = "tests/goal5789_a2_source_custody_replay_test.py"

HELDOUT_CERTIFICATE_REL = (
    "history/internal_docs/goal5789_contract_evidence_20260816/"
    "HELD_OUT_RTXRMQ_CERTIFICATE.json"
)
HELDOUT_CERTIFICATE_SHA256 = "87af6c6357af6165fe51f4c59be19d7b35340a2325c940f2c06a37afa3852fd3"
HELDOUT_CERTIFICATE_BYTES = 9_408
HELDOUT_CERTIFICATE_SEAL = "dcb302c2992029135767fb3d12e0de12f3b30ba491af93d4f5e0d534d0253d38"

MATERIALIZER_REL = "scripts/goal5789_a2_materialize_callback_ir_authority.py"
MATERIALIZER_SHA256 = "facf9273ff5db129b25b5a728c051004fe6802d693e6fed3297aa1cf00a0caef"
MATERIALIZER_BYTES = 40_040
AUTHORITY_REL = (
    "history/internal_docs/goal5789_a2_contract_evidence_20260821/"
    "CALLBACK_IR_AUTHORITY.json"
)
AUTHORITY_SHA256 = "16422fc282b834286f3f3c22db15f1663cc642e7d97bf940e7f594b550a5a59a"
AUTHORITY_BYTES = 261_703
AUTHORITY_INTERNAL_SHA256 = "8383367ba43b92ec88b0f719a507ade4944e635e1a9b6d9243695b0623eaad70"
PIN_REL = (
    "history/internal_docs/goal5789_a2_contract_evidence_20260821/"
    "CALLBACK_IR_AUTHORITY_PIN.json"
)
PIN_SHA256 = "98e2aa6bb258030348dd623ed3609e168143003bae51048230a6dcd665dd1a0d"
PIN_BYTES = 1_787
PIN_INTERNAL_SHA256 = "2defc4649703f0f5bd26c5d6b122d01655886636e2f6880b34dd5e15b33f70e1"

CLAIM_BOUNDARY = {
    "append_only_retrievability_and_replay_repair_only": True,
    "reviewed_a2_packet_or_scientific_output_changed": False,
    "rtxrmq_generalization_claimed": False,
    "semantic_soundness_or_completeness_claimed": False,
    "independent_product_ir_verifier_claimed": False,
    "goal5793_generalization_evidence_count": 0,
    "usability_evidence_count": 0,
}
AUTHORIZATION = {
    "authorizes_goal5793": False,
    "authorizes_entropy_or_candidate_selection": False,
    "authorizes_product_change": False,
    "authorizes_gpu_home_pod_or_ssh": False,
    "authorizes_worker_or_performance_timing": False,
    "authorizes_publication_or_submission": False,
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def pretty(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def safe_relative(value: str) -> str:
    if not value or "\\" in value:
        raise RuntimeError(f"unsafe archive path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value:
        raise RuntimeError(f"noncanonical archive path: {value!r}")
    if any(part in {"", ".", ".."} or ":" in part for part in path.parts):
        raise RuntimeError(f"unsafe archive path: {value!r}")
    return value


def _json(data: bytes, label: str) -> Mapping[str, object]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid JSON: {label}") from exc
    if not isinstance(value, Mapping):
        raise RuntimeError(f"JSON root is not an object: {label}")
    return value


def _read_regular_archive(
    archive_bytes: bytes,
    *,
    prefix: str | None,
    mode: int,
    label: str,
) -> dict[str, bytes]:
    observed: dict[str, bytes] = {}
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(archive_bytes), mode="rb") as zipped:
            tar_bytes = zipped.read()
        with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:") as archive:
            if archive.pax_headers:
                raise RuntimeError(f"{label} has global PAX headers")
            for member in archive.getmembers():
                if not member.isreg() or member.islnk() or member.issym():
                    raise RuntimeError(f"{label} non-regular member: {member.name!r}")
                if (
                    member.mode != mode
                    or member.uid != 0
                    or member.gid != 0
                    or member.mtime != 0
                    or member.uname not in {"", None}
                    or member.gname not in {"", None}
                ):
                    raise RuntimeError(f"{label} noncanonical metadata: {member.name!r}")
                if set(member.pax_headers) - {"path"}:
                    raise RuntimeError(f"{label} unexpected PAX metadata: {member.name!r}")
                if "path" in member.pax_headers and member.pax_headers["path"] != member.name:
                    raise RuntimeError(f"{label} PAX path alias: {member.name!r}")
                name = member.name
                if prefix is not None:
                    exact_prefix = f"{prefix}/"
                    if not name.startswith(exact_prefix):
                        raise RuntimeError(f"{label} member outside exact root: {name!r}")
                    name = name[len(exact_prefix) :]
                safe_relative(name)
                if name in observed:
                    raise RuntimeError(f"{label} duplicate member: {name!r}")
                stream = archive.extractfile(member)
                if stream is None:
                    raise RuntimeError(f"{label} unreadable member: {name!r}")
                data = stream.read()
                if len(data) != member.size:
                    raise RuntimeError(f"{label} truncated member: {name!r}")
                observed[name] = data
    except (gzip.BadGzipFile, tarfile.TarError, EOFError) as exc:
        raise RuntimeError(f"invalid {label} archive") from exc
    return observed


@dataclass(frozen=True)
class FrozenPacket:
    archive: bytes
    manifest: Mapping[str, object]
    manifest_bytes: bytes
    payloads: Mapping[str, bytes]


@dataclass(frozen=True)
class SourceCustody:
    archive: bytes
    manifest: Mapping[str, object]
    manifest_bytes: bytes
    payloads: Mapping[str, bytes]


def load_packet(packet_path: Path) -> FrozenPacket:
    archive = packet_path.read_bytes()
    if len(archive) != PACKET_BYTES or sha(archive) != PACKET_SHA256:
        raise RuntimeError("reviewed A2 packet identity mismatch")
    members = _read_regular_archive(
        archive,
        prefix=PACKET_PREFIX,
        mode=0o444,
        label="reviewed A2 packet",
    )
    manifest_bytes = members.pop("PACKET_MANIFEST.json", None)
    if (
        manifest_bytes is None
        or len(manifest_bytes) != PACKET_MANIFEST_BYTES
        or sha(manifest_bytes) != PACKET_MANIFEST_SHA256
    ):
        raise RuntimeError("reviewed A2 packet manifest identity mismatch")
    manifest = _json(manifest_bytes, "reviewed A2 packet manifest")
    if (
        manifest.get("schema") != "rtdl.goal5789_a2.external_review_packet.v1"
        or manifest.get("status")
        != "FROZEN_EXACT_OWNER_SELECTED_EXTERNAL_REVIEW_PACKET__GOAL5793_BLOCKED"
        or manifest.get("payload_count") != PACKET_PAYLOAD_COUNT
        or manifest.get("payload_bytes") != PACKET_PAYLOAD_BYTES
        or manifest.get("payload_set_sha256") != PACKET_PAYLOAD_SET_SHA256
    ):
        raise RuntimeError("reviewed A2 packet manifest control fields drift")
    rows = manifest.get("payloads")
    if not isinstance(rows, list) or len(rows) != PACKET_PAYLOAD_COUNT:
        raise RuntimeError("reviewed A2 packet manifest row shape mismatch")
    expected: dict[str, Mapping[str, object]] = {}
    digest_rows: list[dict[str, object]] = []
    total = 0
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256", "provenance"}:
            raise RuntimeError("reviewed A2 packet manifest row schema mismatch")
        relative, size = row.get("path"), row.get("bytes")
        identity, provenance = row.get("sha256"), row.get("provenance")
        if (
            not isinstance(relative, str)
            or type(size) is not int
            or size < 0
            or not isinstance(identity, str)
            or len(identity) != 64
            or not isinstance(provenance, str)
            or not provenance
        ):
            raise RuntimeError("reviewed A2 packet manifest row type mismatch")
        safe_relative(relative)
        if relative in expected:
            raise RuntimeError(f"reviewed A2 packet duplicate manifest row: {relative}")
        expected[relative] = row
        total += size
        digest_rows.append({"path": relative, "bytes": size, "sha256": identity})
    if [row["path"] for row in rows] != sorted(expected):
        raise RuntimeError("reviewed A2 packet manifest order mismatch")
    if total != PACKET_PAYLOAD_BYTES or sha(canonical(digest_rows)) != PACKET_PAYLOAD_SET_SHA256:
        raise RuntimeError("reviewed A2 packet manifest payload-set mismatch")
    if set(members) != set(expected):
        raise RuntimeError("reviewed A2 packet exact member set mismatch")
    for relative, row in expected.items():
        data = members[relative]
        if len(data) != row["bytes"] or sha(data) != row["sha256"]:
            raise RuntimeError(f"reviewed A2 packet payload mismatch: {relative}")
    return FrozenPacket(archive, manifest, manifest_bytes, members)


def load_source_custody(source_archive_path: Path) -> SourceCustody:
    archive = source_archive_path.read_bytes()
    if len(archive) != SOURCE_ARCHIVE_BYTES or sha(archive) != SOURCE_ARCHIVE_SHA256:
        raise RuntimeError("Goal5783-A1 source archive identity mismatch")
    members = _read_regular_archive(
        archive,
        prefix=None,
        mode=0o644,
        label="Goal5783-A1 source archive",
    )
    manifest_bytes = members.pop(SOURCE_MANIFEST_MEMBER, None)
    if (
        manifest_bytes is None
        or len(manifest_bytes) != SOURCE_MANIFEST_BYTES
        or sha(manifest_bytes) != SOURCE_MANIFEST_SHA256
    ):
        raise RuntimeError("Goal5783-A1 source manifest identity mismatch")
    manifest = _json(manifest_bytes, "Goal5783-A1 source manifest")
    if (
        set(manifest) != {"schema", "payload_count", "payload_bytes", "payloads"}
        or manifest.get("schema") != "rtdl.goal5783.amendment_a1_external_rehash_manifest.v1"
        or manifest.get("payload_count") != SOURCE_PAYLOAD_COUNT
        or manifest.get("payload_bytes") != SOURCE_PAYLOAD_BYTES
    ):
        raise RuntimeError("Goal5783-A1 source manifest controls mismatch")
    rows = manifest.get("payloads")
    if not isinstance(rows, list) or len(rows) != SOURCE_PAYLOAD_COUNT:
        raise RuntimeError("Goal5783-A1 source manifest rows missing")
    expected: dict[str, Mapping[str, object]] = {}
    total = 0
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {"path", "size", "sha256"}:
            raise RuntimeError("Goal5783-A1 source manifest row schema mismatch")
        relative, size, identity = row.get("path"), row.get("size"), row.get("sha256")
        if (
            not isinstance(relative, str)
            or type(size) is not int
            or size < 0
            or not isinstance(identity, str)
            or len(identity) != 64
        ):
            raise RuntimeError("Goal5783-A1 source manifest row type mismatch")
        safe_relative(relative)
        if relative in expected:
            raise RuntimeError(f"Goal5783-A1 duplicate manifest row: {relative}")
        expected[relative] = row
        total += size
    if total != SOURCE_PAYLOAD_BYTES or set(members) != set(expected):
        raise RuntimeError("Goal5783-A1 exact source payload set mismatch")
    for relative, row in expected.items():
        data = members[relative]
        if len(data) != row["size"] or sha(data) != row["sha256"]:
            raise RuntimeError(f"Goal5783-A1 source payload mismatch: {relative}")
    exact_roots = {
        RTXRMQ_SOURCE_REL: (RTXRMQ_SOURCE_BYTES, RTXRMQ_SOURCE_SHA256),
        GOAL5783_REVIEW_REL: (GOAL5783_REVIEW_BYTES, GOAL5783_REVIEW_SHA256),
        GOAL5783_ABSORPTION_REL: (GOAL5783_ABSORPTION_BYTES, GOAL5783_ABSORPTION_SHA256),
    }
    for relative, (size, identity) in exact_roots.items():
        data = members.get(relative)
        if data is None or len(data) != size or sha(data) != identity:
            raise RuntimeError(f"Goal5783-A1 custody root mismatch: {relative}")
    return SourceCustody(archive, manifest, manifest_bytes, members)


def load_work_authority(work_authority_path: Path) -> tuple[Mapping[str, object], bytes]:
    data = work_authority_path.read_bytes()
    if len(data) != WORK_AUTHORITY_BYTES or sha(data) != WORK_AUTHORITY_SHA256:
        raise RuntimeError("postreview work-authority file identity mismatch")
    authority = _json(data, "postreview work authority")
    body = dict(authority)
    seal = body.pop("work_authority_sha256", None)
    if seal != WORK_AUTHORITY_INTERNAL_SHA256 or sha(canonical(body)) != seal:
        raise RuntimeError("postreview work-authority internal seal mismatch")
    required, scope = authority.get("required_repairs", {}), authority.get("scope", {})
    if (
        not isinstance(required, Mapping)
        or "immutable Goal5783 root" not in str(required.get("p2_2"))
        or not isinstance(scope, Mapping)
        or "new create-only local CPU scripts and tests" not in scope.get("allowed", [])
        or "modifying any externally reviewed byte" not in scope.get("forbidden", [])
    ):
        raise RuntimeError("postreview work authority does not authorize exact P2-2 repair scope")
    return authority, data


def verify_a2_roots(packet: FrozenPacket, custody: SourceCustody) -> None:
    exact_packet_payloads = {
        HELDOUT_CERTIFICATE_REL: (HELDOUT_CERTIFICATE_BYTES, HELDOUT_CERTIFICATE_SHA256),
        MATERIALIZER_REL: (MATERIALIZER_BYTES, MATERIALIZER_SHA256),
        AUTHORITY_REL: (AUTHORITY_BYTES, AUTHORITY_SHA256),
        PIN_REL: (PIN_BYTES, PIN_SHA256),
    }
    for relative, (size, identity) in exact_packet_payloads.items():
        data = packet.payloads.get(relative)
        if data is None or len(data) != size or sha(data) != identity:
            raise RuntimeError(f"A2 replay root mismatch: {relative}")

    certificate = _json(packet.payloads[HELDOUT_CERTIFICATE_REL], "held-out certificate")
    certificate_body = dict(certificate)
    certificate_seal = certificate_body.pop("certificate_sha256", None)
    if certificate_seal != HELDOUT_CERTIFICATE_SEAL or sha(canonical(certificate_body)) != certificate_seal:
        raise RuntimeError("held-out certificate internal seal mismatch")
    source_pins = certificate.get("evidence_contract", {}).get("source_pins", {})
    if not isinstance(source_pins, Mapping) or source_pins.get(RTXRMQ_SOURCE_REL) != RTXRMQ_SOURCE_SHA256:
        raise RuntimeError("held-out certificate does not pin exact RTXRMQ source")

    authority = _json(packet.payloads[AUTHORITY_REL], "stored A2 Callback-IR authority")
    authority_body = dict(authority)
    authority_seal = authority_body.pop("authority_sha256", None)
    if authority_seal != AUTHORITY_INTERNAL_SHA256 or sha(canonical(authority_body)) != authority_seal:
        raise RuntimeError("stored A2 authority internal seal mismatch")
    programs, bindings = authority.get("programs"), authority.get("admitted_bindings")
    if not isinstance(programs, Mapping) or len(programs) != 5:
        raise RuntimeError("stored A2 authority does not contain exact five programs")
    if not isinstance(bindings, list) or len(bindings) != 4:
        raise RuntimeError("stored A2 authority does not contain exact four bindings")
    leaf_count = sum(
        len(row.get("executed_leaf_evidence", []))
        for row in programs.values()
        if isinstance(row, Mapping)
    )
    if leaf_count != 26:
        raise RuntimeError("stored A2 authority does not bind exact 26 leaves")
    source_manifest = authority.get("consumer_source_manifest")
    if not isinstance(source_manifest, Mapping) or source_manifest.get(RTXRMQ_SOURCE_REL) != RTXRMQ_SOURCE_SHA256:
        raise RuntimeError("stored A2 authority RTXRMQ witness mismatch")

    pin = _json(packet.payloads[PIN_REL], "stored A2 authority pin")
    pin_body = dict(pin)
    pin_seal = pin_body.pop("pin_sha256", None)
    if pin_seal != PIN_INTERNAL_SHA256 or sha(canonical(pin_body)) != pin_seal:
        raise RuntimeError("stored A2 pin internal seal mismatch")
    if sha(custody.payloads[RTXRMQ_SOURCE_REL]) != source_manifest[RTXRMQ_SOURCE_REL]:
        raise RuntimeError("Goal5783 source and stored A2 witness differ")


def build_supplement(
    packet: FrozenPacket,
    custody: SourceCustody,
    work_authority: Mapping[str, object],
    work_authority_bytes: bytes,
    validator_bytes: bytes,
    test_bytes: bytes,
) -> dict[str, object]:
    verify_a2_roots(packet, custody)
    supplement: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.postreview_source_custody_supplement.v1",
        "goal": "5789-A2-postreview-P2-2",
        "date": "2026-08-21",
        "status": "APPEND_ONLY_SOURCE_CUSTODY_AND_EXACT_MATERIALIZER_REPLAY_REPAIR",
        "supplement_sha256": "",
        "work_authority": {
            "path": WORK_AUTHORITY_REL,
            "bytes": len(work_authority_bytes),
            "file_sha256": sha(work_authority_bytes),
            "work_authority_sha256": work_authority["work_authority_sha256"],
        },
        "frozen_inputs": {
            "reviewed_a2_packet": {
                "path": PACKET_REL,
                "bytes": len(packet.archive),
                "file_sha256": sha(packet.archive),
                "manifest_bytes": len(packet.manifest_bytes),
                "manifest_sha256": sha(packet.manifest_bytes),
                "payload_count": packet.manifest["payload_count"],
                "payload_bytes": packet.manifest["payload_bytes"],
                "payload_set_sha256": packet.manifest["payload_set_sha256"],
            },
            "goal5783_a1_source_archive": {
                "path": SOURCE_ARCHIVE_REL,
                "bytes": len(custody.archive),
                "file_sha256": sha(custody.archive),
                "manifest_member": SOURCE_MANIFEST_MEMBER,
                "manifest_bytes": len(custody.manifest_bytes),
                "manifest_sha256": sha(custody.manifest_bytes),
                "payload_count": custody.manifest["payload_count"],
                "payload_bytes": custody.manifest["payload_bytes"],
            },
        },
        "source_custody": {
            "rtxrmq_consumer_source": {
                "archive_member_path": RTXRMQ_SOURCE_REL,
                "materialized_repository_path": RTXRMQ_SOURCE_REL,
                "bytes": len(custody.payloads[RTXRMQ_SOURCE_REL]),
                "file_sha256": sha(custody.payloads[RTXRMQ_SOURCE_REL]),
            },
            "goal5783_external_review": {
                "archive_member_path": GOAL5783_REVIEW_REL,
                "bytes": len(custody.payloads[GOAL5783_REVIEW_REL]),
                "file_sha256": sha(custody.payloads[GOAL5783_REVIEW_REL]),
            },
            "goal5783_review_absorption": {
                "archive_member_path": GOAL5783_ABSORPTION_REL,
                "bytes": len(custody.payloads[GOAL5783_ABSORPTION_REL]),
                "file_sha256": sha(custody.payloads[GOAL5783_ABSORPTION_REL]),
            },
            "goal5789_heldout_certificate": {
                "packet_payload_path": HELDOUT_CERTIFICATE_REL,
                "bytes": HELDOUT_CERTIFICATE_BYTES,
                "file_sha256": HELDOUT_CERTIFICATE_SHA256,
                "certificate_sha256": HELDOUT_CERTIFICATE_SEAL,
                "rtxrmq_source_pin": RTXRMQ_SOURCE_SHA256,
            },
            "mutable_workspace_rtxrmq_source_used_as_authority": False,
        },
        "exact_replay_contract": {
            "materializer": {
                "packet_payload_path": MATERIALIZER_REL,
                "bytes": MATERIALIZER_BYTES,
                "file_sha256": MATERIALIZER_SHA256,
            },
            "expected_callback_authority": {
                "packet_payload_path": AUTHORITY_REL,
                "bytes": AUTHORITY_BYTES,
                "file_sha256": AUTHORITY_SHA256,
                "authority_sha256": AUTHORITY_INTERNAL_SHA256,
            },
            "expected_callback_authority_pin": {
                "packet_payload_path": PIN_REL,
                "bytes": PIN_BYTES,
                "file_sha256": PIN_SHA256,
                "pin_sha256": PIN_INTERNAL_SHA256,
            },
            "program_count": 5,
            "executed_leaf_count": 26,
            "admitted_binding_count": 4,
            "consumer_source_count": 5,
            "fresh_temporary_repository_required": True,
            "fresh_interpreter_required": True,
            "authority_and_pin_must_be_byte_identical": True,
        },
        "tooling": {
            "validator": {
                "path": VALIDATOR_REL,
                "bytes": len(validator_bytes),
                "file_sha256": sha(validator_bytes),
            },
            "test": {
                "path": TEST_REL,
                "bytes": len(test_bytes),
                "file_sha256": sha(test_bytes),
            },
        },
        "claim_boundary": dict(CLAIM_BOUNDARY),
        "authorization": dict(AUTHORIZATION),
    }
    supplement["supplement_sha256"] = sha(
        canonical({key: value for key, value in supplement.items() if key != "supplement_sha256"})
    )
    return supplement


def reconstruct_supplement_bytes(
    packet_path: Path,
    source_archive_path: Path,
    work_authority_path: Path,
    validator_path: Path | None = None,
    test_path: Path | None = None,
) -> bytes:
    packet = load_packet(packet_path)
    custody = load_source_custody(source_archive_path)
    work_authority, work_authority_bytes = load_work_authority(work_authority_path)
    exact_validator_path = Path(__file__) if validator_path is None else validator_path
    exact_test_path = ROOT / TEST_REL if test_path is None else test_path
    return pretty(
        build_supplement(
            packet,
            custody,
            work_authority,
            work_authority_bytes,
            exact_validator_path.read_bytes(),
            exact_test_path.read_bytes(),
        )
    )


def load_supplement(
    supplement_path: Path,
    packet: FrozenPacket,
    custody: SourceCustody,
    work_authority: Mapping[str, object],
    work_authority_bytes: bytes,
    validator_bytes: bytes,
    test_bytes: bytes,
) -> tuple[Mapping[str, object], bytes]:
    data = supplement_path.read_bytes()
    value = _json(data, "source-custody supplement")
    body = dict(value)
    seal = body.pop("supplement_sha256", None)
    if not isinstance(seal, str) or sha(canonical(body)) != seal:
        raise RuntimeError("source-custody supplement internal seal mismatch")
    expected = build_supplement(
        packet,
        custody,
        work_authority,
        work_authority_bytes,
        validator_bytes,
        test_bytes,
    )
    if value != expected or data != pretty(expected):
        raise RuntimeError("source-custody supplement is not exact reconstruction")
    return value, data


def _write_fresh_tree(root: Path, payloads: Mapping[str, bytes]) -> None:
    root = root.resolve()
    for relative, data in sorted(payloads.items()):
        safe_relative(relative)
        target = root.joinpath(*PurePosixPath(relative).parts)
        resolved_parent = target.parent.resolve()
        if resolved_parent != root and root not in resolved_parent.parents:
            raise RuntimeError(f"payload escaped replay root: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(data)


def validate_and_replay(
    packet_path: Path,
    source_archive_path: Path,
    supplement_path: Path,
    work_authority_path: Path,
    validator_path: Path | None = None,
    test_path: Path | None = None,
) -> dict[str, object]:
    packet = load_packet(packet_path)
    custody = load_source_custody(source_archive_path)
    work_authority, work_authority_bytes = load_work_authority(work_authority_path)
    exact_validator_path = Path(__file__) if validator_path is None else validator_path
    exact_test_path = ROOT / TEST_REL if test_path is None else test_path
    supplement, supplement_bytes = load_supplement(
        supplement_path,
        packet,
        custody,
        work_authority,
        work_authority_bytes,
        exact_validator_path.read_bytes(),
        exact_test_path.read_bytes(),
    )
    verify_a2_roots(packet, custody)

    with tempfile.TemporaryDirectory(prefix="goal5789_a2_source_custody_replay_") as temporary:
        replay_root = Path(temporary).resolve()
        _write_fresh_tree(replay_root, packet.payloads)
        source_path = replay_root.joinpath(*PurePosixPath(RTXRMQ_SOURCE_REL).parts)
        if source_path.exists():
            if source_path.read_bytes() != custody.payloads[RTXRMQ_SOURCE_REL]:
                raise RuntimeError("packet-carried RTXRMQ path conflicts with frozen source archive")
        else:
            source_path.parent.mkdir(parents=True, exist_ok=True)
            with source_path.open("xb") as handle:
                handle.write(custody.payloads[RTXRMQ_SOURCE_REL])

        authority_path = replay_root.joinpath(*PurePosixPath(AUTHORITY_REL).parts)
        pin_path = replay_root.joinpath(*PurePosixPath(PIN_REL).parts)
        stored_authority, stored_pin = authority_path.read_bytes(), pin_path.read_bytes()
        authority_path.unlink()
        pin_path.unlink()

        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        environment.pop("PYTHONHOME", None)
        # Third-party Python dependencies (notably NumPy) are ordinary replay
        # environment dependencies.  Do not suppress the user site on hosts
        # where they are installed there.  Product-module custody remains
        # enforced by the unchanged materializer's module-location check.
        environment.pop("PYTHONNOUSERSITE", None)
        completed = subprocess.run(
            [sys.executable, str(replay_root.joinpath(*PurePosixPath(MATERIALIZER_REL).parts))],
            cwd=replay_root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "frozen A2 materializer replay failed: "
                f"returncode={completed.returncode}; stdout={completed.stdout!r}; "
                f"stderr={completed.stderr!r}"
            )
        regenerated_authority, regenerated_pin = authority_path.read_bytes(), pin_path.read_bytes()
        if regenerated_authority != stored_authority:
            raise RuntimeError("replayed A2 Callback-IR authority is not byte-identical")
        if regenerated_pin != stored_pin:
            raise RuntimeError("replayed A2 Callback-IR authority pin is not byte-identical")
        try:
            receipt = json.loads(completed.stdout.strip())
        except json.JSONDecodeError as exc:
            raise RuntimeError("A2 materializer replay stdout is not its expected JSON receipt") from exc
        if not isinstance(receipt, Mapping):
            raise RuntimeError("A2 materializer replay receipt shape mismatch")

    authority = _json(regenerated_authority, "replayed A2 authority")
    programs, bindings = authority["programs"], authority["admitted_bindings"]
    leaf_count = sum(len(row["executed_leaf_evidence"]) for row in programs.values())
    result: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.source_custody_replay_validation.v1",
        "goal": "5789-A2-postreview-P2-2",
        "date": "2026-08-21",
        "status": "PASS__EXACT_A2_MATERIALIZER_REPLAY_FROM_TWO_FROZEN_INPUTS",
        "validation_sha256": "",
        "inputs": {
            "reviewed_a2_packet": supplement["frozen_inputs"]["reviewed_a2_packet"],
            "goal5783_a1_source_archive": supplement["frozen_inputs"]["goal5783_a1_source_archive"],
            "source_custody_supplement": {
                "path": SUPPLEMENT_REL,
                "bytes": len(supplement_bytes),
                "file_sha256": sha(supplement_bytes),
                "supplement_sha256": supplement["supplement_sha256"],
            },
            "work_authority": supplement["work_authority"],
        },
        "custody_checks": {
            "reviewed_packet_exact_identity_member_set_and_payloads": True,
            "separate_goal5783_archive_exact_identity": True,
            "goal5783_manifest_exact_member_set_and_payloads": True,
            "goal5783_review_and_absorption_exact": True,
            "source_matches_goal5783_manifest": True,
            "source_matches_heldout_certificate_pin": True,
            "mutable_workspace_rtxrmq_source_read": False,
        },
        "replay": {
            "fresh_temporary_repository": True,
            "fresh_interpreter": True,
            "materializer_file_sha256": MATERIALIZER_SHA256,
            "program_count": len(programs),
            "executed_leaf_count": leaf_count,
            "admitted_binding_count": len(bindings),
            "consumer_source_count": len(authority["consumer_source_manifest"]),
            "callback_authority_byte_identical": True,
            "callback_authority_file_sha256": sha(regenerated_authority),
            "callback_authority_pin_byte_identical": True,
            "callback_authority_pin_file_sha256": sha(regenerated_pin),
            "materializer_receipt": dict(receipt),
        },
        "claim_boundary": dict(CLAIM_BOUNDARY),
        "authorization": dict(AUTHORIZATION),
    }
    if (
        result["replay"]["program_count"] != 5
        or result["replay"]["executed_leaf_count"] != 26
        or result["replay"]["admitted_binding_count"] != 4
        or result["replay"]["consumer_source_count"] != 5
    ):
        raise RuntimeError("replayed A2 authority count contract mismatch")
    result["validation_sha256"] = sha(
        canonical({key: value for key, value in result.items() if key != "validation_sha256"})
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=ROOT / PACKET_REL)
    parser.add_argument("--source-archive", type=Path, default=ROOT / SOURCE_ARCHIVE_REL)
    parser.add_argument("--work-authority", type=Path, default=ROOT / WORK_AUTHORITY_REL)
    parser.add_argument("--supplement", type=Path, default=ROOT / SUPPLEMENT_REL)
    parser.add_argument("--emit-supplement", action="store_true")
    parser.add_argument("--result-output", type=Path)
    args = parser.parse_args()

    packet_path = args.packet.resolve()
    source_archive_path = args.source_archive.resolve()
    work_authority_path = args.work_authority.resolve()
    supplement_path = args.supplement.resolve()
    if args.emit_supplement:
        encoded = reconstruct_supplement_bytes(
            packet_path, source_archive_path, work_authority_path
        )
        supplement_path.parent.mkdir(parents=True, exist_ok=True)
        with supplement_path.open("xb") as handle:
            handle.write(encoded)
        print(
            json.dumps(
                {
                    "path": str(supplement_path),
                    "bytes": len(encoded),
                    "file_sha256": sha(encoded),
                    "supplement_sha256": _json(encoded, "emitted supplement")["supplement_sha256"],
                },
                sort_keys=True,
            )
        )
        return 0

    result = validate_and_replay(
        packet_path, source_archive_path, supplement_path, work_authority_path
    )
    encoded = pretty(result)
    if args.result_output is not None:
        output = args.result_output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("xb") as handle:
            handle.write(encoded)
    print(encoded.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

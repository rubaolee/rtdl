"""Build the deterministic Goal5789-A2 append-only postreview repair packet.

The successor preserves all 120 reviewed packet payloads byte-for-byte and
adds exactly seventeen postreview payloads.  The missing RTXRMQ source is read
only from the immutable Goal5783-A1 archive already carried by the predecessor
packet.  No mutable workspace copy of that source is consulted.

Formal outputs are create-only.  ``fixture_mode`` exists solely so unit tests
can exercise the complete packet machinery before the official postreview
result/report are frozen; :func:`main` never enables it.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "goal5789_a2_postreview_repair_packet_v1"
ARCHIVE = ROOT / "history/internal_docs/goal5789_a2_postreview_repair_packet_v1_20260822.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5789_a2_postreview_repair_packet_v1_twin_20260822.tar.gz"
MANIFEST = ROOT / "history/internal_docs/goal5789_a2_postreview_repair_packet_v1_manifest_20260822.json"

OLD_PACKET_REL = (
    "history/internal_docs/"
    "goal5789_a2_callback_ir_authority_binding_review_packet_v1_20260821.tar.gz"
)
OLD_PACKET_PREFIX = "goal5789_a2_callback_ir_authority_binding_review_packet_v1"
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
    "scripts/goal5789_a2_build_postreview_repair_packet.py": (
        "postreview_successor_packet_tool"
    ),
    "scripts/goal5789_a2_audit_postreview_repair_packet.py": (
        "postreview_successor_packet_tool"
    ),
    "tests/goal5789_a2_postreview_repair_packet_test.py": (
        "postreview_successor_packet_tool"
    ),
}

WORK_AUTHORITY_INTERNAL_SHA256 = (
    "d37051d04ff5b3ed99abd11f7469de5fc79bbbac59301ad6fd7b210946961e25"
)
MATRIX_V2_INTERNAL_SHA256 = (
    "b82d13d2e051ede3d3940fbc54f22c8bba6a8daf1cfac39742f3c6ebc4735190"
)
SOURCE_CUSTODY_INTERNAL_SHA256 = (
    "6ee36af1c85ecb5c5fa79656a1074a4a92da8da24618f5dfb595bd3702b641cf"
)
PACKET_AUDIT_SUPPLEMENT_INTERNAL_SHA256 = (
    "ee6915edaf68146cadd9392cc9b1512f5e6fc6ffa585c0635baeadc148eff482"
)

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

# This schema is accepted only when fixture_mode=True.  It can never be emitted
# by main() and is intentionally distinct from the official result schema.
FIXTURE_RESULT_SCHEMA = "rtdl.goal5789_a2.postreview_repairs_result.test_fixture.v1"
FIXTURE_RESULT_STATUS = "TEST_FIXTURE_ONLY__NOT_A_FORMAL_RESULT"
FIXTURE_REPAIR_STATUS = {
    "p2_1_exact_reason_matrix_closed": True,
    "p2_2_source_custody_and_materializer_replay_closed": True,
    "p2_3_independence_scope_corrected": True,
    "p3_1_packet_audit_reporting_closed": True,
}

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


def _read_fixed(root: Path, relative: str, size: int, identity: str) -> bytes:
    root = root.resolve()
    path = root.joinpath(*PurePosixPath(_safe(relative)).parts)
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"fixed input absent or non-regular: {relative}")
    data = path.read_bytes()
    if len(data) != size or _sha(data) != identity:
        raise RuntimeError(f"fixed input identity mismatch: {relative}")
    return data


def _read_prefixed_archive(
    archive_bytes: bytes, *, prefix: str, mode: int, label: str
) -> dict[str, bytes]:
    observed: dict[str, bytes] = {}
    aliases: set[str] = set()
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(archive_bytes), mode="rb") as zipped:
            raw = zipped.read()
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
            for member in archive.getmembers():
                if not member.isreg() or member.issym() or member.islnk():
                    raise RuntimeError(f"{label} non-regular member: {member.name!r}")
                if (
                    member.mode != mode
                    or member.uid != 0
                    or member.gid != 0
                    or member.mtime != 0
                ):
                    raise RuntimeError(f"{label} noncanonical member metadata")
                marker = prefix + "/" if prefix else ""
                if marker and not member.name.startswith(marker):
                    raise RuntimeError(f"{label} member prefix mismatch: {member.name!r}")
                relative = member.name[len(marker) :]
                _safe(relative)
                alias = _alias_key(relative)
                if relative in observed or alias in aliases:
                    raise RuntimeError(f"{label} duplicate or aliased member: {relative}")
                aliases.add(alias)
                handle = archive.extractfile(member)
                if handle is None:
                    raise RuntimeError(f"{label} unreadable member: {relative}")
                payload = handle.read()
                if len(payload) != member.size:
                    raise RuntimeError(f"{label} member size mismatch: {relative}")
                observed[relative] = payload
    except (gzip.BadGzipFile, tarfile.TarError, EOFError) as exc:
        raise RuntimeError(f"invalid archive: {label}") from exc
    return observed


def _validate_rows(
    manifest: Mapping[str, object], *, expected_count: int, label: str
) -> tuple[dict[str, Mapping[str, object]], list[dict[str, object]], int]:
    rows = manifest.get("payloads")
    if not isinstance(rows, list) or len(rows) != expected_count:
        raise RuntimeError(f"{label} payload count mismatch")
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
            raise RuntimeError(f"{label} payload row schema mismatch")
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
            raise RuntimeError(f"{label} payload row type mismatch")
        alias = _alias_key(relative)
        if alias in aliases:
            raise RuntimeError(f"{label} payload path alias collision")
        aliases.add(alias)
        expected[relative] = row
        total += size
        digest_rows.append({"path": relative, "bytes": size, "sha256": identity})
    if [row["path"] for row in rows] != sorted(expected):
        raise RuntimeError(f"{label} payload rows are not canonically ordered")
    return expected, digest_rows, total


def _load_predecessor(root: Path) -> tuple[dict[str, bytes], dict[str, str]]:
    archive = _read_fixed(root, OLD_PACKET_REL, OLD_PACKET_BYTES, OLD_PACKET_SHA256)
    members = _read_prefixed_archive(
        archive, prefix=OLD_PACKET_PREFIX, mode=0o444, label="reviewed A2 packet"
    )
    manifest_bytes = members.pop("PACKET_MANIFEST.json", None)
    if (
        manifest_bytes is None
        or len(manifest_bytes) != OLD_PACKET_MANIFEST_BYTES
        or _sha(manifest_bytes) != OLD_PACKET_MANIFEST_SHA256
    ):
        raise RuntimeError("reviewed A2 embedded manifest identity mismatch")
    manifest = _object(manifest_bytes, "reviewed A2 packet manifest")
    if (
        set(manifest)
        != {
            "schema",
            "goal",
            "date",
            "status",
            "root_delivery_manifest",
            "payload_count",
            "payload_bytes",
            "payload_set_sha256",
            "payloads",
            "claim_boundary",
            "authorization",
        }
        or manifest.get("schema") != "rtdl.goal5789_a2.external_review_packet.v1"
        or manifest.get("payload_count") != OLD_PACKET_PAYLOAD_COUNT
        or manifest.get("payload_bytes") != OLD_PACKET_PAYLOAD_BYTES
        or manifest.get("payload_set_sha256") != OLD_PACKET_PAYLOAD_SET_SHA256
    ):
        raise RuntimeError("reviewed A2 packet manifest controls mismatch")
    expected, digest_rows, total = _validate_rows(
        manifest, expected_count=OLD_PACKET_PAYLOAD_COUNT, label="reviewed A2 packet"
    )
    if (
        total != OLD_PACKET_PAYLOAD_BYTES
        or _sha(_canonical(digest_rows)) != OLD_PACKET_PAYLOAD_SET_SHA256
        or set(members) != set(expected)
    ):
        raise RuntimeError("reviewed A2 packet payload-set mismatch")
    for relative, row in expected.items():
        data = members[relative]
        if len(data) != row["bytes"] or _sha(data) != row["sha256"]:
            raise RuntimeError(f"reviewed A2 packet payload mismatch: {relative}")
    delivery_bytes = members.get(DELIVERY_REL)
    if (
        delivery_bytes is None
        or len(delivery_bytes) != DELIVERY_BYTES
        or _sha(delivery_bytes) != DELIVERY_SHA256
    ):
        raise RuntimeError("reviewed A2 delivery-manifest identity mismatch")
    delivery = _object(delivery_bytes, "reviewed A2 delivery manifest")
    _self_seal(
        delivery,
        "delivery_manifest_sha256",
        DELIVERY_INTERNAL_SHA256,
        "reviewed A2 delivery manifest",
    )
    provenance = {relative: str(row["provenance"]) for relative, row in expected.items()}
    if RTXRMQ_SOURCE_REL in members:
        raise RuntimeError("reviewed A2 packet unexpectedly contains RTXRMQ source")
    return members, provenance


def _source_from_immutable_archive(source_archive: bytes) -> bytes:
    if len(source_archive) != SOURCE_ARCHIVE_BYTES or _sha(source_archive) != SOURCE_ARCHIVE_SHA256:
        raise RuntimeError("Goal5783-A1 source archive identity mismatch")
    members = _read_prefixed_archive(
        source_archive, prefix="", mode=0o644, label="Goal5783-A1 source archive"
    )
    manifest_bytes = members.pop(SOURCE_MANIFEST_MEMBER, None)
    if (
        manifest_bytes is None
        or len(manifest_bytes) != SOURCE_MANIFEST_BYTES
        or _sha(manifest_bytes) != SOURCE_MANIFEST_SHA256
    ):
        raise RuntimeError("Goal5783-A1 source manifest identity mismatch")
    manifest = _object(manifest_bytes, "Goal5783-A1 source manifest")
    rows = manifest.get("payloads")
    if (
        set(manifest) != {"schema", "payload_count", "payload_bytes", "payloads"}
        or manifest.get("schema")
        != "rtdl.goal5783.amendment_a1_external_rehash_manifest.v1"
        or manifest.get("payload_count") != 10
        or manifest.get("payload_bytes") != 10_857_936
        or not isinstance(rows, list)
        or len(rows) != 10
    ):
        raise RuntimeError("Goal5783-A1 source manifest controls mismatch")
    expected: dict[str, Mapping[str, object]] = {}
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {"path", "size", "sha256"}:
            raise RuntimeError("Goal5783-A1 source manifest row mismatch")
        relative = row["path"]
        if type(relative) is not str or relative in expected:
            raise RuntimeError("Goal5783-A1 duplicate source row")
        _safe(relative)
        expected[relative] = row
    if set(members) != set(expected):
        raise RuntimeError("Goal5783-A1 source payload set mismatch")
    for relative, row in expected.items():
        data = members[relative]
        if len(data) != row["size"] or _sha(data) != row["sha256"]:
            raise RuntimeError(f"Goal5783-A1 payload mismatch: {relative}")
    source = members.get(RTXRMQ_SOURCE_REL)
    if (
        source is None
        or len(source) != RTXRMQ_SOURCE_BYTES
        or _sha(source) != RTXRMQ_SOURCE_SHA256
    ):
        raise RuntimeError("Goal5783-A1 RTXRMQ source identity mismatch")
    return source


def _validate_fixed_json(relative: str, data: bytes) -> None:
    if not relative.endswith(".json"):
        return
    value = _object(data, relative)
    if relative.endswith("postreview_absorption_work_authority_20260821.json"):
        if (
            value.get("schema")
            != "rtdl.goal5789_a2.postreview_absorption_work_authority.v1"
        ):
            raise RuntimeError("work-authority schema mismatch")
        _self_seal(value, "work_authority_sha256", WORK_AUTHORITY_INTERNAL_SHA256, "work authority")
        authorization = value.get("authorization")
        if not isinstance(authorization, Mapping) or any(
            authorization.get(key) is not False
            for key in (
                "authorizes_goal5793_implementation_or_execution",
                "authorizes_goal5793_s0_preregistration_authoring",
                "authorizes_gpu_home_pod_or_ssh",
                "authorizes_product_checker_native_or_app_change",
                "authorizes_publication_or_submission",
                "authorizes_worker_or_performance_timing",
            )
        ):
            raise RuntimeError("work-authority forbidden authorization drift")
    elif relative.endswith("callback_binding_adversarial_matrix_v2_20260821.json"):
        _self_seal(value, "matrix_sha256", MATRIX_V2_INTERNAL_SHA256, "matrix v2")
        if (
            value.get("schema")
            != "rtdl.goal5789_a2.callback_binding_adversarial_matrix.v2"
            or value.get("case_count") != 159
            or value.get("passed_count") != 159
            or value.get("failed_count") != 0
            or value.get("case_accounting", {}).get(
                "certificate_only_exact_reason_set_count"
            )
            != 126
            or value.get("case_accounting", {}).get(
                "certificate_only_generic_substring_oracle_count_in_v2"
            )
            != 0
            or any(item is not False for item in value.get("authorization", {}).values())
        ):
            raise RuntimeError("matrix-v2 schema, count, or authorization mismatch")
    elif relative.endswith("postreview_source_custody_supplement_20260821.json"):
        _self_seal(
            value,
            "supplement_sha256",
            SOURCE_CUSTODY_INTERNAL_SHA256,
            "source-custody supplement",
        )
        if (
            value.get("schema")
            != "rtdl.goal5789_a2.postreview_source_custody_supplement.v1"
            or value.get("source_custody", {})
            .get("rtxrmq_consumer_source", {})
            .get("file_sha256")
            != RTXRMQ_SOURCE_SHA256
            or value.get("claim_boundary", {}).get(
                "independent_product_ir_verifier_claimed"
            )
            is not False
            or any(item is not False for item in value.get("authorization", {}).values())
        ):
            raise RuntimeError("source-custody supplement boundary mismatch")
    elif relative.endswith("postreview_packet_audit_supplement_20260821.json"):
        _self_seal(
            value,
            "supplement_sha256",
            PACKET_AUDIT_SUPPLEMENT_INTERNAL_SHA256,
            "packet-audit supplement",
        )
        if (
            value.get("schema")
            != "rtdl.goal5789_a2.postreview_packet_audit_supplement.v1"
            or value.get("payload_identity_checked_count") != 120
            or value.get("payload_identity_mismatch_count") != 0
            or value.get("checks", {}).get("payload_identity") is not True
            or value.get("checks", {}).get("payload_set_digest") is not True
            or any(item is not False for item in value.get("authorization", {}).values())
        ):
            raise RuntimeError("packet-audit supplement boundary mismatch")


def _fixture_result(report_bytes: bytes) -> dict[str, object]:
    """Return the sole accepted temporary result shape for unit tests."""

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


def _validate_postreview_pair(
    result_bytes: bytes, report_bytes: bytes, *, fixture_mode: bool
) -> dict[str, object]:
    result = _object(result_bytes, "postreview result")
    body = {key: value for key, value in result.items() if key != "result_sha256"}
    if result.get("result_sha256") != _sha(_canonical(body)):
        raise RuntimeError("postreview result internal seal mismatch")
    if fixture_mode:
        expected = _fixture_result(report_bytes)
        if result != expected:
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


def _tar_bytes(payloads: Mapping[str, bytes], manifest_bytes: bytes) -> bytes:
    raw = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as zipped:
        # GNU long-name records avoid per-member PAX metadata.  The independent
        # auditor rejects all global/member PAX headers so ``canonical_metadata``
        # has a literal, reproducible meaning.
        with tarfile.open(fileobj=zipped, mode="w", format=tarfile.GNU_FORMAT) as archive:
            members = dict(payloads)
            members["PACKET_MANIFEST.json"] = manifest_bytes
            for relative, data in sorted(members.items()):
                _safe(relative)
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


def build_packet(
    *,
    root: Path = ROOT,
    result_bytes: bytes | None = None,
    report_bytes: bytes | None = None,
    fixture_mode: bool = False,
) -> tuple[bytes, bytes, dict[str, object]]:
    root = root.resolve()
    predecessor, provenance = _load_predecessor(root)
    source = _source_from_immutable_archive(predecessor[SOURCE_ARCHIVE_REL])
    payloads = dict(predecessor)
    payloads[RTXRMQ_SOURCE_REL] = source
    provenance[RTXRMQ_SOURCE_REL] = "goal5783_a1_immutable_source_archive_member"

    for relative, (size, identity, source_label) in FIXED_ADDITIONS.items():
        if relative in payloads:
            raise RuntimeError(f"postreview payload collides with predecessor: {relative}")
        data = _read_fixed(root, relative, size, identity)
        _validate_fixed_json(relative, data)
        payloads[relative] = data
        provenance[relative] = source_label

    for relative, source_label in DYNAMIC_TOOL_ADDITIONS.items():
        if relative in payloads:
            raise RuntimeError(f"successor tool collides with predecessor: {relative}")
        path = root.joinpath(*PurePosixPath(_safe(relative)).parts)
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"successor packet tool absent or non-regular: {relative}")
        data = path.read_bytes()
        if not data:
            raise RuntimeError(f"successor packet tool is empty: {relative}")
        payloads[relative] = data
        provenance[relative] = source_label

    if result_bytes is None:
        result_path = root.joinpath(*PurePosixPath(POSTREVIEW_RESULT_REL).parts)
        if result_path.is_symlink() or not result_path.is_file():
            raise RuntimeError("official postreview result is absent")
        result_bytes = result_path.read_bytes()
    if report_bytes is None:
        report_path = root.joinpath(*PurePosixPath(POSTREVIEW_REPORT_REL).parts)
        if report_path.is_symlink() or not report_path.is_file():
            raise RuntimeError("official postreview report is absent")
        report_bytes = report_path.read_bytes()
    if not report_bytes:
        raise RuntimeError("postreview report must be nonempty")
    _validate_postreview_pair(result_bytes, report_bytes, fixture_mode=fixture_mode)
    payloads[POSTREVIEW_RESULT_REL] = result_bytes
    provenance[POSTREVIEW_RESULT_REL] = "postreview_absorption_result"
    payloads[POSTREVIEW_REPORT_REL] = report_bytes
    provenance[POSTREVIEW_REPORT_REL] = "postreview_absorption_report"

    if len(predecessor) != 120 or len(payloads) != 137:
        raise RuntimeError("postreview packet exact 120+17 payload accounting mismatch")
    aliases: set[str] = set()
    for relative in payloads:
        alias = _alias_key(relative)
        if alias in aliases:
            raise RuntimeError(f"postreview packet path alias collision: {relative}")
        aliases.add(alias)
    rows = [
        {
            "path": relative,
            "bytes": len(data),
            "sha256": _sha(data),
            "provenance": provenance[relative],
        }
        for relative, data in sorted(payloads.items())
    ]
    digest_rows = [
        {key: row[key] for key in ("path", "bytes", "sha256")} for row in rows
    ]
    manifest: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.postreview_repair_packet.v1",
        "goal": "5789-A2-postreview",
        "date": "2026-08-22",
        "status": (
            "TEST_FIXTURE__NOT_FORMAL_OUTPUT"
            if fixture_mode
            else "FROZEN_APPEND_ONLY_POSTREVIEW_REPAIR_PACKET__GOAL5793_REMAINS_BLOCKED"
        ),
        "predecessor_packet": {
            "path": OLD_PACKET_REL,
            "bytes": OLD_PACKET_BYTES,
            "file_sha256": OLD_PACKET_SHA256,
            "manifest_bytes": OLD_PACKET_MANIFEST_BYTES,
            "manifest_file_sha256": OLD_PACKET_MANIFEST_SHA256,
            "payload_count": OLD_PACKET_PAYLOAD_COUNT,
            "payload_bytes": OLD_PACKET_PAYLOAD_BYTES,
            "payload_set_sha256": OLD_PACKET_PAYLOAD_SET_SHA256,
        },
        "postreview_result": {
            "path": POSTREVIEW_RESULT_REL,
            "bytes": len(result_bytes),
            "file_sha256": _sha(result_bytes),
            "result_sha256": _object(result_bytes, "postreview result")["result_sha256"],
        },
        "postreview_report": {
            "path": POSTREVIEW_REPORT_REL,
            "bytes": len(report_bytes),
            "file_sha256": _sha(report_bytes),
        },
        "payload_count": len(rows),
        "payload_bytes": sum(row["bytes"] for row in rows),
        "payload_set_sha256": _sha(_canonical(digest_rows)),
        "payloads": rows,
        "historical_boundary": dict(HISTORICAL_BOUNDARY),
        "claim_boundary": dict(CLAIM_BOUNDARY),
        "authorization": dict(AUTHORIZATION),
    }
    manifest_bytes = _pretty(manifest)
    return _tar_bytes(payloads, manifest_bytes), manifest_bytes, manifest


def _write_create_only(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)


def main() -> int:
    if ARCHIVE.exists() or TWIN.exists() or MANIFEST.exists():
        raise RuntimeError("Goal5789-A2 postreview repair packet outputs are create-only")
    archive, manifest_bytes, manifest = build_packet(fixture_mode=False)
    _write_create_only(ARCHIVE, archive)
    try:
        _write_create_only(TWIN, archive)
        _write_create_only(MANIFEST, manifest_bytes)
    except BaseException:
        ARCHIVE.unlink(missing_ok=True)
        TWIN.unlink(missing_ok=True)
        MANIFEST.unlink(missing_ok=True)
        raise
    print(
        json.dumps(
            {
                "archive_sha256": _sha(archive),
                "archive_bytes": len(archive),
                "manifest_sha256": _sha(manifest_bytes),
                "manifest_bytes": len(manifest_bytes),
                "payload_count": manifest["payload_count"],
                "payload_bytes": manifest["payload_bytes"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

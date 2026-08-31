"""Independent stdlib recount for Goal5789-A2 callback authority evidence.

This script imports neither RTDL nor either Goal5789 checker/builder.  It
reopens the frozen source and execution-evidence archives, reconstructs the
five full Callback-IR projections, verifies all 26 executed leaf artifacts,
and checks that A2 changes each predecessor certificate only at the declared
successor schema/seal/callback boundary.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT / "history/internal_docs/goal5789_a2_contract_evidence_20260821"
OLD = ROOT / "history/internal_docs/goal5789_contract_evidence_20260816"
OUTPUT = A2 / "INDEPENDENT_RECOUNT.json"
_SHA = re.compile(r"^[0-9a-f]{64}$")

# Independent review roots.  These values are deliberately repeated here
# instead of imported from the materializer, certificate builder, or checker.
# The recount must reject a coherent re-signing that merely points a consumer
# pair at a different real program in the same frozen five-program universe.
EXPECTED_PROGRAM_SHA256S = {
    "371de8d1816ddb8dbce78db9eb160f08cce3d595784509d5c6400e51b50ad476",
    "92697debe1e25227ec770b4d339c7cd248b16b7185612516841f3986a208ea30",
    "c126a788b5e451fc0d76b4c48610bb2e6d6dbbf22fdb0b1c656deac97babc671",
    "eeb2427e72a1f6b9f242adbf588d89e40616f1176c5bef60705ec716fcd06690",
    "c3a17d90e2c8895f6ec14b0c07bafdc734d7ec233b3397bdc99fd478b9941c26",
}

EXPECTED_PROGRAM_METADATA_BY_SHA256 = {
    "371de8d1816ddb8dbce78db9eb160f08cce3d595784509d5c6400e51b50ad476": {
        "alias": "builtin_triangle_adjacency",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.adjacency.v1",
        "compile_entrypoint": "rtdsl.v4_builtin_triangle_standard_library:compile_adjacency_callback",
        "selected_constructor_source_paths": [
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_builtin_triangle_standard_library.py",
        ],
    },
    "92697debe1e25227ec770b4d339c7cd248b16b7185612516841f3986a208ea30": {
        "alias": "builtin_triangle_count",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.count.v1",
        "compile_entrypoint": "rtdsl.v4_triangle_standard_library:compile_count_callback",
        "selected_constructor_source_paths": [
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_triangle_standard_library.py",
        ],
    },
    "c126a788b5e451fc0d76b4c48610bb2e6d6dbbf22fdb0b1c656deac97babc671": {
        "alias": "builtin_triangle_keyed",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.keyed.v1",
        "compile_entrypoint": "rtdsl.v4_triangle_standard_library:compile_keyed_callback",
        "selected_constructor_source_paths": [
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_triangle_standard_library.py",
        ],
    },
    "eeb2427e72a1f6b9f242adbf588d89e40616f1176c5bef60705ec716fcd06690": {
        "alias": "custom_aabb_box_relation",
        "callback_authority_id": "goal5789-a2.callback.custom_aabb.closed_relation.v1",
        "compile_entrypoint": "rtdsl.v4_box_relation_callback:compile_callback",
        "selected_constructor_source_paths": [
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_box_relation_callback.py",
        ],
    },
    "c3a17d90e2c8895f6ec14b0c07bafdc734d7ec233b3397bdc99fd478b9941c26": {
        "alias": "custom_aabb_spatial_candidate",
        "callback_authority_id": "goal5789-a2.callback.custom_aabb.spatial_candidate.v1",
        "compile_entrypoint": "rtdsl.v4_spatial_candidate_callback:compile_callback",
        "selected_constructor_source_paths": [
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_spatial_candidate_callback.py",
        ],
    },
}

EXPECTED_ADMITTED_BINDINGS = [
    {
        "semantic_contract_id": "particle.closest_face_projection.v1",
        "physical_encoding_id": "builtin_triangle.closest_face_projection.v1",
        "authority_program_sha256": "371de8d1816ddb8dbce78db9eb160f08cce3d595784509d5c6400e51b50ad476",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.adjacency.v1",
        "consumer_source_witnesses": [
            {
                "source_path": "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py",
                "source_sha256": "e2d26dd9a67025066ca77d1c57f358c34a8e4446a679b32f772a228ee52712a4",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": ["compile_standard_builtin_triangle_program"],
            },
            {
                "source_path": "src/rtdsl/v4_builtin_triangle_standard_library.py",
                "source_sha256": "71392af802dc5b32a94ed162a79052fa2ac8097e2231bba719eb51dcb0de5868",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": [
                    "def compile_standard_builtin_triangle_program",
                    "compile_adjacency_callback",
                ],
            },
        ],
    },
    {
        "semantic_contract_id": "triangle.rt2a1.weighted_count.v1",
        "physical_encoding_id": "builtin_triangle.weighted_count.v1",
        "authority_program_sha256": "92697debe1e25227ec770b4d339c7cd248b16b7185612516841f3986a208ea30",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.count.v1",
        "consumer_source_witnesses": [
            {
                "source_path": "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
                "source_sha256": "8ab4f4ad6c5913483633b06e70035a26637bc2b2a0589ce470623504d86e6210",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": ["compile_count_callback"],
            }
        ],
    },
    {
        "semantic_contract_id": "librts.inclusive_aabb_relation.v1",
        "physical_encoding_id": "custom_aabb.inclusive_relation.v1",
        "authority_program_sha256": "eeb2427e72a1f6b9f242adbf588d89e40616f1176c5bef60705ec716fcd06690",
        "callback_authority_id": "goal5789-a2.callback.custom_aabb.closed_relation.v1",
        "consumer_source_witnesses": [
            {
                "source_path": "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
                "source_sha256": "2952d38b341525d5b529a4391949df5b1ab59cd463c752f4da4df0823e40b987",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": [
                    "from rtdsl.v4_box_relation_callback import",
                    "compile_callback()",
                ],
            }
        ],
    },
    {
        "semantic_contract_id": "rtxrmq.leftmost_argmin.v1",
        "physical_encoding_id": "builtin_triangle.rtxrmq_leftmost.v1",
        "authority_program_sha256": "371de8d1816ddb8dbce78db9eb160f08cce3d595784509d5c6400e51b50ad476",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.adjacency.v1",
        "consumer_source_witnesses": [
            {
                "source_path": "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py",
                "source_sha256": "0823fdf32e0ade592eebc577b1f43d5c81e4fb1134934f353bbd3e3586a3b0b1",
                "source_root": "goal5789_heldout_certificate_source_pin",
                "required_tokens": ["compile_standard_builtin_triangle_program"],
            },
            {
                "source_path": "src/rtdsl/v4_builtin_triangle_standard_library.py",
                "source_sha256": "71392af802dc5b32a94ed162a79052fa2ac8097e2231bba719eb51dcb0de5868",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": [
                    "def compile_standard_builtin_triangle_program",
                    "compile_adjacency_callback",
                ],
            },
        ],
    },
]

EXPECTED_AUTHORITY_PATH = (
    "history/internal_docs/goal5789_a2_contract_evidence_20260821/"
    "CALLBACK_IR_AUTHORITY.json"
)
EXPECTED_PIN_PATH = (
    "history/internal_docs/goal5789_a2_contract_evidence_20260821/"
    "CALLBACK_IR_AUTHORITY_PIN.json"
)
EXPECTED_MATERIALIZER_PATH = "scripts/goal5789_a2_materialize_callback_ir_authority.py"
EXPECTED_SOURCE_IDENTITY = {
    "path": "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/EXECUTION_SOURCE.tar.gz",
    "size_bytes": 10_836_249,
    "file_sha256": "75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41",
}
EXPECTED_EVIDENCE_IDENTITY = {
    "path": "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/GOAL5785_EVIDENCE.tar.gz",
    "size_bytes": 28_674_437,
    "file_sha256": "2b6d808f566886b74469bbe4cf32fc6d426d2a91858237a7e939883f9b89394a",
}
EXPECTED_CONTROLLING_RESULT_IDENTITY = {
    "path": "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816.json",
    "size_bytes": 4_963,
    "file_sha256": "7f5cd38e625fa62233adfbb9df1f6aa56ebb050999b3154c1604bbc25f4e9064",
}
EXPECTED_EXECUTION_LEAF_MANIFEST_IDENTITY = {
    "member_path": "EXECUTION/FORMAL_NUMBA_LEAF_CACHE_MANIFEST.json",
    "file_sha256": "ecafcfb25190a785ae2cfe704dcb6bc75b137180d23bab4867c1cd40f45ad390",
    "size_bytes": 5_573,
    "entry_count": 26,
    "entries_sha256": "694835a8e5d07afbb935709d424fc9c8abc1afa88c8a1522dbb3859d40594aed",
}
EXPECTED_HELDOUT_SOURCE_CERTIFICATE_IDENTITY = {
    "path": "history/internal_docs/goal5789_contract_evidence_20260816/HELD_OUT_RTXRMQ_CERTIFICATE.json",
    "size_bytes": 9_408,
    "file_sha256": "87af6c6357af6165fe51f4c59be19d7b35340a2325c940f2c06a37afa3852fd3",
    "certificate_sha256": "dcb302c2992029135767fb3d12e0de12f3b30ba491af93d4f5e0d534d0253d38",
}
EXPECTED_CALLBACK_AUTHORITY_CLAIM_BOUNDARY = {
    "source_backed_callback_ir_authority": True,
    "executed_leaf_identity_crossbound": True,
    "controlling_result_source_evidence_crossbound": True,
    "execution_evidence_embeds_exact_source_archive": True,
    "selected_constructor_sources_are_not_claimed_as_complete_import_closure": True,
    "consumer_callsites_exact_hash_and_token_bound": True,
    "callback_authority_bound_inventory_scope": (
        "six_of_fifteen_inventory_rows_plus_legacy_rtxrmq_replay"
    ),
    "authority_producer_is_tcb": True,
    "independently_implemented_product_verifier_claimed": False,
    "jointly_wrong_authorities_detected": False,
    "semantic_soundness_claimed": False,
    "execution_authorized": False,
}
EXPECTED_RESULT_BOUNDARY = (
    "reference-admission replay with exact source-backed Callback-IR authority binding; "
    "authority producers and external authority roots remain TCB; no executable authority, "
    "soundness, completeness, or jointly-wrong-authority detection is claimed"
)
EXPECTED_PREDECESSOR_MANIFEST = {
    "path": "history/internal_docs/goal5789_delivery_manifest_20260816.json",
    "size_bytes": 13_176,
    "file_sha256": "523c95139d24a84ad2ad02ff1e0bb3ee60fc87e540cdaca112c8b74870ef7667",
    "payload_count": 54,
    "payload_bytes": 22_224_751,
}
EXPECTED_TERMINAL_IDENTITY = {
    "path": "history/internal_docs/goal5789_a1_postreview_local_p1_role_effect_binding_terminal_20260821.json",
    "size_bytes": 7_647,
    "file_sha256": "8a2960140381d7564a36a67c7024f2554bafe379621eef844c3edab0157be7be",
    "terminal_sha256": "96d1107848d5a41cfe8016a9dcb056e6b7e85679b1a61c21669eb39449f7f862",
}
EXPECTED_WORK_AUTHORITY_IDENTITY = {
    "path": "history/internal_docs/goal5789_a2_callback_ir_authority_binding_work_authority_20260821.json",
    "size_bytes": 4_556,
    "file_sha256": "7631ca7486afcb5515f79e99de3c3bb4020328c95bafd3d8bfe94697c5da0c1a",
    "work_authority_sha256": "e18658e0ed000de310f6bc3797e938c498f58d2de2071d9d50494781c69b6f08",
}


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_identity(relative: str) -> dict[str, object]:
    path = ROOT / relative
    return {
        "path": relative,
        "size_bytes": path.stat().st_size,
        "file_sha256": _file_sha(path),
    }


def _validate_frozen_predecessor_and_work_roots() -> None:
    """Rehash the immutable predecessor packet roots without shared code."""

    manifest_identity = _file_identity(str(EXPECTED_PREDECESSOR_MANIFEST["path"]))
    expected_manifest_identity = {
        key: EXPECTED_PREDECESSOR_MANIFEST[key]
        for key in ("path", "size_bytes", "file_sha256")
    }
    if _canonical(manifest_identity) != _canonical(expected_manifest_identity):
        raise RuntimeError("frozen Goal5789 predecessor delivery manifest identity mismatch")
    manifest = _load(ROOT / str(EXPECTED_PREDECESSOR_MANIFEST["path"]))
    rows = manifest.get("payloads")
    if (
        manifest.get("schema") != "rtdl.goal5789.delivery_manifest.v1"
        or manifest.get("payload_count") != EXPECTED_PREDECESSOR_MANIFEST["payload_count"]
        or manifest.get("payload_bytes") != EXPECTED_PREDECESSOR_MANIFEST["payload_bytes"]
        or not isinstance(rows, list)
        or len(rows) != EXPECTED_PREDECESSOR_MANIFEST["payload_count"]
    ):
        raise RuntimeError("frozen Goal5789 predecessor delivery manifest content mismatch")
    seen: set[str] = set()
    total_bytes = 0
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {"path", "sha256", "bytes"}:
            raise RuntimeError("invalid predecessor delivery manifest row")
        relative = row["path"]
        size = row["bytes"]
        sha256 = row["sha256"]
        if (
            not isinstance(relative, str)
            or relative in seen
            or type(size) is not int
            or size < 0
            or not isinstance(sha256, str)
            or _SHA.fullmatch(sha256) is None
        ):
            raise RuntimeError("invalid or duplicate predecessor delivery manifest row")
        seen.add(relative)
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size != size or _file_sha(path) != sha256:
            raise RuntimeError(f"frozen Goal5789 predecessor payload mismatch: {relative}")
        total_bytes += size
    if total_bytes != EXPECTED_PREDECESSOR_MANIFEST["payload_bytes"]:
        raise RuntimeError("frozen Goal5789 predecessor payload byte total mismatch")

    terminal_identity = _file_identity(str(EXPECTED_TERMINAL_IDENTITY["path"]))
    expected_terminal_file = {
        key: EXPECTED_TERMINAL_IDENTITY[key]
        for key in ("path", "size_bytes", "file_sha256")
    }
    if _canonical(terminal_identity) != _canonical(expected_terminal_file):
        raise RuntimeError("controlling postreview P1 terminal identity mismatch")
    terminal = _load(ROOT / str(EXPECTED_TERMINAL_IDENTITY["path"]))
    _assert_seal(terminal, "terminal_sha256", "controlling postreview P1 terminal")
    if terminal.get("terminal_sha256") != EXPECTED_TERMINAL_IDENTITY["terminal_sha256"]:
        raise RuntimeError("controlling postreview P1 terminal seal identity mismatch")

    work_identity = _file_identity(str(EXPECTED_WORK_AUTHORITY_IDENTITY["path"]))
    expected_work_file = {
        key: EXPECTED_WORK_AUTHORITY_IDENTITY[key]
        for key in ("path", "size_bytes", "file_sha256")
    }
    if _canonical(work_identity) != _canonical(expected_work_file):
        raise RuntimeError("A2 owner work authority identity mismatch")
    work = _load(ROOT / str(EXPECTED_WORK_AUTHORITY_IDENTITY["path"]))
    _assert_seal(work, "work_authority_sha256", "A2 owner work authority")
    if work.get("work_authority_sha256") != EXPECTED_WORK_AUTHORITY_IDENTITY["work_authority_sha256"]:
        raise RuntimeError("A2 owner work authority seal identity mismatch")


def _pretty(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {path}")
    return value


def _without(value: Mapping[str, object], key: str) -> dict[str, object]:
    body = dict(value)
    body.pop(key, None)
    return body


def _assert_seal(value: Mapping[str, object], field: str, label: str) -> None:
    stored = value.get(field)
    if not isinstance(stored, str) or not _SHA.fullmatch(stored):
        raise RuntimeError(f"{label} seal is missing or malformed")
    if _digest(_without(value, field)) != stored:
        raise RuntimeError(f"{label} seal mismatch")


def _assert_successor_authority(
    predecessor: Mapping[str, object],
    successor: Mapping[str, object],
    callback_authority: Mapping[str, object],
    callback_pin: Mapping[str, object],
    callback_authority_path: Path,
    callback_pin_path: Path,
    *,
    label: str,
) -> None:
    _assert_seal(predecessor, "authority_sha256", f"{label} predecessor authority")
    _assert_seal(successor, "authority_sha256", f"{label} successor authority")
    expected_body = dict(predecessor)
    expected_body["schema"] = "rtdl.goal5789.compatibility_authority_bundle.v2"
    expected_body.pop("authority_sha256", None)
    binding = successor.get("callback_ir_authority_binding")
    if not isinstance(binding, Mapping):
        raise RuntimeError(f"{label} callback authority binding missing")
    _assert_seal(binding, "authority_sha256", f"{label} callback authority binding")
    expected_binding = {
        "schema": "rtdl.goal5789_a2.callback_ir_authority_binding.v1",
        "callback_authority_path": EXPECTED_AUTHORITY_PATH,
        "callback_authority_file_sha256": _file_sha(callback_authority_path),
        "callback_authority_sha256": callback_authority["authority_sha256"],
        "callback_authority_pin_path": EXPECTED_PIN_PATH,
        "callback_authority_pin_file_sha256": _file_sha(callback_pin_path),
        "callback_authority_pin_sha256": callback_pin["pin_sha256"],
    }
    if _canonical(_without(binding, "authority_sha256")) != _canonical(expected_binding):
        raise RuntimeError(f"{label} callback authority binding identity mismatch")
    expected_body["callback_ir_authority_binding"] = dict(binding)
    actual_body = _without(successor, "authority_sha256")
    if _canonical(actual_body) != _canonical(expected_body):
        raise RuntimeError(f"{label} successor authority drift outside the A2 binding")


def _result_projection(result: Mapping[str, object]) -> dict[str, object]:
    return {
        "target_capable": result["target_capable"]["verdict"],
        "semantic_compatible": result["semantic_compatible"]["verdict"],
        "semantic_reasons": list(result["semantic_compatible"]["reasons"]),
        "instance_admissible": result["instance_admissible"]["verdict"],
        "canonical_resolution": result["canonical_resolution"]["verdict"],
        "reference_admission_complete": result["reference_admission_complete"],
        "performance": result["performance"]["verdict"],
    }


def _assert_result_identity_and_unchanged_axes(
    predecessor: Mapping[str, object],
    successor: Mapping[str, object],
    certificate: Mapping[str, object],
    authority: Mapping[str, object],
    callback_authority: Mapping[str, object],
    callback_pin: Mapping[str, object],
    *,
    label: str,
) -> None:
    _assert_seal(predecessor, "result_sha256", f"{label} predecessor result")
    _assert_seal(successor, "result_sha256", f"{label} successor result")
    expected_result_keys = {
        "schema",
        "result_sha256",
        "certificate_sha256",
        "authority_sha256",
        "callback_authority_sha256",
        "callback_authority_pin_sha256",
        "target_capable",
        "semantic_compatible",
        "instance_admissible",
        "canonical_resolution",
        "reference_admission_complete",
        "performance",
        "executable",
        "execution_authorized",
        "authority_boundary",
    }
    if set(successor) != expected_result_keys:
        raise RuntimeError(f"{label} successor result top-level schema mismatch")
    semantic = successor.get("semantic_compatible")
    if not isinstance(semantic, Mapping) or set(semantic) != {"verdict", "reasons"}:
        raise RuntimeError(f"{label} successor semantic result schema mismatch")
    if not isinstance(semantic["reasons"], list) or any(
        not isinstance(reason, str) for reason in semantic["reasons"]
    ):
        raise RuntimeError(f"{label} successor semantic reasons are malformed")
    if successor.get("schema") != "rtdl.goal5789.compatibility_check_result.v2":
        raise RuntimeError(f"{label} successor result schema mismatch")
    identities = {
        "certificate_sha256": certificate["certificate_sha256"],
        "authority_sha256": authority["authority_sha256"],
        "callback_authority_sha256": callback_authority["authority_sha256"],
        "callback_authority_pin_sha256": callback_pin["pin_sha256"],
    }
    for field, expected in identities.items():
        if successor.get(field) != expected:
            raise RuntimeError(f"{label} successor result identity mismatch: {field}")
    for field in (
        "target_capable",
        "instance_admissible",
        "canonical_resolution",
        "performance",
        "executable",
        "execution_authorized",
    ):
        if _canonical(successor.get(field)) != _canonical(predecessor.get(field)):
            raise RuntimeError(f"{label} non-callback result axis drift: {field}")
    if successor.get("authority_boundary") != EXPECTED_RESULT_BOUNDARY:
        raise RuntimeError(f"{label} authority boundary drift")


def _safe(name: str) -> None:
    posix = PurePosixPath(name)
    if (
        not name
        or "\\" in name
        or posix.is_absolute()
        or any(part in {"", ".", ".."} or ":" in part for part in posix.parts)
    ):
        raise RuntimeError(f"unsafe archive member: {name!r}")


def _statement_projection(statements: object) -> tuple[int, set[str]]:
    if not isinstance(statements, list):
        raise RuntimeError("Callback IR statement list required")
    iterations = 0
    effects: set[str] = set()
    for statement in statements:
        if not isinstance(statement, dict) or not isinstance(statement.get("kind"), str):
            raise RuntimeError("invalid Callback IR statement")
        kind = statement["kind"]
        if kind == "if":
            left_count, left_effects = _statement_projection(statement["then"])
            right_count, right_effects = _statement_projection(statement["else"])
            iterations += left_count + right_count
            effects.update(left_effects)
            effects.update(right_effects)
        elif kind == "static_for":
            trip_count = statement["trip_count"]
            if not isinstance(trip_count, int) or isinstance(trip_count, bool) or trip_count < 0:
                raise RuntimeError("invalid Callback IR static trip count")
            body_count, body_effects = _statement_projection(statement["body"])
            iterations += trip_count * max(1, 1 + body_count)
            effects.update(body_effects)
        elif kind == "return_effect":
            effects.add(statement["effect"]["kind"])
        elif kind not in {"let", "set", "return_value"}:
            raise RuntimeError(f"unknown Callback IR statement: {kind}")
    return iterations, effects


def _type_slots(
    value: object,
    records: Mapping[str, Mapping[str, object]],
    visiting: frozenset[str] = frozenset(),
) -> int:
    if not isinstance(value, Mapping) or not isinstance(value.get("kind"), str):
        raise RuntimeError("invalid Callback IR register type")
    kind = value["kind"]
    if kind == "scalar":
        scalar = value.get("scalar")
        if not isinstance(scalar, str):
            raise RuntimeError("invalid scalar register type")
        return 2 if scalar in {"i64", "u64", "f64"} else 1
    if kind == "vector":
        lanes, scalar = value.get("lanes"), value.get("scalar")
        if not isinstance(lanes, int) or isinstance(lanes, bool) or lanes <= 0 or not isinstance(scalar, str):
            raise RuntimeError("invalid vector register type")
        return lanes * (2 if scalar == "f64" else 1)
    if kind == "tuple":
        items = value.get("items")
        if not isinstance(items, list):
            raise RuntimeError("invalid tuple register type")
        return sum(_type_slots(item, records, visiting) for item in items)
    if kind == "record":
        name = value.get("name")
        if not isinstance(name, str) or name in visiting or name not in records:
            raise RuntimeError("recursive or missing Callback IR record")
        fields = records[name].get("fields")
        if not isinstance(fields, list):
            raise RuntimeError("invalid Callback IR record fields")
        total = 0
        for field in fields:
            if not isinstance(field, Mapping) or set(field) != {"name", "type"}:
                raise RuntimeError("invalid Callback IR record field")
            total += _type_slots(field["type"], records, visiting | {name})
        return total
    raise RuntimeError(f"non-register Callback IR type: {kind}")


def _walk_expressions(value: object):
    if isinstance(value, Mapping):
        if isinstance(value.get("opcode"), str):
            yield value
        for nested in value.values():
            yield from _walk_expressions(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_expressions(nested)


def _resource_projection(program: Mapping[str, object]) -> tuple[int, int, int]:
    records_value, manifest, functions = program.get("records"), program.get("manifest"), program.get("functions")
    if not isinstance(records_value, list) or not isinstance(manifest, Mapping) or not isinstance(functions, list):
        raise RuntimeError("Callback IR resource inputs missing")
    records: dict[str, Mapping[str, object]] = {}
    for record in records_value:
        if not isinstance(record, Mapping) or set(record) != {"name", "purpose", "fields"}:
            raise RuntimeError("invalid Callback IR record")
        name = record.get("name")
        if not isinstance(name, str) or name in records:
            raise RuntimeError("invalid or duplicate Callback IR record")
        records[name] = record
    payload_name = manifest.get("payload_record")
    if not isinstance(payload_name, str) or payload_name not in records or records[payload_name].get("purpose") != "payload":
        raise RuntimeError("Callback IR payload record mismatch")
    payload_slots = _type_slots({"kind": "record", "name": payload_name}, records)
    attribute_types = manifest.get("attribute_types")
    if not isinstance(attribute_types, list):
        raise RuntimeError("Callback IR attribute types missing")
    attribute_slots = sum(_type_slots(item, records) for item in attribute_types)
    names: set[str] = set()
    helpers: set[str] = set()
    rows: list[Mapping[str, object]] = []
    for function in functions:
        if not isinstance(function, Mapping) or not isinstance(function.get("name"), str):
            raise RuntimeError("invalid Callback IR function")
        name = function["name"]
        if name in names:
            raise RuntimeError("duplicate Callback IR function")
        names.add(name)
        if function.get("role") is None:
            helpers.add(name)
        rows.append(function)
    graph = {name: set() for name in names}
    for function in rows:
        source = str(function["name"])
        for expression in _walk_expressions(function.get("body")):
            if expression.get("opcode") != "helper_call":
                continue
            attributes = expression.get("attributes")
            target = attributes.get("name") if isinstance(attributes, Mapping) else None
            if not isinstance(target, str) or target not in helpers:
                raise RuntimeError("unknown Callback IR helper call")
            graph[source].add(target)
    visiting: set[str] = set()
    memo: dict[str, int] = {}
    def depth(name: str) -> int:
        if name in visiting:
            raise RuntimeError("recursive Callback IR helper graph")
        if name in memo:
            return memo[name]
        visiting.add(name)
        value = 0 if not graph[name] else 1 + max(depth(target) for target in graph[name])
        visiting.remove(name); memo[name] = value
        return value
    return payload_slots, attribute_slots, max((depth(name) for name in graph), default=0)


def _program_projection(program_sha: str, row: Mapping[str, object]) -> dict[str, object]:
    program = row["callback_program"]
    if not isinstance(program, dict) or _digest(program) != program_sha or row["callback_program_sha256"] != program_sha:
        raise RuntimeError(f"program digest mismatch: {program_sha}")
    if hashlib.sha256(program["normalized_source"].encode("utf-8")).hexdigest() != program["source_sha256"]:
        raise RuntimeError(f"normalized source digest mismatch: {program_sha}")
    ir_body = dict(program)
    ir_body.pop("normalized_source")
    ir_body.pop("source_sha256")
    roles = []
    effect_rows = []
    total_iterations = 0
    for function in program["functions"]:
        count, effects = _statement_projection(function["body"])
        total_iterations += count
        sorted_effects = sorted(effects)
        effect_rows.append([function["name"], sorted_effects])
        if function["role"] is not None:
            roles.append({"role": function["role"], "effects": sorted_effects})
    summary = row["verified_summary"]
    payload_slots, attribute_slots, helper_depth = _resource_projection(program)
    projection = {
        "callback_authority_id": row["callback_authority_id"],
        "authority_program_sha256": program_sha,
        "ir_sha256": _digest(ir_body),
        "effect_digest": _digest(effect_rows),
        "roles": roles,
        "payload_u32_slots": payload_slots,
        "attribute_u32_slots": attribute_slots,
        "trace_depth": program["manifest"]["resources"]["max_trace_depth"],
        "callable_depth": program["manifest"]["resources"]["max_callable_depth"],
        "total_static_iterations": total_iterations,
        "helper_call_depth": helper_depth,
    }
    if _canonical(projection) != _canonical(row["callback_contract"]):
        raise RuntimeError(f"callback projection mismatch: {program_sha}")
    expected_summary = {
        "ir_sha256": projection["ir_sha256"],
        "effect_digest": projection["effect_digest"],
        "payload_u32_slots": payload_slots,
        "attribute_u32_slots": attribute_slots,
        "total_static_iterations": total_iterations,
        "helper_call_depth": helper_depth,
    }
    if _canonical(summary) != _canonical(expected_summary):
        raise RuntimeError(f"verified summary mismatch: {program_sha}")
    return projection


def _archive_member_map(path: Path) -> tuple[tarfile.TarFile, dict[str, tarfile.TarInfo]]:
    handle = tarfile.open(path, "r:gz")
    members: dict[str, tarfile.TarInfo] = {}
    for member in handle.getmembers():
        _safe(member.name)
        if member.name in members:
            handle.close()
            raise RuntimeError(f"duplicate archive member: {member.name}")
        members[member.name] = member
    return handle, members


def recount(a2_dir: Path = A2) -> dict[str, object]:
    _validate_frozen_predecessor_and_work_roots()
    callback_authority_path = a2_dir / "CALLBACK_IR_AUTHORITY.json"
    callback_pin_path = a2_dir / "CALLBACK_IR_AUTHORITY_PIN.json"
    callback_authority = _load(callback_authority_path)
    callback_pin = _load(callback_pin_path)
    if callback_authority.get("schema") != "rtdl.goal5789_a2.callback_ir_authority.v1":
        raise RuntimeError("callback authority schema mismatch")
    if callback_pin.get("schema") != "rtdl.goal5789_a2.callback_ir_authority_pin.v1":
        raise RuntimeError("callback authority pin schema mismatch")
    _assert_seal(callback_authority, "authority_sha256", "callback authority")
    _assert_seal(callback_pin, "pin_sha256", "callback authority pin")
    expected_authority_keys = {
        "schema",
        "authority_sha256",
        "source_archive",
        "execution_evidence_archive",
        "controlling_result",
        "execution_leaf_manifest",
        "selected_constructor_source_manifest",
        "consumer_source_manifest",
        "consumer_source_authority_roots",
        "programs",
        "admitted_bindings",
        "claim_boundary",
    }
    if set(callback_authority) != expected_authority_keys:
        raise RuntimeError("callback authority top-level schema mismatch")
    if _canonical(callback_authority.get("claim_boundary")) != _canonical(
        EXPECTED_CALLBACK_AUTHORITY_CLAIM_BOUNDARY
    ):
        raise RuntimeError("callback authority claim boundary is not exact")
    expected_pin_keys = {
        "schema",
        "pin_sha256",
        "callback_authority",
        "source_archive",
        "execution_evidence_archive",
        "controlling_result",
        "materializer",
        "authorization",
    }
    if set(callback_pin) != expected_pin_keys:
        raise RuntimeError("callback authority pin top-level schema mismatch")
    expected_pin_authority = {
        "path": EXPECTED_AUTHORITY_PATH,
        "size_bytes": callback_authority_path.stat().st_size,
        "file_sha256": _file_sha(callback_authority_path),
        "authority_sha256": callback_authority["authority_sha256"],
    }
    if _canonical(callback_pin.get("callback_authority")) != _canonical(expected_pin_authority):
        raise RuntimeError("callback authority file pin mismatch")
    if _canonical(callback_authority.get("source_archive")) != _canonical(EXPECTED_SOURCE_IDENTITY):
        raise RuntimeError("callback authority source root is not the reviewed Goal5785 source")
    if _canonical(callback_authority.get("execution_evidence_archive")) != _canonical(EXPECTED_EVIDENCE_IDENTITY):
        raise RuntimeError("callback authority evidence root is not the reviewed Goal5785 evidence")
    if _canonical(callback_authority.get("controlling_result")) != _canonical(EXPECTED_CONTROLLING_RESULT_IDENTITY):
        raise RuntimeError("callback authority result root is not the reviewed Goal5785 result")
    for field, expected in (
        ("source_archive", EXPECTED_SOURCE_IDENTITY),
        ("execution_evidence_archive", EXPECTED_EVIDENCE_IDENTITY),
        ("controlling_result", EXPECTED_CONTROLLING_RESULT_IDENTITY),
    ):
        if _canonical(callback_pin.get(field)) != _canonical(expected):
            raise RuntimeError(f"callback authority pin root mismatch: {field}")
    expected_materializer = {
        "path": EXPECTED_MATERIALIZER_PATH,
        "file_sha256": _file_sha(ROOT / EXPECTED_MATERIALIZER_PATH),
    }
    if _canonical(callback_pin.get("materializer")) != _canonical(expected_materializer):
        raise RuntimeError("callback authority materializer identity mismatch")
    expected_authorization_keys = {
        "authorizes_goal5793",
        "authorizes_entropy_draw",
        "authorizes_candidate_selection",
        "authorizes_product_change",
        "authorizes_gpu",
        "authorizes_home",
        "authorizes_pod",
        "authorizes_worker",
        "authorizes_performance_timing",
        "authorizes_publication",
    }
    authorization = callback_pin.get("authorization")
    if (
        not isinstance(authorization, Mapping)
        or set(authorization) != expected_authorization_keys
        or any(value is not False for value in authorization.values())
    ):
        raise RuntimeError("callback authority pin authorization is not exact all-false")

    source_identity = callback_authority["source_archive"]
    evidence_identity = callback_authority["execution_evidence_archive"]
    result_identity = callback_authority["controlling_result"]
    source_path = ROOT / source_identity["path"]
    evidence_path = ROOT / evidence_identity["path"]
    result_path = ROOT / result_identity["path"]
    for path, identity in ((source_path, source_identity), (evidence_path, evidence_identity), (result_path, result_identity)):
        if path.stat().st_size != identity["size_bytes"] or _file_sha(path) != identity["file_sha256"]:
            raise RuntimeError(f"frozen provenance identity mismatch: {path}")
    controlling_result = _load(result_path)
    if controlling_result["run_goal_id"] != 5785 or controlling_result["lineage"]["execution_source_sha256"] != source_identity["file_sha256"] or controlling_result["evidence"]["archive_sha256"] != evidence_identity["file_sha256"]:
        raise RuntimeError("controlling result provenance crossbind mismatch")

    source_tar, source_members = _archive_member_map(source_path)
    consumer_source_payloads: dict[str, bytes] = {}
    try:
        for relative, expected_sha in callback_authority["selected_constructor_source_manifest"].items():
            member = source_members.get(relative)
            if member is None or not member.isfile():
                raise RuntimeError(f"source member missing: {relative}")
            payload = source_tar.extractfile(member).read()
            if hashlib.sha256(payload).hexdigest() != expected_sha:
                raise RuntimeError(f"source member hash mismatch: {relative}")
        for relative, expected_sha in callback_authority["consumer_source_manifest"].items():
            member = source_members.get(relative)
            if member is not None and member.isfile():
                payload = source_tar.extractfile(member).read()
            else:
                payload = (ROOT / relative).read_bytes()
            if hashlib.sha256(payload).hexdigest() != expected_sha:
                raise RuntimeError(f"consumer source identity mismatch: {relative}")
            consumer_source_payloads[relative] = payload
    finally:
        source_tar.close()

    consumer_roots = callback_authority["consumer_source_authority_roots"]
    if set(consumer_roots) != {"goal5789_heldout_certificate"}:
        raise RuntimeError("consumer source authority roots schema mismatch")
    heldout_identity = consumer_roots["goal5789_heldout_certificate"]
    if _canonical(heldout_identity) != _canonical(EXPECTED_HELDOUT_SOURCE_CERTIFICATE_IDENTITY):
        raise RuntimeError("held-out source-pin certificate is not the reviewed frozen identity")
    heldout_path = ROOT / heldout_identity["path"]
    if (
        heldout_path.stat().st_size != heldout_identity["size_bytes"]
        or _file_sha(heldout_path) != heldout_identity["file_sha256"]
    ):
        raise RuntimeError("held-out source-pin certificate identity mismatch")
    heldout_certificate = _load(heldout_path)
    if (
        _digest(_without(heldout_certificate, "certificate_sha256"))
        != heldout_identity["certificate_sha256"]
        or heldout_certificate["certificate_sha256"] != heldout_identity["certificate_sha256"]
    ):
        raise RuntimeError("held-out source-pin certificate seal mismatch")

    evidence_tar, evidence_members = _archive_member_map(evidence_path)
    try:
        embedded = evidence_tar.extractfile(evidence_members["EXECUTION/EXECUTION_SOURCE.tar.gz"]).read()
        if len(embedded) != source_identity["size_bytes"] or hashlib.sha256(embedded).hexdigest() != source_identity["file_sha256"]:
            raise RuntimeError("embedded execution source mismatch")
        manifest_identity = callback_authority["execution_leaf_manifest"]
        if _canonical(manifest_identity) != _canonical(
            EXPECTED_EXECUTION_LEAF_MANIFEST_IDENTITY
        ):
            raise RuntimeError("execution leaf manifest authority identity mismatch")
        manifest_payload = evidence_tar.extractfile(evidence_members[manifest_identity["member_path"]]).read()
        if len(manifest_payload) != manifest_identity["size_bytes"] or hashlib.sha256(manifest_payload).hexdigest() != manifest_identity["file_sha256"]:
            raise RuntimeError("leaf manifest identity mismatch")
        leaf_manifest = json.loads(manifest_payload)
        if leaf_manifest["entry_count"] != 26 or leaf_manifest["entries_sha256"] != _digest(leaf_manifest["entries"]):
            raise RuntimeError("leaf manifest content mismatch")
        manifest_rows = {row["key_sha256"]: row for row in leaf_manifest["entries"]}
        projections: dict[str, dict[str, object]] = {}
        seen_leaf_keys: set[str] = set()
        programs = callback_authority.get("programs")
        if not isinstance(programs, Mapping) or set(programs) != EXPECTED_PROGRAM_SHA256S:
            raise RuntimeError("Callback program universe is not the reviewed exact five-program set")
        for program_sha, row in programs.items():
            actual_metadata = {
                key: row.get(key)
                for key in (
                    "alias",
                    "callback_authority_id",
                    "compile_entrypoint",
                    "selected_constructor_source_paths",
                )
            }
            if _canonical(actual_metadata) != _canonical(
                EXPECTED_PROGRAM_METADATA_BY_SHA256[program_sha]
            ):
                raise RuntimeError(f"Callback program producer metadata mismatch: {program_sha}")
            projection = _program_projection(program_sha, row)
            projections[program_sha] = projection
            roles = []
            for leaf in row["executed_leaf_evidence"]:
                key_sha = leaf["key_sha256"]
                if key_sha in seen_leaf_keys or key_sha not in manifest_rows:
                    raise RuntimeError("leaf evidence duplicate or absent from manifest")
                seen_leaf_keys.add(key_sha)
                manifest_row = manifest_rows[key_sha]
                member = evidence_members[leaf["member_path"]]
                payload = evidence_tar.extractfile(member).read()
                if (
                    len(payload) != leaf["size_bytes"]
                    or hashlib.sha256(payload).hexdigest() != leaf["file_sha256"]
                    or leaf["file_sha256"] != manifest_row["artifact_json_sha256"]
                    or leaf["size_bytes"] != manifest_row["artifact_json_size_bytes"]
                ):
                    raise RuntimeError("leaf artifact identity mismatch")
                artifact = json.loads(payload)
                key = artifact["key"]
                if (
                    artifact.get("key_sha256") != key_sha
                    or _digest(key) != key_sha
                    or key["callback_ir_sha256"] != projection["ir_sha256"]
                    or key["callback_effect_digest"] != projection["effect_digest"]
                    or key["role"] != leaf["role"]
                    or artifact["artifact"]["role"] != leaf["role"]
                    or artifact["artifact"]["ir_sha256"] != key["callback_ir_sha256"]
                    or hashlib.sha256(artifact["artifact"]["ptx"].encode("utf-8")).hexdigest()
                    != artifact["artifact"]["ptx_sha256"]
                ):
                    raise RuntimeError("leaf artifact callback binding mismatch")
                roles.append(leaf["role"])
            if sorted(roles) != sorted(item["role"] for item in projection["roles"]):
                raise RuntimeError("leaf role coverage mismatch")
        if len(projections) != 5 or seen_leaf_keys != set(manifest_rows):
            raise RuntimeError("five Callback programs do not partition the 26-leaf universe")
    finally:
        evidence_tar.close()

    bindings = callback_authority.get("admitted_bindings")
    if _canonical(bindings) != _canonical(EXPECTED_ADMITTED_BINDINGS):
        raise RuntimeError("admitted pair-to-program mapping differs from the independent reviewed map")
    binding_map = {
        (row["semantic_contract_id"], row["physical_encoding_id"]): row
        for row in bindings
    }
    if len(binding_map) != 4:
        raise RuntimeError("admitted callback binding count mismatch")
    heldout_source_pins = heldout_certificate["evidence_contract"]["source_pins"]
    for binding in binding_map.values():
        witnesses = binding.get("consumer_source_witnesses")
        if not isinstance(witnesses, list) or not witnesses:
            raise RuntimeError("admitted callback binding lacks consumer witness")
        for witness in witnesses:
            path = witness["source_path"]
            payload = consumer_source_payloads.get(path)
            if payload is None or hashlib.sha256(payload).hexdigest() != witness["source_sha256"]:
                raise RuntimeError("consumer source witness identity mismatch")
            if witness["source_root"] == "goal5789_heldout_certificate_source_pin":
                if heldout_source_pins.get(path) != witness["source_sha256"]:
                    raise RuntimeError("held-out certificate does not bind consumer source witness")
            elif witness["source_root"] != "goal5785_execution_source_archive":
                raise RuntimeError("unknown consumer source witness root")
            text = payload.decode("utf-8")
            tokens = witness["required_tokens"]
            if not isinstance(tokens, list) or not tokens or any(token not in text for token in tokens):
                raise RuntimeError("consumer source callsite token mismatch")

    old_authority = _load(OLD / "AUTHORITY_BUNDLE.json")
    new_authority = _load(a2_dir / "AUTHORITY_BUNDLE.json")
    _assert_successor_authority(
        old_authority,
        new_authority,
        callback_authority,
        callback_pin,
        callback_authority_path,
        callback_pin_path,
        label="inventory",
    )
    old_held_authority = _load(OLD / "HELD_OUT_AUTHORITY_BUNDLE.json")
    new_held_authority = _load(a2_dir / "HELD_OUT_AUTHORITY_BUNDLE.json")
    _assert_successor_authority(
        old_held_authority,
        new_held_authority,
        callback_authority,
        callback_pin,
        callback_authority_path,
        callback_pin_path,
        label="held-out RTXRMQ",
    )

    old_inventory = _load(OLD / "BOUNDED_INVENTORY.json")
    new_inventory = _load(a2_dir / "BOUNDED_INVENTORY.json")
    _assert_seal(new_inventory, "inventory_sha256", "A2 bounded inventory")
    if new_inventory.get("schema") != "rtdl.goal5789_a2.bounded_inventory.v1":
        raise RuntimeError("A2 bounded inventory schema mismatch")
    counts = {"COMPATIBLE_FOR_DECLARED_DOMAIN": 0, "UNKNOWN": 0, "INCOMPATIBLE": 0}
    rows = []
    for old_row, new_row in zip(old_inventory["inventory"], new_inventory["inventory"], strict=True):
        unit_id = old_row["unit_id"]
        if new_row["unit_id"] != unit_id:
            raise RuntimeError("inventory order drift")
        old_certificate = _load(OLD / "certificates" / f"{unit_id}.json")
        new_certificate = _load(a2_dir / "certificates" / f"{unit_id}.json")
        old_result = _load(OLD / "results" / f"{unit_id}.json")
        new_result = _load(a2_dir / "results" / f"{unit_id}.json")
        old_body = {key: value for key, value in old_certificate.items() if key not in {"schema", "certificate_sha256", "callback_contract"}}
        new_body = {key: value for key, value in new_certificate.items() if key not in {"schema", "certificate_sha256", "callback_contract"}}
        if old_body != new_body:
            raise RuntimeError(f"certificate non-callback drift: {unit_id}")
        if new_certificate.get("schema") != "rtdl.goal5789.semantic_physical_certificate.v2":
            raise RuntimeError(f"certificate successor schema mismatch: {unit_id}")
        if _digest(_without(new_certificate, "certificate_sha256")) != new_certificate["certificate_sha256"]:
            raise RuntimeError(f"certificate seal mismatch: {unit_id}")
        _assert_result_identity_and_unchanged_axes(
            old_result,
            new_result,
            new_certificate,
            new_authority,
            callback_authority,
            callback_pin,
            label=unit_id,
        )
        pair = (new_certificate["semantic_request"]["contract_id"], new_certificate["physical_encoding"]["encoding_id"])
        admitted = binding_map.get(pair)
        old_verdict = old_result["semantic_compatible"]["verdict"]
        new_verdict = new_result["semantic_compatible"]["verdict"]
        if old_verdict == "COMPATIBLE_FOR_DECLARED_DOMAIN":
            if admitted is None or new_certificate["callback_contract"] != projections[admitted["authority_program_sha256"]]:
                raise RuntimeError(f"compatible row lacks exact callback binding: {unit_id}")
            if new_verdict != old_verdict or new_result["reference_admission_complete"] is not True:
                raise RuntimeError(f"compatible row successor disposition drift: {unit_id}")
            if new_result["semantic_compatible"]["reasons"] != old_result["semantic_compatible"]["reasons"]:
                raise RuntimeError(f"compatible row semantic reasons drift: {unit_id}")
        else:
            if admitted is not None or new_certificate["callback_contract"] is not None:
                raise RuntimeError(f"unknown row gained callback admission: {unit_id}")
            if new_verdict != "UNKNOWN" or "callback_authority_not_established_for_semantic_physical_pair" not in new_result["semantic_compatible"]["reasons"]:
                raise RuntimeError(f"unknown row successor reason drift: {unit_id}")
            if new_result["reference_admission_complete"] is not False:
                raise RuntimeError(f"unknown row unexpectedly completed admission: {unit_id}")
            if not set(old_result["semantic_compatible"]["reasons"]).issubset(
                set(new_result["semantic_compatible"]["reasons"])
            ):
                raise RuntimeError(f"unknown row lost predecessor semantic reason: {unit_id}")
        expected_inventory_row = {
            "unit_id": unit_id,
            "contract_id": new_certificate["semantic_request"]["contract_id"],
            "encoding_id": new_certificate["physical_encoding"]["encoding_id"],
            "callback_authority_id": (
                None
                if new_certificate["callback_contract"] is None
                else new_certificate["callback_contract"]["callback_authority_id"]
            ),
            **_result_projection(new_result),
            "semantic_authority_present": old_row["semantic_authority_present"],
            "predecessor_semantic_compatible": old_verdict,
        }
        if _canonical(new_row) != _canonical(expected_inventory_row):
            raise RuntimeError(f"bounded inventory row is not an exact certificate/result projection: {unit_id}")
        counts[new_verdict] += 1
        rows.append({
            "unit_id": unit_id,
            "predecessor": old_verdict,
            "successor": new_verdict,
            "callback_bound": admitted is not None,
        })
    if counts != {"COMPATIBLE_FOR_DECLARED_DOMAIN": 6, "UNKNOWN": 9, "INCOMPATIBLE": 0}:
        raise RuntimeError(f"unexpected successor count vector: {counts}")
    callback_bound_count = sum(row["callback_bound"] is True for row in rows)
    callback_unbound_count = len(rows) - callback_bound_count
    if callback_bound_count != 6 or callback_unbound_count != 9:
        raise RuntimeError("callback authority coverage must be reported as exact 6/15 bound, 9/15 unbound")

    old_held_certificate = _load(OLD / "HELD_OUT_RTXRMQ_CERTIFICATE.json")
    new_held_certificate = _load(a2_dir / "HELD_OUT_RTXRMQ_CERTIFICATE.json")
    old_held_body = {
        key: value
        for key, value in old_held_certificate.items()
        if key not in {"schema", "certificate_sha256", "callback_contract"}
    }
    new_held_body = {
        key: value
        for key, value in new_held_certificate.items()
        if key not in {"schema", "certificate_sha256", "callback_contract"}
    }
    if _canonical(old_held_body) != _canonical(new_held_body):
        raise RuntimeError("held-out RTXRMQ certificate drifted outside the A2 callback migration")
    if new_held_certificate.get("schema") != "rtdl.goal5789.semantic_physical_certificate.v2":
        raise RuntimeError("held-out RTXRMQ certificate successor schema mismatch")
    _assert_seal(old_held_certificate, "certificate_sha256", "held-out predecessor certificate")
    _assert_seal(new_held_certificate, "certificate_sha256", "held-out successor certificate")
    held_pair = (
        new_held_certificate["semantic_request"]["contract_id"],
        new_held_certificate["physical_encoding"]["encoding_id"],
    )
    expected_held_pair = (
        "rtxrmq.leftmost_argmin.v1",
        "builtin_triangle.rtxrmq_leftmost.v1",
    )
    if held_pair != expected_held_pair:
        raise RuntimeError("held-out RTXRMQ semantic/physical pair drift")
    held_binding = binding_map.get(held_pair)
    if (
        held_binding is None
        or held_binding["authority_program_sha256"]
        != "371de8d1816ddb8dbce78db9eb160f08cce3d595784509d5c6400e51b50ad476"
        or _canonical(new_held_certificate.get("callback_contract"))
        != _canonical(projections[held_binding["authority_program_sha256"]])
    ):
        raise RuntimeError("held-out RTXRMQ is not exactly bound to the reviewed adjacency program")
    old_held_result = _load(OLD / "HELD_OUT_RTXRMQ_RESULT.json")
    new_held_result = _load(a2_dir / "HELD_OUT_RTXRMQ_RESULT.json")
    _assert_result_identity_and_unchanged_axes(
        old_held_result,
        new_held_result,
        new_held_certificate,
        new_held_authority,
        callback_authority,
        callback_pin,
        label="held-out RTXRMQ",
    )
    if (
        old_held_result["semantic_compatible"]["verdict"]
        != "COMPATIBLE_FOR_DECLARED_DOMAIN"
        or new_held_result["semantic_compatible"]["verdict"]
        != "COMPATIBLE_FOR_DECLARED_DOMAIN"
        or new_held_result["semantic_compatible"]["reasons"]
        != old_held_result["semantic_compatible"]["reasons"]
        or new_held_result["reference_admission_complete"] is not True
    ):
        raise RuntimeError("held-out RTXRMQ successor is not an exact compatible no-special-case replay")

    expected_predecessor_summary = {
        "compatible_count": old_inventory["semantic_compatible_count"],
        "unknown_count": old_inventory["semantic_unknown_count"],
        "incompatible_count": old_inventory["semantic_incompatible_count"],
        "observation_is_immutable_and_not_replaced": True,
    }
    expected_successor_summary = {
        "compatible_count": counts["COMPATIBLE_FOR_DECLARED_DOMAIN"],
        "unknown_count": counts["UNKNOWN"],
        "incompatible_count": counts["INCOMPATIBLE"],
        "counts_were_not_forced": True,
        "callback_authority_bound_count": callback_bound_count,
        "callback_authority_unbound_count": callback_unbound_count,
        "callback_authority_coverage_denominator": len(rows),
    }
    expected_heldout_summary = {
        "predecessor_semantic_compatible": old_held_result["semantic_compatible"]["verdict"],
        "successor_semantic_compatible": new_held_result["semantic_compatible"]["verdict"],
        "legacy_held_out_name_is_not_checker_held_out_claim": True,
        "no_special_case_replay_only": True,
    }
    expected_claim_boundary = {
        "registered_catalog_only": True,
        "two_geometry_families_only": True,
        "callback_summary_source_backed_and_authority_bound_for_all_inventory_rows": False,
        "callback_summary_source_backed_and_authority_bound_for_compatible_rows": True,
        "unbound_unknown_callback_integrity_claimed": False,
        "callback_authority_bound_inventory_count": callback_bound_count,
        "callback_authority_unbound_inventory_count": callback_unbound_count,
        "callback_authority_inventory_denominator": len(rows),
        "authority_producer_is_tcb": True,
        "jointly_wrong_authorities_detected": False,
        "soundness_claimed": False,
        "completeness_claimed": False,
        "false_rejection_rate_claimed": False,
        "goal5793_authorized": False,
        "execution_authorized": False,
    }
    if _canonical(new_inventory.get("predecessor")) != _canonical(expected_predecessor_summary):
        raise RuntimeError("bounded inventory predecessor summary drift")
    if _canonical(new_inventory.get("successor")) != _canonical(expected_successor_summary):
        raise RuntimeError("bounded inventory successor summary drift")
    if _canonical(new_inventory.get("held_out_result")) != _canonical(expected_heldout_summary):
        raise RuntimeError("bounded inventory held-out result projection drift")
    if _canonical(new_inventory.get("claim_boundary")) != _canonical(expected_claim_boundary):
        raise RuntimeError("bounded inventory claim boundary drift")
    if set(new_inventory) != {
        "schema",
        "inventory_sha256",
        "predecessor",
        "successor",
        "inventory",
        "held_out_result",
        "claim_boundary",
    }:
        raise RuntimeError("bounded inventory top-level schema drift")

    predecessor_rows = []
    for old_row in old_inventory["inventory"]:
        unit_id = old_row["unit_id"]
        certificate_relative = (
            "history/internal_docs/goal5789_contract_evidence_20260816/"
            f"certificates/{unit_id}.json"
        )
        result_relative = (
            "history/internal_docs/goal5789_contract_evidence_20260816/"
            f"results/{unit_id}.json"
        )
        old_certificate = _load(ROOT / certificate_relative)
        old_result = _load(ROOT / result_relative)
        certificate_identity = _file_identity(certificate_relative)
        certificate_identity["certificate_sha256"] = old_certificate["certificate_sha256"]
        result_identity_row = _file_identity(result_relative)
        result_identity_row["result_sha256"] = old_result["result_sha256"]
        result_identity_row["semantic_compatible"] = old_result["semantic_compatible"]["verdict"]
        predecessor_rows.append(
            {
                "unit_id": unit_id,
                "certificate": certificate_identity,
                "result": result_identity_row,
            }
        )
    expected_lineage = {
        "schema": "rtdl.goal5789_a2.predecessor_lineage.v1",
        "predecessor_delivery_manifest": _file_identity(
            str(EXPECTED_PREDECESSOR_MANIFEST["path"])
        ),
        "predecessor_authority": _file_identity(
            "history/internal_docs/goal5789_contract_evidence_20260816/AUTHORITY_BUNDLE.json"
        ),
        "predecessor_inventory": _file_identity(
            "history/internal_docs/goal5789_contract_evidence_20260816/BOUNDED_INVENTORY.json"
        ),
        "predecessor_rows": predecessor_rows,
        "predecessor_held_out": {
            "authority": _file_identity(
                "history/internal_docs/goal5789_contract_evidence_20260816/HELD_OUT_AUTHORITY_BUNDLE.json"
            ),
            "certificate": _file_identity(
                "history/internal_docs/goal5789_contract_evidence_20260816/HELD_OUT_RTXRMQ_CERTIFICATE.json"
            ),
            "result": _file_identity(
                "history/internal_docs/goal5789_contract_evidence_20260816/HELD_OUT_RTXRMQ_RESULT.json"
            ),
        },
        "controlling_p1_terminal": _file_identity(
            "history/internal_docs/goal5789_a1_postreview_local_p1_role_effect_binding_terminal_20260821.json"
        ),
        "owner_work_authority": _file_identity(
            "history/internal_docs/goal5789_a2_callback_ir_authority_binding_work_authority_20260821.json"
        ),
        "predecessor_bytes_modified_count": 0,
        "predecessor_observation_replaced": False,
        "goal5793_authorized": False,
    }
    lineage = _load(a2_dir / "PREDECESSOR_LINEAGE.json")
    _assert_seal(lineage, "lineage_sha256", "A2 predecessor lineage")
    if _canonical(_without(lineage, "lineage_sha256")) != _canonical(expected_lineage):
        raise RuntimeError("A2 predecessor lineage is not the exact immutable predecessor projection")
    work_authority = _load(
        ROOT
        / "history/internal_docs/goal5789_a2_callback_ir_authority_binding_work_authority_20260821.json"
    )
    _assert_seal(work_authority, "work_authority_sha256", "A2 owner work authority")
    if (
        work_authority.get("schema")
        != "rtdl.goal5789_a2.callback_ir_authority_binding_work_authority.v1"
        or work_authority.get("status")
        != "AUTHORIZED_LOCAL_EVIDENCE_REPAIR_OPTION_A__GOAL5793_BLOCKED__NO_GPU_POD_PRODUCT_OR_TIMING"
    ):
        raise RuntimeError("A2 owner work authority scope drift")
    expected_work_authorization = {
        "authorizes_create_only_local_a2_artifacts": True,
        "authorizes_editing_new_a2_scripts_tests_and_docs": True,
        "authorizes_entropy_draw": False,
        "authorizes_external_reviewer_contact": False,
        "authorizes_goal5793": False,
        "authorizes_goal5793_candidate_selection": False,
        "authorizes_goal5793_execution": False,
        "authorizes_gpu": False,
        "authorizes_home": False,
        "authorizes_local_a2_evidence_repair": True,
        "authorizes_pod": False,
        "authorizes_prepare_owner_selected_external_review_packet": True,
        "authorizes_product_or_native_change": False,
        "authorizes_publication_or_submission": False,
        "authorizes_registered_timing": False,
        "authorizes_ssh": False,
        "authorizes_worker": False,
    }
    if _canonical(work_authority.get("authorization")) != _canonical(
        expected_work_authorization
    ):
        raise RuntimeError("A2 owner work authority authorization drift")

    result: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.independent_recount.v1",
        "recount_sha256": "",
        "status": "PASS__FROZEN_SOURCE_AND_EXECUTED_LEAF_BACKED_CALLBACK_AUTHORITY__FIVE_PROGRAMS_26_LEAVES__PREDECESSOR_AND_SUCCESSOR_6_9_0",
        "callback_authority": {
            "file_sha256": _file_sha(callback_authority_path),
            "authority_sha256": callback_authority["authority_sha256"],
            "program_count": len(projections),
            "executed_leaf_count": len(seen_leaf_keys),
            "admitted_binding_count": len(binding_map),
        },
        "predecessor_counts": {"compatible": 6, "unknown": 9, "incompatible": 0},
        "successor_counts": {"compatible": 6, "unknown": 9, "incompatible": 0},
        "callback_authority_coverage": {
            "bound_inventory_count": callback_bound_count,
            "unbound_inventory_count": callback_unbound_count,
            "inventory_denominator": len(rows),
            "all_inventory_rows_bound": False,
            "unbound_unknown_callback_integrity_claimed": False,
        },
        "rows": rows,
        "claim_boundary": {
            "authority_producer_is_tcb": True,
            "jointly_wrong_external_roots_detected": False,
            "semantic_soundness_claimed": False,
            "completeness_claimed": False,
            "false_rejection_rate_claimed": False,
            "all_inventory_callback_summaries_bound_claimed": False,
            "goal5793_authorized": False,
            "execution_authorized": False,
        },
        "authorization": {
            "authorizes_goal5793": False,
            "authorizes_entropy_draw": False,
            "authorizes_candidate_selection": False,
            "authorizes_product_change": False,
            "authorizes_gpu": False,
            "authorizes_home": False,
            "authorizes_pod": False,
            "authorizes_worker": False,
            "authorizes_performance_timing": False,
            "authorizes_publication": False,
        },
    }
    result["recount_sha256"] = _digest(_without(result, "recount_sha256"))
    return result


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError("A2 independent recount output is create-only")
    result = recount()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("xb") as handle:
        handle.write(_pretty(result))
    print(json.dumps({
        "file_sha256": _file_sha(OUTPUT),
        "recount_sha256": result["recount_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

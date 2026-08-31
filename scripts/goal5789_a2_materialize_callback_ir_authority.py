"""Materialize the Goal5789-A2 Callback-IR authority from frozen source.

The producer imports no Goal5789 evidence builder or compatibility checker.
It safely extracts the exact Goal5785 execution-source archive into a fresh
temporary directory, materializes five app-neutral Callback-IR programs
through their frozen product constructors, and preserves each complete
normalized program.  It also
cross-binds every role to already executed Goal5785 Numba leaf artifacts.

Both outputs are create-only.  Generating them grants no execution, Goal5793,
POD, performance, publication, or semantic-soundness authority.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile
from typing import Any, Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "history/internal_docs/goal5789_a2_contract_evidence_20260821"
AUTHORITY_OUTPUT = OUT_DIR / "CALLBACK_IR_AUTHORITY.json"
PIN_OUTPUT = OUT_DIR / "CALLBACK_IR_AUTHORITY_PIN.json"

SOURCE_ARCHIVE_REL = "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/EXECUTION_SOURCE.tar.gz"
SOURCE_ARCHIVE_SHA256 = "75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41"
SOURCE_ARCHIVE_BYTES = 10_836_249
EVIDENCE_ARCHIVE_REL = "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/GOAL5785_EVIDENCE.tar.gz"
EVIDENCE_ARCHIVE_SHA256 = "2b6d808f566886b74469bbe4cf32fc6d426d2a91858237a7e939883f9b89394a"
EVIDENCE_ARCHIVE_BYTES = 28_674_437
LEAF_MANIFEST_MEMBER = "EXECUTION/FORMAL_NUMBA_LEAF_CACHE_MANIFEST.json"
LEAF_MANIFEST_SHA256 = "ecafcfb25190a785ae2cfe704dcb6bc75b137180d23bab4867c1cd40f45ad390"
LEAF_MANIFEST_BYTES = 5_573
RESULT_REL = "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816.json"
RESULT_SHA256 = "7f5cd38e625fa62233adfbb9df1f6aa56ebb050999b3154c1604bbc25f4e9064"
RESULT_BYTES = 4_963
EMBEDDED_SOURCE_MEMBER = "EXECUTION/EXECUTION_SOURCE.tar.gz"

SELECTED_CONSTRUCTOR_SOURCE_PATHS = (
    "src/rtdsl/v4_callback_frontend.py",
    "src/rtdsl/v4_callback_ir.py",
    "src/rtdsl/v4_callback_abi.py",
    "src/rtdsl/v4_typed_physical_schema.py",
    "src/rtdsl/v4_builtin_triangle_standard_library.py",
    "src/rtdsl/v4_triangle_standard_library.py",
    "src/rtdsl/v4_triangle_reduction.py",
    "src/rtdsl/v4_box_relation_callback.py",
    "src/rtdsl/v4_spatial_candidate_callback.py",
)

HELD_OUT_CERTIFICATE_REL = "history/internal_docs/goal5789_contract_evidence_20260816/HELD_OUT_RTXRMQ_CERTIFICATE.json"
HELD_OUT_CERTIFICATE_SHA256 = "87af6c6357af6165fe51f4c59be19d7b35340a2325c940f2c06a37afa3852fd3"
HELD_OUT_CERTIFICATE_BYTES = 9_408

PROGRAM_SPECS = (
    {
        "alias": "builtin_triangle_adjacency",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.adjacency.v1",
        "module": "rtdsl.v4_builtin_triangle_standard_library",
        "function": "compile_adjacency_callback",
        "selected_constructor_source_paths": (
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_builtin_triangle_standard_library.py",
        ),
    },
    {
        "alias": "builtin_triangle_count",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.count.v1",
        "module": "rtdsl.v4_triangle_standard_library",
        "function": "compile_count_callback",
        "selected_constructor_source_paths": (
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_triangle_standard_library.py",
        ),
    },
    {
        "alias": "builtin_triangle_keyed",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.keyed.v1",
        "module": "rtdsl.v4_triangle_standard_library",
        "function": "compile_keyed_callback",
        "selected_constructor_source_paths": (
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_triangle_standard_library.py",
        ),
    },
    {
        "alias": "custom_aabb_box_relation",
        "callback_authority_id": "goal5789-a2.callback.custom_aabb.closed_relation.v1",
        "module": "rtdsl.v4_box_relation_callback",
        "function": "compile_callback",
        "selected_constructor_source_paths": (
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_box_relation_callback.py",
        ),
    },
    {
        "alias": "custom_aabb_spatial_candidate",
        "callback_authority_id": "goal5789-a2.callback.custom_aabb.spatial_candidate.v1",
        "module": "rtdsl.v4_spatial_candidate_callback",
        "function": "compile_callback",
        "selected_constructor_source_paths": (
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_spatial_candidate_callback.py",
        ),
    },
)

ADMITTED_BINDINGS = (
    {
        "semantic_contract_id": "particle.closest_face_projection.v1",
        "physical_encoding_id": "builtin_triangle.closest_face_projection.v1",
        "program_alias": "builtin_triangle_adjacency",
        "consumer_source_witnesses": (
            {
                "source_path": "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": ("compile_standard_builtin_triangle_program",),
            },
            {
                "source_path": "src/rtdsl/v4_builtin_triangle_standard_library.py",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": (
                    "def compile_standard_builtin_triangle_program",
                    "compile_adjacency_callback",
                ),
            },
        ),
    },
    {
        "semantic_contract_id": "triangle.rt2a1.weighted_count.v1",
        "physical_encoding_id": "builtin_triangle.weighted_count.v1",
        "program_alias": "builtin_triangle_count",
        "consumer_source_witnesses": (
            {
                "source_path": "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": ("compile_count_callback",),
            },
        ),
    },
    {
        "semantic_contract_id": "librts.inclusive_aabb_relation.v1",
        "physical_encoding_id": "custom_aabb.inclusive_relation.v1",
        "program_alias": "custom_aabb_box_relation",
        "consumer_source_witnesses": (
            {
                "source_path": "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": (
                    "from rtdsl.v4_box_relation_callback import",
                    "compile_callback()",
                ),
            },
        ),
    },
    {
        "semantic_contract_id": "rtxrmq.leftmost_argmin.v1",
        "physical_encoding_id": "builtin_triangle.rtxrmq_leftmost.v1",
        "program_alias": "builtin_triangle_adjacency",
        "consumer_source_witnesses": (
            {
                "source_path": "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py",
                "source_root": "goal5789_heldout_certificate_source_pin",
                "required_tokens": ("compile_standard_builtin_triangle_program",),
            },
            {
                "source_path": "src/rtdsl/v4_builtin_triangle_standard_library.py",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": (
                    "def compile_standard_builtin_triangle_program",
                    "compile_adjacency_callback",
                ),
            },
        ),
    },
)

# These identities are independently frozen review inputs, not values inferred
# from the certificate builder.  The materializer must reproduce them from the
# exact Goal5785 source/evidence roots before it is allowed to emit an
# authority.  In particular, changing a consumer pair to another real,
# executed Callback program is a provenance failure rather than a harmless
# catalog relabeling.
EXPECTED_PROGRAM_SHA256_BY_ALIAS = {
    "builtin_triangle_adjacency": "371de8d1816ddb8dbce78db9eb160f08cce3d595784509d5c6400e51b50ad476",
    "builtin_triangle_count": "92697debe1e25227ec770b4d339c7cd248b16b7185612516841f3986a208ea30",
    "builtin_triangle_keyed": "c126a788b5e451fc0d76b4c48610bb2e6d6dbbf22fdb0b1c656deac97babc671",
    "custom_aabb_box_relation": "eeb2427e72a1f6b9f242adbf588d89e40616f1176c5bef60705ec716fcd06690",
    "custom_aabb_spatial_candidate": "c3a17d90e2c8895f6ec14b0c07bafdc734d7ec233b3397bdc99fd478b9941c26",
}

EXPECTED_ADMITTED_PAIR_TO_PROGRAM_SHA256 = {
    (
        "particle.closest_face_projection.v1",
        "builtin_triangle.closest_face_projection.v1",
    ): EXPECTED_PROGRAM_SHA256_BY_ALIAS["builtin_triangle_adjacency"],
    (
        "triangle.rt2a1.weighted_count.v1",
        "builtin_triangle.weighted_count.v1",
    ): EXPECTED_PROGRAM_SHA256_BY_ALIAS["builtin_triangle_count"],
    (
        "librts.inclusive_aabb_relation.v1",
        "custom_aabb.inclusive_relation.v1",
    ): EXPECTED_PROGRAM_SHA256_BY_ALIAS["custom_aabb_box_relation"],
    (
        "rtxrmq.leftmost_argmin.v1",
        "builtin_triangle.rtxrmq_leftmost.v1",
    ): EXPECTED_PROGRAM_SHA256_BY_ALIAS["builtin_triangle_adjacency"],
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def pretty_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _archive_identity(relative: str, expected_bytes: int, expected_sha256: str) -> tuple[Path, dict[str, object]]:
    path = ROOT / relative
    if not path.is_file() or path.stat().st_size != expected_bytes or sha_file(path) != expected_sha256:
        raise RuntimeError(f"frozen archive identity mismatch: {relative}")
    return path, {"path": relative, "size_bytes": expected_bytes, "file_sha256": expected_sha256}


def _safe_member_name(name: str) -> PurePosixPath:
    if not name or "\\" in name:
        raise RuntimeError(f"unsafe archive member: {name!r}")
    posix = PurePosixPath(name)
    if posix.is_absolute() or any(part in {"", ".", ".."} for part in posix.parts):
        raise RuntimeError(f"unsafe archive member: {name!r}")
    if any(":" in part for part in posix.parts):
        raise RuntimeError(f"unsafe archive drive member: {name!r}")
    return posix


def _extract_source(archive: Path, destination: Path) -> None:
    seen: set[str] = set()
    with tarfile.open(archive, "r:gz") as handle:
        for member in handle.getmembers():
            posix = _safe_member_name(member.name)
            if member.name in seen:
                raise RuntimeError(f"duplicate source member: {member.name}")
            seen.add(member.name)
            target = destination.joinpath(*posix.parts)
            resolved = target.resolve()
            if destination.resolve() not in resolved.parents and resolved != destination.resolve():
                raise RuntimeError(f"source member escapes extraction root: {member.name}")
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                source = handle.extractfile(member)
                if source is None:
                    raise RuntimeError(f"regular member unreadable: {member.name}")
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as output:
                    output.write(source.read())
            else:
                raise RuntimeError(f"link or special source member rejected: {member.name}")


def _walk_effects(statements: Sequence[object], classes: Mapping[str, type]) -> tuple[int, set[str]]:
    iterations = 0
    effects: set[str] = set()
    for statement in statements:
        if isinstance(statement, classes["IfStatement"]):
            left_iterations, left_effects = _walk_effects(statement.then_body, classes)
            right_iterations, right_effects = _walk_effects(statement.else_body, classes)
            iterations += left_iterations + right_iterations
            effects.update(left_effects)
            effects.update(right_effects)
        elif isinstance(statement, classes["StaticForStatement"]):
            body_iterations, body_effects = _walk_effects(statement.body, classes)
            iterations += statement.trip_count * max(1, 1 + body_iterations)
            effects.update(body_effects)
        elif isinstance(statement, classes["ReturnEffectStatement"]):
            effects.add(statement.effect.kind.value)
    return iterations, effects


def _json_type_u32_slots(
    value: object,
    records: Mapping[str, Mapping[str, object]],
    visiting: frozenset[str] = frozenset(),
) -> int:
    if not isinstance(value, Mapping) or not isinstance(value.get("kind"), str):
        raise RuntimeError("invalid register-layout type in Callback IR")
    kind = value["kind"]
    if kind == "scalar":
        scalar = value.get("scalar")
        if not isinstance(scalar, str):
            raise RuntimeError("invalid scalar register-layout type")
        return 2 if scalar in {"i64", "u64", "f64"} else 1
    if kind == "vector":
        lanes = value.get("lanes")
        scalar = value.get("scalar")
        if not isinstance(lanes, int) or isinstance(lanes, bool) or lanes <= 0 or not isinstance(scalar, str):
            raise RuntimeError("invalid vector register-layout type")
        return lanes * (2 if scalar == "f64" else 1)
    if kind == "tuple":
        items = value.get("items")
        if not isinstance(items, list):
            raise RuntimeError("invalid tuple register-layout type")
        return sum(_json_type_u32_slots(item, records, visiting) for item in items)
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
            total += _json_type_u32_slots(field["type"], records, visiting | {name})
        return total
    raise RuntimeError(f"non-register-layout Callback IR type: {kind}")


def _json_expression_walk(value: object):
    if isinstance(value, Mapping):
        if isinstance(value.get("opcode"), str):
            yield value
        for nested in value.values():
            yield from _json_expression_walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _json_expression_walk(nested)


def _independent_json_resource_projection(program: Mapping[str, object]) -> tuple[int, int, int]:
    records_value = program.get("records")
    manifest = program.get("manifest")
    functions = program.get("functions")
    if not isinstance(records_value, list) or not isinstance(manifest, Mapping) or not isinstance(functions, list):
        raise RuntimeError("Callback IR resource inputs missing")
    records: dict[str, Mapping[str, object]] = {}
    for record in records_value:
        if not isinstance(record, Mapping) or set(record) != {"name", "purpose", "fields"}:
            raise RuntimeError("invalid Callback IR record")
        name = record.get("name")
        if not isinstance(name, str) or name in records:
            raise RuntimeError("invalid or duplicate Callback IR record name")
        records[name] = record
    payload_name = manifest.get("payload_record")
    if not isinstance(payload_name, str) or payload_name not in records or records[payload_name].get("purpose") != "payload":
        raise RuntimeError("Callback IR payload record mismatch")
    payload_slots = _json_type_u32_slots({"kind": "record", "name": payload_name}, records)
    attribute_types = manifest.get("attribute_types")
    if not isinstance(attribute_types, list):
        raise RuntimeError("Callback IR attribute type list missing")
    attribute_slots = sum(_json_type_u32_slots(item, records) for item in attribute_types)

    names: set[str] = set()
    helpers: set[str] = set()
    function_rows: list[Mapping[str, object]] = []
    for function in functions:
        if not isinstance(function, Mapping) or not isinstance(function.get("name"), str):
            raise RuntimeError("invalid Callback IR function")
        name = function["name"]
        if name in names:
            raise RuntimeError("duplicate Callback IR function")
        names.add(name)
        if function.get("role") is None:
            helpers.add(name)
        function_rows.append(function)
    graph: dict[str, set[str]] = {name: set() for name in names}
    for function in function_rows:
        source = str(function["name"])
        for expression in _json_expression_walk(function.get("body")):
            if expression.get("opcode") == "helper_call":
                attributes = expression.get("attributes")
                target = attributes.get("name") if isinstance(attributes, Mapping) else None
                if not isinstance(target, str) or target not in helpers:
                    raise RuntimeError("unknown Callback IR helper call")
                graph[source].add(target)
    visiting: set[str] = set()
    memo: dict[str, int] = {}

    def depth(name: str) -> int:
        if name in visiting:
            raise RuntimeError("recursive Callback IR helper call graph")
        if name in memo:
            return memo[name]
        visiting.add(name)
        value = 0 if not graph[name] else 1 + max(depth(target) for target in graph[name])
        visiting.remove(name)
        memo[name] = value
        return value

    helper_depth = max((depth(name) for name in graph), default=0)
    return payload_slots, attribute_slots, helper_depth


def _program_material(
    verified: object,
    callback_authority_id: str,
    classes: Mapping[str, type],
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    program = verified.program.to_dict()
    program_sha256 = digest(program)
    roles: list[dict[str, object]] = []
    effect_rows: list[list[object]] = []
    total_iterations = 0
    for function in verified.program.functions:
        function_iterations, effects = _walk_effects(function.body, classes)
        total_iterations += function_iterations
        sorted_effects = sorted(effects)
        effect_rows.append([function.name, sorted_effects])
        if function.role is not None:
            roles.append({"role": function.role.value, "effects": sorted_effects})
    verified_summary = verified.to_dict()
    payload_slots, attribute_slots, helper_depth = _independent_json_resource_projection(program)
    if verified_summary["effect_digest"] != digest(effect_rows):
        raise RuntimeError("independent effect projection disagrees with product verifier")
    if verified_summary["total_static_iterations"] != total_iterations:
        raise RuntimeError("independent static-iteration projection disagrees with product verifier")
    ir_body = dict(program)
    ir_body.pop("normalized_source")
    ir_body.pop("source_sha256")
    if verified_summary["ir_sha256"] != digest(ir_body):
        raise RuntimeError("independent IR projection disagrees with product verifier")
    if verified_summary["payload_u32_slots"] != payload_slots:
        raise RuntimeError("independent payload-slot projection disagrees with product verifier")
    if verified_summary["attribute_u32_slots"] != attribute_slots:
        raise RuntimeError("independent attribute-slot projection disagrees with product verifier")
    if verified_summary["helper_call_depth"] != helper_depth:
        raise RuntimeError("independent helper-depth projection disagrees with product verifier")
    callback_contract = {
        "callback_authority_id": callback_authority_id,
        "authority_program_sha256": program_sha256,
        "ir_sha256": verified_summary["ir_sha256"],
        "effect_digest": verified_summary["effect_digest"],
        "roles": roles,
        "payload_u32_slots": payload_slots,
        "attribute_u32_slots": attribute_slots,
        "trace_depth": verified.program.manifest.resources.max_trace_depth,
        "callable_depth": verified.program.manifest.resources.max_callable_depth,
        "total_static_iterations": verified_summary["total_static_iterations"],
        "helper_call_depth": helper_depth,
    }
    return program, verified_summary, callback_contract


def _load_leaf_evidence(
    evidence_archive: Path,
    expected_programs: Mapping[str, tuple[str, str]],
) -> tuple[dict[str, object], dict[str, list[dict[str, object]]]]:
    with tarfile.open(evidence_archive, "r:gz") as handle:
        names = handle.getnames()
        if len(names) != len(set(names)):
            raise RuntimeError("duplicate evidence archive member")
        for name in names:
            _safe_member_name(name)
        embedded_source = handle.extractfile(EMBEDDED_SOURCE_MEMBER)
        if embedded_source is None:
            raise RuntimeError("execution evidence omits embedded execution source")
        embedded_source_bytes = embedded_source.read()
        if len(embedded_source_bytes) != SOURCE_ARCHIVE_BYTES or hashlib.sha256(embedded_source_bytes).hexdigest() != SOURCE_ARCHIVE_SHA256:
            raise RuntimeError("execution evidence embedded source does not match standalone source archive")
        manifest_bytes = handle.extractfile(LEAF_MANIFEST_MEMBER).read()
        if len(manifest_bytes) != LEAF_MANIFEST_BYTES or hashlib.sha256(manifest_bytes).hexdigest() != LEAF_MANIFEST_SHA256:
            raise RuntimeError("frozen leaf manifest identity mismatch")
        manifest = json.loads(manifest_bytes)
        entries = manifest.get("entries")
        if not isinstance(entries, list) or manifest.get("entry_count") != len(entries):
            raise RuntimeError("invalid leaf manifest entry count")
        if manifest.get("entries_sha256") != digest(entries):
            raise RuntimeError("leaf manifest entries digest mismatch")
        for row in entries:
            if not isinstance(row, dict) or set(row) != {
                "artifact_json_sha256", "artifact_json_size_bytes", "key_sha256"
            }:
                raise RuntimeError("invalid leaf manifest row schema")
        entry_map = {row["key_sha256"]: row for row in entries}
        if len(entry_map) != len(entries):
            raise RuntimeError("duplicate leaf manifest key")
        selected: dict[str, list[dict[str, object]]] = {key: [] for key in expected_programs}
        for key_sha256, manifest_row in entry_map.items():
            member_path = f"EXECUTION/FORMAL_NUMBA_LEAF_CACHE/{key_sha256}/artifact.json"
            if member_path not in names:
                raise RuntimeError(f"leaf artifact missing: {member_path}")
            payload = handle.extractfile(member_path).read()
            if len(payload) != manifest_row["artifact_json_size_bytes"] or hashlib.sha256(payload).hexdigest() != manifest_row["artifact_json_sha256"]:
                raise RuntimeError(f"leaf artifact identity mismatch: {member_path}")
            artifact = json.loads(payload)
            key = artifact.get("key", {})
            ir_sha = key.get("callback_ir_sha256")
            effect_sha = key.get("callback_effect_digest")
            for program_key, (expected_ir, expected_effect) in expected_programs.items():
                if ir_sha == expected_ir and effect_sha == expected_effect:
                    if key.get("role") != artifact.get("artifact", {}).get("role"):
                        raise RuntimeError(f"leaf artifact role mismatch: {member_path}")
                    selected[program_key].append(
                        {
                            "member_path": member_path,
                            "file_sha256": manifest_row["artifact_json_sha256"],
                            "size_bytes": manifest_row["artifact_json_size_bytes"],
                            "key_sha256": key_sha256,
                            "role": key["role"],
                            "callback_ir_sha256": ir_sha,
                            "callback_effect_digest": effect_sha,
                        }
                    )
        return manifest, {key: sorted(rows, key=lambda row: row["role"]) for key, rows in selected.items()}


def build_outputs() -> tuple[dict[str, object], dict[str, object]]:
    preloaded_rtdsl = sorted(
        name for name in sys.modules if name == "rtdsl" or name.startswith("rtdsl.")
    )
    if preloaded_rtdsl:
        raise RuntimeError(
            "A2 authority materialization requires a fresh interpreter with no preloaded "
            f"RTDL modules: {preloaded_rtdsl!r}"
        )
    source_archive, source_identity = _archive_identity(
        SOURCE_ARCHIVE_REL, SOURCE_ARCHIVE_BYTES, SOURCE_ARCHIVE_SHA256
    )
    evidence_archive, evidence_identity = _archive_identity(
        EVIDENCE_ARCHIVE_REL, EVIDENCE_ARCHIVE_BYTES, EVIDENCE_ARCHIVE_SHA256
    )
    result_path, result_identity = _archive_identity(
        RESULT_REL, RESULT_BYTES, RESULT_SHA256
    )
    controlling_result = json.loads(result_path.read_text(encoding="utf-8"))
    if (
        controlling_result.get("run_goal_id") != 5785
        or controlling_result.get("lineage", {}).get("execution_source_sha256") != SOURCE_ARCHIVE_SHA256
        or controlling_result.get("evidence", {}).get("archive_sha256") != EVIDENCE_ARCHIVE_SHA256
    ):
        raise RuntimeError("Goal5785 controlling result does not cross-bind source and evidence archives")
    with tempfile.TemporaryDirectory(prefix="goal5789_a2_callback_authority_") as temporary:
        extraction_root = Path(temporary)
        _extract_source(source_archive, extraction_root)
        selected_constructor_source_manifest = {
            path: sha_file(extraction_root / path)
            for path in SELECTED_CONSTRUCTOR_SOURCE_PATHS
        }
        heldout_certificate_path = ROOT / HELD_OUT_CERTIFICATE_REL
        if (
            not heldout_certificate_path.is_file()
            or heldout_certificate_path.stat().st_size != HELD_OUT_CERTIFICATE_BYTES
            or sha_file(heldout_certificate_path) != HELD_OUT_CERTIFICATE_SHA256
        ):
            raise RuntimeError("frozen Goal5789 held-out certificate identity mismatch")
        heldout_certificate = json.loads(heldout_certificate_path.read_text(encoding="utf-8"))
        heldout_body = dict(heldout_certificate)
        heldout_seal = heldout_body.pop("certificate_sha256", None)
        if digest(heldout_body) != heldout_seal:
            raise RuntimeError("frozen Goal5789 held-out certificate seal mismatch")
        heldout_source_pins = heldout_certificate.get("evidence_contract", {}).get("source_pins", {})
        consumer_source_manifest: dict[str, str] = {}
        consumer_source_payloads: dict[str, bytes] = {}
        for binding_spec in ADMITTED_BINDINGS:
            for witness in binding_spec["consumer_source_witnesses"]:
                path = str(witness["source_path"])
                root_kind = str(witness["source_root"])
                if root_kind == "goal5785_execution_source_archive":
                    source_path = extraction_root / path
                elif root_kind == "goal5789_heldout_certificate_source_pin":
                    source_path = ROOT / path
                else:
                    raise RuntimeError(f"unknown consumer witness source root: {root_kind}")
                payload = source_path.read_bytes()
                payload_sha = hashlib.sha256(payload).hexdigest()
                if root_kind == "goal5789_heldout_certificate_source_pin" and heldout_source_pins.get(path) != payload_sha:
                    raise RuntimeError(f"held-out consumer source pin mismatch: {path}")
                previous = consumer_source_manifest.get(path)
                if previous is not None and previous != payload_sha:
                    raise RuntimeError(f"consumer source identity conflict: {path}")
                consumer_source_manifest[path] = payload_sha
                consumer_source_payloads[path] = payload
                text = payload.decode("utf-8")
                for token in witness["required_tokens"]:
                    if not isinstance(token, str) or not token or token not in text:
                        raise RuntimeError(f"consumer callsite token missing: {path}:{token!r}")
        sys.path.insert(0, str(extraction_root / "src"))
        sys.path.insert(0, str(extraction_root))
        try:
            ir_module = importlib.import_module("rtdsl.v4_callback_ir")
            classes = {
                "IfStatement": ir_module.IfStatement,
                "StaticForStatement": ir_module.StaticForStatement,
                "ReturnEffectStatement": ir_module.ReturnEffectStatement,
            }
            partial_rows: dict[str, dict[str, object]] = {}
            expected_programs: dict[str, tuple[str, str]] = {}
            alias_to_program_sha: dict[str, str] = {}
            for spec in PROGRAM_SPECS:
                module = importlib.import_module(str(spec["module"]))
                constructor: Callable[[], object] = getattr(module, str(spec["function"]))
                verified = constructor()
                program, summary, contract = _program_material(
                    verified,
                    str(spec["callback_authority_id"]),
                    classes,
                )
                program_sha256 = digest(program)
                alias = str(spec["alias"])
                if program_sha256 in partial_rows or alias in alias_to_program_sha:
                    raise RuntimeError(f"duplicate Callback-IR program or alias: {alias}")
                alias_to_program_sha[alias] = program_sha256
                partial_rows[program_sha256] = {
                    "callback_authority_id": spec["callback_authority_id"],
                    "alias": alias,
                    "compile_entrypoint": f"{spec['module']}:{spec['function']}",
                    "selected_constructor_source_paths": list(spec["selected_constructor_source_paths"]),
                    "executed_leaf_evidence": [],
                    "callback_program": program,
                    "callback_program_sha256": program_sha256,
                    "verified_summary": summary,
                    "callback_contract": contract,
                }
                expected_programs[program_sha256] = (
                    str(summary["ir_sha256"]), str(summary["effect_digest"])
                )
            if alias_to_program_sha != EXPECTED_PROGRAM_SHA256_BY_ALIAS:
                raise RuntimeError(
                    "frozen Callback-IR constructor output identities do not match the reviewed five-program universe"
                )
            actual_pair_to_program = {
                (str(row["semantic_contract_id"]), str(row["physical_encoding_id"])):
                alias_to_program_sha[str(row["program_alias"])]
                for row in ADMITTED_BINDINGS
            }
            if actual_pair_to_program != EXPECTED_ADMITTED_PAIR_TO_PROGRAM_SHA256:
                raise RuntimeError(
                    "semantic/physical pair to Callback-program mapping does not match the reviewed binding map"
                )
            extracted_root = extraction_root.resolve()
            for name, module in tuple(sys.modules.items()):
                if name != "rtdsl" and not name.startswith("rtdsl."):
                    continue
                module_file = getattr(module, "__file__", None)
                if not isinstance(module_file, str):
                    raise RuntimeError(f"loaded RTDL module has no file identity: {name}")
                resolved_module = Path(module_file).resolve()
                if extracted_root not in resolved_module.parents:
                    raise RuntimeError(
                        f"loaded RTDL module escaped frozen extracted source: {name} -> {resolved_module}"
                    )
            leaf_manifest, selected_leaves = _load_leaf_evidence(
                evidence_archive, expected_programs
            )
            all_leaf_keys: list[str] = []
            for program_sha256, row in partial_rows.items():
                row["executed_leaf_evidence"] = selected_leaves[program_sha256]
                expected_roles = sorted(item["role"] for item in row["callback_contract"]["roles"])
                actual_roles = sorted(item["role"] for item in row["executed_leaf_evidence"])
                if expected_roles != actual_roles:
                    raise RuntimeError(f"executed leaf role set mismatch: {program_sha256}")
                all_leaf_keys.extend(item["key_sha256"] for item in row["executed_leaf_evidence"])
            if len(all_leaf_keys) != 26 or len(set(all_leaf_keys)) != 26:
                raise RuntimeError("five-program leaf evidence does not partition all 26 frozen entries")
        finally:
            sys.path.pop(0)
            sys.path.pop(0)
            for name in tuple(sys.modules):
                if name == "rtdsl" or name.startswith("rtdsl."):
                    del sys.modules[name]

    authority: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.callback_ir_authority.v1",
        "authority_sha256": "",
        "source_archive": source_identity,
        "execution_evidence_archive": evidence_identity,
        "controlling_result": result_identity,
        "execution_leaf_manifest": {
            "member_path": LEAF_MANIFEST_MEMBER,
            "file_sha256": LEAF_MANIFEST_SHA256,
            "size_bytes": LEAF_MANIFEST_BYTES,
            "entry_count": leaf_manifest["entry_count"],
            "entries_sha256": leaf_manifest["entries_sha256"],
        },
        "selected_constructor_source_manifest": selected_constructor_source_manifest,
        "consumer_source_manifest": consumer_source_manifest,
        "consumer_source_authority_roots": {
            "goal5789_heldout_certificate": {
                "path": HELD_OUT_CERTIFICATE_REL,
                "size_bytes": HELD_OUT_CERTIFICATE_BYTES,
                "file_sha256": HELD_OUT_CERTIFICATE_SHA256,
                "certificate_sha256": heldout_certificate["certificate_sha256"],
            }
        },
        "programs": partial_rows,
        "admitted_bindings": [
            {
                "semantic_contract_id": row["semantic_contract_id"],
                "physical_encoding_id": row["physical_encoding_id"],
                "authority_program_sha256": alias_to_program_sha[row["program_alias"]],
                "callback_authority_id": partial_rows[
                    alias_to_program_sha[row["program_alias"]]
                ]["callback_authority_id"],
                "consumer_source_witnesses": [
                    {
                        "source_path": witness["source_path"],
                        "source_sha256": consumer_source_manifest[witness["source_path"]],
                        "source_root": witness["source_root"],
                        "required_tokens": list(witness["required_tokens"]),
                    }
                    for witness in row["consumer_source_witnesses"]
                ],
            }
            for row in ADMITTED_BINDINGS
        ],
        "claim_boundary": {
            "source_backed_callback_ir_authority": True,
            "executed_leaf_identity_crossbound": True,
            "controlling_result_source_evidence_crossbound": True,
            "execution_evidence_embeds_exact_source_archive": True,
            "selected_constructor_sources_are_not_claimed_as_complete_import_closure": True,
            "consumer_callsites_exact_hash_and_token_bound": True,
            "callback_authority_bound_inventory_scope": "six_of_fifteen_inventory_rows_plus_legacy_rtxrmq_replay",
            "authority_producer_is_tcb": True,
            "independently_implemented_product_verifier_claimed": False,
            "jointly_wrong_authorities_detected": False,
            "semantic_soundness_claimed": False,
            "execution_authorized": False,
        },
    }
    authority["authority_sha256"] = digest({key: value for key, value in authority.items() if key != "authority_sha256"})
    authority_bytes = pretty_json_bytes(authority)
    materializer_relative = "scripts/goal5789_a2_materialize_callback_ir_authority.py"
    pin: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.callback_ir_authority_pin.v1",
        "pin_sha256": "",
        "callback_authority": {
            "path": "history/internal_docs/goal5789_a2_contract_evidence_20260821/CALLBACK_IR_AUTHORITY.json",
            "size_bytes": len(authority_bytes),
            "file_sha256": hashlib.sha256(authority_bytes).hexdigest(),
            "authority_sha256": authority["authority_sha256"],
        },
        "source_archive": source_identity,
        "execution_evidence_archive": evidence_identity,
        "controlling_result": result_identity,
        "materializer": {
            "path": materializer_relative,
            "file_sha256": sha_file(ROOT / materializer_relative),
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
    pin["pin_sha256"] = digest({key: value for key, value in pin.items() if key != "pin_sha256"})
    return authority, pin


def _write_create_only(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(pretty_json_bytes(payload))


def main() -> int:
    if AUTHORITY_OUTPUT.exists() or PIN_OUTPUT.exists():
        raise RuntimeError("A2 callback authority outputs are create-only and already exist")
    authority, pin = build_outputs()
    _write_create_only(AUTHORITY_OUTPUT, authority)
    try:
        _write_create_only(PIN_OUTPUT, pin)
    except BaseException:
        # Do not leave a partial authority without its separately pinned root.
        AUTHORITY_OUTPUT.unlink(missing_ok=True)
        raise
    print(json.dumps({
        "authority_file_sha256": sha_file(AUTHORITY_OUTPUT),
        "authority_sha256": authority["authority_sha256"],
        "pin_file_sha256": sha_file(PIN_OUTPUT),
        "pin_sha256": pin["pin_sha256"],
        "program_count": len(authority["programs"]),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

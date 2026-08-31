"""Rebuild the historical 15-lane replay and seven-positive X1 vector freeze.

This is a local, retrospective derivation from frozen Goal5789-A2 bytes.  The
A2 checker is invoked only to replay those historical rows; it is never used
to decide a future candidate.  Structural vectors exclude row identity,
source path, source digest, expected disposition, and performance metadata.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
A2_ROOT = ROOT / "history/internal_docs/goal5789_a2_contract_evidence_20260821"
S0_PROTOCOL = (
    ROOT / "history/internal_docs/goal5793_s0_protocol_and_stage_authority_20260822.json"
)
OUTPUT_PATH = (
    ROOT / "history/internal_docs/goal5793_x1_positive_vector_freeze_20260822.json"
)
PACKET_MANIFEST_PATH = (
    ROOT
    / "history/internal_docs/goal5789_a2_postreview_repair_packet_v1_manifest_20260822.json"
)
EXPECTED_PACKET_MANIFEST_SHA256 = (
    "f33ddfcad448c4f8954751e627d2448bd3070a2ac7f26476f9bd758798762c04"
)
A2_CHECKER_PATH = ROOT / "scripts/goal5789_a2_independent_compatibility_checker.py"
V1_CHECKER_PATH = ROOT / "scripts/goal5789_independent_compatibility_checker.py"
CANONICAL_PATH = ROOT / "scripts/goal5793_x1_canonical.py"
EXPECTED_DEPENDENCY_SHA256 = {
    A2_CHECKER_PATH: "6dea6a474b8225a99e96508ef1cf56d3f1147cbaa3adb8acf8124c845597e210",
    V1_CHECKER_PATH: "abb1f1575af824cc37e9d9984aff8679f79cb89f4ad7ed2792ede5a3db75ac2e",
    CANONICAL_PATH: "13b22dbae22b0a70763fdf46031c7975ab1eaebe20c37789f397242b7a1c9b3a",
    S0_PROTOCOL: "126ee3c1dfe930a7bb25b2f19df8a6c4889c7ef8b619abe3cc69da54efa8b7c2",
}

EXPECTED_POSITIVE_IDS = (
    "particle__microfluidics_5000",
    "triangle__com_dblp__rt_2a1",
    "triangle__cit_patents__rt_2a1",
    "triangle__soc_livejournal1__rt_2a1",
    "librts__parks_point_contains",
    "librts__parks_range_contains",
)
HELD_OUT_ID = "legacy_held_out__rtxrmq"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_exact(path: Path, name: str, expected_sha256: str):
    resolved = path.resolve(strict=True)
    if _sha256(resolved) != expected_sha256:
        raise ValueError(f"frozen dependency hash mismatch: {resolved}")
    spec = importlib.util.spec_from_file_location(name, resolved)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load frozen dependency: {resolved}")
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
        raise ValueError(f"frozen dependency origin mismatch: {resolved}")
    return module


def _load_a2_checker():
    import scripts

    v1_name = "scripts.goal5789_independent_compatibility_checker"
    v1 = _load_exact(
        V1_CHECKER_PATH,
        "_goal5793_x1_positive_freeze_v1_checker",
        EXPECTED_DEPENDENCY_SHA256[V1_CHECKER_PATH],
    )
    previous_module = sys.modules.get(v1_name)
    previous_attribute = getattr(
        scripts, "goal5789_independent_compatibility_checker", None
    )
    sys.modules[v1_name] = v1
    setattr(scripts, "goal5789_independent_compatibility_checker", v1)
    try:
        return _load_exact(
            A2_CHECKER_PATH,
            "_goal5793_x1_positive_freeze_a2_checker",
            EXPECTED_DEPENDENCY_SHA256[A2_CHECKER_PATH],
        )
    finally:
        if previous_module is None:
            sys.modules.pop(v1_name, None)
        else:
            sys.modules[v1_name] = previous_module
        if previous_attribute is None:
            delattr(scripts, "goal5789_independent_compatibility_checker")
        else:
            setattr(
                scripts,
                "goal5789_independent_compatibility_checker",
                previous_attribute,
            )


canonical = _load_exact(
    CANONICAL_PATH,
    "_goal5793_x1_positive_freeze_canonical",
    EXPECTED_DEPENDENCY_SHA256[CANONICAL_PATH],
)
a2 = _load_a2_checker()
CANONICALIZATION_NAME = canonical.CANONICALIZATION_NAME
canonical_digest = canonical.canonical_digest
canonical_json_bytes = canonical.canonical_json_bytes
seal_document = canonical.seal_document


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def _record(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _packet_payloads() -> dict[str, Mapping[str, object]]:
    if _sha256(PACKET_MANIFEST_PATH) != EXPECTED_PACKET_MANIFEST_SHA256:
        raise ValueError("postreview packet manifest bytes changed")
    manifest = _json(PACKET_MANIFEST_PATH)
    rows = manifest.get("payloads")
    if not isinstance(rows, list) or len(rows) != manifest.get("payload_count"):
        raise ValueError("postreview packet payload count mismatch")
    indexed: dict[str, Mapping[str, object]] = {}
    for index, raw in enumerate(rows):
        row = _as_mapping(raw, f"packet.payloads[{index}]")
        path = row.get("path")
        if not isinstance(path, str) or path in indexed:
            raise ValueError("invalid or duplicate postreview packet payload path")
        indexed[path] = row
    return indexed


def _packet_record(
    path: Path, payloads: Mapping[str, Mapping[str, object]]
) -> dict[str, object]:
    rel = path.relative_to(ROOT).as_posix()
    if rel not in payloads:
        raise ValueError(f"path absent from frozen postreview packet: {rel}")
    frozen = payloads[rel]
    observed = _record(path)
    if observed["bytes"] != frozen.get("bytes") \
            or observed["sha256"] != frozen.get("sha256"):
        raise ValueError(f"postreview packet payload drift: {rel}")
    return observed


def _fixed_record(path: Path) -> dict[str, object]:
    expected = EXPECTED_DEPENDENCY_SHA256.get(path)
    if expected is None or _sha256(path) != expected:
        raise ValueError(f"fixed root bytes changed: {path}")
    return _record(path)


def _as_list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{path}: expected list")
    return value


def _as_mapping(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path}: expected object")
    return value


def _map_stage(physical: Mapping[str, object], kind: str) -> dict[str, object]:
    matches = [
        _as_mapping(item, f"physical_encoding.maps[{index}]")
        for index, item in enumerate(_as_list(physical.get("maps"), "maps"))
        if isinstance(item, Mapping) and item.get("kind") == kind
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {kind!r} map")
    item = matches[0]
    return {
        "kind": kind,
        "consumes": deepcopy(item.get("consumes")),
        "produces": deepcopy(item.get("produces")),
    }


def _roles(callback: Mapping[str, object], selected: set[str]) -> list[dict[str, object]]:
    rows = []
    for index, raw in enumerate(_as_list(callback.get("roles"), "callback.roles")):
        role = _as_mapping(raw, f"callback.roles[{index}]")
        if role.get("role") in selected:
            rows.append({
                "role": role.get("role"),
                "effects": deepcopy(role.get("effects")),
            })
    return sorted(rows, key=lambda row: str(row["role"]).encode("utf-8"))


def structural_vector(certificate: Mapping[str, object]) -> dict[str, object]:
    semantic = _as_mapping(certificate.get("semantic_request"), "semantic_request")
    physical = _as_mapping(certificate.get("physical_encoding"), "physical_encoding")
    callback = _as_mapping(certificate.get("callback_contract"), "callback_contract")
    instance = _as_mapping(certificate.get("instance_contract"), "instance_contract")
    policy = _as_mapping(semantic.get("policy"), "semantic_request.policy")
    gas = _as_mapping(physical.get("gas"), "physical_encoding.gas")
    hit_channels = [
        deepcopy(dict(_as_mapping(raw, f"hit_channels[{index}]")))
        for index, raw in enumerate(
            _as_list(physical.get("hit_channels"), "physical_encoding.hit_channels")
        )
    ]
    buffers = [
        deepcopy(dict(_as_mapping(raw, f"buffers[{index}]")))
        for index, raw in enumerate(
            _as_list(physical.get("buffers"), "physical_encoding.buffers")
        )
    ]
    bindings = []
    for index, raw in enumerate(
        _as_list(instance.get("bindings"), "instance_contract.bindings")
    ):
        binding = _as_mapping(raw, f"instance_contract.bindings[{index}]")
        bindings.append({
            "semantic": binding.get("semantic"),
            "writable": binding.get("writable"),
            "device_id": binding.get("device_id"),
            "stream_id": binding.get("stream_id"),
            "mutation_epoch": binding.get("mutation_epoch"),
        })
    vector = {
        "geometry_family": physical.get("geometry_family"),
        "primitive_type": {
            "geometry_family": physical.get("geometry_family"),
            "hit_channel_producers": sorted(
                {str(item.get("producer")) for item in hit_channels},
                key=lambda item: item.encode("utf-8"),
            ),
        },
        "ray_construction": {
            "map": _map_stage(physical, "ray"),
            "roles": _roles(callback, {"make_ray"}),
        },
        "hit_policy": {
            "required_hit_semantics": deepcopy(
                semantic.get("required_hit_semantics")
            ),
            "channels": hit_channels,
            "roles": _roles(
                callback, {"intersection", "any_hit", "closest_hit", "miss"}
            ),
        },
        "multiplicity": policy.get("multiplicity"),
        "boundary_convention": {
            "exactness": policy.get("exactness"),
            "input_type": policy.get("input_type"),
        },
        "tie_break": policy.get("tie_policy"),
        "numeric_domain": policy.get("numeric_precision"),
        "overflow_domain": policy.get("overflow_policy"),
        "decode": {
            "map": _map_stage(physical, "decode"),
            "output_type": policy.get("output_type"),
            "order_policy": policy.get("order_policy"),
            "roles": _roles(callback, {"finalize"}),
        },
        "continuation": {
            "map": _map_stage(physical, "continuation"),
            "roles": _roles(callback, {"any_hit", "closest_hit", "miss"}),
            "trace_depth": callback.get("trace_depth"),
            "total_static_iterations": callback.get("total_static_iterations"),
        },
        "composition": {
            "multiplicity": policy.get("multiplicity"),
            "order_policy": policy.get("order_policy"),
            "output_type": policy.get("output_type"),
        },
        "ownership_epoch": {
            "gas_update_policy": gas.get("update_policy"),
            "buffers": buffers,
            "bindings": bindings,
        },
    }
    return vector


def _replay(
    certificate: Mapping[str, object],
    authority: Mapping[str, object],
    callback_authority: Mapping[str, object],
    callback_pin: Mapping[str, object],
    expected: Mapping[str, object],
) -> dict[str, object]:
    observed = a2.evaluate_certificate(
        deepcopy(certificate),
        deepcopy(authority),
        deepcopy(callback_authority),
        deepcopy(callback_pin),
    )
    if canonical_json_bytes(observed) != canonical_json_bytes(expected):
        raise ValueError("historical A2 replay differs from frozen result")
    return observed


def build_freeze() -> dict[str, object]:
    payloads = _packet_payloads()
    protocol = _json(S0_PROTOCOL)
    axes = protocol["x3_preentropy_science_projection"][
        "structural_axis_vocabulary"
    ]
    callback_authority_path = A2_ROOT / "CALLBACK_IR_AUTHORITY.json"
    callback_pin_path = A2_ROOT / "CALLBACK_IR_AUTHORITY_PIN.json"
    authority_path = A2_ROOT / "AUTHORITY_BUNDLE.json"
    held_authority_path = A2_ROOT / "HELD_OUT_AUTHORITY_BUNDLE.json"
    inventory_path = A2_ROOT / "BOUNDED_INVENTORY.json"
    callback_authority = _json(callback_authority_path)
    callback_pin = _json(callback_pin_path)
    authority = _json(authority_path)
    held_authority = _json(held_authority_path)
    inventory = _json(inventory_path)
    rows = inventory["inventory"]
    if not isinstance(rows, list) or len(rows) != 15:
        raise ValueError("frozen inventory is not 15 rows")

    replay_rows = []
    positives = []
    counts = {"COMPATIBLE_FOR_DECLARED_DOMAIN": 0, "UNKNOWN": 0, "INCOMPATIBLE": 0}
    for inventory_row in rows:
        unit_id = inventory_row["unit_id"]
        certificate_path = A2_ROOT / "certificates" / f"{unit_id}.json"
        result_path = A2_ROOT / "results" / f"{unit_id}.json"
        certificate = _json(certificate_path)
        expected = _json(result_path)
        observed = _replay(
            certificate, authority, callback_authority, callback_pin, expected
        )
        verdict = observed["semantic_compatible"]["verdict"]
        counts[verdict] += 1
        replay_rows.append({
            "unit_id": unit_id,
            "certificate": _packet_record(certificate_path, payloads),
            "result": _packet_record(result_path, payloads),
            "semantic_verdict": verdict,
            "result_sha256": observed["result_sha256"],
        })
        if verdict == a2.COMPATIBLE:
            vector = structural_vector(certificate)
            if list(vector) != list(axes):
                raise ValueError("positive vector key order differs from S0 vocabulary")
            positives.append({
                "row_id": unit_id,
                "provenance": "A2_15_LANE_INVENTORY",
                "certificate": _packet_record(certificate_path, payloads),
                "stored_result": _packet_record(result_path, payloads),
                "structural_vector": vector,
                "structural_vector_sha256": canonical_digest(
                    vector,
                    domain="rtdl.goal5793.x1.positive_structural_vector",
                    version=1,
                    projection="exact_13_axis_vector",
                )["sha256"],
                "callback_program_sha256": certificate["callback_contract"][
                    "authority_program_sha256"
                ],
                "callback_ir_sha256": certificate["callback_contract"]["ir_sha256"],
                "callback_effect_digest": certificate["callback_contract"][
                    "effect_digest"
                ],
            })

    if tuple(row["row_id"] for row in positives) != EXPECTED_POSITIVE_IDS:
        raise ValueError("six inventory-positive row identities changed")
    if counts != {
        "COMPATIBLE_FOR_DECLARED_DOMAIN": 6,
        "UNKNOWN": 9,
        "INCOMPATIBLE": 0,
    }:
        raise ValueError(f"historical 15-lane counts changed: {counts}")

    held_certificate_path = A2_ROOT / "HELD_OUT_RTXRMQ_CERTIFICATE.json"
    held_result_path = A2_ROOT / "HELD_OUT_RTXRMQ_RESULT.json"
    held_certificate = _json(held_certificate_path)
    held_expected = _json(held_result_path)
    held_observed = _replay(
        held_certificate,
        held_authority,
        callback_authority,
        callback_pin,
        held_expected,
    )
    if held_observed["semantic_compatible"]["verdict"] != a2.COMPATIBLE:
        raise ValueError("legacy held-out RTXRMQ no longer replays compatible")
    held_vector = structural_vector(held_certificate)
    positives.append({
        "row_id": HELD_OUT_ID,
        "provenance": "A2_LEGACY_HELD_OUT_REPLAY",
        "certificate": _packet_record(held_certificate_path, payloads),
        "stored_result": _packet_record(held_result_path, payloads),
        "structural_vector": held_vector,
        "structural_vector_sha256": canonical_digest(
            held_vector,
            domain="rtdl.goal5793.x1.positive_structural_vector",
            version=1,
            projection="exact_13_axis_vector",
        )["sha256"],
        "callback_program_sha256": held_certificate["callback_contract"][
            "authority_program_sha256"
        ],
        "callback_ir_sha256": held_certificate["callback_contract"]["ir_sha256"],
        "callback_effect_digest": held_certificate["callback_contract"][
            "effect_digest"
        ],
    })

    particle_certificate = _json(
        A2_ROOT / "certificates/particle__microfluidics_5000.json"
    )
    callback_same = canonical_json_bytes(
        particle_certificate["callback_contract"]
    ) == canonical_json_bytes(held_certificate["callback_contract"])
    if not callback_same:
        raise ValueError("Particle/RTXRMQ callback contracts are no longer byte-identical")

    grouped: dict[str, dict[str, object]] = {}
    for row in positives:
        digest = str(row["structural_vector_sha256"])
        if digest not in grouped:
            grouped[digest] = {
                "structural_vector_sha256": digest,
                "structural_vector": deepcopy(row["structural_vector"]),
                "row_provenance": [],
            }
        grouped[digest]["row_provenance"].append(row["row_id"])
    unique_vectors = [grouped[key] for key in sorted(grouped)]

    result: dict[str, object] = {
        "schema": "rtdl.goal5793.x1.positive_vector_freeze.v1",
        "date": "2026-08-22",
        "status": "FORMAL_HISTORICAL_POSITIVE_VECTOR_AUTHORITY__NOT_FUTURE_GENERALIZATION_EVIDENCE",
        "canonicalization": CANONICALIZATION_NAME,
        "authority_sha256": "",
        "scope": {
            "formal_history_authority": True,
            "historical_a2_replay_only": True,
            "a2_controls_future_candidate": False,
            "future_candidate_examiner_invocation_count": 0,
            "search_call_count": 0,
            "entropy_call_count": 0,
            "candidate_implementation_count": 0,
            "candidate_execution_count": 0,
            "gpu_or_ssh_count": 0,
            "registered_timing_count": 0,
            "authorizes_future_candidate_exam": False,
            "authorizes_execution": False,
            "publication_authorized": False,
        },
        "frozen_roots": {
            "s0_protocol": _fixed_record(S0_PROTOCOL),
            "a2_postreview_packet_manifest": {
                **_record(PACKET_MANIFEST_PATH),
                "expected_sha256_hard_pin": EXPECTED_PACKET_MANIFEST_SHA256,
            },
            "a2_authority": _packet_record(authority_path, payloads),
            "a2_held_out_authority": _packet_record(held_authority_path, payloads),
            "a2_callback_authority": _packet_record(callback_authority_path, payloads),
            "a2_callback_pin": _packet_record(callback_pin_path, payloads),
            "a2_inventory": _packet_record(inventory_path, payloads),
            "exact_loaded_dependencies": {
                path.relative_to(ROOT).as_posix(): {
                    **_fixed_record(path),
                    "loaded_origin": path.resolve().as_posix(),
                }
                for path in (A2_CHECKER_PATH, V1_CHECKER_PATH, CANONICAL_PATH)
            },
        },
        "historical_replay": {
            "lane_count": len(replay_rows),
            "semantic_counts": counts,
            "rows": replay_rows,
            "all_stored_results_reproduced_exactly": True,
        },
        "structural_axis_vocabulary": axes,
        "derivation_boundary": {
            "included": (
                "certificate semantic policy; geometry; map graph without source "
                "identity; hit channels; callback role/effect structure; GAS, "
                "buffer and binding ownership/epoch shape"
            ),
            "excluded": [
                "row or candidate identity",
                "source path or source digest",
                "certificate/result/authority digest",
                "expected disposition or role",
                "performance or implementation ease",
                "instance input digest, owner nonce, element count or capacity",
            ],
            "candidate_or_outcome_specific_edit_allowed": False,
        },
        "positive_row_count": len(positives),
        "positive_rows": positives,
        "unique_structural_vector_count": len(unique_vectors),
        "unique_structural_vectors": unique_vectors,
        "particle_rtxrmq_callback_identity": {
            "byte_identical_callback_contract": True,
            "shared_callback_program_sha256": positives[0][
                "callback_program_sha256"
            ],
            "shared_callback_ir_sha256": positives[0]["callback_ir_sha256"],
            "shared_callback_effect_digest": positives[0][
                "callback_effect_digest"
            ],
            "semantic_discrimination_added_by_shared_callback_identity": False,
            "note": (
                "the two row provenances remain separate; their shared callback "
                "program cannot be counted as a second callback-level discriminator"
            ),
        },
    }
    result["authority_sha256"] = seal_document(
        result,
        seal_field="authority_sha256",
        domain="rtdl.goal5793.x1.positive_vector_freeze",
        version=1,
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    result = build_freeze()
    if args.check:
        existing = _json(args.output)
        if canonical_json_bytes(existing) != canonical_json_bytes(result):
            raise SystemExit("positive vector freeze is not current")
    elif args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as handle:
            handle.write(canonical_json_bytes(result) + b"\n")
    print(
        result["positive_row_count"],
        result["unique_structural_vector_count"],
        result["authority_sha256"],
        "WROTE" if args.write else "DRY_RUN_NO_HISTORY_WRITE",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rtdsl.v4_callback_ir import (
    AnyHitDeliveryContract,
    CALLBACK_IR_SCHEMA_VERSION,
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    CallbackRole,
    EffectKind,
    GeometryAdmission,
    LinkageMechanism,
    MAX_HELPER_CALL_DEPTH,
    MAX_STATIC_LOOP_TRIP_COUNT,
    RuntimeStatus,
    ScalarKind,
    TypeKind,
)
from rtdsl.v4_typed_physical_schema import (
    BufferAccess,
    BufferDomain,
    BufferSemantic,
    CountRelation,
    GasUpdatePolicy,
    GeometryFamily,
    HitChannelProducer,
    HitChannelSemantic,
    PhysicalValueType,
    ReferenceTemplateId,
)


ROOT = Path(__file__).resolve().parents[1]
CORE_MANIFEST = ROOT / "history/internal_docs/goal5757_v4_core_freeze_manifest_20260811.json"


def values(enum_type) -> list[str]:
    return [item.value for item in enum_type]


def main() -> None:
    manifest = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
    manifest_sha = hashlib.sha256(CORE_MANIFEST.read_bytes()).hexdigest()
    capability = {
        "schema": "rtdl.goal5757.frozen_v4_capability_vocabulary.v1",
        "baseline_commit": manifest["baseline_commit"],
        "core_manifest_sha256": manifest_sha,
        "callback_ir_schema_versions": [
            CALLBACK_IR_SCHEMA_VERSION,
            CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
        ],
        "callback_roles": values(CallbackRole),
        "effect_kinds": values(EffectKind),
        "scalar_kinds": values(ScalarKind),
        "type_kinds": values(TypeKind),
        "geometry_admissions": values(GeometryAdmission),
        "any_hit_delivery_contracts": values(AnyHitDeliveryContract),
        "linkage_mechanisms": values(LinkageMechanism),
        "runtime_statuses": values(RuntimeStatus),
        "static_limits": {
            "max_static_loop_trip_count": MAX_STATIC_LOOP_TRIP_COUNT,
            "max_helper_call_depth": MAX_HELPER_CALL_DEPTH,
            "max_trace_depth": 1,
            "max_callable_depth": 0,
        },
        "physical_schema": {
            "geometry_families": values(GeometryFamily),
            "buffer_semantics": values(BufferSemantic),
            "buffer_domains": values(BufferDomain),
            "buffer_access": values(BufferAccess),
            "count_relations": values(CountRelation),
            "physical_value_types": values(PhysicalValueType),
            "hit_channel_semantics": values(HitChannelSemantic),
            "hit_channel_producers": values(HitChannelProducer),
            "gas_update_policies": values(GasUpdatePolicy),
            "canonical_reference_templates": values(ReferenceTemplateId),
        },
        "trusted_execution_frontdoors": [
            "compile_callback_abi",
            "generate_formal_numba_leaves",
            "compose_callback_ptx",
            "prepare_v4_partner_session__custom_aabb_sphere_rows",
            "compile_verified_triangle_executable__builtin_triangle",
            "consume_verified_triangle_executable__single_use",
        ],
        "closed_world_absences": [
            "arbitrary_python_execution",
            "opaque_user_ptx",
            "user_native_callback_binary",
            "recursive_or_dynamic_loop",
            "device_allocation_from_callback",
            "global_atomic_or_arbitrary_global_store_effect",
            "multi_level_gas_graph",
            "motion_geometry",
            "curve_or_custom_triangle_geometry_family",
            "dynamic_callable",
            "app_paper_or_dataset_named_dispatch",
        ],
        "claim_boundary": {
            "capability_vocabulary_only": True,
            "paper_lane_support_observed": False,
            "performance_or_gpu_execution": False,
        },
    }
    print(json.dumps(capability, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

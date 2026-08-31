"""Validate the Goal5754 machine-readable design model.

This is a design audit tool. It is not imported by the V4 product runtime and
does not mint physical execution authority.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESIGN = (
    ROOT
    / "history"
    / "internal_docs"
    / "goal5754_typed_physical_schema_design_20260811.json"
)


class DesignValidationError(ValueError):
    pass


@dataclass(frozen=True)
class AdmissionProbe:
    geometry_family: str
    roles: frozenset[str]
    requested_channels: frozenset[str] = frozenset()
    user_produced_channels: frozenset[str] = frozenset()
    canonical_template_count: int = 1
    app_identity_in_dispatch_key: bool = False


@dataclass(frozen=True)
class BindingProbe:
    geometry_family: str
    vertex_count: int = 0
    primitive_count: int = 0
    maximum_triangle_index: int = -1
    primitive_metadata_count: int = 0
    device_identities: tuple[str, ...] = ("cuda:0",)
    mutation_epoch: int = 1
    gas_epoch: int = 1
    geometry_grade: str = "tested_user_geometry"
    geometry_proof_authority_present: bool = False
    all_identity_digests_match: bool = True


def load_design(path: Path = DEFAULT_DESIGN) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "rtdl.goal5754.typed_physical_schema_design.v1":
        raise DesignValidationError("unsupported design schema")
    return value


def _as_set(values: Iterable[str]) -> frozenset[str]:
    return frozenset(str(value) for value in values)


def admit_probe(design: dict[str, Any], probe: AdmissionProbe) -> str:
    families = design["geometry_families"]
    if probe.geometry_family not in families:
        raise DesignValidationError("unsupported_physical_schema")
    family = families[probe.geometry_family]
    required = _as_set(family["required_roles"])
    forbidden = _as_set(family["forbidden_roles"])
    allowed_hit = _as_set(family["allowed_hit_roles"])
    missing = required - probe.roles
    if missing:
        raise DesignValidationError(f"missing_required_roles:{sorted(missing)}")
    conflicting = forbidden & probe.roles
    if conflicting:
        raise DesignValidationError(f"forbidden_roles:{sorted(conflicting)}")
    if len(allowed_hit & probe.roles) < int(family["required_hit_role_count_minimum"]):
        raise DesignValidationError("missing_hit_role")
    available = _as_set(family["compiler_owned_hit_channels"])
    unavailable = probe.requested_channels - available
    if unavailable:
        raise DesignValidationError(f"unavailable_hit_channels:{sorted(unavailable)}")
    illegal_writes = probe.user_produced_channels & available
    if illegal_writes:
        raise DesignValidationError(f"compiler_owned_channel_write:{sorted(illegal_writes)}")
    if probe.canonical_template_count == 0:
        raise DesignValidationError("unsupported_physical_schema")
    if probe.canonical_template_count != 1:
        raise DesignValidationError("ambiguous_canonical_template")
    if probe.app_identity_in_dispatch_key:
        raise DesignValidationError("application_identity_in_dispatch_key")
    return probe.geometry_family


def validate_binding(design: dict[str, Any], probe: BindingProbe) -> str:
    if probe.geometry_family not in design["geometry_families"]:
        raise DesignValidationError("unsupported_physical_schema")
    if len(set(probe.device_identities)) != 1:
        raise DesignValidationError("cross_device_binding")
    if probe.mutation_epoch != probe.gas_epoch:
        raise DesignValidationError("stale_metadata_or_geometry_epoch")
    if not probe.all_identity_digests_match:
        raise DesignValidationError("schema_callback_provider_target_or_native_replay")
    if probe.geometry_family == "builtin_triangle":
        if probe.vertex_count <= 0 or probe.primitive_count <= 0:
            raise DesignValidationError("empty_triangle_build_input")
        if probe.maximum_triangle_index < 0 or probe.maximum_triangle_index >= probe.vertex_count:
            raise DesignValidationError("triangle_index_out_of_range")
        if probe.primitive_metadata_count != probe.primitive_count:
            raise DesignValidationError("primitive_metadata_count_mismatch")
    if (
        probe.geometry_family == "custom_aabb"
        and probe.geometry_grade == "verified_contract"
        and not probe.geometry_proof_authority_present
    ):
        raise DesignValidationError("verified_geometry_authority_missing")
    return probe.geometry_family


def validate_design(design: dict[str, Any]) -> dict[str, Any]:
    properties = design["non_negotiable_properties"]
    assert properties["application_or_publication_named_dispatch_allowed"] is False
    assert properties["opaque_user_callback_allowed"] is False
    assert properties["silent_semantic_fallback_allowed"] is False
    assert properties["exactly_one_canonical_template_required_for_admitted_schema"] is True
    assert properties["goal5753_may_be_relabelled_as_held_out_pass"] is False

    custom = design["geometry_families"]["custom_aabb"]
    triangle = design["geometry_families"]["builtin_triangle"]
    assert {"bounds", "intersection"} <= set(custom["required_roles"])
    assert {"bounds", "intersection"} <= set(triangle["forbidden_roles"])
    assert "primitive_index_u32" in triangle["compiler_owned_hit_channels"]
    assert "triangle_front_back_hit_kind_u32" in triangle["compiler_owned_hit_channels"]
    assert triangle["intersection_authority"] == "optix_builtin_triangle"
    assert triangle["winding_and_adjacency_policy"].startswith("explicit_schema_bound")
    assert triangle["invalid_primitive_policy"].startswith("reject_nonfinite")

    sphere = AdmissionProbe(
        "custom_aabb",
        frozenset({
            "bounds", "make_ray", "intersection", "any_hit", "closest_hit", "miss", "finalize"
        }),
    )
    triangle_reference = AdmissionProbe(
        "builtin_triangle",
        frozenset({"make_ray", "closest_hit", "miss", "finalize"}),
        frozenset({"primitive_index_u32", "triangle_front_back_hit_kind_u32"}),
    )
    assert admit_probe(design, sphere) == "custom_aabb"
    assert admit_probe(design, triangle_reference) == "builtin_triangle"
    assert validate_binding(
        design,
        BindingProbe(
            "builtin_triangle",
            vertex_count=4,
            primitive_count=2,
            maximum_triangle_index=3,
            primitive_metadata_count=2,
            geometry_grade="optix_builtin_semantics",
        ),
    ) == "builtin_triangle"

    attacks = design["attack_matrix"]
    if len(attacks) != 12 or len(set(attacks)) != len(attacks):
        raise DesignValidationError("attack matrix must contain 12 unique attacks")
    boundary = design["claim_boundary"]
    if any(boundary.values()):
        raise DesignValidationError("design-only claim boundary was broadened")
    return {
        "schema": design["schema"],
        "geometry_family_count": len(design["geometry_families"]),
        "reference_examples_admitted": 2,
        "attack_count": len(attacks),
        "claim_boundary_all_false": True,
        "product_runtime_imported": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, default=DEFAULT_DESIGN)
    args = parser.parse_args()
    print(json.dumps(validate_design(load_design(args.design)), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

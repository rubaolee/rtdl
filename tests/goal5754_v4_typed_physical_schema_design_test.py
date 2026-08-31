from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5754_validate_typed_physical_schema_design.py"
SPEC = importlib.util.spec_from_file_location("goal5754_design", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Goal5754TypedPhysicalSchemaDesignTest(unittest.TestCase):
    def setUp(self) -> None:
        self.design = MODULE.load_design()

    def assert_rejected(self, probe: object, expected: str) -> None:
        with self.assertRaisesRegex(MODULE.DesignValidationError, expected):
            MODULE.admit_probe(self.design, probe)

    def test_design_self_validation(self) -> None:
        result = MODULE.validate_design(self.design)
        self.assertEqual(result["geometry_family_count"], 2)
        self.assertEqual(result["reference_examples_admitted"], 2)
        self.assertEqual(result["attack_count"], 12)

    def test_custom_aabb_reference_is_admitted(self) -> None:
        probe = MODULE.AdmissionProbe(
            "custom_aabb",
            frozenset({
                "bounds", "make_ray", "intersection", "any_hit", "miss", "finalize"
            }),
        )
        self.assertEqual(MODULE.admit_probe(self.design, probe), "custom_aabb")

    def test_builtin_triangle_reference_is_admitted(self) -> None:
        probe = MODULE.AdmissionProbe(
            "builtin_triangle",
            frozenset({"make_ray", "closest_hit", "miss", "finalize"}),
            frozenset({"primitive_index_u32", "triangle_front_back_hit_kind_u32"}),
        )
        self.assertEqual(MODULE.admit_probe(self.design, probe), "builtin_triangle")

    def test_triangle_user_bounds_or_intersection_rejected(self) -> None:
        self.assert_rejected(
            MODULE.AdmissionProbe(
                "builtin_triangle",
                frozenset({"bounds", "make_ray", "intersection", "closest_hit", "miss", "finalize"}),
            ),
            "forbidden_roles",
        )

    def test_custom_missing_intersection_rejected(self) -> None:
        self.assert_rejected(
            MODULE.AdmissionProbe(
                "custom_aabb",
                frozenset({"bounds", "make_ray", "any_hit", "miss", "finalize"}),
            ),
            "missing_required_roles",
        )

    def test_custom_cannot_request_triangle_channel(self) -> None:
        self.assert_rejected(
            MODULE.AdmissionProbe(
                "custom_aabb",
                frozenset({"bounds", "make_ray", "intersection", "closest_hit", "miss", "finalize"}),
                frozenset({"primitive_index_u32"}),
            ),
            "unavailable_hit_channels",
        )

    def test_user_cannot_write_compiler_owned_triangle_channel(self) -> None:
        self.assert_rejected(
            MODULE.AdmissionProbe(
                "builtin_triangle",
                frozenset({"make_ray", "closest_hit", "miss", "finalize"}),
                frozenset({"primitive_index_u32"}),
                frozenset({"primitive_index_u32"}),
            ),
            "compiler_owned_channel_write",
        )

    def test_zero_template_rejected(self) -> None:
        self.assert_rejected(
            MODULE.AdmissionProbe(
                "builtin_triangle",
                frozenset({"make_ray", "closest_hit", "miss", "finalize"}),
                canonical_template_count=0,
            ),
            "unsupported_physical_schema",
        )

    def test_multiple_canonical_templates_rejected(self) -> None:
        self.assert_rejected(
            MODULE.AdmissionProbe(
                "builtin_triangle",
                frozenset({"make_ray", "closest_hit", "miss", "finalize"}),
                canonical_template_count=2,
            ),
            "ambiguous_canonical_template",
        )

    def test_application_named_dispatch_rejected(self) -> None:
        self.assert_rejected(
            MODULE.AdmissionProbe(
                "builtin_triangle",
                frozenset({"make_ray", "closest_hit", "miss", "finalize"}),
                app_identity_in_dispatch_key=True,
            ),
            "application_identity_in_dispatch_key",
        )

    def test_triangle_index_out_of_range_rejected(self) -> None:
        with self.assertRaisesRegex(MODULE.DesignValidationError, "triangle_index_out_of_range"):
            MODULE.validate_binding(
                self.design,
                MODULE.BindingProbe(
                    "builtin_triangle",
                    vertex_count=4,
                    primitive_count=2,
                    maximum_triangle_index=4,
                    primitive_metadata_count=2,
                    geometry_grade="optix_builtin_semantics",
                ),
            )

    def test_primitive_metadata_count_mismatch_rejected(self) -> None:
        with self.assertRaisesRegex(MODULE.DesignValidationError, "primitive_metadata_count_mismatch"):
            MODULE.validate_binding(
                self.design,
                MODULE.BindingProbe(
                    "builtin_triangle",
                    vertex_count=4,
                    primitive_count=2,
                    maximum_triangle_index=3,
                    primitive_metadata_count=1,
                    geometry_grade="optix_builtin_semantics",
                ),
            )

    def test_cross_device_binding_rejected(self) -> None:
        with self.assertRaisesRegex(MODULE.DesignValidationError, "cross_device_binding"):
            MODULE.validate_binding(
                self.design,
                MODULE.BindingProbe(
                    "custom_aabb",
                    device_identities=("cuda:0", "cuda:1"),
                ),
            )

    def test_stale_epoch_rejected(self) -> None:
        with self.assertRaisesRegex(MODULE.DesignValidationError, "stale_metadata"):
            MODULE.validate_binding(
                self.design,
                MODULE.BindingProbe("custom_aabb", mutation_epoch=2, gas_epoch=1),
            )

    def test_unproved_custom_geometry_cannot_be_relabelled_verified(self) -> None:
        with self.assertRaisesRegex(MODULE.DesignValidationError, "verified_geometry_authority_missing"):
            MODULE.validate_binding(
                self.design,
                MODULE.BindingProbe(
                    "custom_aabb",
                    geometry_grade="verified_contract",
                    geometry_proof_authority_present=False,
                ),
            )

    def test_identity_replay_rejected(self) -> None:
        with self.assertRaisesRegex(MODULE.DesignValidationError, "replay"):
            MODULE.validate_binding(
                self.design,
                MODULE.BindingProbe("custom_aabb", all_identity_digests_match=False),
            )

    def test_claim_boundary_broadening_rejected(self) -> None:
        changed = copy.deepcopy(self.design)
        changed["claim_boundary"]["application_correctness_claimed"] = True
        with self.assertRaisesRegex(MODULE.DesignValidationError, "claim boundary"):
            MODULE.validate_design(changed)

    def test_goal5753_can_never_be_relabelled_as_held_out_pass(self) -> None:
        self.assertFalse(
            self.design["non_negotiable_properties"]["goal5753_may_be_relabelled_as_held_out_pass"]
        )
        example = self.design["reference_examples"]["builtin_triangle_adjacency_reference"]
        self.assertIn("known_regression_not_held_out_pass", example["expected_admission"])


if __name__ == "__main__":
    unittest.main()

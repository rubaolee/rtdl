from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
from pathlib import Path
import unittest

from scripts import goal5789_independent_compatibility_checker as checker


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/goal5789_independent_compatibility_checker.py"


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _seal_certificate(certificate: dict[str, object]) -> None:
    certificate["certificate_sha256"] = checker.certificate_digest(certificate)


def _seal_section(section: dict[str, object]) -> None:
    section["authority_sha256"] = checker.nested_authority_digest(section)


def _seal_authority(authority: dict[str, object]) -> None:
    for name in (
        "semantic_authority",
        "physical_authority",
        "target_authority",
        "instance_authority",
        "evidence_authority",
    ):
        _seal_section(authority[name])
    authority["authority_sha256"] = checker.authority_digest(authority)


def _source_row(kind: str, namespace: str) -> tuple[str, str]:
    path = f"frozen/{namespace}/{kind}.py"
    return path, _sha(path)


def _maps(namespace: str) -> tuple[list[dict[str, object]], dict[str, str]]:
    graph = {
        "encode": (["semantic_input"], ["geometry", "query_state"]),
        "ray": (["query_state"], ["ray"]),
        "trace": (["geometry", "ray"], ["hit_stream"]),
        "continuation": (["hit_stream"], ["candidate_output"]),
        "decode": (["candidate_output"], ["semantic_output"]),
    }
    rows: list[dict[str, object]] = []
    manifest: dict[str, str] = {}
    for kind, (consumes, produces) in graph.items():
        path, source_sha = _source_row(kind, namespace)
        manifest[path] = source_sha
        rows.append(
            {
                "kind": kind,
                "source_pin": path,
                "source_sha256": source_sha,
                "consumes": consumes,
                "produces": produces,
            }
        )
    return rows, manifest


def _policy(kind: str) -> dict[str, str]:
    if kind == "builtin_triangle":
        return {
            "input_type": "oriented_edge_segments_u32",
            "output_type": "checked_u64_scalar",
            "exactness": "exact",
            "tie_policy": "not_applicable_scalar",
            "order_policy": "commutative_checked_reduction",
            "multiplicity": "weighted_hit_multiplicity",
            "numeric_precision": "u32_inputs_checked_u64_accumulator",
            "overflow_policy": "fail_closed_before_wraparound",
        }
    return {
        "input_type": "bounded_relation_query_u32",
        "output_type": "source_ordered_u32_rows",
        "exactness": "exact",
        "tie_policy": "ascending_u32_identifier",
        "order_policy": "source_then_ascending_u32_identifier",
        "multiplicity": "set_per_source",
        "numeric_precision": "binary32_geometry_with_exact_u32_identity",
        "overflow_policy": "fail_closed_on_capacity_or_counter_overflow",
    }


def _roles(kind: str) -> list[dict[str, object]]:
    if kind == "builtin_triangle":
        return [
            {"role": "make_ray", "effects": ["trace_request"]},
            {"role": "any_hit", "effects": ["accept_continue", "ignore"]},
            {"role": "miss", "effects": ["payload"]},
            {"role": "finalize", "effects": ["output"]},
        ]
    return [
        {"role": "bounds", "effects": ["aabb"]},
        {"role": "make_ray", "effects": ["trace_request"]},
        {"role": "intersection", "effects": ["hit", "no_hit"]},
        {"role": "any_hit", "effects": ["accept_continue", "ignore"]},
        {"role": "miss", "effects": ["payload"]},
        {"role": "finalize", "effects": ["output"]},
    ]


def _hit_contract(kind: str) -> tuple[list[str], list[dict[str, object]]]:
    if kind == "builtin_triangle":
        specs = [
            ("primitive_index_u32", "optix_builtin"),
            ("triangle_front_back_hit_kind_u32", "optix_builtin"),
            ("triangle_barycentrics_f32x2", "optix_builtin"),
            ("primitive_metadata_lookup", "compiler_metadata_lookup"),
        ]
    else:
        specs = [("custom_hit_kind", "verified_intersection_effect")]
    return (
        [semantic for semantic, _ in specs],
        [
            {
                "semantic": semantic,
                "producer": producer,
                "read_roles": ["any_hit"],
            }
            for semantic, producer in specs
        ],
    )


def _make_fixture(
    geometry_family: str,
    *,
    namespace: str,
    contract_id: str | None = None,
    encoding_id: str | None = None,
    algorithm_identity: str | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    if geometry_family not in {"custom_aabb", "builtin_triangle"}:
        raise AssertionError(geometry_family)
    contract_id = contract_id or f"semantic.{namespace}.v1"
    encoding_id = encoding_id or f"physical.{namespace}.v1"
    algorithm_identity = algorithm_identity or f"algorithm.{namespace}.v1"
    policy = _policy(geometry_family)
    maps, source_manifest = _maps(namespace)
    spec_pin, spec_sha = _source_row("specification", namespace)
    provider_pin, provider_sha = _source_row("provider", namespace)
    source_manifest[spec_pin] = spec_sha
    source_manifest[provider_pin] = provider_sha
    required_hits, hit_channels = _hit_contract(geometry_family)
    schema_sha = _sha(f"schema:{namespace}")
    semantic = {
        "contract_id": contract_id,
        "algorithm_identity": algorithm_identity,
        "declared_domain_sha256": _sha(f"domain:{namespace}"),
        "policy": deepcopy(policy),
        "required_hit_semantics": required_hits,
        "specification_source_pin": spec_pin,
    }
    physical = {
        "encoding_id": encoding_id,
        "geometry_family": geometry_family,
        "schema_sha256": schema_sha,
        "maps": maps,
        "guarantees": deepcopy(policy),
        "hit_channels": hit_channels,
        "gas": {
            "geometry_family": geometry_family,
            "graph_depth": 1,
            "sbt_record_stride": 1,
            "update_policy": "static",
        },
        "buffers": [
            {
                "semantic": "input_rows",
                "access": "read_only",
                "residency": "device",
                "count_relation": "bound_to_declared_input",
            },
            {
                "semantic": "output_rows",
                "access": "write_only",
                "residency": "device",
                "count_relation": "bounded_by_declared_capacity",
            },
            {
                "semantic": "status",
                "access": "internal_status",
                "residency": "device",
                "count_relation": "one_per_launch",
            },
        ],
        "provider_source_pin": provider_pin,
    }
    callback = {
        "ir_sha256": _sha(f"ir:{namespace}"),
        "effect_digest": _sha(f"effects:{namespace}"),
        "roles": _roles(geometry_family),
        "payload_u32_slots": 4,
        "attribute_u32_slots": 2,
        "trace_depth": 1,
        "callable_depth": 0,
        "total_static_iterations": 64,
    }
    target_sha = _sha(f"target:{namespace}")
    native_sha = _sha(f"native:{namespace}")
    target = {
        "target_sha256": target_sha,
        "provider": "optix",
        "native_sha256": native_sha,
        "capabilities": [
            "optix",
            "bound_program_bundle",
            f"optix_{geometry_family}",
        ],
        "max_payload_u32_slots": 8,
        "max_attribute_u32_slots": 8,
        "max_trace_depth": 2,
        "max_callable_depth": 0,
    }
    input_sha = _sha(f"input:{namespace}")
    bindings = []
    for name, writable in (
        ("input_rows", False),
        ("output_rows", True),
        ("status", True),
    ):
        bindings.append(
            {
                "semantic": name,
                "element_count": 16 if name != "status" else 1,
                "writable": writable,
                "owner_nonce": f"owner-{namespace}",
                "device_id": 0,
                "stream_id": 7,
                "mutation_epoch": 3,
            }
        )
    instance = {
        "input_sha256": input_sha,
        "element_count": 16,
        "capacity": 32,
        "numeric_inputs_finite": True,
        "overflow_observed": False,
        "bindings": bindings,
    }
    oracle_sha = _sha(f"oracle:{namespace}")
    receipt_sha = _sha(f"receipt:{namespace}")
    output_sha = _sha(f"output:{namespace}")
    evidence = {
        "source_pins": deepcopy(source_manifest),
        "independent_oracle_sha256": oracle_sha,
        "behavioral_receipt_sha256": receipt_sha,
        "oracle_output_sha256": output_sha,
        "physical_output_sha256": output_sha,
    }
    candidate = {
        "template_id": f"canonical.{namespace}.v1",
        "canonical": True,
        "algorithm_identity": algorithm_identity,
        "geometry_family": geometry_family,
        "schema_sha256": schema_sha,
        "guarantees": deepcopy(policy),
    }
    certificate: dict[str, object] = {
        "schema": checker.CERTIFICATE_SCHEMA,
        "certificate_sha256": "",
        "semantic_request": semantic,
        "physical_encoding": physical,
        "callback_contract": callback,
        "canonical_candidates": [candidate],
        "target_contract": target,
        "instance_contract": instance,
        "evidence_contract": evidence,
    }
    authority: dict[str, object] = {
        "schema": checker.AUTHORITY_SCHEMA,
        "authority_sha256": "",
        "semantic_authority": {
            "schema": checker.SEMANTIC_AUTHORITY_SCHEMA,
            "authority_sha256": "",
            "contracts": {contract_id: deepcopy(semantic)},
        },
        "physical_authority": {
            "schema": checker.PHYSICAL_AUTHORITY_SCHEMA,
            "authority_sha256": "",
            "encodings": {encoding_id: deepcopy(physical)},
            "source_manifest": deepcopy(source_manifest),
        },
        "target_authority": {
            "schema": checker.TARGET_AUTHORITY_SCHEMA,
            "authority_sha256": "",
            "target_profiles": {target_sha: deepcopy(target)},
        },
        "instance_authority": {
            "schema": checker.INSTANCE_AUTHORITY_SCHEMA,
            "authority_sha256": "",
            "instances": {input_sha: deepcopy(instance)},
        },
        "evidence_authority": {
            "schema": checker.EVIDENCE_AUTHORITY_SCHEMA,
            "authority_sha256": "",
            "oracle_sha256_allowlist": [oracle_sha],
            "receipt_sha256_allowlist": [receipt_sha],
        },
    }
    _seal_certificate(certificate)
    _seal_authority(authority)
    return certificate, authority


def _replace_semantic_authority(
    certificate: dict[str, object], authority: dict[str, object]
) -> None:
    semantic = deepcopy(certificate["semantic_request"])
    authority["semantic_authority"]["contracts"] = {
        semantic["contract_id"]: semantic
    }


def _replace_physical_authority(
    certificate: dict[str, object], authority: dict[str, object]
) -> None:
    physical = deepcopy(certificate["physical_encoding"])
    authority["physical_authority"]["encodings"] = {
        physical["encoding_id"]: physical
    }


def _replace_target_authority(
    certificate: dict[str, object], authority: dict[str, object]
) -> None:
    target = deepcopy(certificate["target_contract"])
    authority["target_authority"]["target_profiles"] = {
        target["target_sha256"]: target
    }


def _replace_instance_authority(
    certificate: dict[str, object], authority: dict[str, object]
) -> None:
    instance = deepcopy(certificate["instance_contract"])
    authority["instance_authority"]["instances"] = {
        instance["input_sha256"]: instance
    }


def _reseal_both(
    certificate: dict[str, object], authority: dict[str, object]
) -> None:
    _seal_certificate(certificate)
    _seal_authority(authority)


class Goal5789SemanticPhysicalContractTest(unittest.TestCase):
    def assertCompatible(
        self, certificate: dict[str, object], authority: dict[str, object]
    ) -> dict[str, object]:
        result = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(
            result["semantic_compatible"]["verdict"], checker.COMPATIBLE, result
        )
        self.assertEqual(result["target_capable"]["verdict"], checker.CAPABLE, result)
        self.assertEqual(
            result["instance_admissible"]["verdict"], checker.ADMISSIBLE, result
        )
        self.assertEqual(
            result["canonical_resolution"]["verdict"],
            "SOLE_CANONICAL_REFERENCE",
            result,
        )
        self.assertTrue(result["reference_admission_complete"], result)
        self.assertFalse(result["executable"])
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(result["performance"]["verdict"], checker.NOT_EVALUATED)
        return result

    def test_two_deep_generic_geometry_examples_are_compatible(self) -> None:
        for family in ("custom_aabb", "builtin_triangle"):
            with self.subTest(family=family):
                certificate, authority = _make_fixture(
                    family, namespace=f"deep_{family}"
                )
                self.assertCompatible(certificate, authority)

    def test_certificate_cannot_rewrite_independent_semantic_authority(self) -> None:
        certificate, authority = _make_fixture(
            "custom_aabb", namespace="authority_separation"
        )
        certificate["semantic_request"]["policy"]["tie_policy"] = "largest_id"
        _seal_certificate(certificate)
        result = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(result["semantic_compatible"]["verdict"], checker.INCOMPATIBLE)
        self.assertIn(
            "semantic_requirement_authority_mismatch",
            result["semantic_compatible"]["reasons"],
        )

    def test_missing_independent_semantic_authority_is_unknown_and_fail_closed(self) -> None:
        certificate, authority = _make_fixture(
            "custom_aabb", namespace="missing_authority"
        )
        authority["semantic_authority"]["contracts"] = {}
        _seal_authority(authority)
        result = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(result["semantic_compatible"]["verdict"], checker.UNKNOWN)
        self.assertIn(
            "semantic_contract_not_in_independent_authority",
            result["semantic_compatible"]["reasons"],
        )
        self.assertFalse(result["reference_admission_complete"])

    def test_target_and_instance_authority_failures_do_not_poison_semantic_judgment(self) -> None:
        certificate, authority = _make_fixture(
            "builtin_triangle", namespace="target_authority_separation"
        )
        authority["target_authority"]["authority_sha256"] = "0" * 64
        authority["authority_sha256"] = checker.authority_digest(authority)
        target_failure = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(
            target_failure["semantic_compatible"]["verdict"], checker.COMPATIBLE
        )
        self.assertEqual(target_failure["target_capable"]["verdict"], checker.INCAPABLE)
        self.assertIn(
            "authority_section_digest_mismatch:target_authority",
            target_failure["target_capable"]["reasons"],
        )
        self.assertEqual(
            target_failure["instance_admissible"]["verdict"], checker.ADMISSIBLE
        )

        certificate, authority = _make_fixture(
            "custom_aabb", namespace="instance_authority_separation"
        )
        del authority["instance_authority"]["instances"]
        authority["authority_sha256"] = checker.authority_digest(authority)
        instance_failure = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(
            instance_failure["semantic_compatible"]["verdict"], checker.COMPATIBLE
        )
        self.assertEqual(instance_failure["target_capable"]["verdict"], checker.CAPABLE)
        self.assertEqual(
            instance_failure["instance_admissible"]["verdict"], checker.UNKNOWN
        )
        self.assertIn(
            "missing:authority.instance_authority.instances",
            instance_failure["instance_admissible"]["reasons"],
        )
        self.assertFalse(instance_failure["reference_admission_complete"])

    def test_deleted_required_field_is_unknown_not_compatible(self) -> None:
        certificate, authority = _make_fixture(
            "custom_aabb", namespace="field_deletion"
        )
        del certificate["semantic_request"]["required_hit_semantics"]
        _seal_certificate(certificate)
        result = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(result["semantic_compatible"]["verdict"], checker.UNKNOWN)
        self.assertIn(
            "missing:semantic_request.required_hit_semantics",
            result["semantic_compatible"]["reasons"],
        )
        self.assertFalse(result["reference_admission_complete"])

    def test_zero_and_multiple_canonical_matches_fail_closed(self) -> None:
        certificate, authority = _make_fixture(
            "builtin_triangle", namespace="candidate_cardinality"
        )
        certificate["canonical_candidates"] = []
        _seal_certificate(certificate)
        zero = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(zero["canonical_resolution"]["verdict"], "UNSUPPORTED")
        self.assertEqual(zero["semantic_compatible"]["verdict"], checker.INCOMPATIBLE)
        self.assertFalse(zero["reference_admission_complete"])

        certificate, authority = _make_fixture(
            "builtin_triangle", namespace="candidate_cardinality"
        )
        duplicate = deepcopy(certificate["canonical_candidates"][0])
        duplicate["template_id"] = "canonical.second.v1"
        certificate["canonical_candidates"].append(duplicate)
        _seal_certificate(certificate)
        multiple = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(multiple["canonical_resolution"]["verdict"], "AMBIGUOUS")
        self.assertEqual(multiple["semantic_compatible"]["verdict"], checker.INCOMPATIBLE)
        self.assertFalse(multiple["reference_admission_complete"])

    def test_matching_names_do_not_override_semantic_mismatch(self) -> None:
        certificate, authority = _make_fixture(
            "custom_aabb",
            namespace="matching_name_mismatch",
            contract_id="matching_name",
            encoding_id="matching_name",
            algorithm_identity="matching_name",
        )
        certificate["physical_encoding"]["guarantees"]["multiplicity"] = (
            "bag_with_duplicates"
        )
        _replace_physical_authority(certificate, authority)
        _reseal_both(certificate, authority)
        result = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(result["semantic_compatible"]["verdict"], checker.INCOMPATIBLE)
        self.assertTrue(
            any(
                reason.startswith("semantic_guarantee_mismatch:multiplicity")
                for reason in result["semantic_compatible"]["reasons"]
            ),
            result,
        )

    def test_valid_behavioral_receipt_cannot_prove_wrong_semantics(self) -> None:
        certificate, authority = _make_fixture(
            "custom_aabb", namespace="receipt_not_semantics"
        )
        receipt = certificate["evidence_contract"]["behavioral_receipt_sha256"]
        self.assertIn(receipt, authority["evidence_authority"]["receipt_sha256_allowlist"])
        certificate["semantic_request"]["policy"]["order_policy"] = (
            "descending_u32_identifier"
        )
        certificate["canonical_candidates"][0]["guarantees"] = deepcopy(
            certificate["semantic_request"]["policy"]
        )
        _replace_semantic_authority(certificate, authority)
        _reseal_both(certificate, authority)
        result = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(result["semantic_compatible"]["verdict"], checker.INCOMPATIBLE)
        self.assertTrue(
            any(
                reason.startswith("semantic_guarantee_mismatch:order_policy")
                for reason in result["semantic_compatible"]["reasons"]
            ),
            result,
        )
        self.assertFalse(result["reference_admission_complete"])

    def test_distinct_incompatibility_classes_report_predeclared_reason(self) -> None:
        cases = []

        certificate, authority = _make_fixture("custom_aabb", namespace="bad_effect")
        certificate["callback_contract"]["roles"][0]["effects"] = ["payload"]
        _seal_certificate(certificate)
        cases.append((certificate, authority, "semantic_compatible", "role_effect_violation:bounds:payload"))

        certificate, authority = _make_fixture("custom_aabb", namespace="bad_hit")
        certificate["physical_encoding"]["hit_channels"][0]["producer"] = "optix_builtin"
        _replace_physical_authority(certificate, authority)
        _reseal_both(certificate, authority)
        cases.append((certificate, authority, "semantic_compatible", "hit_producer_mismatch:custom_hit_kind"))

        certificate, authority = _make_fixture("custom_aabb", namespace="bad_owner")
        certificate["instance_contract"]["bindings"][0]["owner_nonce"] = "other-owner"
        _replace_instance_authority(certificate, authority)
        _reseal_both(certificate, authority)
        cases.append((certificate, authority, "instance_admissible", "buffer_binding_owner_device_stream_epoch_mismatch"))

        certificate, authority = _make_fixture("builtin_triangle", namespace="bad_target")
        certificate["target_contract"]["capabilities"].remove("optix_builtin_triangle")
        _replace_target_authority(certificate, authority)
        _reseal_both(certificate, authority)
        cases.append((certificate, authority, "target_capable", "target_capability_absent:optix_builtin_triangle"))

        certificate, authority = _make_fixture("custom_aabb", namespace="bad_numeric")
        certificate["physical_encoding"]["guarantees"]["numeric_precision"] = "binary16"
        _replace_physical_authority(certificate, authority)
        _reseal_both(certificate, authority)
        cases.append((certificate, authority, "semantic_compatible", "semantic_guarantee_mismatch:numeric_precision:'binary32_geometry_with_exact_u32_identity'!='binary16'"))

        certificate, authority = _make_fixture("custom_aabb", namespace="bad_capacity")
        certificate["instance_contract"]["capacity"] = 8
        _replace_instance_authority(certificate, authority)
        _reseal_both(certificate, authority)
        cases.append((certificate, authority, "instance_admissible", "instance_capacity_exceeded"))

        for certificate, authority, judgment, reason in cases:
            with self.subTest(reason=reason):
                result = checker.evaluate_certificate(certificate, authority)
                self.assertIn(
                    result[judgment]["verdict"],
                    {checker.INCOMPATIBLE, checker.INCAPABLE, checker.INADMISSIBLE},
                    result,
                )
                self.assertIn(reason, result[judgment]["reasons"], result)
                self.assertFalse(result["reference_admission_complete"])

    def test_application_owned_triangle_algorithms_cannot_be_merged_by_output_type(self) -> None:
        certificate, authority = _make_fixture(
            "builtin_triangle",
            namespace="algorithm_identity",
            algorithm_identity="triangle_count.rt_1a2",
        )
        certificate["canonical_candidates"][0]["algorithm_identity"] = (
            "triangle_count.rt_2a1"
        )
        _seal_certificate(certificate)
        result = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(result["canonical_resolution"]["verdict"], "UNSUPPORTED")
        self.assertIn(
            "unsupported_physical_schema:no_canonical_match",
            result["semantic_compatible"]["reasons"],
        )

    def test_buffer_count_relations_and_hit_readers_are_enforced(self) -> None:
        certificate, authority = _make_fixture(
            "custom_aabb", namespace="count_relation"
        )
        certificate["instance_contract"]["bindings"][0]["element_count"] = 15
        _replace_instance_authority(certificate, authority)
        _reseal_both(certificate, authority)
        result = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(result["instance_admissible"]["verdict"], checker.INADMISSIBLE)
        self.assertIn(
            "buffer_input_count_mismatch:input_rows",
            result["instance_admissible"]["reasons"],
        )

        certificate, authority = _make_fixture(
            "builtin_triangle", namespace="missing_hit_reader"
        )
        certificate["physical_encoding"]["hit_channels"][0]["read_roles"] = [
            "closest_hit"
        ]
        _replace_physical_authority(certificate, authority)
        _reseal_both(certificate, authority)
        result = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(result["semantic_compatible"]["verdict"], checker.INCOMPATIBLE)
        self.assertIn(
            "hit_channel_has_no_present_reader:primitive_index_u32",
            result["semantic_compatible"]["reasons"],
        )

    def test_counterfeit_source_identity_is_incompatible(self) -> None:
        certificate, authority = _make_fixture(
            "custom_aabb", namespace="counterfeit_source"
        )
        certificate["physical_encoding"]["maps"][0]["source_sha256"] = _sha(
            "counterfeit"
        )
        _replace_physical_authority(certificate, authority)
        _reseal_both(certificate, authority)
        result = checker.evaluate_certificate(certificate, authority)
        self.assertEqual(result["semantic_compatible"]["verdict"], checker.INCOMPATIBLE)
        self.assertTrue(
            any(
                reason.startswith("source_identity_mismatch:")
                for reason in result["semantic_compatible"]["reasons"]
            ),
            result,
        )

    def test_postfreeze_held_out_encoding_needs_no_checker_special_case(self) -> None:
        held_out_contract = "postfreeze.spatial_encoding.contract.8f0a"
        held_out_encoding = "postfreeze.spatial_encoding.physical.3b91"
        certificate, authority = _make_fixture(
            "custom_aabb",
            namespace="postfreeze_held_out_8f0a",
            contract_id=held_out_contract,
            encoding_id=held_out_encoding,
            algorithm_identity="postfreeze.spatial_encoding.algorithm.a71c",
        )
        checker_source = CHECKER_PATH.read_text(encoding="utf-8")
        self.assertNotIn(held_out_contract, checker_source)
        self.assertNotIn(held_out_encoding, checker_source)
        self.assertCompatible(certificate, authority)

    def test_checker_imports_no_product_or_application_route_and_has_no_app_dispatch(self) -> None:
        source = CHECKER_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".")[0])
        self.assertLessEqual(
            imported_roots,
            {"__future__", "argparse", "hashlib", "json", "pathlib", "re", "typing"},
        )
        lowered = source.lower()
        for forbidden in (
            "particle_tracking",
            "triangle_counting",
            "raydb",
            "librts",
            "x_hd",
            "rtnn",
            "rt_dbscan",
            "rayjoin",
            "rt_barneshut",
            "rtxrmq",
            "arkade",
        ):
            self.assertNotIn(forbidden, lowered)
        self.assertNotIn("import rtdsl", lowered)
        self.assertNotIn("lowering_selector", lowered)


if __name__ == "__main__":
    unittest.main()

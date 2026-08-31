from __future__ import annotations

import ast
import base64
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scripts import goal5789_independent_compatibility_checker as checker
from scripts import goal5793_x1_generic_examiner as examiner
from scripts import goal5793_x1_independent_product_recount as independent_product
from scripts.goal5793_x1_canonical import canonical_digest
from rtdsl.v4_semantic_physical_admission import (
    AdmissionRuleId,
    evaluate_semantic_physical_admission,
)


EXAMINER_PATH = ROOT / "scripts/goal5793_x1_generic_examiner.py"


def _load_frozen_fixture_module():
    path = ROOT / "tests/goal5789_semantic_physical_contract_test.py"
    spec = importlib.util.spec_from_file_location("goal5789_frozen_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FROZEN = _load_frozen_fixture_module()


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _reseal(certificate: dict[str, object], authority: dict[str, object]) -> None:
    certificate["certificate_sha256"] = checker.certificate_digest(certificate)
    for name in (
        "semantic_authority",
        "physical_authority",
        "target_authority",
        "instance_authority",
        "evidence_authority",
    ):
        authority[name]["authority_sha256"] = checker.nested_authority_digest(
            authority[name]
        )
    authority["authority_sha256"] = checker.authority_digest(authority)


def _input(namespace: str = "x1_generic") -> dict[str, object]:
    certificate, authority = FROZEN._make_fixture(
        "custom_aabb", namespace=namespace
    )
    semantic_ref = certificate["semantic_request"]
    physical_ref = certificate["physical_encoding"]
    callback_ref = certificate["callback_contract"]
    target_ref = certificate["target_contract"]
    evidence_ref = certificate["evidence_contract"]
    orientation_sha = _sha(f"orientation:{namespace}")
    buffers_sha = canonical_digest(
        physical_ref["buffers"],
        domain="rtdl.goal5793.x1.reference_buffer_contract",
        version=1,
        projection="goal5789_v1.physical_encoding.buffers",
    )["sha256"]
    maps = [
        {
            "kind": item["kind"],
            "source_id": item["source_pin"],
            "source_sha256": item["source_sha256"],
            "consumes": deepcopy(item["consumes"]),
            "produces": deepcopy(item["produces"]),
        }
        for item in physical_ref["maps"]
    ]
    source_manifest = {
        item["source_pin"]: evidence_ref["source_pins"][item["source_pin"]]
        for item in physical_ref["maps"]
    }
    semantic = {
        "contract_id": semantic_ref["contract_id"],
        "algorithm_identity": semantic_ref["algorithm_identity"],
        "declared_domain_sha256": semantic_ref["declared_domain_sha256"],
        "policy": deepcopy(semantic_ref["policy"]),
        "required_hit_semantics": deepcopy(semantic_ref["required_hit_semantics"]),
        "orientation_contract_sha256": orientation_sha,
        "specification_source_sha256": evidence_ref["source_pins"][
            semantic_ref["specification_source_pin"]
        ],
    }
    physical = {
        "encoding_id": physical_ref["encoding_id"],
        "supported_algorithm_identity": semantic_ref["algorithm_identity"],
        "supported_domain_sha256": semantic_ref["declared_domain_sha256"],
        "orientation_contract_sha256": orientation_sha,
        "geometry_family": physical_ref["geometry_family"],
        "schema_sha256": physical_ref["schema_sha256"],
        "callback_ir_sha256": callback_ref["ir_sha256"],
        "effect_digest": callback_ref["effect_digest"],
        "guarantees": deepcopy(physical_ref["guarantees"]),
        "maps": maps,
        "hit_semantics": [item["semantic"] for item in physical_ref["hit_channels"]],
        "gas_graph_depth": physical_ref["gas"]["graph_depth"],
        "gas_sbt_record_stride": physical_ref["gas"]["sbt_record_stride"],
        "gas_update_policy": physical_ref["gas"]["update_policy"],
        "buffer_contract_sha256": buffers_sha,
        "required_target_capabilities": [
            "optix",
            "bound_program_bundle",
            "optix_custom_aabb",
        ],
        "source_manifest": source_manifest,
    }
    candidates = [
        {
            **deepcopy(certificate["canonical_candidates"][0]),
            "declared_domain_sha256": semantic_ref["declared_domain_sha256"],
            "orientation_contract_sha256": orientation_sha,
        }
    ]
    live_binding = {
        "callback_ir_sha256": callback_ref["ir_sha256"],
        "effect_digest": callback_ref["effect_digest"],
        "family_schema_sha256": physical_ref["schema_sha256"],
        "target_sha256": target_ref["target_sha256"],
        "target_provider": target_ref["provider"],
        "target_capabilities": deepcopy(target_ref["capabilities"]),
        "canonical_artifact_sha256": target_ref["native_sha256"],
        "canonical_template_id": candidates[0]["template_id"],
        "family_authority_sha256": _sha(f"family-authority:{namespace}"),
        "family_authority_nonce": f"nonce-{namespace}",
    }
    return {
        "schema": examiner.INPUT_SCHEMA,
        "semantic_requirement": semantic,
        "physical_guarantee": physical,
        "live_binding": live_binding,
        "canonical_candidates": candidates,
        "reference_certificate": certificate,
        "reference_authority": authority,
    }


class Goal5793X1GenericExaminerTest(unittest.TestCase):
    def assertProductParity(self, payload: dict[str, object]) -> None:
        product = evaluate_semantic_physical_admission(
            deepcopy(payload["semantic_requirement"]),
            deepcopy(payload["physical_guarantee"]),
            live_binding=deepcopy(payload["live_binding"]),
            canonical_candidates=deepcopy(payload["canonical_candidates"]),
        ).to_dict()
        independent = independent_product.evaluate_product_schema(
            deepcopy(payload["semantic_requirement"]),
            deepcopy(payload["physical_guarantee"]),
            live_binding=deepcopy(payload["live_binding"]),
            canonical_candidates=deepcopy(payload["canonical_candidates"]),
        )
        product_projection = (
            product["verdict"],
            product["matching_candidate_count"],
            product["canonical_template_id"],
            product["executable"],
        )
        independent_projection = (
            independent["verdict"],
            independent["matching_candidate_count"],
            independent["canonical_template_id"],
            independent["executable"],
        )
        self.assertEqual(product_projection, independent_projection, (product, independent))

    def test_compatible_dual_path_and_inert_result(self) -> None:
        result = examiner._examine_declaration_core(_input())
        self.assertEqual(result["status"], "VALID_LAYERED_EXAMINATION", result)
        self.assertEqual(result["final_verdict"], checker.COMPATIBLE, result)
        self.assertFalse(result["executable"])
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["performance_evaluated"])
        self.assertEqual(len(result["result_sha256"]), 64)

    def test_coherent_incompatible_declaration_agrees(self) -> None:
        payload = _input("coherent_bad")
        bad = "bag_with_duplicates"
        payload["physical_guarantee"]["guarantees"]["multiplicity"] = bad
        certificate = payload["reference_certificate"]
        authority = payload["reference_authority"]
        certificate["physical_encoding"]["guarantees"]["multiplicity"] = bad
        encoding_id = certificate["physical_encoding"]["encoding_id"]
        authority["physical_authority"]["encodings"][encoding_id] = deepcopy(
            certificate["physical_encoding"]
        )
        _reseal(certificate, authority)
        result = examiner._examine_declaration_core(payload)
        self.assertEqual(result["status"], "VALID_LAYERED_EXAMINATION", result)
        self.assertEqual(result["final_verdict"], checker.INCOMPATIBLE, result)

    def test_unused_product_source_remains_scientific_incompatible_not_crosswalk_infra(self) -> None:
        payload = _input("unused_source")
        path = "frozen/unused_source/extra.py"
        digest = _sha(path)
        payload["physical_guarantee"]["source_manifest"][path] = digest
        certificate = payload["reference_certificate"]
        authority = payload["reference_authority"]
        certificate["evidence_contract"]["source_pins"][path] = digest
        authority["physical_authority"]["source_manifest"][path] = digest
        _reseal(certificate, authority)
        result = examiner._examine_declaration_core(payload)
        self.assertEqual(result["status"], "VALID_LAYERED_EXAMINATION", result)
        self.assertEqual(result["final_verdict"], checker.INCOMPATIBLE, result)
        self.assertEqual(
            result["product_result"]["verdict"],
            result["independent_product_recount"]["verdict"],
        )

    def test_product_recount_disagreement_is_infrastructure_invalid(self) -> None:
        payload = _input("disagreement")
        counterfeit = {
            "verdict": checker.INCOMPATIBLE,
            "unknown_reasons": [],
            "incompatible_reasons": ["hostile_counterfeit"],
            "matching_candidate_count": 0,
            "canonical_template_id": None,
            "executable": False,
        }
        product_module, reference_module, _ = examiner._load_scientific_modules()
        fake_recount = SimpleNamespace(
            evaluate_product_schema=lambda *args, **kwargs: counterfeit
        )
        with patch.object(
            examiner,
            "_load_scientific_modules",
            return_value=(product_module, reference_module, fake_recount),
        ):
            result = examiner._examine_declaration_core(payload)
        self.assertEqual(result["status"], examiner.DISAGREEMENT, result)
        self.assertIsNone(result["final_verdict"])

    def test_product_only_extension_axes_are_independently_recounted(self) -> None:
        mutations = (
            ("physical_guarantee", "supported_algorithm_identity", "other.algorithm"),
            ("physical_guarantee", "supported_domain_sha256", _sha("other-domain")),
            ("physical_guarantee", "orientation_contract_sha256", _sha("other-orientation")),
            ("canonical_candidates", 0, "declared_domain_sha256", _sha("candidate-domain")),
            ("canonical_candidates", 0, "orientation_contract_sha256", _sha("candidate-orientation")),
            ("live_binding", "callback_ir_sha256", _sha("other-callback")),
            ("live_binding", "effect_digest", _sha("other-effects")),
            ("live_binding", "family_schema_sha256", _sha("other-schema")),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                payload = _input("extension_axis")
                if mutation[0] == "canonical_candidates":
                    payload[mutation[0]][mutation[1]][mutation[2]] = mutation[3]
                else:
                    payload[mutation[0]][mutation[1]] = mutation[2]
                result = examiner._examine_declaration_core(payload)
                self.assertEqual(result["status"], "VALID_LAYERED_EXAMINATION", result)
                self.assertEqual(result["final_verdict"], checker.INCOMPATIBLE, result)
                self.assertEqual(
                    result["product_result"]["verdict"],
                    result["independent_product_recount"]["verdict"],
                    result,
                )

    def test_product_evaluator_exception_is_infrastructure_invalid(self) -> None:
        _, reference_module, recount_module = examiner._load_scientific_modules()

        def raise_product(*args, **kwargs):
            del args, kwargs
            raise RuntimeError("hostile product exception")

        fake_product = SimpleNamespace(
            evaluate_semantic_physical_admission=raise_product
        )
        with patch.object(
            examiner,
            "_load_scientific_modules",
            return_value=(fake_product, reference_module, recount_module),
        ):
            result = examiner._examine_declaration_core(_input("product_exception"))
        self.assertEqual(result["status"], examiner.INFRA_INVALID, result)
        self.assertTrue(
            any("product_evaluator_exception:RuntimeError" in x for x in result["reasons"])
        )

    def test_plain_integer_and_unique_string_sequence_parity_regressions(self) -> None:
        mutations = (
            ("physical_guarantee", "gas_graph_depth", True),
            ("physical_guarantee", "gas_graph_depth", 1.0),
            ("physical_guarantee", "gas_sbt_record_stride", True),
            ("physical_guarantee", "gas_sbt_record_stride", 1.0),
        )
        for section, field, value in mutations:
            with self.subTest(field=field, value=value):
                payload = _input("plain_int")
                payload[section][field] = value
                self.assertProductParity(payload)
        duplicate_fields = (
            ("semantic_requirement", "required_hit_semantics"),
            ("physical_guarantee", "hit_semantics"),
            ("physical_guarantee", "required_target_capabilities"),
            ("live_binding", "target_capabilities"),
        )
        for section, field in duplicate_fields:
            with self.subTest(section=section, field=field):
                payload = _input("duplicate_string")
                payload[section][field].append(payload[section][field][0])
                self.assertProductParity(payload)

    def test_exhaustive_schema_leaf_type_container_and_none_parity(self) -> None:
        invalid_values = (None, [], {}, True, 1, 1.0, "", b"x", ["x", "x"], {"x": "y"})
        baseline = _input("exhaustive")
        section_names = (
            "semantic_requirement",
            "physical_guarantee",
            "live_binding",
        )
        checked = 0
        for section_name in section_names:
            for field in tuple(baseline[section_name]):
                for value in invalid_values:
                    with self.subTest(section=section_name, field=field, value=repr(value)):
                        payload = _input("exhaustive")
                        payload[section_name][field] = deepcopy(value)
                        self.assertProductParity(payload)
                        checked += 1
                with self.subTest(section=section_name, field=field, mutation="missing"):
                    payload = _input("exhaustive")
                    del payload[section_name][field]
                    self.assertProductParity(payload)
                    checked += 1
            with self.subTest(section=section_name, mutation="extra"):
                payload = _input("exhaustive")
                payload[section_name]["hostile_extra"] = "x"
                self.assertProductParity(payload)
                checked += 1

        for field in tuple(baseline["canonical_candidates"][0]):
            for value in invalid_values:
                with self.subTest(section="candidate", field=field, value=repr(value)):
                    payload = _input("exhaustive")
                    payload["canonical_candidates"][0][field] = deepcopy(value)
                    self.assertProductParity(payload)
                    checked += 1
            with self.subTest(section="candidate", field=field, mutation="missing"):
                payload = _input("exhaustive")
                del payload["canonical_candidates"][0][field]
                self.assertProductParity(payload)
                checked += 1
        payload = _input("exhaustive")
        payload["canonical_candidates"][0]["hostile_extra"] = "x"
        self.assertProductParity(payload)
        checked += 1

        for index, field in enumerate(tuple(baseline["physical_guarantee"]["maps"][0])):
            del index
            for value in invalid_values:
                with self.subTest(section="map", field=field, value=repr(value)):
                    payload = _input("exhaustive")
                    payload["physical_guarantee"]["maps"][0][field] = deepcopy(value)
                    self.assertProductParity(payload)
                    checked += 1
            with self.subTest(section="map", field=field, mutation="missing"):
                payload = _input("exhaustive")
                del payload["physical_guarantee"]["maps"][0][field]
                self.assertProductParity(payload)
                checked += 1
        payload = _input("exhaustive")
        payload["physical_guarantee"]["maps"][0]["hostile_extra"] = "x"
        self.assertProductParity(payload)
        checked += 1

        for section_name, field in (
            ("semantic_requirement", "required_hit_semantics"),
            ("physical_guarantee", "hit_semantics"),
            ("physical_guarantee", "required_target_capabilities"),
            ("live_binding", "target_capabilities"),
        ):
            payload = _input("exhaustive")
            payload[section_name][field].append(payload[section_name][field][0])
            self.assertProductParity(payload)
            checked += 1
            payload = _input("exhaustive")
            payload[section_name][field].reverse()
            self.assertProductParity(payload)
            checked += 1

        payload = _input("exhaustive")
        payload["physical_guarantee"]["maps"].append(
            deepcopy(payload["physical_guarantee"]["maps"][0])
        )
        self.assertProductParity(payload)
        checked += 1
        payload = _input("exhaustive")
        payload["physical_guarantee"]["maps"].reverse()
        self.assertProductParity(payload)
        checked += 1
        payload = _input("exhaustive")
        duplicate = deepcopy(payload["canonical_candidates"][0])
        duplicate["template_id"] = "canonical.exhaustive.second"
        payload["canonical_candidates"].append(duplicate)
        self.assertProductParity(payload)
        checked += 1

        for missing in (
            "semantic_requirement",
            "physical_guarantee",
            "live_binding",
            "canonical_candidates",
        ):
            with self.subTest(direct_none=missing):
                payload = _input("exhaustive")
                payload[missing] = None
                self.assertProductParity(payload)
                checked += 1
        self.assertGreaterEqual(checked, 500)

    def test_all_35_reachable_declaration_rules_exact_and_parity(self) -> None:
        """Reach 35 declaration rules; do not misreport authority-only as replayed."""

        cases = {}

        def register(rule_id, mutation):
            cases[rule_id] = mutation

        register("SP000_MALFORMED_INPUT", lambda p: p["semantic_requirement"].__setitem__("contract_id", []))
        register("SP001_SEMANTIC_REQUIREMENT_UNKNOWN", lambda p: p.__setitem__("semantic_requirement", None))
        register("SP002_PHYSICAL_GUARANTEE_UNKNOWN", lambda p: p.__setitem__("physical_guarantee", None))
        register("SP003_LIVE_BINDING_UNKNOWN", lambda p: p.__setitem__("live_binding", None))
        register("SP004_CANONICAL_CANDIDATES_UNKNOWN", lambda p: p.__setitem__("canonical_candidates", None))
        register("SP010_IDENTITY_INVALID", lambda p: p["semantic_requirement"].__setitem__("contract_id", "BAD"))
        register("SP011_DIGEST_INVALID", lambda p: p["semantic_requirement"].__setitem__("declared_domain_sha256", "x"))
        register("SP020_POLICY_INCOMPLETE", lambda p: p["semantic_requirement"]["policy"].pop("exactness"))
        register("SP021_POLICY_UNSUPPORTED_FIELD", lambda p: p["semantic_requirement"]["policy"].__setitem__("extra", "x"))
        register("SP023_REQUIRED_HIT_SEMANTIC_MISSING", lambda p: p["physical_guarantee"].__setitem__("hit_semantics", []))
        for rule_id, field in (
            ("SP024_EXACTNESS_POLICY_MISMATCH", "exactness"),
            ("SP025_TIE_POLICY_MISMATCH", "tie_policy"),
            ("SP026_MULTIPLICITY_POLICY_MISMATCH", "multiplicity"),
            ("SP027_OVERFLOW_POLICY_MISMATCH", "overflow_policy"),
            ("SP028_NUMERIC_PRECISION_POLICY_MISMATCH", "numeric_precision"),
            ("SP029_ORDER_POLICY_MISMATCH", "order_policy"),
            ("SP035_INPUT_TYPE_POLICY_MISMATCH", "input_type"),
            ("SP036_OUTPUT_TYPE_POLICY_MISMATCH", "output_type"),
        ):
            register(
                rule_id,
                lambda p, field=field: p["physical_guarantee"]["guarantees"].__setitem__(field, "hostile"),
            )
        register("SP030_MAP_STAGE_UNKNOWN", lambda p: p["physical_guarantee"]["maps"].pop())
        register("SP031_MAP_STAGE_DUPLICATE", lambda p: p["physical_guarantee"]["maps"].append(deepcopy(p["physical_guarantee"]["maps"][0])))
        register("SP032_MAP_GRAPH_MISMATCH", lambda p: p["physical_guarantee"]["maps"][0].__setitem__("produces", ["wrong"]))

        def remove_used_source(payload):
            source = payload["physical_guarantee"]["maps"][0]["source_id"]
            payload["physical_guarantee"]["source_manifest"].pop(source)

        register("SP033_MAP_SOURCE_UNKNOWN", remove_used_source)
        register("SP034_MAP_SOURCE_DIGEST_MISMATCH", lambda p: p["physical_guarantee"]["maps"][0].__setitem__("source_sha256", _sha("valid-other-source")))
        register("SP037_ALGORITHM_IDENTITY_MISMATCH", lambda p: p["physical_guarantee"].__setitem__("supported_algorithm_identity", "other.algorithm"))
        register("SP038_DECLARED_DOMAIN_MISMATCH", lambda p: p["physical_guarantee"].__setitem__("supported_domain_sha256", _sha("other-domain")))
        register("SP039_ORIENTATION_CONTRACT_MISMATCH", lambda p: p["physical_guarantee"].__setitem__("orientation_contract_sha256", _sha("other-orientation")))
        register("SP040_GAS_CONTRACT_MISMATCH", lambda p: p["physical_guarantee"].__setitem__("gas_graph_depth", 2))
        register("SP041_MAP_SOURCE_UNUSED", lambda p: p["physical_guarantee"]["source_manifest"].__setitem__("unused", _sha("unused")))
        register("SP050_CALLBACK_BINDING_MISMATCH", lambda p: p["live_binding"].__setitem__("callback_ir_sha256", _sha("other-callback")))
        register("SP051_SCHEMA_BINDING_MISMATCH", lambda p: p["live_binding"].__setitem__("family_schema_sha256", _sha("other-schema")))
        register("SP052_TARGET_PROVIDER_MISMATCH", lambda p: p["live_binding"].__setitem__("target_provider", "cuda"))
        register("SP053_TARGET_CAPABILITY_MISSING", lambda p: p["live_binding"].__setitem__("target_capabilities", []))
        register("SP060_CANONICAL_CANDIDATE_UNSUPPORTED", lambda p: p["canonical_candidates"][0].__setitem__("canonical", False))

        def add_matching_candidate(payload):
            second = deepcopy(payload["canonical_candidates"][0])
            second["template_id"] = "canonical.second.v1"
            payload["canonical_candidates"].append(second)

        register("SP061_CANONICAL_CANDIDATE_AMBIGUOUS", add_matching_candidate)
        register("SP062_CANONICAL_LIVE_BINDING_MISMATCH", lambda p: p["live_binding"].__setitem__("canonical_template_id", "canonical.other.v1"))

        classification = examiner.DECLARATION_RULE_CLASSIFICATION
        self.assertEqual(set(cases), set(classification["REACHED"]))
        enum_rules = {item.value for item in AdmissionRuleId}
        classified = set().union(*map(set, classification.values()))
        self.assertEqual(classified, enum_rules)
        self.assertEqual(len(enum_rules), 39)
        self.assertEqual(
            classification["UNREACHABLE_BY_CURRENT_CODE"],
            ("SP022_SEMANTIC_GUARANTEE_MISMATCH",),
        )
        self.assertEqual(set(classification["AUTHORITY_ONLY"]), {
            "SP063_PHYSICAL_AUTHORITY_NONCANONICAL",
            "SP070_AUTHORITY_NOT_LIVE",
            "SP071_AUTHORITY_BINDING_DRIFT",
        })

        reached = set()
        for rule_id, mutation in cases.items():
            with self.subTest(rule_id=rule_id):
                payload = _input(f"rule_{rule_id.lower()}")
                mutation(payload)
                product = evaluate_semantic_physical_admission(
                    deepcopy(payload["semantic_requirement"]),
                    deepcopy(payload["physical_guarantee"]),
                    live_binding=deepcopy(payload["live_binding"]),
                    canonical_candidates=deepcopy(payload["canonical_candidates"]),
                ).to_dict()
                recount = independent_product.evaluate_product_schema(
                    deepcopy(payload["semantic_requirement"]),
                    deepcopy(payload["physical_guarantee"]),
                    live_binding=deepcopy(payload["live_binding"]),
                    canonical_candidates=deepcopy(payload["canonical_candidates"]),
                )
                product_projection = (
                    product["verdict"], product["matching_candidate_count"],
                    product["canonical_template_id"], product["executable"],
                )
                recount_projection = (
                    recount["verdict"], recount["matching_candidate_count"],
                    recount["canonical_template_id"], recount["executable"],
                )
                self.assertEqual(product_projection, recount_projection)
                observed = {row["rule_id"] for row in product["findings"]}
                self.assertIn(rule_id, observed, product)
                reached.add(rule_id)
        self.assertEqual(reached, set(classification["REACHED"]))

    def test_absent_declaration_roots_preserve_product_unknown_without_fake_v1(self) -> None:
        expected = {
            "semantic_requirement": "SP001_SEMANTIC_REQUIREMENT_UNKNOWN",
            "physical_guarantee": "SP002_PHYSICAL_GUARANTEE_UNKNOWN",
            "live_binding": "SP003_LIVE_BINDING_UNKNOWN",
            "canonical_candidates": "SP004_CANONICAL_CANDIDATES_UNKNOWN",
        }
        for root, rule_id in expected.items():
            with self.subTest(root=root):
                payload = _input(f"absent_{root}")
                payload[root] = None
                result = examiner._examine_declaration_core(payload)
                self.assertEqual(
                    result["status"], "VALID_LAYERED_EXAMINATION", result
                )
                self.assertEqual(result["final_verdict"], "UNKNOWN", result)
                self.assertEqual(
                    result["product_result"]["findings"][0]["rule_id"],
                    rule_id,
                    result,
                )
                self.assertEqual(
                    result["product_result"]["verdict"],
                    result["independent_product_recount"]["verdict"],
                    result,
                )
                self.assertEqual(
                    result["reference_overlap_result"]["status"],
                    "NOT_EXPRESSIBLE_IN_GOAL5789_V1__NOT_EVALUATED",
                )
                self.assertEqual(
                    result["reference_overlap_result"][
                        "absent_product_declaration_roots"
                    ],
                    [root],
                )
                self.assertEqual(result["reference_overlap_verdict"], "NOT_EVALUATED")
                self.assertIsNone(result["crosswalk_sha256"])

    def test_same_verdict_wrong_count_or_template_is_infrastructure_invalid(self) -> None:
        payload = _input("projection_counterfeit")
        baseline = independent_product.evaluate_product_schema(
            payload["semantic_requirement"],
            payload["physical_guarantee"],
            live_binding=payload["live_binding"],
            canonical_candidates=payload["canonical_candidates"],
        )
        for field, value in (
            ("matching_candidate_count", 99),
            ("canonical_template_id", "canonical.counterfeit.v1"),
            ("executable", True),
        ):
            with self.subTest(field=field):
                counterfeit = deepcopy(baseline)
                counterfeit[field] = value
                product_module, reference_module, _ = examiner._load_scientific_modules()
                fake_recount = SimpleNamespace(
                    evaluate_product_schema=lambda *args, **kwargs: counterfeit
                )
                with patch.object(
                    examiner,
                    "_load_scientific_modules",
                    return_value=(product_module, reference_module, fake_recount),
                ):
                    result = examiner._examine_declaration_core(payload)
                self.assertEqual(result["status"], examiner.DISAGREEMENT, result)

    def test_outer_candidate_domain_is_sequence_or_none_only(self) -> None:
        for value in (False, True, 0, 1, 1.0, {}, "candidate"):
            with self.subTest(value=repr(value)):
                payload = _input("outer_candidate_domain")
                payload["canonical_candidates"] = value
                result = examiner._examine_declaration_core(payload)
                self.assertEqual(result["status"], examiner.INFRA_INVALID, result)

    def test_preloaded_fake_scientific_modules_cannot_control_fresh_exam(self) -> None:
        payload = _input("preload_attack")
        payload["physical_guarantee"]["gas_graph_depth"] = 99
        payload["reference_certificate"]["physical_encoding"]["gas"][
            "graph_depth"
        ] = 99
        packed = base64.b64encode(
            zlib.compress(json.dumps(payload, sort_keys=True).encode("utf-8"))
        ).decode("ascii")
        code = f"""
import base64, json, sys, types, zlib
import scripts

class Decision:
    def to_dict(self):
        return {{'verdict':'COMPATIBLE_FOR_DECLARED_DOMAIN','findings':[],
                 'matching_candidate_count':1,'canonical_template_id':'canonical.preload_attack.v1',
                 'executable':False}}

fake_product = types.ModuleType('rtdsl.v4_semantic_physical_admission')
fake_product.evaluate_semantic_physical_admission = lambda *a, **k: Decision()
fake_reference = types.ModuleType('scripts.goal5789_independent_compatibility_checker')
fake_reference.COMPATIBLE = 'COMPATIBLE_FOR_DECLARED_DOMAIN'
fake_reference.INCOMPATIBLE = 'INCOMPATIBLE'
fake_reference.UNKNOWN = 'UNKNOWN'
fake_reference.CAPABLE = 'TARGET_CAPABLE'
fake_reference.INCAPABLE = 'TARGET_INCAPABLE'
fake_reference.evaluate_certificate = lambda *a, **k: {{
    'semantic_compatible':{{'verdict':fake_reference.COMPATIBLE}},
    'target_capable':{{'verdict':fake_reference.CAPABLE}},
    'canonical_resolution':{{'verdict':'SOLE_CANONICAL_REFERENCE'}},
}}
fake_recount = types.ModuleType('scripts.goal5793_x1_independent_product_recount')
fake_recount.evaluate_product_schema = lambda *a, **k: {{
    'verdict':'COMPATIBLE_FOR_DECLARED_DOMAIN','matching_candidate_count':1,
    'canonical_template_id':'canonical.preload_attack.v1','executable':False,
}}
sys.modules[fake_product.__name__] = fake_product
sys.modules[fake_reference.__name__] = fake_reference
sys.modules[fake_recount.__name__] = fake_recount
setattr(scripts, 'goal5789_independent_compatibility_checker', fake_reference)
setattr(scripts, 'goal5793_x1_independent_product_recount', fake_recount)
from scripts import goal5793_x1_generic_examiner as examiner
payload = json.loads(zlib.decompress(base64.b64decode('{packed}')))
result = examiner._examine_declaration_core(payload)
if result.get('final_verdict') == 'COMPATIBLE_FOR_DECLARED_DOMAIN':
    raise SystemExit('preloaded fake modules controlled the result')
print(result.get('status'), result.get('final_verdict'))
"""
        environment = dict(**__import__("os").environ)
        environment["PYTHONPATH"] = str(ROOT / "src") + __import__("os").pathsep + str(ROOT)
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)

    def test_forbidden_metadata_is_rejected_before_evaluation(self) -> None:
        for key in sorted(examiner.FORBIDDEN_DECISION_INPUT_KEYS):
            with self.subTest(key=key):
                payload = _input(f"forbidden_{key}")
                payload["reference_certificate"][key] = "tempting"
                result = examiner._examine_declaration_core(payload)
                self.assertEqual(result["status"], examiner.INFRA_INVALID, result)
                self.assertTrue(
                    any("forbidden_decision_input" in x for x in result["reasons"])
                )

    def test_external_labels_and_mapping_permutation_cannot_change_verdict(self) -> None:
        payload = _input("metadata_invariant")
        first = examiner._examine_declaration_core(payload)
        wrapper_a = {"label": "first", "exam": payload, "outcome_hint": "bad"}
        wrapper_b = {"label": "renamed", "exam": payload, "outcome_hint": "good"}
        second = examiner._examine_declaration_core(wrapper_b["exam"])
        self.assertEqual(first["final_verdict"], second["final_verdict"])
        reversed_payload = dict(reversed(list(wrapper_a["exam"].items())))
        third = examiner._examine_declaration_core(reversed_payload)
        self.assertEqual(first["result_sha256"], third["result_sha256"])

    def test_external_expected_disposition_mutation_leaves_decision_projection_invariant(self) -> None:
        payload = _input("expected_disposition_external")
        external_a = {"expected_disposition": "COMPATIBLE", "exam": payload}
        external_b = {"expected_disposition": "INCOMPATIBLE", "exam": payload}
        result_a = examiner._examine_declaration_core(external_a["exam"])
        result_b = examiner._examine_declaration_core(external_b["exam"])

        def projection(result):
            return (
                result["status"],
                result["final_verdict"],
                result["product_result"]["verdict"],
                result["product_result"]["matching_candidate_count"],
                result["product_result"]["canonical_template_id"],
                result["reference_overlap_verdict"],
                result["crosswalk_sha256"],
            )

        self.assertEqual(projection(result_a), projection(result_b))

    def test_coherent_identity_rename_has_no_dispatch_effect(self) -> None:
        base = examiner._examine_declaration_core(_input("identity_alpha"))
        renamed = examiner._examine_declaration_core(_input("identity_beta"))
        self.assertEqual(base["final_verdict"], checker.COMPATIBLE)
        self.assertEqual(renamed["final_verdict"], checker.COMPATIBLE)

    def test_ast_has_no_a2_or_application_dispatch(self) -> None:
        source = EXAMINER_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        self.assertFalse(any("goal5789_a2" in name for name in imported))
        lowered = source.lower()
        for forbidden in (
            "particle_tracking",
            "triangle_counting",
            "raydb",
            "rtnn",
            "rt_dbscan",
            "rayjoin",
            "rt_barneshut",
            "rtxrmq",
            "arkade",
        ):
            self.assertNotIn(forbidden, lowered)
        self.assertIn("evaluate_semantic_physical_admission", source)
        self.assertIn("goal5789_independent_compatibility_checker", source)


if __name__ == "__main__":
    unittest.main()

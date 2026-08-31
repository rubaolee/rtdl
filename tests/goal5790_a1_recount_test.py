from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import goal5790_a1_build_evidence as BUILD  # noqa: E402
import goal5790_a1_independent_recount as R  # noqa: E402
import goal5790_a1_rejected_encoding_cases as CPU  # noqa: E402


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _bundle_id(name: str) -> int:
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & ((1 << 64) - 1)
    return value


def _seal(value: dict, field: str) -> dict:
    result = copy.deepcopy(value)
    result.pop(field, None)
    result[field] = R.digest(result)
    return result


def _json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def _semantic_authority(case: dict) -> dict:
    policy = copy.deepcopy(case["semantic_authority"]["policy"])
    contract_id = case["semantic_authority"]["contract_id"]
    policy["input_type"] = "frozen_minimal_witness:" + contract_id
    policy["output_type"] = "declared_semantic_output:" + contract_id
    requirement = {
        "schema": "rtdl.v4.semantic_requirement.v1",
        "contract_id": case["semantic_authority"]["contract_id"],
        "algorithm_identity": "goal5790_a1." + case["case_id"],
        "declared_domain_sha256": R.digest(case["minimal_witness"]),
        "policy": policy,
        "required_hit_semantics": ["bound_hit_stream"],
        "orientation_contract_sha256": _sha(case["case_id"] + ":orientation"),
        "specification_source_sha256": case["semantic_authority"][
            "oracle_source_sha256"],
    }
    authority_sha = R.digest({
        "schema": R.SEMANTIC_AUTHORITY_SCHEMA,
        "requirement_sha256": R.digest(requirement),
        "specification_source_sha256": requirement[
            "specification_source_sha256"],
        "oracle_source_sha256": case["semantic_authority"][
            "oracle_source_sha256"],
        "issuer_domain": "rtdl.app.goal5790_a1",
    })
    return {
        "schema": R.SEMANTIC_AUTHORITY_SCHEMA,
        "requirement": requirement,
        "oracle_source_sha256": case["semantic_authority"][
            "oracle_source_sha256"],
        "issuer_domain": "rtdl.app.goal5790_a1",
        "authority_sha256": authority_sha,
        "authority_nonce": R.digest({
            "kind": R.SEMANTIC_AUTHORITY_SCHEMA,
            "authority_sha256": authority_sha,
        }),
    }


def _pre_run_snapshot(case: dict, *, classifier_sha: str,
                      target_sha: str, source_manifest: dict[str, str]) -> dict:
    semantic = _semantic_authority(case)
    orientation = semantic["requirement"]["orientation_contract_sha256"]

    def guarantee(tag: str, diagnostic: bool) -> dict:
        policy = copy.deepcopy(case[
            "physical_authority" if diagnostic else "semantic_authority"])
        policy = policy["guarantees" if diagnostic else "policy"]
        contract_id = case["semantic_authority"]["contract_id"]
        policy["input_type"] = "frozen_minimal_witness:" + contract_id
        policy["output_type"] = "declared_semantic_output:" + contract_id
        source_id = next(iter(source_manifest))
        graph = {
            "encode": (["semantic_input"], ["geometry", "query_state"]),
            "ray": (["query_state"], ["ray"]),
            "trace": (["geometry", "ray"], ["hit_stream"]),
            "continuation": (["hit_stream"], ["candidate_output"]),
            "decode": (["candidate_output"], ["semantic_output"]),
        }
        return {
            "schema": "rtdl.v4.physical_guarantee.v1",
            "encoding_id": f"{tag}.encoding.v1",
            "supported_algorithm_identity": semantic["requirement"][
                "algorithm_identity"],
            "supported_domain_sha256": semantic["requirement"][
                "declared_domain_sha256"],
            "orientation_contract_sha256": orientation,
            "geometry_family": case["geometry_family"],
            "schema_sha256": _sha(f"{tag}:schema"),
            "callback_ir_sha256": _sha(f"{tag}:callback"),
            "effect_digest": _sha(f"{tag}:effect"),
            "guarantees": copy.deepcopy(policy),
            "maps": [{
                "kind": kind,
                "source_id": source_id,
                "source_sha256": source_manifest[source_id],
                "consumes": consumes,
                "produces": produces,
            } for kind, (consumes, produces) in graph.items()],
            "hit_semantics": ["bound_hit_stream"],
            "gas_graph_depth": 1, "gas_sbt_record_stride": 1,
            "gas_update_policy": "static",
            "buffer_contract_sha256": _sha(f"{tag}:buffer"),
            "required_target_capabilities": [
                "bound_program_bundle", "optix",
                ("optix_builtin_triangle"
                 if case["geometry_family"] == "builtin_triangle"
                 else "optix_custom_aabb"),
            ],
            "source_manifest": copy.deepcopy(source_manifest),
        }

    def entry(tag: str, diagnostic: bool) -> dict:
        return {
            "entry_id": f"{tag}.entry",
            "guarantee": guarantee(tag, diagnostic),
            "eligibility": ("DIAGNOSTIC_NONREGISTRABLE" if diagnostic
                            else "CANONICAL_PRODUCTION"),
            "canonical_template_id": None if diagnostic else f"{tag}.template",
            "classifier_source_sha256": classifier_sha,
            "source_bytes_manifest_sha256": R.digest(source_manifest),
        }

    canonical_entry = entry("canonical." + case["case_id"], False)
    diagnostic_entry = None if case["case_id"] == R.CASE_IDS[4] else entry(
        "diagnostic." + case["case_id"], True)
    entries = [canonical_entry] + ([] if diagnostic_entry is None
                                   else [diagnostic_entry])
    registry_sha = R.digest({
        "schema": R.PHYSICAL_REGISTRY_SCHEMA,
        "issuer_domain": "rtdsl.compiler.physical_guarantee_registry.v1",
        "registry_source_sha256": classifier_sha,
        "entries": entries,
    })
    registry = {
        "schema": R.PHYSICAL_REGISTRY_SCHEMA,
        "entries": entries,
        "registry_source_sha256": classifier_sha,
        "issuer_domain": "rtdsl.compiler.physical_guarantee_registry.v1",
        "registry_sha256": registry_sha,
        "authority_nonce": R.digest({
            "kind": R.PHYSICAL_REGISTRY_SCHEMA,
            "registry_sha256": registry_sha,
        }),
    }

    def physical_authority(value: dict) -> dict:
        entry_sha = R.digest(value)
        authority_sha = R.digest({
            "schema": R.PHYSICAL_AUTHORITY_SCHEMA,
            "registry_sha256": registry_sha,
            "entry_sha256": entry_sha,
            "entry_id": value["entry_id"],
            "eligibility": value["eligibility"],
        })
        return {
            "schema": R.PHYSICAL_AUTHORITY_SCHEMA,
            "registry_sha256": registry_sha,
            "entry": copy.deepcopy(value),
            "entry_sha256": entry_sha,
            "authority_sha256": authority_sha,
            "authority_nonce": R.digest({
                "kind": R.PHYSICAL_AUTHORITY_SCHEMA,
                "authority_sha256": authority_sha,
                "registry_nonce": registry["authority_nonce"],
            }),
        }

    canonical_authority = physical_authority(canonical_entry)
    diagnostic_authority = (None if diagnostic_entry is None
                            else physical_authority(diagnostic_entry))

    def live(value: dict, tag: str) -> dict:
        guarantee_value = value["entry"]["guarantee"]
        return {
            "family": ("bounded_relation" if case["geometry_family"] == "custom_aabb"
                       else ("triangle_reduction" if case["case_id"]
                             in R.CASE_IDS[2:4] else "builtin_triangle")),
            "callback_ir_sha256": guarantee_value["callback_ir_sha256"],
            "effect_digest": guarantee_value["effect_digest"],
            "schema_sha256": guarantee_value["schema_sha256"],
            "target_sha256": target_sha,
            "artifact_kind": ("plan" if case["case_id"] in R.CASE_IDS[:2]
                              or case["case_id"] == R.CASE_IDS[4]
                              else "contract"),
            "artifact_sha256": _sha(f"{tag}:artifact"),
            "abi_sha256": _sha(f"{tag}:abi"),
            "orientation_contract_sha256": guarantee_value[
                "orientation_contract_sha256"],
            "canonical_template_id": value["entry"]["canonical_template_id"],
            "proof_sha256": _sha(f"{tag}:proof"),
            "family_authority_sha256": _sha(f"{tag}:family-authority"),
            "family_authority_nonce": _sha(f"{tag}:family-nonce"),
        }

    transform = {
        "case_id": case["case_id"],
        "transform_id": case["unsafe_transform"]["transform_id"],
        "unsafe_transform_sha256": R.digest(case["unsafe_transform"]),
        "implementation_path": "scripts/goal5790_a1_home_worker.py",
        "implementation_sha256": classifier_sha,
        "test_only_nonregistrable": True,
        "production_authority_minted": False,
    }
    if case["case_id"] == R.CASE_IDS[2]:
        transform.update({
            "unchecked_u64_kernel_source_sha256": hashlib.sha256(
                R.UNCHECKED_U64_CONTINUATION_SOURCE.encode("utf-8")).hexdigest(),
            "unchecked_u64_kernel_entry":
                "goal5790_a1_unchecked_weighted_sum",
        })
    if case["case_id"] == R.CASE_IDS[5]:
        transform["strict_callback_source_sha256"] = _sha("strict-callback")
    transform = _seal(transform, "transform_authority_sha256")
    attempt = None
    if diagnostic_authority is None:
        attempt = {
            "family": "builtin_triangle",
            "callback_ir_sha256": canonical_authority["entry"]["guarantee"]
                ["callback_ir_sha256"],
            "effect_digest": canonical_authority["entry"]["guarantee"]
                ["effect_digest"],
            "schema_sha256": _sha("swapped-orientation-schema"),
            "target_sha256": target_sha,
            "orientation_authority_sha256": _sha("swapped-orientation"),
            "orientation_author_source_sha256": _sha("orientation-source"),
            "orientation_independent_oracle_sha256": _sha("orientation-oracle"),
            "front_hit_kind": 254, "back_hit_kind": 255,
            "front_hit_selects": "back", "back_hit_selects": "front",
            "verified_family_authority_issued": False,
            "plan_issued": False, "abi_issued": False,
        }
    result = {
        "schema": R.PRE_RUN_AUTHORITIES_SCHEMA,
        "case_id": case["case_id"], "case_sha256": case["case_sha256"],
        "classifier_source_sha256": classifier_sha,
        "semantic_authority": semantic, "physical_registry": registry,
        "canonical_physical_authority": canonical_authority,
        "diagnostic_physical_authority": diagnostic_authority,
        "canonical_live_family": live(canonical_authority, "canonical"),
        "diagnostic_live_family": (None if diagnostic_authority is None
                                   else live(diagnostic_authority, "diagnostic")),
        "diagnostic_early_reject": ({
            "gate": "verify_typed_physical_schema",
            "code": "triangle_orientation_mapping", "path": "triangle",
            "message": "swapped orientation",
        } if diagnostic_authority is None else None),
        "diagnostic_family_attempt": attempt,
        "diagnostic_transform_authority": transform,
        "low_level_compiler_call_count": 0,
        "native_prepare_call_count": 0, "native_execute_call_count": 0,
        "traversal_launch_count": 0,
    }
    return _seal(result, "snapshot_sha256")


def _physical(case: dict, live: dict, scientific: dict, *, diagnostic: bool) -> dict:
    plan = live["artifact_sha256"] if live["artifact_kind"] == "plan" else None
    contract = (live["artifact_sha256"]
                if live["artifact_kind"] == "contract" else None)
    result = {
        "schema": R.PHYSICAL_IDENTITY_SCHEMA,
        "family": {
            R.CASE_IDS[0]: "builtin_triangle.rtxrmq",
            R.CASE_IDS[1]: "builtin_triangle.rtxrmq",
            R.CASE_IDS[2]: "builtin_triangle.triangle_reduction",
            R.CASE_IDS[3]: "builtin_triangle.triangle_reduction",
            R.CASE_IDS[4]: "builtin_triangle.particle_orientation",
            R.CASE_IDS[5]: "custom_aabb.bounded_relation",
        }[case["case_id"]],
        "callback_ir_sha256": live["callback_ir_sha256"],
        "callback_effect_digest": live["effect_digest"],
        "physical_or_family_schema_sha256": live["schema_sha256"],
        "target_sha256": scientific["target_identity_sha256"],
        "abi_sha256": live["abi_sha256"],
        "plan_sha256": plan, "contract_sha256": contract,
        "executable_sha256": _sha(case["case_id"] + (":diagnostic" if diagnostic
                                                       else ":accepted")),
        "composed_program_sha256": _sha(
            case["case_id"] + (":diagnostic:ptx" if diagnostic
                               else ":accepted:ptx")),
        "semantic_admission_sha256": None if diagnostic else _sha(
            case["case_id"] + ":admission"),
        "native_library_sha256": scientific["native_library_sha256"],
        "program_bundle": "goal5790_a1." + case["case_id"],
    }
    return _seal(result, "observation_sha256")


def _snapshot(program: str, program_id: int) -> dict:
    return {
        "nonce_hi": 1,
        "nonce_lo": 2,
        "attempted_launch_count": 1,
        "successful_launch_count": 1,
        "failed_launch_count": 0,
        "complete_context_launch_count": 1,
        "incomplete_context_launch_count": 0,
        "context_bind_count": 1,
        "raygen_invocation_count": 1,
        "program_bundle_mix": 0,
        "traversable_mix": 0,
        "pipeline_mix": 0,
        "sbt_mix": 0,
        "stream_mix": 0,
        "params_mix": 0,
        "callsite_mix": 0,
        "first_program_bundle_id": program_id,
        "last_program_bundle_id": program_id,
        "first_traversable": 11,
        "last_traversable": 11,
        "pending_context_at_finish": 0,
        "session_error": 0,
        "incomplete_callsite_record_count": 0,
        "incomplete_callsite_lines": [0] * 32,
    }


def _traversal(identity: dict, live: dict, outcome_sha: str,
               nonce: str) -> tuple[dict, dict]:
    binding = {
        "authority": live["family_authority_nonce"],
        "contract": (identity["plan_sha256"]
                     if identity["plan_sha256"] is not None
                     else identity["contract_sha256"]),
        "abi": identity["abi_sha256"],
        "composed_ptx": identity["composed_program_sha256"],
        "native": identity["native_library_sha256"],
        "device_column_count": 1,
    }
    program_id = _bundle_id(identity["program_bundle"])
    receipt = {
        "schema": R.TRAVERSAL_SCHEMA,
        "provider_library": "synthetic_optix_provider",
        "provider_library_path": "/synthetic/librtdl_optix.so",
        "provider_library_sha256": identity["native_library_sha256"],
        "route_identity": "goal5790_a1_test_only",
        "semantic_digest": R.digest(binding),
        "output_digest": outcome_sha,
        "nonce": nonce,
        "physical_executor_classification": "optix_traversal_observed",
        "expected_program_bundles": [identity["program_bundle"]],
        "expected_program_bundle_ids": [program_id],
        "expected_program_observed_at_receipt_edge": True,
        "native_snapshot": _snapshot(identity["program_bundle"], program_id),
        "claim_rules": copy.deepcopy(R.CLAIM_RULES),
    }
    return _seal(receipt, "receipt_sha256"), binding


def _actual_identity(case: dict, live: dict, scientific: dict,
                     *, diagnostic: bool) -> dict:
    family = {
        R.CASE_IDS[0]: "builtin_triangle.rtxrmq",
        R.CASE_IDS[1]: "builtin_triangle.rtxrmq",
        R.CASE_IDS[2]: "builtin_triangle.triangle_reduction",
        R.CASE_IDS[3]: "builtin_triangle.triangle_reduction",
        R.CASE_IDS[4]: "builtin_triangle.particle_orientation",
        R.CASE_IDS[5]: "custom_aabb.bounded_relation",
    }[case["case_id"]]
    bundle = {
        "builtin_triangle.rtxrmq":
            "v4_builtin_triangle_callback_ir_four_role_composed",
        "builtin_triangle.particle_orientation":
            "v4_builtin_triangle_callback_ir_four_role_composed",
        "builtin_triangle.triangle_reduction":
            "v4_builtin_triangle_checked_reduction_composed",
        "custom_aabb.bounded_relation":
            "v4_custom_aabb_bounded_relation_composed",
    }[family]
    return {
        "family": family,
        "callback_ir_sha256": live["callback_ir_sha256"],
        "callback_effect_digest": live["effect_digest"],
        "physical_or_family_schema_sha256": live["schema_sha256"],
        "target_sha256": scientific["target_identity_sha256"],
        "abi_sha256": live["abi_sha256"],
        "plan_sha256": (live["artifact_sha256"]
                        if live["artifact_kind"] == "plan" else None),
        "contract_sha256": (live["artifact_sha256"]
                            if live["artifact_kind"] == "contract" else None),
        "executable_sha256": _sha(case["case_id"] + ":actual-executable:" + str(diagnostic)),
        "composed_program_sha256": _sha(
            case["case_id"] + ":actual-composed:" + str(diagnostic)),
        "expected_program_bundle": bundle,
        "family_authority_nonce": live["family_authority_nonce"],
        "family_authority_sha256": live["family_authority_sha256"],
        "semantic_admission_sha256": (
            None if diagnostic else _sha(case["case_id"] + ":actual-admission")),
        "native_library_sha256": scientific["native_library_sha256"],
    }


def _actual_output_inputs(case_id: str, own: object) -> list[object]:
    if case_id in R.CASE_IDS[:2]:
        return [[[own, own, own]]]
    if case_id == R.CASE_IDS[4]:
        return [[own]]
    if case_id == R.CASE_IDS[5]:
        return [own]
    if case_id == R.CASE_IDS[2] and isinstance(own, list):
        return [own]
    return [own]


def _actual_device_continuation(case: dict, identity: dict,
                                toolchain_sha256: str) -> dict:
    per_ray = list(case["minimal_witness"]["values"])
    weights = list(case["minimal_witness"]["weights"])
    source = R.UNCHECKED_U64_CONTINUATION_SOURCE
    recipe = {
        "operation": "unchecked_weighted_u64_product_sum",
        "arithmetic": "cuda_unsigned_long_long_modulo_2_pow_64",
        "grid": [1], "block": [1], "compiler_options": ["-std=c++11"],
        "input_origin": "exact_optix_per_ray_plus_frozen_query_weights",
        "host_fallback": False,
    }
    return {
        "schema": (
            "rtdl.goal5790_a1.test_only_unchecked_u64_device_continuation.v1"),
        "test_only_nonregistrable": True,
        "production_authority_minted": False,
        "kernel_source": source,
        "kernel_source_sha256": hashlib.sha256(
            source.encode("utf-8")).hexdigest(),
        "kernel_entry": "goal5790_a1_unchecked_weighted_sum",
        "compiler_options": ["-std=c++11"],
        "cupy_version": R.EXPECTED_CUPY_VERSION,
        "cuda_runtime_version": 12090,
        "device_id": 0,
        "target_sha256": identity["target_sha256"],
        "frozen_home_authority_file_sha256": R.HOME_AUTHORITY_FILE_SHA256,
        "frozen_home_authority_receipt_sha256": (
            R.HOME_AUTHORITY_RECEIPT_SHA256),
        "home_toolchain_identity_sha256": toolchain_sha256,
        "input_per_ray_sha256": R.digest(per_ray),
        "input_weights_sha256": R.digest(weights),
        "per_ray_u64": per_ray,
        "weights_u64": weights,
        "input_pair_sha256": R.digest({
            "per_ray": per_ray, "weights": weights}),
        "output_value": 0,
        "output_sha256": R.digest(0),
        "operation_recipe": recipe,
        "operation_recipe_sha256": R.digest(recipe),
        "device_kernel_launch_count": 1,
        "host_synchronization_count": 1,
        "launch_count": 1,
        "synchronization_count": 1,
        "device_output_u64": 0,
        "host_fallback_used": False,
        "evidence_kind": (
            "trusted_test_harness_not_hardware_capability_claim"),
        "registered_performance_timing_created": False,
    }


def _actual_traversal(identity: dict, output_value: object, nonce: str,
                      *, u64_producer: bool = False) -> tuple[dict, dict]:
    family = identity["family"]
    if family in {
            "builtin_triangle.rtxrmq", "builtin_triangle.particle_orientation"}:
        binding = {
            "authority_nonce": identity["family_authority_nonce"],
            "schema_sha256": identity["physical_or_family_schema_sha256"],
            "plan_sha256": identity["plan_sha256"],
            "abi_sha256": identity["abi_sha256"],
            "composed_ptx_sha256": identity["composed_program_sha256"],
            "native_library_sha256": identity["native_library_sha256"],
            "buffer_binding_sha256": _sha(nonce + ":buffer"),
        }
    else:
        binding = {
            "authority": identity["family_authority_nonce"],
            "contract": identity["contract_sha256"],
            "abi": identity["abi_sha256"],
            "composed_ptx": identity["composed_program_sha256"],
            "native": identity["native_library_sha256"],
        }
        if u64_producer:
            binding["diagnostic_scope"] = "weighted_per_ray_producer_only"
    bundle = identity["expected_program_bundle"]
    program_id = _bundle_id(bundle)
    receipt = {
        "schema": R.TRAVERSAL_SCHEMA,
        "provider_library": "synthetic_optix_provider",
        "provider_library_path": "/synthetic/librtdl_optix.so",
        "provider_library_sha256": identity["native_library_sha256"],
        "route_identity": "goal5790_a1_test_only",
        "semantic_digest": R.digest(binding),
        "output_digest": R.digest(output_value),
        "nonce": nonce,
        "physical_executor_classification": "optix_traversal_observed",
        "expected_program_bundles": [bundle],
        "expected_program_bundle_ids": [program_id],
        "expected_program_observed_at_receipt_edge": True,
        "native_snapshot": _snapshot(bundle, program_id),
        "claim_rules": copy.deepcopy(R.CLAIM_RULES),
    }
    return _seal(receipt, "receipt_sha256"), binding


class Fixture:
    def __init__(self, root: Path):
        self.root = root
        authoritative_home = (
            ROOT / "history/internal_docs/"
            "goal5790_frozen_home_machine_authority_20260816.json")
        self.home_authority_path = (
            root / "AUTHORITIES/HOME_MACHINE_AUTHORITY.json")
        self.home_authority_path.parent.mkdir(parents=True, exist_ok=True)
        self.home_authority_path.write_bytes(authoritative_home.read_bytes())
        self.home_authority = R.verify_home_machine_authority(
            self.home_authority_path)
        self.toolchain_sha = R.home_toolchain_identity(self.home_authority)
        self.cpu_suite = CPU.build_suite()
        self.cpu_path = root / "CPU_SUITE.json"
        _json(self.cpu_path, self.cpu_suite)
        self.entrypoint = root / "audit" / "diagnostic_entrypoint.py"
        self.entrypoint.parent.mkdir(parents=True, exist_ok=True)
        self.symbol = "goal5790_a1_test_only_counterfactual"
        self.entrypoint.write_text(
            f"def {self.symbol}():\n    return None\n\n"
            "def diagnostic_builtin_program():\n    return None\n",
            encoding="utf-8")
        self.product_source = root / "audit" / "product" / "api.py"
        self.product_source.parent.mkdir(parents=True, exist_ok=True)
        self.product_source.write_text("def public_compile():\n    return None\n",
                                       encoding="utf-8")
        self.governance_authority = (
            root / "AUTHORITIES" / Path(BUILD.PARTICLE_GATE_AUTHORITY).name)
        self.governance_authority.parent.mkdir(parents=True, exist_ok=True)
        self.governance_authority.write_bytes(
            (ROOT / BUILD.PARTICLE_GATE_AUTHORITY).read_bytes())
        self.plan_authority = (
            root / "AUTHORITIES" / Path(BUILD.CONTROLLING_PLAN_AUTHORITY).name)
        self.plan_authority.write_bytes(
            (ROOT / BUILD.CONTROLLING_PLAN_AUTHORITY).read_bytes())
        self.scientific_identity = {
            "execution_source_archive_sha256": _sha("source-archive"),
            "execution_source_tree_sha256": _sha("source-tree"),
            "native_library_sha256": _sha("native"),
            "target_provider": "optix", "optix_sdk": "8.0.0",
            "compute_capability": "6.1",
            "target_identity_sha256": _sha("target"),
        }
        self.spec = self._build_spec()
        self.spec_path = root / "EXECUTION_SPEC.json"
        _json(self.spec_path, self.spec)
        self.raw: dict[str, dict] = {}
        for index, (case, case_spec) in enumerate(zip(
                self.cpu_suite["cases"], self.spec["cases"])):
            raw = self._build_raw(case, case_spec, index)
            self.raw[case["case_id"]] = raw
            _json(root / "raw" / f"{case['case_id']}.json", raw)

    def _build_spec(self) -> dict:
        classifier_sha = BUILD.sha_file(self.entrypoint)
        source_manifest = {
            "scripts/goal5790_a1_home_worker.py": classifier_sha,
        }
        rows = []
        for case in self.cpu_suite["cases"]:
            snapshot = _pre_run_snapshot(
                case, classifier_sha=classifier_sha,
                target_sha=self.scientific_identity["target_identity_sha256"],
                source_manifest=source_manifest)
            row = {
                "schema": R.EXECUTION_CASE_SCHEMA,
                "case_id": case["case_id"],
                "upstream_case_sha256": case["case_sha256"],
                "shared_case_identity": R._shared_case(case),
                "pre_run_case_authorities": snapshot,
                "expected_product_rejection": {
                    "verdict": "INCOMPATIBLE",
                    "expected_rule_id": case["expected_rule_id"],
                    "required_stable_product_rule_ids": [
                        R.PRODUCT_RULE_BY_CASE_RULE[case["expected_rule_id"]]
                    ],
                    "executable": False,
                    "execution_authorized": False,
                },
                "accepted_control_expected_disposition": (
                    "FAIL_CLOSED_OVERFLOW" if case["case_id"] == R.CASE_IDS[2]
                    else "VALUE"
                ),
                "accepted_executed_input_sha256": R.digest(
                    R.expected_executed_input(case, diagnostic=False)),
                "diagnostic_executed_input_sha256": R.digest(
                    R.expected_executed_input(case, diagnostic=True)),
                "declared_executed_input_differences": copy.deepcopy(
                    R.EXECUTED_INPUT_DELTA_BY_CASE[case["case_id"]]),
                "allowed_postrun_observation_fields": list(
                    R.POSTRUN_OBSERVATION_FIELDS),
            }
            rows.append(_seal(row, "case_execution_spec_sha256"))
        empty_process = {
            "modules": [], "modules_sha256": R.digest([]),
            "relevant_memory_maps": [],
            "relevant_memory_maps_sha256": R.digest([]),
        }
        capture_audit = _seal({
            "schema": "rtdl.goal5790_a1.pre_run_capture_audit.v1",
            "process_audit_before": copy.deepcopy(empty_process),
            "process_audit_after": copy.deepcopy(empty_process),
            "new_module_names": ["rtdsl"],
            "forbidden_low_level_imports": [],
            "rtdsl_namespace_preseeded": True,
            "broad_rtdsl_initializer_executed": False,
            "low_level_compiler_call_count": 0,
            "native_prepare_call_count": 0,
            "native_execute_call_count": 0,
            "traversal_launch_count": 0,
        }, "audit_sha256")
        result = {
            "schema": R.EXECUTION_SPEC_SCHEMA,
            "upstream_suite_sha256": self.cpu_suite["suite_sha256"],
            "home_machine_authority_sha256":
                R.HOME_AUTHORITY_RECEIPT_SHA256,
            "home_machine_authority_file_sha256":
                R.HOME_AUTHORITY_FILE_SHA256,
            "home_machine_authority_evidence_path":
                "AUTHORITIES/HOME_MACHINE_AUTHORITY.json",
            "home_toolchain_identity_sha256": self.toolchain_sha,
            "cupy_version": R.EXPECTED_CUPY_VERSION,
            "scientific_identity": copy.deepcopy(self.scientific_identity),
            "pre_run_capture_audit": capture_audit,
            "pre_run_source_members": [{
                "logical_path": "scripts/goal5790_a1_home_worker.py",
                "evidence_path": "audit/diagnostic_entrypoint.py",
                "sha256": classifier_sha,
                "roles": [
                    "diagnostic_entrypoint", "trusted_test_classifier",
                    "unchecked_u64_kernel_source",
                    "unsafe_transform_implementation",
                ],
            }, {
                "logical_path": "src/rtdsl/v4_semantic_physical_admission.py",
                "evidence_path": "audit/product/api.py",
                "sha256": BUILD.sha_file(self.product_source),
                "roles": ["product_public_facade_source"],
            }, {
                "logical_path": "src/rtdsl/v4_semantically_admitted_compiler.py",
                "evidence_path": "audit/product/api.py",
                "sha256": BUILD.sha_file(self.product_source),
                "roles": ["product_public_facade_source"],
            }, {
                "logical_path": "src/rtdsl/v4_typed_physical_schema.py",
                "evidence_path": "audit/product/api.py",
                "sha256": BUILD.sha_file(self.product_source),
                "roles": ["product_public_facade_source"],
            }],
            "governance_authority_members": [{
                "logical_path": BUILD.CONTROLLING_PLAN_AUTHORITY,
                "evidence_path": "AUTHORITIES/" + self.plan_authority.name,
                "sha256": BUILD.sha_file(self.plan_authority),
                "role": "goal5790_a1_controlling_plan_authority",
            }, {
                "logical_path": BUILD.PARTICLE_GATE_AUTHORITY,
                "evidence_path": (
                    "AUTHORITIES/" + self.governance_authority.name),
                "sha256": BUILD.sha_file(self.governance_authority),
                "role": "particle_earliest_product_gate_authority",
            }],
            "case_count": 6,
            "cases": rows,
            "diagnostic_api_audit": {
                "diagnostic_entrypoint_path": "scripts/goal5790_a1_diagnostic.py",
                "diagnostic_entrypoint_sha256": BUILD.sha_file(self.entrypoint),
                "diagnostic_entrypoint_evidence_path": "audit/diagnostic_entrypoint.py",
                "diagnostic_symbol": self.symbol,
                "product_source_members": [{
                    "logical_path": "src/rtdsl/v4_semantic_physical_admission.py",
                    "evidence_path": "audit/product/api.py",
                    "sha256": BUILD.sha_file(self.product_source),
                }],
                "diagnostic_symbol_absent_from_product_api": True,
                "test_only_entrypoint_not_imported_by_product": True,
                "production_bypass_parameter_present": False,
            },
            "claim_boundary": {
                "home_only": True,
                "pod_authorized": False,
                "performance_timing_authorized": False,
                "performance_claimed": False,
                "formal_worker": False,
                "diagnostic_is_product_bypass": False,
            },
        }
        return _seal(result, "execution_spec_sha256")

    def _audit_rows(self, index: int) -> list[dict]:
        base = self.root / "audit" / "reject" / f"case_{index}"
        contents = {
            "modules": json.dumps([
                "json", "sys", R.ISOLATED_ADMISSION_MODULE,
            ]).encode("utf-8") + b"\n",
            "maps_before": b"python-runtime-only\n",
            "maps_after": b"python-runtime-only\n",
            "strace": b'openat(AT_FDCWD, "/usr/lib/python.json", O_RDONLY) = 3\n',
        }
        rows = []
        for kind, data in contents.items():
            path = base / f"{kind}.txt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            rows.append({
                "kind": kind,
                "path": path.relative_to(self.root).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
            })
        return rows

    def _execution_arm(self, case: dict, case_spec: dict, index: int,
                       arm_name: str) -> dict:
        accepted = arm_name == "accepted_control"
        snapshot = case_spec["pre_run_case_authorities"]
        live = snapshot[
            "canonical_live_family" if accepted else "diagnostic_live_family"]
        if live is None:
            live = snapshot["canonical_live_family"]
        identity = _physical(
            case, live, self.scientific_identity, diagnostic=not accepted)
        expected, counterfactual = R.evaluate_case(case["case_id"], case["minimal_witness"])
        oracle = expected if accepted else counterfactual
        outcome = R._expected_outcome(case["case_id"], oracle, accepted)
        outcome_sha = R.digest(outcome)
        executed_input = R.expected_executed_input(case, diagnostic=not accepted)
        overflow = accepted and case["case_id"] == R.CASE_IDS[2]
        if overflow:
            receipts, bindings = [], []
        else:
            receipt, binding = _traversal(
                identity, live, outcome_sha, f"nonce-{index}-{arm_name}")
            receipts, bindings = [receipt], [binding]
        arm = {
            "schema": R.EXECUTION_ARM_SCHEMA,
            "arm": arm_name,
            "status": "PASS",
            "parent_pid": 10_000 + index * 3 + (2 if accepted else 1),
            "upstream_suite_sha256": self.cpu_suite["suite_sha256"],
            "case_sha256": case["case_sha256"],
            "case_execution_spec_sha256": case_spec["case_execution_spec_sha256"],
            "shared_case_identity": copy.deepcopy(case_spec["shared_case_identity"]),
            "home_machine_authority_sha256":
                R.HOME_AUTHORITY_RECEIPT_SHA256,
            "home_machine_authority_file_sha256":
                R.HOME_AUTHORITY_FILE_SHA256,
            "physical_identity": identity,
            "executed_input": executed_input,
            "executed_input_sha256": R.digest(executed_input),
            "execution_binding_sha256": None,
            "outcome": outcome,
            "outcome_sha256": outcome_sha,
            "oracle_value": oracle,
            "oracle_value_sha256": R.digest(oracle),
            "matches_own_oracle": True,
            "matches_requested_semantics": accepted,
            "counterexample_observed": not accepted,
            "isolated_test_only_diagnostic": not accepted,
            "production_authority_minted": accepted,
            "product_api_bypass_parameter_present": False,
            "product_source_modified": False,
            "traversal_receipts": receipts,
            "traversal_semantic_bindings": bindings,
            "traversal_receipt_count": len(receipts),
            "device_continuation_receipt": None,
            "elapsed_values_recorded": False,
            "registered_performance_timing_created": False,
            "performance_claimed": False,
            "pod_used": False,
            "formal_worker": False,
        }
        if not accepted and case["case_id"] == R.CASE_IDS[2]:
            arm["device_continuation_receipt"] = (
                R.expected_u64_device_continuation(
                    executed_input, identity, self.toolchain_sha, case))
        arm["execution_binding_sha256"] = R.digest({
            "case_sha256": case["case_sha256"],
            "physical_identity_sha256": identity["observation_sha256"],
            "executed_input_sha256": R.digest(executed_input),
            "outcome_sha256": outcome_sha,
            "traversal_receipt_sha256s": [
                receipt["receipt_sha256"] for receipt in receipts],
            "device_continuation_receipt_sha256": (
                None if arm["device_continuation_receipt"] is None
                else arm["device_continuation_receipt"]["receipt_sha256"]),
        })
        return _seal(arm, "receipt_sha256")

    def _build_raw(self, case: dict, case_spec: dict, index: int) -> dict:
        decision = _seal({
            "schema": R.DECISION_SCHEMA,
            "verdict": "INCOMPATIBLE",
            "expected_rule_id": case["expected_rule_id"],
            "stable_product_rule_ids": [
                R.PRODUCT_RULE_BY_CASE_RULE[case["expected_rule_id"]]
            ],
            "executable": False,
            "execution_authorized": False,
        }, "decision_sha256")
        reject = _seal({
            "schema": R.REJECT_SCHEMA,
            "arm": "product_admission_reject",
            "status": "PASS",
            "parent_pid": 10_000 + index * 3,
            "upstream_suite_sha256": self.cpu_suite["suite_sha256"],
            "case_sha256": case["case_sha256"],
            "case_execution_spec_sha256": case_spec["case_execution_spec_sha256"],
            "shared_case_identity": copy.deepcopy(case_spec["shared_case_identity"]),
            "home_machine_authority_sha256":
                R.HOME_AUTHORITY_RECEIPT_SHA256,
            "home_machine_authority_file_sha256":
                R.HOME_AUTHORITY_FILE_SHA256,
            "rejected_physical_identity_sha256": (
                R.digest(case_spec["pre_run_case_authorities"]
                         ["diagnostic_early_reject"])
                if case["case_id"] == R.CASE_IDS[4] else
                case_spec["pre_run_case_authorities"]
                ["diagnostic_physical_authority"]["authority_sha256"]),
            "admission_decision": decision,
            "process_audit": {
                "compiler_call_count": 0,
                "native_prepare_call_count": 0,
                "native_execute_call_count": 0,
                "traversal_launch_count": 0,
                "admission_module_imported": True,
                "admission_module_name": R.ISOLATED_ADMISSION_MODULE,
                "admission_module_source_sha256": BUILD.sha_file(
                    self.product_source),
                "admission_module_loaded_from_exact_source": True,
                "rtdsl_package_imported": False,
                "compiler_or_runtime_module_imported": False,
                "cupy_imported": False,
                "numba_imported": False,
                "ctypes_imported": False,
            },
            "raw_audit_artifacts": self._audit_rows(index),
            "compile_count": 0,
            "native_prepare_count": 0,
            "native_execute_count": 0,
            "traversal_launch_count": 0,
            "elapsed_values_recorded": False,
            "registered_performance_timing_created": False,
            "performance_claimed": False,
            "pod_used": False,
            "formal_worker": False,
        }, "receipt_sha256")
        raw = {
            "schema": R.RAW_SCHEMA,
            "status": "PASS",
            "upstream_suite_sha256": self.cpu_suite["suite_sha256"],
            "execution_spec_sha256": self.spec["execution_spec_sha256"],
            "case_id": case["case_id"],
            "case_sha256": case["case_sha256"],
            "case_execution_spec_sha256": case_spec["case_execution_spec_sha256"],
            "shared_case_identity": copy.deepcopy(case_spec["shared_case_identity"]),
            "home_machine_authority_sha256":
                R.HOME_AUTHORITY_RECEIPT_SHA256,
            "home_machine_authority_file_sha256":
                R.HOME_AUTHORITY_FILE_SHA256,
            "product_admission_reject": reject,
            "diagnostic_counterfactual": self._execution_arm(
                case, case_spec, index, "diagnostic_counterfactual"),
            "accepted_control": self._execution_arm(
                case, case_spec, index, "accepted_control"),
            "claim_boundary": copy.deepcopy(self.spec["claim_boundary"]),
        }
        return _seal(raw, "raw_result_sha256")

    def write_raw(self, case_id: str) -> None:
        _json(self.root / "raw" / f"{case_id}.json", self.raw[case_id])

    def resign_raw(self, case_id: str) -> None:
        raw = self.raw[case_id]
        for arm_name in ("product_admission_reject", "diagnostic_counterfactual",
                         "accepted_control"):
            field = "receipt_sha256"
            raw[arm_name] = _seal(raw[arm_name], field)
        self.raw[case_id] = _seal(raw, "raw_result_sha256")
        self.write_raw(case_id)


class ActualControllerFixture:
    """Synthetic exact-shape controller bytes for adapter attack tests only."""

    def __init__(self, base: Fixture, root: Path):
        self.base = base
        self.root = root
        self.controller_root = root / "controller"
        self.adapted_root = root / "adapted"
        self.machine = R._expected_home_machine(base.home_authority)
        self.controller = self._build_controller()

    def _reject_result(self, case: dict, case_spec: dict) -> dict:
        snapshot = case_spec["pre_run_case_authorities"]
        particle = case["case_id"] == R.CASE_IDS[4]
        gate = ("verify_typed_physical_schema" if particle
                else "v4_semantically_admitted_compiler.admit_*")
        finding = {
            "rule_id": R.PRODUCT_RULE_BY_CASE_RULE[case["expected_rule_id"]],
            "path": "synthetic.attack.fixture",
            "detail": "exact frozen test rejection",
            "gate": gate,
        }
        decision = {
            "verdict": "INCOMPATIBLE",
            "finding": finding,
            "semantic_authority_sha256": snapshot["semantic_authority"][
                "authority_sha256"],
            "physical_authority_sha256": (
                None if snapshot["diagnostic_physical_authority"] is None else
                snapshot["diagnostic_physical_authority"]["authority_sha256"]),
            "canonical_live_family": copy.deepcopy(
                snapshot["canonical_live_family"]),
            "diagnostic_live_family": copy.deepcopy(
                snapshot["diagnostic_live_family"]),
            "diagnostic_family_attempt": copy.deepcopy(
                snapshot["diagnostic_family_attempt"]),
        }
        empty_process = {
            "modules": [], "modules_sha256": R.digest([]),
            "relevant_memory_maps": [],
            "relevant_memory_maps_sha256": R.digest([]),
        }
        source_sha = BUILD.sha_file(self.base.product_source)
        classifier_sha = BUILD.sha_file(self.base.entrypoint)
        return {
            "engine": "production_semantically_admitted_compiler_facade_v1",
            "verdict": "INCOMPATIBLE",
            "product_rule_ids": [finding["rule_id"]],
            "named_case_rule_id": case["expected_rule_id"],
            "product_rejection_gate": gate,
            "production_facade_called": not particle,
            "decision": decision,
            "decision_sha256": R.digest(decision),
            "product_facade_path": "src/rtdsl/v4_semantically_admitted_compiler.py",
            "product_facade_sha256": source_sha,
            "semantic_physical_calculus_path":
                "src/rtdsl/v4_semantic_physical_admission.py",
            "semantic_physical_calculus_sha256": source_sha,
            "trusted_test_classifier_path": "scripts/goal5790_a1_home_worker.py",
            "trusted_test_classifier_sha256": classifier_sha,
            "semantic_authority": copy.deepcopy(snapshot["semantic_authority"]),
            "physical_registry": copy.deepcopy(snapshot["physical_registry"]),
            "canonical_physical_authority": copy.deepcopy(
                snapshot["canonical_physical_authority"]),
            "diagnostic_physical_authority": copy.deepcopy(
                snapshot["diagnostic_physical_authority"]),
            "canonical_live_family": copy.deepcopy(snapshot["canonical_live_family"]),
            "diagnostic_live_family": copy.deepcopy(snapshot["diagnostic_live_family"]),
            "diagnostic_family_attempt": copy.deepcopy(
                snapshot["diagnostic_family_attempt"]),
            "target_sha256": self.base.scientific_identity["target_identity_sha256"],
            "native_library_sha256": self.base.scientific_identity[
                "native_library_sha256"],
            "process_audit_before": copy.deepcopy(empty_process),
            "process_audit_after": copy.deepcopy(empty_process),
            "new_module_names": [],
            "forbidden_gpu_or_compiler_imports": [],
            "compiler_call_count": 0,
            "low_level_compiler_call_count": 0,
            "native_prepare_call_count": 0,
            "native_execute_call_count": 0,
            "traversal_launch_count": 0,
            "cuda_or_gpu_library_map_observed": False,
            "cuda_driver_initialization_observed": False,
            "cuda_driver_initialization_proven_absent": False,
            "cuda_initialization_evidence_kind": (
                "negative_module_and_proc_maps_observation__not_a_formal_absence_proof"),
            "execution_authorized": False,
            "executable_issued": False,
            "claim_boundary": {
                "public_facade_rejects_raw_caller_self_proof": True,
                "compiler_internal_classifier_is_trusted_tcb": True,
                "malicious_same_process_reflection_resisted": False,
                "python_semantics_automatically_inferred": False,
                "concrete_runtime_input_certified_by_compile_admission": False,
            },
        }

    def _execution_result(self, case: dict, case_spec: dict, arm: str) -> dict:
        diagnostic = arm == "diagnostic_counterfactual"
        snapshot = case_spec["pre_run_case_authorities"]
        live = snapshot["diagnostic_live_family" if diagnostic
                        else "canonical_live_family"]
        if live is None:
            live = snapshot["canonical_live_family"]
        identity = _actual_identity(
            case, live, self.base.scientific_identity, diagnostic=diagnostic)
        expected, counterfactual = R.evaluate_case(
            case["case_id"], case["minimal_witness"])
        executed_input = R.expected_executed_input(case, diagnostic=diagnostic)
        overflow_accepted = not diagnostic and case["case_id"] == R.CASE_IDS[2]
        if overflow_accepted:
            return {
                "declared_semantics": "checked_weighted_reduction",
                "output": None,
                "accepted_disposition": {
                    "status": "FAIL_CLOSED_OVERFLOW",
                    "error_type": "TriangleReductionError",
                    "error_code": "unsigned_overflow",
                    "error_path": "rows[1].sum",
                    "output_produced": False,
                },
                "own_oracle": {
                    "required_mathematical_value": expected,
                    "required_disposition": "FAIL_CLOSED_OVERFLOW",
                },
                "requested_semantic_oracle": expected,
                "matches_own_oracle": True,
                "matches_requested_semantics": True,
                "correct_fail_closed": True,
                "counterexample_observed": False,
                "execution_identity": identity,
                "executed_input": executed_input,
                "executed_input_sha256": R.digest(executed_input),
                "declared_input_delta": "none",
                "traversal_receipts": [],
                "traversal_semantic_bindings": [],
                "traversal_output_digest_inputs": [],
                "expected_program_bundles": [],
                "behaviorally_true_optix": False,
                "admitted_run_gate": True,
                "compile_admission_certifies_concrete_runtime_arrays": False,
                "zero_receipt_reason": (
                    "checked reducer rejected overflow before audit receipt capture"),
            }
        own = counterfactual if diagnostic else expected
        receipt_input = _actual_output_inputs(case["case_id"], own)[0]
        if case["case_id"] == R.CASE_IDS[2] and diagnostic:
            receipt_input = list(case["minimal_witness"]["values"])
        receipt, binding = _actual_traversal(
            identity, receipt_input, "nonce:" + case["case_id"] + ":" + arm,
            u64_producer=(case["case_id"] == R.CASE_IDS[2] and diagnostic))
        result = {
            "declared_semantics": (
                "test_only_counterfactual_encoding" if diagnostic
                else "requested_semantic_contract"),
            "output": own,
            "own_oracle": own,
            "requested_semantic_oracle": expected,
            "matches_own_oracle": True,
            "matches_requested_semantics": not diagnostic,
            "counterexample_observed": diagnostic,
            "execution_identity": identity,
            "executed_input": executed_input,
            "executed_input_sha256": R.digest(executed_input),
            "declared_input_delta": (
                "none" if not diagnostic else R._actual_diagnostic_input_delta(case)),
            "traversal_receipts": [receipt],
            "traversal_semantic_bindings": [binding],
            "traversal_output_digest_inputs": [receipt_input],
            "expected_program_bundles": [identity["expected_program_bundle"]],
            "behaviorally_true_optix": True,
            "admitted_run_gate": not diagnostic,
            "compile_admission_certifies_concrete_runtime_arrays": False,
        }
        if case["case_id"] in R.CASE_IDS[2:4]:
            result.update({
                "accepted_disposition": None,
                "declared_physical_delta": (
                    str(case["unsafe_transform"]["transform_id"])
                    if diagnostic else "none"),
                "traversal_receipt_claim_scope": (
                    "optix_hit_collection_only__test_continuation_separately_bound"
                    if diagnostic else "accepted_checked_route"),
                "per_ray_u64": (
                    list(case["minimal_witness"]["values"])
                    if case["case_id"] == R.CASE_IDS[2] else [1, 1]),
                "test_only_device_continuation": None,
                "test_only_optix_producer_diagnostic": None,
            })
        if case["case_id"] == R.CASE_IDS[2] and diagnostic:
            continuation = _actual_device_continuation(
                case, identity, self.base.toolchain_sha)
            result["test_only_device_continuation"] = continuation
            result["test_only_optix_producer_diagnostic"] = {
                "per_ray_u64": list(case["minimal_witness"]["values"]),
                "traversal_receipt": receipt,
                "role_counters": [0, 2, 0, 2, 0, 2, 2],
                "native_library_sha256": identity["native_library_sha256"],
                "composed_program_sha256": identity["composed_program_sha256"],
                "traversal_semantic_binding": binding,
                "expected_program_bundle": identity["expected_program_bundle"],
                "test_only_nonregistrable": True,
                "standard_product_reduction_receipt_minted": False,
            }
        return result

    def _worker(self, case: dict, case_spec: dict, index: int, arm: str) -> dict:
        arm_index = R.ACTUAL_ARMS.index(arm)
        result = {
            "schema": R.WORKER_SCHEMA,
            "status": "PASS",
            "case_id": case["case_id"],
            "case_sha256": case["case_sha256"],
            "upstream_suite_sha256": self.base.cpu_suite["suite_sha256"],
            "execution_spec_sha256": self.base.spec["execution_spec_sha256"],
            "execution_spec_file_sha256": BUILD.sha_file(self.base.spec_path),
            "case_execution_spec_sha256": case_spec["case_execution_spec_sha256"],
            "input_sha256": R.digest(case["minimal_witness"]),
            "arm": arm,
            "parent_pid": 20_000 + index * 3 + arm_index,
            "home_machine": copy.deepcopy(self.machine),
            "home_machine_authority_sha256": self.machine[
                "home_machine_authority_sha256"],
            "cache_policy": {
                "formal_leaf_cache_environment_cleared": True,
                "cupy_cache_dir": f"/tmp/case-{index}/{arm}/cupy",
                "numba_cache_dir": f"/tmp/case-{index}/{arm}/numba",
                "initially_empty": True,
                "per_arm_isolated": True,
                "cache_is_execution_authority": False,
                "cache_contents_used_as_evidence": False,
            },
            "arm_result": (
                self._reject_result(case, case_spec)
                if arm == "product_admission_reject" else
                self._execution_result(case, case_spec, arm)),
            "elapsed_values_recorded": False,
            "registered_performance_timing_created": False,
            "performance_claimed": False,
            "pod_used": False,
            "formal_worker": False,
        }
        return _seal(result, "worker_result_sha256")

    def _build_controller(self) -> dict:
        raw_root = self.controller_root / "RAW"
        rows = []
        for index, (case, case_spec) in enumerate(zip(
                self.base.cpu_suite["cases"], self.base.spec["cases"])):
            arms = {}
            for arm in R.ACTUAL_ARMS:
                worker = self._worker(case, case_spec, index, arm)
                arms[arm] = worker
                _json(raw_root / BUILD._worker_filename(case["case_id"], arm), worker)
            rows.append({
                "case_id": case["case_id"],
                "case_sha256": case["case_sha256"],
                "expected_rule_id": case["expected_rule_id"],
                "arms": arms,
            })
        controller = {
            "schema": R.CONTROLLER_SCHEMA,
            "status": "PASS",
            "scope": "home_functional_only__zero_registered_timing",
            "suite_sha256": self.base.cpu_suite["suite_sha256"],
            "suite_file_sha256": BUILD.sha_file(self.base.cpu_path),
            "execution_spec_file_sha256": BUILD.sha_file(self.base.spec_path),
            "execution_spec_sha256": self.base.spec["execution_spec_sha256"],
            "native_library_sha256": self.base.scientific_identity[
                "native_library_sha256"],
            "home_machine": copy.deepcopy(self.machine),
            "frozen_home_authority_file": "/frozen/home-authority.json",
            "frozen_home_authority_file_sha256": R.HOME_AUTHORITY_FILE_SHA256,
            "frozen_home_authority_receipt_sha256":
                R.HOME_AUTHORITY_RECEIPT_SHA256,
            "compute_capability": "61",
            "optix_sdk": self.base.scientific_identity["optix_sdk"],
            "case_count": 6,
            "arm_count": 18,
            "fresh_parent_pid_count": 18,
            "product_admission_reject_count": 6,
            "production_facade_reject_count": 5,
            "typed_physical_schema_reject_count": 1,
            "product_admission_launch_count": 0,
            "accepted_control_count": 6,
            "diagnostic_counterexample_count": 6,
            "registered_performance_timing_count": 0,
            "performance_claimed": False,
            "pod_used": False,
            "formal_worker_count": 0,
            "cache_policy": {
                "formal_leaf_cache_environment_cleared": True,
                "per_arm_cupy_cache": "create_only_isolated_non_authority",
                "per_arm_numba_cache": "create_only_isolated_non_authority",
                "cache_contents_used_as_evidence": False,
            },
            "cases": rows,
        }
        controller = _seal(controller, "result_sha256")
        _json(self.controller_root / "RESULT.json", controller)
        return controller


class Goal5790A1RecountTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fixture = Fixture(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def recount(self):
        return R.recount(
            self.fixture.cpu_path, self.fixture.spec_path, self.root,
            self.fixture.cpu_suite["suite_sha256"])

    def _resign_spec_registry(self, case_id: str) -> None:
        index = R.CASE_IDS.index(case_id)
        case_spec = self.fixture.spec["cases"][index]
        snapshot = case_spec["pre_run_case_authorities"]
        registry = snapshot["physical_registry"]
        registry["registry_sha256"] = R.digest({
            "schema": R.PHYSICAL_REGISTRY_SCHEMA,
            "issuer_domain": registry["issuer_domain"],
            "registry_source_sha256": registry["registry_source_sha256"],
            "entries": registry["entries"],
        })
        registry["authority_nonce"] = R.digest({
            "kind": R.PHYSICAL_REGISTRY_SCHEMA,
            "registry_sha256": registry["registry_sha256"],
        })
        by_id = {entry["entry_id"]: entry for entry in registry["entries"]}
        for field in ("canonical_physical_authority",
                      "diagnostic_physical_authority"):
            authority = snapshot.get(field)
            if authority is None:
                continue
            authority["entry"] = copy.deepcopy(
                by_id[authority["entry"]["entry_id"]])
            authority["registry_sha256"] = registry["registry_sha256"]
            authority["entry_sha256"] = R.digest(authority["entry"])
            authority["authority_sha256"] = R.digest({
                "schema": R.PHYSICAL_AUTHORITY_SCHEMA,
                "registry_sha256": registry["registry_sha256"],
                "entry_sha256": authority["entry_sha256"],
                "entry_id": authority["entry"]["entry_id"],
                "eligibility": authority["entry"]["eligibility"],
            })
            authority["authority_nonce"] = R.digest({
                "kind": R.PHYSICAL_AUTHORITY_SCHEMA,
                "authority_sha256": authority["authority_sha256"],
                "registry_nonce": registry["authority_nonce"],
            })
        snapshot["physical_registry"] = registry
        case_spec["pre_run_case_authorities"] = _seal(
            snapshot, "snapshot_sha256")
        self.fixture.spec["cases"][index] = _seal(
            case_spec, "case_execution_spec_sha256")
        self.fixture.spec = _seal(self.fixture.spec, "execution_spec_sha256")
        _json(self.fixture.spec_path, self.fixture.spec)

    def test_valid_three_arm_suite_recounts_six_cases_and_eleven_receipts(self):
        result = self.recount()
        self.assertEqual(result["case_count"], 6)
        self.assertEqual(result["arm_count"], 18)
        self.assertEqual(result["unique_parent_pid_count"], 18)
        self.assertEqual(result["behavioral_true_optix_execution_count"], 11)

    def _real_goal5783_snapshot(self):
        path = (
            ROOT / "history/internal_docs/"
            "goal5783_home_functional_result_20260814/"
            "GOAL5783_FUNCTIONAL_RECEIPT.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        receipt = payload["cold_cases"][0]["traversal_receipt"]
        return receipt["native_snapshot"], receipt["expected_program_bundles"][0]

    def test_real_goal5783_native_snapshot_exact_integer_schema_passes(self):
        snapshot, bundle = self._real_goal5783_snapshot()
        R._verify_snapshot(snapshot, bundle, "real_goal5783")

    def test_real_s3_two_launch_distinct_traversables_pass(self):
        path = (
            ROOT / "history/internal_docs/"
            "goal5790_a1_real_native_snapshot_fixture_20260816.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        snapshot = payload["native_snapshot"]
        self.assertEqual(snapshot["attempted_launch_count"], 2)
        self.assertNotEqual(snapshot["first_traversable"],
                            snapshot["last_traversable"])
        R._verify_snapshot(
            snapshot, payload["expected_program_bundle"], "real_s3_librts")

    def test_real_snapshot_rejects_bool_in_positive_count(self):
        snapshot, bundle = self._real_goal5783_snapshot()
        snapshot["attempted_launch_count"] = True
        with self.assertRaisesRegex(AssertionError, "exact positive integer"):
            R._verify_snapshot(snapshot, bundle, "tampered")

    def test_real_snapshot_rejects_bool_in_zero_status(self):
        snapshot, bundle = self._real_goal5783_snapshot()
        snapshot["pending_context_at_finish"] = False
        with self.assertRaisesRegex(AssertionError, "exact integer zero"):
            R._verify_snapshot(snapshot, bundle, "tampered")

    def test_real_snapshot_rejects_missing_status_field(self):
        snapshot, bundle = self._real_goal5783_snapshot()
        del snapshot["session_error"]
        with self.assertRaisesRegex(AssertionError, "fields drift"):
            R._verify_snapshot(snapshot, bundle, "tampered")

    def test_real_snapshot_rejects_nonzero_status(self):
        snapshot, bundle = self._real_goal5783_snapshot()
        snapshot["session_error"] = 1
        with self.assertRaisesRegex(AssertionError, "exact integer zero"):
            R._verify_snapshot(snapshot, bundle, "tampered")

    def test_real_snapshot_rejects_callsite_line_shape_and_value_tampering(self):
        original, bundle = self._real_goal5783_snapshot()
        candidates = []
        short = copy.deepcopy(original)
        short["incomplete_callsite_lines"] = [0] * 31
        candidates.append(short)
        boolean = copy.deepcopy(original)
        boolean["incomplete_callsite_lines"][0] = False
        candidates.append(boolean)
        nonzero = copy.deepcopy(original)
        nonzero["incomplete_callsite_lines"][31] = 7
        candidates.append(nonzero)
        for snapshot in candidates:
            with self.subTest(snapshot=snapshot["incomplete_callsite_lines"]):
                with self.assertRaisesRegex(AssertionError, "exact 32x integer zero"):
                    R._verify_snapshot(snapshot, bundle, "tampered")

    def test_exact_s3_adapted_raw_full_recount_regression(self):
        root = (
            ROOT / "history/internal_docs/"
            "goal5790_a1_home_s3_execution_evidence_staging_20260816/adapted")
        if not root.is_dir():
            self.skipTest("exact Home s3 staging is intentionally outside portable source")
        result = R.recount(
            root / "AUTHORITIES/CPU_SUITE.json",
            root / "AUTHORITIES/HOME_EXECUTION_SPEC.json",
            root,
            "3f39450f610e294c1540e9f6ec96fa925123567713567ba7f999f740bd9fb35e",
        )
        self.assertEqual(result["recount_sha256"],
                         "2ae88fb404fcaa9dcf09559c56c52ed15abdf69948d3a7d619535d9b711a3f5a")
        self.assertEqual((result["case_count"], result["arm_count"],
                          result["unique_parent_pid_count"],
                          result["behavioral_true_optix_execution_count"]),
                         (6, 18, 18, 11))
        overflow = self.fixture.raw[R.CASE_IDS[2]]["accepted_control"]
        self.assertEqual(overflow["traversal_receipt_count"], 0)
        self.assertEqual(overflow["outcome"]["exception_type"], "OverflowError")

    def test_pre_run_spec_contains_no_postrun_executable_or_receipt_identity(self):
        for row in self.fixture.spec["cases"]:
            snapshot = row["pre_run_case_authorities"]
            rendered = json.dumps(snapshot, sort_keys=True)
            self.assertNotIn("executable_sha256", rendered)
            self.assertNotIn("composed_program_sha256", rendered)
            self.assertNotIn("receipt_sha256", rendered)
        self.assertEqual(
            self.fixture.spec["cases"][0]["allowed_postrun_observation_fields"],
            list(R.POSTRUN_OBSERVATION_FIELDS))

    def test_create_only_prerun_builder_freezes_authorities_before_results(self):
        repository = self.root / "synthetic_repository"
        worker = repository / "scripts/goal5790_a1_home_worker.py"
        worker.parent.mkdir(parents=True)
        worker.write_bytes(self.fixture.entrypoint.read_bytes())
        product_sources = tuple(BUILD.DEFAULT_PRODUCT_SOURCES)
        for logical in product_sources:
            path = repository / logical
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.fixture.product_source.read_bytes())
        for case in self.fixture.cpu_suite["cases"]:
            logical = case["semantic_authority"]["oracle_source_path"]
            path = repository / logical
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / logical).read_bytes())
        amendment = repository / BUILD.PARTICLE_GATE_AUTHORITY
        amendment.parent.mkdir(parents=True, exist_ok=True)
        amendment.write_bytes((ROOT / BUILD.PARTICLE_GATE_AUTHORITY).read_bytes())
        plan = repository / BUILD.CONTROLLING_PLAN_AUTHORITY
        plan.parent.mkdir(parents=True, exist_ok=True)
        plan.write_bytes((ROOT / BUILD.CONTROLLING_PLAN_AUTHORITY).read_bytes())
        snapshots = {
            row["case_id"]: copy.deepcopy(row["pre_run_case_authorities"])
            for row in self.fixture.spec["cases"]
        }
        output_root = self.root / "fresh_pre_run_authority"
        result = BUILD.build_pre_run_execution_spec(
            cpu_suite=self.fixture.cpu_path,
            home_authority=self.fixture.home_authority_path,
            repository_root=repository,
            scientific_identity=copy.deepcopy(self.fixture.scientific_identity),
            case_authority_snapshots=snapshots,
            pre_run_capture_audit=copy.deepcopy(
                self.fixture.spec["pre_run_capture_audit"]),
            output_root=output_root,
            product_sources=product_sources,
        )
        self.assertTrue((output_root / "HOME_EXECUTION_SPEC.json").is_file())
        self.assertEqual(result["execution_spec_sha256"],
                         result["execution_spec"]["execution_spec_sha256"])
        suite, cases = R.verify_cpu_suite(
            self.fixture.cpu_suite, self.fixture.cpu_suite["suite_sha256"])
        verified, rows = R.verify_execution_spec(
            result["execution_spec"], suite, cases, output_root)
        self.assertEqual(verified["case_count"], 6)
        self.assertEqual(tuple(rows), R.CASE_IDS)
        with self.assertRaises(FileExistsError):
            BUILD.build_pre_run_execution_spec(
                cpu_suite=self.fixture.cpu_path,
                home_authority=self.fixture.home_authority_path,
                repository_root=repository,
                scientific_identity=copy.deepcopy(
                    self.fixture.scientific_identity),
                case_authority_snapshots=snapshots,
                pre_run_capture_audit=copy.deepcopy(
                    self.fixture.spec["pre_run_capture_audit"]),
                output_root=output_root,
                product_sources=product_sources,
            )

    def test_resigned_diagnostic_registry_eligibility_upgrade_fails(self):
        case_id = R.CASE_IDS[0]
        index = R.CASE_IDS.index(case_id)
        case_spec = self.fixture.spec["cases"][index]
        snapshot = case_spec["pre_run_case_authorities"]
        registry = snapshot["physical_registry"]
        authority = snapshot["diagnostic_physical_authority"]
        entry = authority["entry"]
        entry["eligibility"] = "CANONICAL_PRODUCTION"
        entry["canonical_template_id"] = "forged.production.template"
        for offset, candidate in enumerate(registry["entries"]):
            if candidate["entry_id"] == entry["entry_id"]:
                registry["entries"][offset] = copy.deepcopy(entry)
        registry["registry_sha256"] = R.digest({
            "schema": R.PHYSICAL_REGISTRY_SCHEMA,
            "issuer_domain": registry["issuer_domain"],
            "registry_source_sha256": registry["registry_source_sha256"],
            "entries": registry["entries"],
        })
        registry["authority_nonce"] = R.digest({
            "kind": R.PHYSICAL_REGISTRY_SCHEMA,
            "registry_sha256": registry["registry_sha256"],
        })
        def resign_authority(value: dict) -> None:
            value["registry_sha256"] = registry["registry_sha256"]
            value["entry_sha256"] = R.digest(value["entry"])
            value["authority_sha256"] = R.digest({
                "schema": R.PHYSICAL_AUTHORITY_SCHEMA,
                "registry_sha256": registry["registry_sha256"],
                "entry_sha256": value["entry_sha256"],
                "entry_id": value["entry"]["entry_id"],
                "eligibility": value["entry"]["eligibility"],
            })
            value["authority_nonce"] = R.digest({
                "kind": R.PHYSICAL_AUTHORITY_SCHEMA,
                "authority_sha256": value["authority_sha256"],
                "registry_nonce": registry["authority_nonce"],
            })

        resign_authority(authority)
        canonical_authority = snapshot["canonical_physical_authority"]
        resign_authority(canonical_authority)
        snapshot["physical_registry"] = registry
        snapshot["diagnostic_physical_authority"] = authority
        snapshot["canonical_physical_authority"] = canonical_authority
        case_spec["pre_run_case_authorities"] = _seal(
            snapshot, "snapshot_sha256")
        self.fixture.spec["cases"][index] = _seal(
            case_spec, "case_execution_spec_sha256")
        self.fixture.spec = _seal(self.fixture.spec, "execution_spec_sha256")
        _json(self.fixture.spec_path, self.fixture.spec)
        with self.assertRaisesRegex(
                AssertionError,
                "entry/eligibility mismatch|case cardinality mismatch"):
            self.recount()

    def test_resigned_map_deletion_fails(self):
        case_id = R.CASE_IDS[0]
        snapshot = self.fixture.spec["cases"][0]["pre_run_case_authorities"]
        for entry in snapshot["physical_registry"]["entries"]:
            entry["guarantee"]["maps"].pop()
        self._resign_spec_registry(case_id)
        with self.assertRaisesRegex(AssertionError, "map stage count mismatch"):
            self.recount()

    def test_resigned_map_source_substitution_fails(self):
        case_id = R.CASE_IDS[1]
        snapshot = self.fixture.spec["cases"][1]["pre_run_case_authorities"]
        for entry in snapshot["physical_registry"]["entries"]:
            entry["guarantee"]["maps"][0]["source_id"] = (
                "src/rtdsl/v4_semantic_physical_admission.py")
        self._resign_spec_registry(case_id)
        with self.assertRaisesRegex(AssertionError, "map source binding mismatch"):
            self.recount()

    def test_resigned_unused_manifest_member_fails(self):
        case_id = R.CASE_IDS[2]
        snapshot = self.fixture.spec["cases"][2]["pre_run_case_authorities"]
        extra = "src/rtdsl/v4_semantic_physical_admission.py"
        extra_sha = self.fixture.spec["pre_run_source_members"][1]["sha256"]
        for entry in snapshot["physical_registry"]["entries"]:
            manifest = entry["guarantee"]["source_manifest"]
            manifest[extra] = extra_sha
            entry["source_bytes_manifest_sha256"] = R.digest(manifest)
        self._resign_spec_registry(case_id)
        with self.assertRaisesRegex(AssertionError,
                                    "not exact map-source union"):
            self.recount()

    def test_resigned_extra_canonical_registry_entry_fails(self):
        case_id = R.CASE_IDS[5]
        index = R.CASE_IDS.index(case_id)
        snapshot = self.fixture.spec["cases"][index]["pre_run_case_authorities"]
        extra = copy.deepcopy(snapshot["physical_registry"]["entries"][0])
        extra["entry_id"] = "forged.second.canonical.entry"
        snapshot["physical_registry"]["entries"].append(extra)
        self._resign_spec_registry(case_id)
        with self.assertRaisesRegex(AssertionError,
                                    "case cardinality mismatch"):
            self.recount()

    def test_resigned_semantic_and_physical_policy_substitution_fails(self):
        case_id = R.CASE_IDS[3]
        index = R.CASE_IDS.index(case_id)
        snapshot = self.fixture.spec["cases"][index]["pre_run_case_authorities"]
        authority = snapshot["semantic_authority"]
        authority["requirement"]["policy"]["exactness"] = "forged_exactness"
        authority["authority_sha256"] = R.digest({
            "schema": R.SEMANTIC_AUTHORITY_SCHEMA,
            "requirement_sha256": R.digest(authority["requirement"]),
            "specification_source_sha256": authority["requirement"][
                "specification_source_sha256"],
            "oracle_source_sha256": authority["oracle_source_sha256"],
            "issuer_domain": authority["issuer_domain"],
        })
        authority["authority_nonce"] = R.digest({
            "kind": R.SEMANTIC_AUTHORITY_SCHEMA,
            "authority_sha256": authority["authority_sha256"],
        })
        for entry in snapshot["physical_registry"]["entries"]:
            entry["guarantee"]["guarantees"]["exactness"] = "forged_exactness"
        self._resign_spec_registry(case_id)
        with self.assertRaisesRegex(AssertionError,
                                    "not the frozen case contract"):
            self.recount()

    def test_resigned_governance_authority_replacement_fails(self):
        replacement = b"replacement governance authority\n"
        self.fixture.governance_authority.write_bytes(replacement)
        row = next(item for item in
                   self.fixture.spec["governance_authority_members"]
                   if item["logical_path"] == BUILD.PARTICLE_GATE_AUTHORITY)
        row["sha256"] = hashlib.sha256(replacement).hexdigest()
        self.fixture.spec = _seal(self.fixture.spec, "execution_spec_sha256")
        _json(self.fixture.spec_path, self.fixture.spec)
        with self.assertRaisesRegex(AssertionError,
                                    "amendment authority is not exact"):
            self.recount()

    def test_resigned_pre_run_capture_import_pollution_fails(self):
        audit = self.fixture.spec["pre_run_capture_audit"]
        audit["new_module_names"] = ["cupy", "rtdsl"]
        audit["forbidden_low_level_imports"] = []
        self.fixture.spec["pre_run_capture_audit"] = _seal(
            audit, "audit_sha256")
        self.fixture.spec = _seal(self.fixture.spec, "execution_spec_sha256")
        _json(self.fixture.spec_path, self.fixture.spec)
        with self.assertRaisesRegex(AssertionError,
                                    "forbidden/eager modules"):
            self.recount()

    def test_resigned_postrun_target_cannot_redefine_prerun_target(self):
        case_id = R.CASE_IDS[5]
        arm = self.fixture.raw[case_id]["diagnostic_counterfactual"]
        arm["physical_identity"]["target_sha256"] = _sha("forged-target")
        arm["physical_identity"] = _seal(
            arm["physical_identity"], "observation_sha256")
        arm["execution_binding_sha256"] = R.digest({
            "case_sha256": arm["case_sha256"],
            "physical_identity_sha256": arm["physical_identity"][
                "observation_sha256"],
            "executed_input_sha256": arm["executed_input_sha256"],
            "outcome_sha256": arm["outcome_sha256"],
            "traversal_receipt_sha256s": [
                row["receipt_sha256"] for row in arm["traversal_receipts"]],
            "device_continuation_receipt_sha256": None,
        })
        self.fixture.resign_raw(case_id)
        with self.assertRaisesRegex(AssertionError,
                                    "frozen pre-run family"):
            self.recount()

    def test_resigned_wrong_counterfactual_output_fails(self):
        case_id = R.CASE_IDS[3]
        arm = self.fixture.raw[case_id]["diagnostic_counterfactual"]
        arm["outcome"]["value"] = 5
        arm["outcome_sha256"] = R.digest(arm["outcome"])
        self.fixture.resign_raw(case_id)
        with self.assertRaisesRegex(AssertionError, "outcome mismatch"):
            self.recount()

    def test_resigned_numeric_gpu_input_drift_fails(self):
        case_id = R.CASE_IDS[0]
        arm = self.fixture.raw[case_id]["diagnostic_counterfactual"]
        column = arm["executed_input"]["columns"][
            "query_origin_direction_tmax"]
        raw = bytearray.fromhex(column["bytes_hex"])
        raw[-1] ^= 1
        column["bytes_hex"] = bytes(raw).hex()
        column["bytes_sha256"] = hashlib.sha256(bytes(raw)).hexdigest()
        arm["executed_input_sha256"] = R.digest(arm["executed_input"])
        arm["execution_binding_sha256"] = R.digest({
            "case_sha256": arm["case_sha256"],
            "physical_identity_sha256": arm["physical_identity"][
                "observation_sha256"],
            "executed_input_sha256": arm["executed_input_sha256"],
            "outcome_sha256": arm["outcome_sha256"],
            "traversal_receipt_sha256s": [
                row["receipt_sha256"] for row in arm["traversal_receipts"]],
            "device_continuation_receipt_sha256": None,
        })
        self.fixture.resign_raw(case_id)
        with self.assertRaisesRegex(AssertionError,
                                    "independent numeric-input mismatch"):
            self.recount()

    def test_resigned_u64_host_fallback_device_receipt_fails(self):
        case_id = R.CASE_IDS[2]
        arm = self.fixture.raw[case_id]["diagnostic_counterfactual"]
        receipt = arm["device_continuation_receipt"]
        receipt["host_fallback_used"] = True
        arm["device_continuation_receipt"] = _seal(
            receipt, "receipt_sha256")
        arm["execution_binding_sha256"] = R.digest({
            "case_sha256": arm["case_sha256"],
            "physical_identity_sha256": arm["physical_identity"][
                "observation_sha256"],
            "executed_input_sha256": arm["executed_input_sha256"],
            "outcome_sha256": arm["outcome_sha256"],
            "traversal_receipt_sha256s": [
                row["receipt_sha256"] for row in arm["traversal_receipts"]],
            "device_continuation_receipt_sha256": arm[
                "device_continuation_receipt"]["receipt_sha256"],
        })
        self.fixture.resign_raw(case_id)
        with self.assertRaisesRegex(AssertionError,
                                    "device continuation evidence mismatch"):
            self.recount()

    def test_resigned_case_swap_fails(self):
        left, right = R.CASE_IDS[:2]
        self.fixture.raw[left]["shared_case_identity"] = copy.deepcopy(
            self.fixture.raw[right]["shared_case_identity"])
        self.fixture.resign_raw(left)
        with self.assertRaisesRegex(AssertionError, "raw cross-binding mismatch"):
            self.recount()

    def test_reject_with_one_launch_fails_even_when_resigned(self):
        case_id = R.CASE_IDS[0]
        reject = self.fixture.raw[case_id]["product_admission_reject"]
        reject["traversal_launch_count"] = 1
        reject["process_audit"]["traversal_launch_count"] = 1
        self.fixture.resign_raw(case_id)
        with self.assertRaisesRegex(AssertionError, "traversal_launch_count"):
            self.recount()

    def test_resigned_generic_product_rule_cannot_replace_case_specific_rule(self):
        case_id = R.CASE_IDS[1]
        case_index = R.CASE_IDS.index(case_id)
        spec_case = self.fixture.spec["cases"][case_index]
        spec_case["expected_product_rejection"][
            "required_stable_product_rule_ids"] = [
                "SP022_SEMANTIC_GUARANTEE_MISMATCH"]
        self.fixture.spec["cases"][case_index] = _seal(
            spec_case, "case_execution_spec_sha256")
        self.fixture.spec = _seal(self.fixture.spec, "execution_spec_sha256")
        _json(self.fixture.spec_path, self.fixture.spec)
        raw = self.fixture.raw[case_id]
        raw["execution_spec_sha256"] = self.fixture.spec["execution_spec_sha256"]
        raw["case_execution_spec_sha256"] = spec_case["case_execution_spec_sha256"]
        raw["product_admission_reject"]["case_execution_spec_sha256"] = \
            spec_case["case_execution_spec_sha256"]
        raw["product_admission_reject"]["admission_decision"][
            "stable_product_rule_ids"] = ["SP022_SEMANTIC_GUARANTEE_MISMATCH"]
        raw["product_admission_reject"]["admission_decision"] = _seal(
            raw["product_admission_reject"]["admission_decision"],
            "decision_sha256")
        for arm_name in ("diagnostic_counterfactual", "accepted_control"):
            raw[arm_name]["case_execution_spec_sha256"] = \
                spec_case["case_execution_spec_sha256"]
        self.fixture.raw[case_id] = raw
        self.fixture.resign_raw(case_id)
        with self.assertRaisesRegex(AssertionError, "stable product rule mapping"):
            self.recount()

    def test_resigned_traversal_semantic_binding_fails(self):
        case_id = R.CASE_IDS[0]
        arm = self.fixture.raw[case_id]["diagnostic_counterfactual"]
        arm["traversal_semantic_bindings"][0]["contract"] = _sha("forged")
        receipt = arm["traversal_receipts"][0]
        receipt["semantic_digest"] = R.digest(arm["traversal_semantic_bindings"][0])
        arm["traversal_receipts"][0] = _seal(receipt, "receipt_sha256")
        self.fixture.resign_raw(case_id)
        with self.assertRaisesRegex(AssertionError, "semantic binding mismatch"):
            self.recount()

    def test_diagnostic_symbol_in_product_api_fails_after_full_resign(self):
        self.fixture.product_source.write_text(
            f"def {self.fixture.symbol}():\n    return 'leak'\n", encoding="utf-8")
        row = self.fixture.spec["diagnostic_api_audit"]["product_source_members"][0]
        row["sha256"] = BUILD.sha_file(self.fixture.product_source)
        self.fixture.spec = _seal(self.fixture.spec, "execution_spec_sha256")
        _json(self.fixture.spec_path, self.fixture.spec)
        for case_id in R.CASE_IDS:
            raw = self.fixture.raw[case_id]
            raw["execution_spec_sha256"] = self.fixture.spec["execution_spec_sha256"]
            raw["product_admission_reject"]["process_audit"][
                "admission_module_source_sha256"] = row["sha256"]
            raw["product_admission_reject"] = _seal(
                raw["product_admission_reject"], "receipt_sha256")
            self.fixture.raw[case_id] = _seal(raw, "raw_result_sha256")
            self.fixture.write_raw(case_id)
        with self.assertRaisesRegex(
                AssertionError,
                "pre-run source bytes mismatch|diagnostic symbol leaked"):
            self.recount()

    def test_pod_or_timing_claim_fails_when_resigned(self):
        case_id = R.CASE_IDS[5]
        arm = self.fixture.raw[case_id]["accepted_control"]
        arm["pod_used"] = True
        arm["registered_performance_timing_created"] = True
        self.fixture.resign_raw(case_id)
        with self.assertRaisesRegex(AssertionError, "claim boundary drift"):
            self.recount()

    def test_resigned_home_authority_drift_fails_file_identity(self):
        authority = copy.deepcopy(self.fixture.home_authority)
        authority["driver_version"] = "forged-driver"
        authority = _seal(authority, "receipt_sha256")
        _json(self.fixture.home_authority_path, authority)
        with self.assertRaisesRegex(AssertionError,
                                    "authority file SHA mismatch"):
            self.recount()

    def test_actual_controller_adapter_recounts_exact_18_worker_bytes(self):
        actual = ActualControllerFixture(self.fixture, self.root / "actual")
        result = BUILD.adapt_controller_result(
            cpu_suite=self.fixture.cpu_path,
            execution_spec=self.fixture.spec_path,
            pre_run_root=self.root,
            controller_root=actual.controller_root,
            expected_suite_sha256=self.fixture.cpu_suite["suite_sha256"],
            output_root=actual.adapted_root,
        )
        self.assertEqual(result["case_count"], 6)
        self.assertEqual(result["worker_count"], 18)
        recount = R.recount(
            actual.adapted_root / "AUTHORITIES/CPU_SUITE.json",
            actual.adapted_root / "AUTHORITIES/HOME_EXECUTION_SPEC.json",
            actual.adapted_root,
            self.fixture.cpu_suite["suite_sha256"],
        )
        self.assertEqual(recount["arm_count"], 18)
        self.assertEqual(recount["unique_parent_pid_count"], 18)
        self.assertEqual(recount["behavioral_true_optix_execution_count"], 11)
        archive = actual.root / "adapted-evidence.tar.gz"
        twin = actual.root / "adapted-evidence.twin.tar.gz"
        packaged = BUILD.build(
            cpu_suite=actual.adapted_root / "AUTHORITIES/CPU_SUITE.json",
            execution_spec=(actual.adapted_root /
                            "AUTHORITIES/HOME_EXECUTION_SPEC.json"),
            raw_root=actual.adapted_root,
            expected_suite_sha256=self.fixture.cpu_suite["suite_sha256"],
            output=archive, twin=twin)
        self.assertEqual(archive.read_bytes(), twin.read_bytes())
        self.assertEqual(packaged["recount_sha256"], recount["recount_sha256"])

    def test_actual_controller_fully_resigned_wrong_output_fails(self):
        actual = ActualControllerFixture(self.fixture, self.root / "actual")
        BUILD.adapt_controller_result(
            cpu_suite=self.fixture.cpu_path,
            execution_spec=self.fixture.spec_path,
            pre_run_root=self.root,
            controller_root=actual.controller_root,
            expected_suite_sha256=self.fixture.cpu_suite["suite_sha256"],
            output_root=actual.adapted_root,
        )
        case_id = R.CASE_IDS[3]
        arm_name = "diagnostic_counterfactual"
        worker_path = (actual.adapted_root / "CONTROLLER/RAW" /
                       BUILD._worker_filename(case_id, arm_name))
        worker = json.loads(worker_path.read_text(encoding="utf-8"))
        worker["arm_result"]["output"] = 999
        worker["arm_result"]["own_oracle"] = 999
        worker = _seal(worker, "worker_result_sha256")
        _json(worker_path, worker)
        controller_path = actual.adapted_root / "CONTROLLER/RESULT.json"
        controller = json.loads(controller_path.read_text(encoding="utf-8"))
        target_case = next(row for row in controller["cases"]
                           if row["case_id"] == case_id)
        target_case["arms"][arm_name] = copy.deepcopy(worker)
        controller = _seal(controller, "result_sha256")
        _json(controller_path, controller)
        for manifest_path in sorted((actual.adapted_root / "raw").glob("*.json")):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["controller_result_file_sha256"] = BUILD.sha_file(
                controller_path)
            manifest["controller_result_sha256"] = controller["result_sha256"]
            controller_case = next(row for row in controller["cases"]
                                   if row["case_id"] == manifest["case_id"])
            manifest["controller_case_sha256"] = R.digest(controller_case)
            if manifest["case_id"] == case_id:
                ref = manifest["source_workers"][arm_name]
                ref["file_sha256"] = BUILD.sha_file(worker_path)
                ref["worker_result_sha256"] = worker["worker_result_sha256"]
                manifest["source_worker_set_sha256"] = R.digest(
                    manifest["source_workers"])
            manifest = _seal(manifest, "raw_result_sha256")
            _json(manifest_path, manifest)
        with self.assertRaisesRegex(AssertionError, "output/oracle mismatch"):
            R.recount(
                actual.adapted_root / "AUTHORITIES/CPU_SUITE.json",
                actual.adapted_root / "AUTHORITIES/HOME_EXECUTION_SPEC.json",
                actual.adapted_root,
                self.fixture.cpu_suite["suite_sha256"],
            )

    def test_deterministic_nonself_archive_and_twin(self):
        output = self.root / "evidence.tar.gz"
        twin = self.root / "evidence.twin.tar.gz"
        result = BUILD.build(
            cpu_suite=self.fixture.cpu_path,
            execution_spec=self.fixture.spec_path,
            raw_root=self.root,
            expected_suite_sha256=self.fixture.cpu_suite["suite_sha256"],
            output=output,
            twin=twin,
        )
        self.assertEqual(output.read_bytes(), twin.read_bytes())
        self.assertEqual(result["archive_sha256"], BUILD.sha_file(output))
        with tarfile.open(output, "r:gz") as archive:
            names = archive.getnames()
            manifest = json.load(archive.extractfile("MANIFEST.json"))
            extracted = self.root / "extracted"
            archive.extractall(extracted, filter="data")
        self.assertNotIn("MANIFEST.json", {row["path"] for row in manifest["payloads"]})
        self.assertEqual(manifest["payload_count"], len(manifest["payloads"]))
        self.assertTrue(all(not name.endswith((".cubin", ".so")) for name in names))
        extracted_recount = R.recount(
            extracted / "AUTHORITIES" / "CPU_SUITE.json",
            extracted / "AUTHORITIES" / "HOME_EXECUTION_SPEC.json",
            extracted,
            self.fixture.cpu_suite["suite_sha256"],
        )
        self.assertEqual(extracted_recount["recount_sha256"], result["recount_sha256"])


if __name__ == "__main__":
    unittest.main()

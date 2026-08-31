from __future__ import annotations

import ast
from dataclasses import dataclass, replace
import hashlib
import inspect
import os
from pathlib import Path
import subprocess
import sys
import textwrap
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from rtdsl.v4_bounded_relation import (
    BOUNDED_RELATION_TEMPLATE,
    CompiledBoundedRelationContract,
    VerifiedBoundedRelationAuthority,
)
from rtdsl.v4_callback_abi import CompiledCallbackAbi
from rtdsl.v4_semantic_physical_admission import (
    NO_ORIENTATION_CONTRACT_SHA256,
    PhysicalEncodingEligibility,
    SemanticPhysicalAdmissionError,
    _issue_compiler_physical_guarantee_registry,
    issue_registered_physical_guarantee_authority,
    issue_semantic_requirement_authority,
    physical_guarantee_registry_entry,
)
from rtdsl.v4_semantically_admitted_compiler import (
    SemanticallyAdmittedCompilerError,
    admit_bounded_relation_compilation,
    admit_builtin_triangle_compilation,
    admit_triangle_reduction_compilation,
    compile_semantically_admitted_bounded_relation_executable,
    compile_semantically_admitted_builtin_triangle_executable,
    compile_semantically_admitted_triangle_reduction_executable,
    consume_semantically_admitted_bounded_relation_executable,
    consume_semantically_admitted_builtin_triangle_executable,
    consume_semantically_admitted_triangle_reduction_executable,
    require_semantically_admitted_bounded_relation_executable,
    require_semantically_admitted_builtin_triangle_executable,
    require_semantically_admitted_triangle_reduction_executable,
    run_semantically_admitted_bounded_relation_callback,
    run_semantically_admitted_builtin_triangle_callback,
    run_semantically_admitted_triangle_reduction_callback,
)
from rtdsl.v4_triangle_reduction import (
    TRIANGLE_REDUCTION_TEMPLATE,
    CompiledTriangleReductionContract,
    VerifiedTriangleReductionAuthority,
)
from rtdsl.v4_typed_physical_schema import (
    CanonicalPhysicalPlan,
    GeometryFamily,
    ReferenceTargetProfile,
    ReferenceTemplateId,
    VerifiedPhysicalSchemaAuthority,
)


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _policy(label: str) -> dict[str, str]:
    return {
        "input_type": f"{label}_input",
        "output_type": f"{label}_output",
        "exactness": "exact",
        "tie_policy": "deterministic_u32",
        "order_policy": "canonical",
        "multiplicity": "declared",
        "numeric_precision": "checked_integer",
        "overflow_policy": "fail_closed",
    }


def _semantic_and_physical(
    label: str,
    *,
    geometry: str,
    schema_sha256: str,
    callback_ir_sha256: str,
    effect_digest: str,
    orientation_contract_sha256: str = NO_ORIENTATION_CONTRACT_SHA256,
) -> tuple[dict[str, object], dict[str, object]]:
    policy = _policy(label)
    graph = {
        "encode": (["semantic_input"], ["geometry", "query_state"]),
        "ray": (["query_state"], ["ray"]),
        "trace": (["geometry", "ray"], ["hit_stream"]),
        "continuation": (["hit_stream"], ["candidate_output"]),
        "decode": (["candidate_output"], ["semantic_output"]),
    }
    sources = {kind: f"provider/{label}/{kind}.py" for kind in graph}
    semantic = {
        "contract_id": f"semantic.{label}.v1",
        "algorithm_identity": f"algorithm.{label}.v1",
        "declared_domain_sha256": _sha(f"domain:{label}"),
        "policy": policy,
        "required_hit_semantics": [f"{label}_hit"],
        "orientation_contract_sha256": orientation_contract_sha256,
        "specification_source_sha256": _sha(f"spec:{label}"),
    }
    physical = {
        "encoding_id": f"physical.{label}.v1",
        "supported_algorithm_identity": semantic["algorithm_identity"],
        "supported_domain_sha256": semantic["declared_domain_sha256"],
        "orientation_contract_sha256": orientation_contract_sha256,
        "geometry_family": geometry,
        "schema_sha256": schema_sha256,
        "callback_ir_sha256": callback_ir_sha256,
        "effect_digest": effect_digest,
        "guarantees": dict(policy),
        "maps": [
            {
                "kind": kind,
                "source_id": sources[kind],
                "source_sha256": _sha(sources[kind]),
                "consumes": consumes,
                "produces": produces,
            }
            for kind, (consumes, produces) in graph.items()
        ],
        "hit_semantics": [f"{label}_hit"],
        "gas_graph_depth": 1,
        "gas_sbt_record_stride": 1,
        "gas_update_policy": "static",
        "buffer_contract_sha256": _sha(f"buffer:{label}"),
        "required_target_capabilities": [
            "bound_program_bundle", "optix", "optix_builtin_triangle",
            "optix_custom_aabb",
        ],
        "source_manifest": {
            path: _sha(path) for path in sources.values()
        },
    }
    return semantic, physical


def _issued_declarations(
    semantic: dict[str, object], physical: dict[str, object], *,
    template_id: str,
):
    semantic_authority = issue_semantic_requirement_authority(
        semantic,
        oracle_source_sha256=_sha("independent-test-oracle"),
        issuer_domain="app.test.semantic.v1",
    )
    entry = physical_guarantee_registry_entry(
        "compiler.test.canonical.v1", physical,
        eligibility=PhysicalEncodingEligibility.CANONICAL_PRODUCTION,
        canonical_template_id=template_id,
        classifier_source_sha256=_sha("compiler-classifier-source"),
    )
    registry = _issue_compiler_physical_guarantee_registry(
        (entry,), registry_source_sha256=_sha("compiler-registry-source"))
    physical_authority = issue_registered_physical_guarantee_authority(
        registry, entry.entry_id)
    return semantic_authority, physical_authority


def _target(label: str) -> ReferenceTargetProfile:
    return ReferenceTargetProfile(
        provider="optix",
        optix_sdk="9.0",
        compute_capability="8.9",
        native_sha256=_sha(f"native:{label}"),
        supports_custom_aabb=True,
        supports_builtin_triangle=True,
    )


def _callback_and_abi(label: str):
    callback = SimpleNamespace(
        ir_sha256=_sha(f"callback:{label}"),
        effect_digest=_sha(f"effect:{label}"),
    )
    abi = CompiledCallbackAbi(
        schema_id="test.callback.abi",
        schema_version="v1",
        callback_ir_sha256=callback.ir_sha256,
        callback_effect_digest=callback.effect_digest,
        any_hit_proof_sha256=None,
        any_hit_proof_kind=None,
        any_hit_delivery_contract=None,
        runtime_status_codes=(),
        roles=(),
        abi_sha256=_sha(f"abi:{label}"),
    )
    return callback, abi


def _builtin(label: str):
    callback, abi = _callback_and_abi(label)
    target = _target(label)
    schema = SimpleNamespace(
        schema_sha256=_sha(f"typed-schema:{label}"),
        geometry_family=GeometryFamily.BUILTIN_TRIANGLE,
    )
    orientation = SimpleNamespace(authority_sha256=_sha(f"orientation:{label}"))
    authority = VerifiedPhysicalSchemaAuthority(
        callback, schema, target, orientation, f"authority-{label}")
    plan = CanonicalPhysicalPlan(
        template_id=ReferenceTemplateId.BUILTIN_TRIANGLE_V1,
        schema_sha256=schema.schema_sha256,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        target_sha256=target.target_sha256,
        role_topology=(),
        ordered_buffer_semantics=(),
        authority_nonce=authority.authority_nonce,
        executable=False,
    )
    raw_declarations = _semantic_and_physical(
        label,
        geometry=GeometryFamily.BUILTIN_TRIANGLE.value,
        schema_sha256=schema.schema_sha256,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        orientation_contract_sha256=orientation.authority_sha256,
    )
    declarations = _issued_declarations(
        *raw_declarations, template_id=plan.template_id.value)
    return declarations, authority, plan, abi


def _triangle_reduction(label: str):
    callback, abi = _callback_and_abi(label)
    target = _target(label)
    schema = SimpleNamespace(schema_sha256=_sha(f"reduction-schema:{label}"))
    authority = VerifiedTriangleReductionAuthority(
        callback, schema, target, f"authority-{label}")
    contract = CompiledTriangleReductionContract(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        schema_sha256=schema.schema_sha256,
        target_sha256=target.target_sha256,
        abi_sha256=abi.abi_sha256,
        template_id=TRIANGLE_REDUCTION_TEMPLATE,
        metadata_channels=(),
        reducer={},
        role_topology=(),
        authority_nonce=authority.authority_nonce,
        executable=False,
    )
    raw_declarations = _semantic_and_physical(
        label,
        geometry=GeometryFamily.BUILTIN_TRIANGLE.value,
        schema_sha256=schema.schema_sha256,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
    )
    declarations = _issued_declarations(
        *raw_declarations, template_id=contract.template_id)
    return declarations, authority, contract, abi


def _bounded_relation(label: str):
    callback, abi = _callback_and_abi(label)
    target = _target(label)
    physical_schema = SimpleNamespace(
        schema_sha256=_sha(f"typed-schema:{label}"),
        geometry_family=GeometryFamily.CUSTOM_AABB,
    )
    physical = VerifiedPhysicalSchemaAuthority(
        callback, physical_schema, target, None, f"physical-{label}")
    relation_schema = SimpleNamespace(
        schema_sha256=_sha(f"relation-schema:{label}"))
    authority = VerifiedBoundedRelationAuthority(
        physical, relation_schema, f"authority-{label}")
    contract = CompiledBoundedRelationContract(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        physical_schema_sha256=physical_schema.schema_sha256,
        relation_schema_sha256=relation_schema.schema_sha256,
        target_sha256=target.target_sha256,
        abi_sha256=abi.abi_sha256,
        capacity=16,
        minimum_overlap_f32=0.0,
        row_sources=("launch_source_id", "verified_item_id"),
        ordering="lexicographic_u32_pair",
        duplicate_policy="keyed_identical_dedup",
        authority_nonce=authority.authority_nonce,
        template_id=BOUNDED_RELATION_TEMPLATE,
        executable=False,
    )
    raw_declarations = _semantic_and_physical(
        label,
        geometry=GeometryFamily.CUSTOM_AABB.value,
        schema_sha256=relation_schema.schema_sha256,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
    )
    declarations = _issued_declarations(
        *raw_declarations, template_id=contract.template_id)
    return declarations, authority, contract, abi


@dataclass(frozen=True, eq=False)
class _FakeExecutable:
    executable_sha256: str


class SemanticallyAdmittedCompilerTest(unittest.TestCase):
    def test_pure_standard_library_admission_imports_no_gpu_compiler_stack(self):
        root = Path(__file__).resolve().parents[1]
        for relative in (
            "src/rtdsl/v4_builtin_triangle_standard_library.py",
            "src/rtdsl/v4_triangle_standard_library.py",
            "src/rtdsl/v4_bounded_relation_standard_library.py",
        ):
            tree = ast.parse((root / relative).read_text(encoding="utf-8"))
            eager = []
            for node in tree.body:
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if "optix_compiler" in module or "optix_runtime" in module:
                        eager.append(module)
                elif isinstance(node, ast.Import):
                    eager.extend(
                        alias.name for alias in node.names
                        if "optix_compiler" in alias.name
                        or "optix_runtime" in alias.name)
            self.assertEqual(eager, [], relative)

        code = textwrap.dedent("""
            import importlib, pathlib, sys, types
            package = types.ModuleType("rtdsl")
            package.__path__ = [str(pathlib.Path("src/rtdsl").resolve())]
            package.__package__ = "rtdsl"
            sys.modules["rtdsl"] = package
            before = set(sys.modules)
            builtin = importlib.import_module(
                "rtdsl.v4_builtin_triangle_standard_library")
            callback = builtin.compile_adjacency_callback()
            orientation = builtin.make_orientation_authority(
                callback, source_semantics_sha256="a" * 64,
                independent_oracle_sha256="b" * 64)
            builtin.adjacency_schema(
                callback,
                orientation_authority_sha256=orientation.authority_sha256)
            reduction = importlib.import_module(
                "rtdsl.v4_triangle_standard_library")
            reduced = reduction.compile_count_callback()
            reduction.all_hit_count_schema(reduced)
            relation = importlib.import_module(
                "rtdsl.v4_bounded_relation_standard_library")
            assert callable(relation.compile_standard_bounded_relation_authority)
            loaded = set(sys.modules) - before
            forbidden = sorted(name for name in loaded if
                "optix_compiler" in name or "optix_runtime" in name
                or name == "numba" or name.startswith("numba.")
                or name == "cupy" or name.startswith("cupy."))
            if forbidden:
                raise SystemExit(repr(forbidden))
        """)
        environment = dict(os.environ)
        environment["PYTHONPATH"] = os.pathsep.join((
            str(root / "src"), str(root)))
        completed = subprocess.run(
            [sys.executable, "-c", code], cwd=root, env=environment,
            text=True, capture_output=True, check=False)
        self.assertEqual(
            completed.returncode, 0,
            completed.stdout + completed.stderr)

    def test_standard_compile_entrypoints_still_delegate_after_lazy_import(self):
        from rtdsl.v4_builtin_triangle_standard_library import (
            compile_standard_builtin_triangle_program,
        )
        fake_builtin = object()
        with patch(
                "rtdsl.v4_triangle_optix_compiler."
                "compile_verified_triangle_executable",
                return_value=(fake_builtin, "builtin-log")) as low_builtin:
            program = compile_standard_builtin_triangle_program(
                _target("lazy-standard-builtin"),
                source_semantics_sha256=_sha("source-semantics"),
                independent_oracle_sha256=_sha("independent-oracle"),
                compute_capability=(8, 9), optix_include="optix",
                cuda_include="cuda", expected_python_version="3.11",
                expected_numba_version="test", expected_numpy_version="test")
        self.assertIs(program.executable, fake_builtin)
        low_builtin.assert_called_once()

        from rtdsl.v4_callback_abi import AnyHitProofAuthority
        from rtdsl.v4_callback_ir import AnyHitDeliveryContract
        from rtdsl.v4_triangle_standard_library import (
            all_hit_count_schema,
            compile_count_callback,
            compile_standard_triangle_program,
        )
        callback = compile_count_callback()
        proof = AnyHitProofAuthority(
            callback_ir_sha256=callback.ir_sha256,
            effect_digest=callback.effect_digest,
            delivery_contract=(
                AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL),
            proof_sha256=_sha("order-independent-proof"),
            proof_kind="external_machine_checked_order_independence_v1",
        )
        fake_reduction = object()
        with patch(
                "rtdsl.v4_triangle_reduction_optix_compiler."
                "compile_verified_triangle_reduction_executable",
                return_value=(fake_reduction, "reduction-log")) as low_reduction:
            reduced = compile_standard_triangle_program(
                callback, all_hit_count_schema(callback),
                _target("lazy-standard-reduction"), proof,
                compute_capability=(8, 9), optix_include="optix",
                cuda_include="cuda", expected_python_version="3.11",
                expected_numba_version="test", expected_numpy_version="test")
        self.assertIs(reduced.executable, fake_reduction)
        low_reduction.assert_called_once()

    def test_all_three_families_reverify_then_call_low_level_exactly_once(self):
        rows = (
            (_builtin("builtin"), admit_builtin_triangle_compilation,
             compile_semantically_admitted_builtin_triangle_executable,
             require_semantically_admitted_builtin_triangle_executable,
             "_compile_verified_triangle_executable"),
            (_triangle_reduction("reduction"),
             admit_triangle_reduction_compilation,
             compile_semantically_admitted_triangle_reduction_executable,
             require_semantically_admitted_triangle_reduction_executable,
             "_compile_verified_triangle_reduction_executable"),
            (_bounded_relation("relation"), admit_bounded_relation_compilation,
             compile_semantically_admitted_bounded_relation_executable,
             require_semantically_admitted_bounded_relation_executable,
             "_compile_verified_bounded_relation_executable"),
        )
        for index, (fixture, admit, compile_admitted, require_admitted,
                    low_name) in enumerate(rows):
            with self.subTest(family=low_name):
                declarations, authority, artifact, abi = fixture
                admission = admit(
                    *declarations, authority=authority,
                    **({"plan": artifact} if isinstance(
                        artifact, CanonicalPhysicalPlan) else {"contract": artifact}),
                    abi=abi,
                )
                executable = _FakeExecutable(_sha(f"executable:{index}"))
                with patch(
                    "rtdsl.v4_semantically_admitted_compiler." + low_name,
                    return_value=(executable, "compiler log"),
                ) as low_level:
                    result = compile_admitted(
                        admission, authority, artifact, abi,
                        compute_capability=(8, 9))
                self.assertEqual(result, (executable, "compiler log"))
                self.assertEqual(low_level.call_count, 1)
                self.assertIs(
                    require_admitted(
                        executable, admission, authority, artifact, abi),
                    executable,
                )

    def test_wrong_admission_stops_before_low_level_compiler(self):
        first, first_authority, first_plan, first_abi = _builtin("first")
        admission = admit_builtin_triangle_compilation(
            *first, authority=first_authority, plan=first_plan, abi=first_abi)
        _, second_authority, second_plan, second_abi = _builtin("second")
        with patch(
                "rtdsl.v4_semantically_admitted_compiler."
                "_compile_verified_triangle_executable") as low_level:
            with self.assertRaises(SemanticallyAdmittedCompilerError):
                compile_semantically_admitted_builtin_triangle_executable(
                    admission, second_authority, second_plan, second_abi)
        low_level.assert_not_called()

    def test_algorithm_or_domain_substitution_cannot_reach_low_level_compiler(self):
        for field, value, rule in (
            ("algorithm_identity", "algorithm.attacker.v1",
             "SP037_ALGORITHM_IDENTITY_MISMATCH"),
            ("declared_domain_sha256", _sha("attacker-domain"),
             "SP038_DECLARED_DOMAIN_MISMATCH"),
            ("orientation_contract_sha256", _sha("swapped-orientation"),
             "SP039_ORIENTATION_CONTRACT_MISMATCH"),
        ):
            with self.subTest(field=field):
                declarations, authority, plan, abi = _builtin("semantic-attack")
                semantic_authority, physical_authority = declarations
                semantic = semantic_authority.requirement.to_dict()
                semantic.pop("schema")
                semantic[field] = value
                semantic_authority = issue_semantic_requirement_authority(
                    semantic,
                    oracle_source_sha256=_sha("attacker-independent-oracle"),
                    issuer_domain="app.test.attacker.semantic.v1",
                )
                with patch(
                        "rtdsl.v4_semantically_admitted_compiler."
                        "_compile_verified_triangle_executable") as low_level:
                    with self.assertRaisesRegex(
                            SemanticPhysicalAdmissionError, rule):
                        admit_builtin_triangle_compilation(
                            semantic_authority, physical_authority,
                            authority=authority,
                            plan=plan, abi=abi)
                low_level.assert_not_called()

    def test_raw_and_synchronously_rewritten_declarations_cannot_self_prove(self):
        callback, abi = _callback_and_abi("raw-self-proof")
        target = _target("raw-self-proof")
        schema = SimpleNamespace(
            schema_sha256=_sha("typed-schema:raw-self-proof"),
            geometry_family=GeometryFamily.BUILTIN_TRIANGLE,
        )
        orientation = SimpleNamespace(
            authority_sha256=_sha("orientation:raw-self-proof"))
        authority = VerifiedPhysicalSchemaAuthority(
            callback, schema, target, orientation, "authority-raw-self-proof")
        plan = CanonicalPhysicalPlan(
            template_id=ReferenceTemplateId.BUILTIN_TRIANGLE_V1,
            schema_sha256=schema.schema_sha256,
            callback_ir_sha256=callback.ir_sha256,
            effect_digest=callback.effect_digest,
            target_sha256=target.target_sha256,
            role_topology=(), ordered_buffer_semantics=(),
            authority_nonce=authority.authority_nonce, executable=False,
        )
        semantic, physical = _semantic_and_physical(
            "raw-self-proof", geometry=GeometryFamily.BUILTIN_TRIANGLE.value,
            schema_sha256=schema.schema_sha256,
            callback_ir_sha256=callback.ir_sha256,
            effect_digest=callback.effect_digest,
            orientation_contract_sha256=orientation.authority_sha256,
        )
        semantic["policy"]["exactness"] = "synchronized_false_claim"
        physical["guarantees"]["exactness"] = "synchronized_false_claim"
        semantic_authority = issue_semantic_requirement_authority(
            semantic, oracle_source_sha256=_sha("raw-self-proof-oracle"),
            issuer_domain="app.test.raw_self_proof.v1")
        with patch(
                "rtdsl.v4_semantically_admitted_compiler."
                "_compile_verified_triangle_executable") as low_level:
            with self.assertRaisesRegex(
                    SemanticallyAdmittedCompilerError,
                    "SA001_DECLARATION_REQUIRED"):
                admit_builtin_triangle_compilation(
                    semantic_authority, physical, authority=authority,
                    plan=plan, abi=abi)
        low_level.assert_not_called()

    def test_facade_derives_zero_and_multiple_candidates_from_registry(self):
        declarations, authority, plan, abi = _builtin("registry-cardinality")
        semantic_authority, physical_authority = declarations
        physical = physical_authority.guarantee.to_dict()
        physical.pop("schema")

        diagnostic = physical_guarantee_registry_entry(
            "compiler.test.diagnostic_only.v1", physical,
            eligibility=PhysicalEncodingEligibility.DIAGNOSTIC_NONREGISTRABLE,
            canonical_template_id=None,
            classifier_source_sha256=_sha("diagnostic-classifier"))
        zero_registry = _issue_compiler_physical_guarantee_registry(
            (diagnostic,), registry_source_sha256=_sha("zero-registry"))
        zero_authority = issue_registered_physical_guarantee_authority(
            zero_registry, diagnostic.entry_id)
        with patch(
                "rtdsl.v4_semantically_admitted_compiler."
                "_compile_verified_triangle_executable") as low_level:
            with self.assertRaisesRegex(
                    SemanticPhysicalAdmissionError,
                    "SP060_CANONICAL_CANDIDATE_UNSUPPORTED"):
                admit_builtin_triangle_compilation(
                    semantic_authority, zero_authority,
                    authority=authority, plan=plan, abi=abi)
        low_level.assert_not_called()

        entries = tuple(
            physical_guarantee_registry_entry(
                f"compiler.test.canonical_{index}.v1", physical,
                eligibility=PhysicalEncodingEligibility.CANONICAL_PRODUCTION,
                canonical_template_id=plan.template_id.value,
                classifier_source_sha256=_sha(f"classifier:{index}"))
            for index in range(2))
        many_registry = _issue_compiler_physical_guarantee_registry(
            entries, registry_source_sha256=_sha("many-registry"))
        many_authority = issue_registered_physical_guarantee_authority(
            many_registry, entries[0].entry_id)
        with patch(
                "rtdsl.v4_semantically_admitted_compiler."
                "_compile_verified_triangle_executable") as low_level:
            with self.assertRaisesRegex(
                    SemanticPhysicalAdmissionError,
                    "SP061_CANONICAL_CANDIDATE_AMBIGUOUS"):
                admit_builtin_triangle_compilation(
                    semantic_authority, many_authority,
                    authority=authority, plan=plan, abi=abi)
        low_level.assert_not_called()

    def test_live_plan_identity_drift_stops_before_low_level_compiler(self):
        declarations, authority, plan, abi = _builtin("drift")
        admission = admit_builtin_triangle_compilation(
            *declarations, authority=authority, plan=plan, abi=abi)
        drifted = replace(plan, target_sha256=_sha("attacker-target"))
        with patch(
                "rtdsl.v4_semantically_admitted_compiler."
                "_compile_verified_triangle_executable") as low_level:
            with self.assertRaisesRegex(
                    SemanticallyAdmittedCompilerError,
                    "SA015_LIVE_IDENTITY_DRIFT"):
                compile_semantically_admitted_builtin_triangle_executable(
                    admission, authority, drifted, abi)
        low_level.assert_not_called()

    def test_reconstructed_admission_stops_before_low_level_compiler(self):
        declarations, authority, plan, abi = _builtin("reconstructed")
        admission = admit_builtin_triangle_compilation(
            *declarations, authority=authority, plan=plan, abi=abi)
        copied = replace(admission)
        with patch(
                "rtdsl.v4_semantically_admitted_compiler."
                "_compile_verified_triangle_executable") as low_level:
            with self.assertRaises(SemanticPhysicalAdmissionError):
                compile_semantically_admitted_builtin_triangle_executable(
                    copied, authority, plan, abi)
        low_level.assert_not_called()

    def test_runtime_rejects_current_binding_drift_and_other_admission(self):
        declarations, authority, plan, abi = _builtin("runtime")
        admission = admit_builtin_triangle_compilation(
            *declarations, authority=authority, plan=plan, abi=abi)
        executable = _FakeExecutable(_sha("runtime-executable"))
        with patch(
                "rtdsl.v4_semantically_admitted_compiler."
                "_compile_verified_triangle_executable",
                return_value=(executable, "log")):
            compile_semantically_admitted_builtin_triangle_executable(
                admission, authority, plan, abi)
        drifted_plan = replace(plan, target_sha256=_sha("new-target"))
        with self.assertRaisesRegex(
                SemanticallyAdmittedCompilerError,
                "SA015_LIVE_IDENTITY_DRIFT"):
            require_semantically_admitted_builtin_triangle_executable(
                executable, admission, authority, drifted_plan, abi)

        drifted_family = replace(
            authority,
            triangle_orientation_authority=SimpleNamespace(
                authority_sha256=_sha("other-orientation")),
        )
        with self.assertRaisesRegex(
                SemanticallyAdmittedCompilerError,
                "SA015_LIVE_IDENTITY_DRIFT"):
            require_semantically_admitted_builtin_triangle_executable(
                executable, admission, drifted_family, plan, abi)

        other_declarations, other_authority, other_plan, other_abi = _builtin("other")
        other = admit_builtin_triangle_compilation(
            *other_declarations, authority=other_authority,
            plan=other_plan, abi=other_abi)
        with self.assertRaisesRegex(
                SemanticallyAdmittedCompilerError,
                "SA007_RUNTIME_FAMILY_DRIFT"):
            require_semantically_admitted_builtin_triangle_executable(
                executable, other, other_authority, other_plan, other_abi)

    def test_consume_gate_reverifies_then_calls_low_level_once_for_all_families(self):
        rows = (
            (_builtin("consume-builtin"), admit_builtin_triangle_compilation,
             compile_semantically_admitted_builtin_triangle_executable,
             consume_semantically_admitted_builtin_triangle_executable,
             "_compile_verified_triangle_executable",
             "_consume_verified_triangle_executable"),
            (_triangle_reduction("consume-reduction"),
             admit_triangle_reduction_compilation,
             compile_semantically_admitted_triangle_reduction_executable,
             consume_semantically_admitted_triangle_reduction_executable,
             "_compile_verified_triangle_reduction_executable",
             "_consume_verified_triangle_reduction_executable"),
            (_bounded_relation("consume-relation"),
             admit_bounded_relation_compilation,
             compile_semantically_admitted_bounded_relation_executable,
             consume_semantically_admitted_bounded_relation_executable,
             "_compile_verified_bounded_relation_executable",
             "_consume_verified_bounded_relation_executable"),
        )
        for index, (fixture, admit, compile_admitted, consume_admitted,
                    compile_name, consume_name) in enumerate(rows):
            with self.subTest(family=consume_name):
                declarations, authority, artifact, abi = fixture
                artifact_arg = (
                    {"plan": artifact} if isinstance(
                        artifact, CanonicalPhysicalPlan)
                    else {"contract": artifact})
                admission = admit(
                    *declarations, authority=authority, **artifact_arg, abi=abi)
                executable = _FakeExecutable(_sha(f"consume-executable:{index}"))
                with patch(
                        "rtdsl.v4_semantically_admitted_compiler." + compile_name,
                        return_value=(executable, "compiler log")):
                    compile_admitted(admission, authority, artifact, abi)
                with patch(
                        "rtdsl.v4_semantically_admitted_compiler." + consume_name,
                        return_value="composed-ptx") as low_consume:
                    self.assertEqual(
                        consume_admitted(
                            executable, admission, authority, artifact, abi),
                        "composed-ptx")
                low_consume.assert_called_once()
                with self.assertRaisesRegex(
                        SemanticallyAdmittedCompilerError,
                        "SA004_EXECUTABLE_NOT_ADMITTED"):
                    consume_admitted(
                        executable, admission, authority, artifact, abi)

    def test_consume_gate_identity_drift_calls_low_level_zero_times(self):
        declarations, authority, plan, abi = _builtin("consume-drift")
        admission = admit_builtin_triangle_compilation(
            *declarations, authority=authority, plan=plan, abi=abi)
        executable = _FakeExecutable(_sha("consume-drift-executable"))
        with patch(
                "rtdsl.v4_semantically_admitted_compiler."
                "_compile_verified_triangle_executable",
                return_value=(executable, "compiler log")):
            compile_semantically_admitted_builtin_triangle_executable(
                admission, authority, plan, abi)
        for label, drifted_authority, drifted_plan, drifted_abi in (
            ("source/schema/authority", replace(
                authority,
                triangle_orientation_authority=SimpleNamespace(
                    authority_sha256=_sha("drifted-orientation"))), plan, abi),
            ("plan/target", authority,
             replace(plan, target_sha256=_sha("drifted-target")), abi),
            ("abi", authority, plan,
             replace(abi, abi_sha256=_sha("drifted-abi"))),
        ):
            with self.subTest(drift=label), patch(
                    "rtdsl.v4_semantically_admitted_compiler."
                    "_consume_verified_triangle_executable") as low_consume:
                with self.assertRaises(SemanticallyAdmittedCompilerError):
                    consume_semantically_admitted_builtin_triangle_executable(
                        executable, admission, drifted_authority,
                        drifted_plan, drifted_abi)
                low_consume.assert_not_called()

    def test_run_gate_reverifies_and_calls_real_runtime_once_for_all_families(self):
        rows = (
            (_builtin("run-builtin"), admit_builtin_triangle_compilation,
             compile_semantically_admitted_builtin_triangle_executable,
             run_semantically_admitted_builtin_triangle_callback,
             "_compile_verified_triangle_executable",
             "_run_builtin_triangle_callback"),
            (_triangle_reduction("run-reduction"),
             admit_triangle_reduction_compilation,
             compile_semantically_admitted_triangle_reduction_executable,
             run_semantically_admitted_triangle_reduction_callback,
             "_compile_verified_triangle_reduction_executable",
             "_run_builtin_triangle_reduction_callback"),
            (_bounded_relation("run-relation"),
             admit_bounded_relation_compilation,
             compile_semantically_admitted_bounded_relation_executable,
             run_semantically_admitted_bounded_relation_callback,
             "_compile_verified_bounded_relation_executable",
             "_run_bounded_relation_callback"),
        )
        for index, (fixture, admit, compile_admitted, run_admitted,
                    compile_name, run_name) in enumerate(rows):
            with self.subTest(family=run_name):
                declarations, authority, artifact, abi = fixture
                artifact_arg = (
                    {"plan": artifact} if isinstance(
                        artifact, CanonicalPhysicalPlan)
                    else {"contract": artifact})
                admission = admit(
                    *declarations, authority=authority, **artifact_arg, abi=abi)
                executable = _FakeExecutable(_sha(f"run-executable:{index}"))
                with patch(
                        "rtdsl.v4_semantically_admitted_compiler." + compile_name,
                        return_value=(executable, "compiler log")):
                    compile_admitted(admission, authority, artifact, abi)
                runtime_result = object()
                with patch(
                        "rtdsl.v4_semantically_admitted_compiler." + run_name,
                        return_value=runtime_result) as low_run:
                    self.assertIs(
                        run_admitted(
                            executable, admission, authority, artifact, abi,
                            expected_output=(1, 2, 3)),
                        runtime_result)
                low_run.assert_called_once()
                self.assertEqual(
                    low_run.call_args.kwargs["expected_output"], (1, 2, 3))

    def test_run_gate_drift_invokes_runtime_zero_times(self):
        declarations, authority, plan, abi = _builtin("run-drift")
        admission = admit_builtin_triangle_compilation(
            *declarations, authority=authority, plan=plan, abi=abi)
        executable = _FakeExecutable(_sha("run-drift-executable"))
        with patch(
                "rtdsl.v4_semantically_admitted_compiler."
                "_compile_verified_triangle_executable",
                return_value=(executable, "compiler log")):
            compile_semantically_admitted_builtin_triangle_executable(
                admission, authority, plan, abi)
        for label, drifted_authority, drifted_plan, drifted_abi, expected in (
            ("source/authority", replace(
                authority,
                triangle_orientation_authority=SimpleNamespace(
                    authority_sha256=_sha("run-drift-orientation"))), plan, abi,
             "SA015_LIVE_IDENTITY_DRIFT"),
            ("target/plan", authority,
             replace(plan, target_sha256=_sha("run-drift-target")), abi,
             "SA015_LIVE_IDENTITY_DRIFT"),
            ("abi", authority, plan,
             replace(abi, abi_sha256=_sha("run-drift-abi")),
             "SA007_RUNTIME_FAMILY_DRIFT"),
        ):
            with self.subTest(drift=label), patch(
                    "rtdsl.v4_semantically_admitted_compiler."
                    "_run_builtin_triangle_callback") as low_run:
                with self.assertRaisesRegex(
                        SemanticallyAdmittedCompilerError,
                        expected):
                    run_semantically_admitted_builtin_triangle_callback(
                        executable, admission, drifted_authority,
                        drifted_plan, drifted_abi)
                low_run.assert_not_called()

    def test_runtime_exception_revokes_admitted_executable_without_retry(self):
        declarations, authority, plan, abi = _builtin("run-exception")
        admission = admit_builtin_triangle_compilation(
            *declarations, authority=authority, plan=plan, abi=abi)
        executable = _FakeExecutable(_sha("run-exception-executable"))
        with patch(
                "rtdsl.v4_semantically_admitted_compiler."
                "_compile_verified_triangle_executable",
                return_value=(executable, "compiler log")):
            compile_semantically_admitted_builtin_triangle_executable(
                admission, authority, plan, abi)
        with patch(
                "rtdsl.v4_semantically_admitted_compiler."
                "_run_builtin_triangle_callback",
                side_effect=RuntimeError("device execution failed")) as low_run:
            with self.assertRaisesRegex(RuntimeError, "device execution failed"):
                run_semantically_admitted_builtin_triangle_callback(
                    executable, admission, authority, plan, abi)
        low_run.assert_called_once()
        with patch(
                "rtdsl.v4_semantically_admitted_compiler."
                "_run_builtin_triangle_callback") as stale_runtime:
            with self.assertRaisesRegex(
                    SemanticallyAdmittedCompilerError,
                    "SA004_EXECUTABLE_NOT_ADMITTED"):
                run_semantically_admitted_builtin_triangle_callback(
                    executable, admission, authority, plan, abi)
            stale_runtime.assert_not_called()

    def test_compile_wrappers_have_no_binding_candidate_or_bypass_parameter(self):
        for function in (
            compile_semantically_admitted_builtin_triangle_executable,
            compile_semantically_admitted_triangle_reduction_executable,
            compile_semantically_admitted_bounded_relation_executable,
            consume_semantically_admitted_builtin_triangle_executable,
            consume_semantically_admitted_triangle_reduction_executable,
            consume_semantically_admitted_bounded_relation_executable,
            run_semantically_admitted_builtin_triangle_callback,
            run_semantically_admitted_triangle_reduction_callback,
            run_semantically_admitted_bounded_relation_callback,
        ):
            parameters = inspect.signature(function).parameters
            self.assertNotIn("live_binding", parameters)
            self.assertNotIn("canonical_candidates", parameters)
            self.assertNotIn("unsafe", parameters)
            self.assertNotIn("skip_admission", parameters)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from rtdsl.v4 import (
    CompilerProtocolProjection,
    ProtocolContractDeclaration,
    ProtocolMechanism,
    ProtocolFamily,
    verify_protocol_contract,
)
from rtdsl.v4_callback_lifecycle import MaterializedProtocolProgram


ROOT = Path(__file__).resolve().parents[1]


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _objects():
    declaration = ProtocolContractDeclaration(
        family="builtin_triangle_reduction_v1",
        task_semantics_sha256=_sha("task"),
        role_effects=(("any_hit", ("accept_continue", "payload_write")),),
        attribute_abi_ownership=(("attr0", "application_item_id_u32"),),
        physical_bindings=(("query.lower.x", "host.query.lower.x"),),
        continuation_policy="REQUIRE_COMPLETE_BEFORE_CONSUME",
        checked_executable_sha256=_sha("executable-a"),
    )
    projection = CompilerProtocolProjection(
        family=declaration.family,
        task_semantics_sha256=declaration.task_semantics_sha256,
        role_effects=declaration.role_effects,
        attribute_abi_ownership=declaration.attribute_abi_ownership,
        physical_bindings=declaration.physical_bindings,
        continuation_policy=declaration.continuation_policy,
        actual_executable_sha256=declaration.checked_executable_sha256,
        generated_device_source_sha256=_sha("device"),
        generated_host_source_sha256=_sha("host"),
    )
    return declaration, projection


class Goal5797ProtocolContractTest(unittest.TestCase):
    def test_valid_full_contract_accepts(self):
        declaration, projection = _objects()
        decision = verify_protocol_contract(
            declaration.to_mapping(), projection.to_mapping())
        self.assertEqual(decision.verdict, "ACCEPT")
        self.assertEqual(decision.findings, ())
        self.assertFalse(decision.to_mapping()["executable_capability_issued"])

    def test_each_single_declaration_mutation_is_live_and_exact(self):
        declaration, projection = _objects()
        rows = [
            (
                ProtocolMechanism.ROLE_EFFECT_CLOSURE,
                "CP001_ROLE_EFFECT_MISMATCH",
                {"role_effects": {"any_hit": []}},
            ),
            (
                ProtocolMechanism.PAYLOAD_ATTRIBUTE_ABI_OWNERSHIP,
                "CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH",
                {"attribute_abi_ownership": {"attr0": "primitive_index_u32"}},
            ),
            (
                ProtocolMechanism.PHYSICAL_GEOMETRY_BINDING,
                "CP003_PHYSICAL_BINDING_MISMATCH",
                {"physical_bindings": {"query.lower.x": "host.query.lower.y"}},
            ),
            (
                ProtocolMechanism.DEVICE_STATUS_CONTINUATION,
                "CP004_CONTINUATION_STATUS_MISMATCH",
                {"continuation_policy": "ALLOW_PARTIAL"},
            ),
            (
                ProtocolMechanism.CHECKED_PROGRAM_EXECUTABLE_IDENTITY,
                "CP005_EXECUTABLE_IDENTITY_MISMATCH",
                {"checked_executable_sha256": _sha("executable-b")},
            ),
        ]
        baseline_projection_bytes = json.dumps(
            projection.to_mapping(), sort_keys=True).encode()
        for mechanism, reason, delta in rows:
            mapping = declaration.to_mapping()
            mapping.pop("contract_sha256")
            mapping.update(delta)
            mutated = ProtocolContractDeclaration(
                family=mapping["family"],
                task_semantics_sha256=mapping["task_semantics_sha256"],
                role_effects=tuple(
                    (key, tuple(value))
                    for key, value in sorted(mapping["role_effects"].items())),
                attribute_abi_ownership=tuple(sorted(
                    mapping["attribute_abi_ownership"].items())),
                physical_bindings=tuple(sorted(mapping["physical_bindings"].items())),
                continuation_policy=mapping["continuation_policy"],
                checked_executable_sha256=mapping["checked_executable_sha256"],
            )
            decision = verify_protocol_contract(mutated, projection)
            self.assertEqual(decision.verdict, "REJECT")
            self.assertEqual(len(decision.findings), 1)
            self.assertEqual(decision.findings[0].mechanism, mechanism)
            self.assertEqual(decision.findings[0].reason_id, reason)
            self.assertEqual(
                decision.verdict_with_mechanism_ablated(mechanism), "ACCEPT")
            self.assertEqual(
                json.dumps(projection.to_mapping(), sort_keys=True).encode(),
                baseline_projection_bytes,
            )

    def test_seal_tampering_rejects_before_comparison(self):
        declaration, projection = _objects()
        bad = deepcopy(declaration.to_mapping())
        bad["continuation_policy"] = "ALLOW_PARTIAL"
        with self.assertRaisesRegex(ValueError, "seal mismatch"):
            verify_protocol_contract(bad, projection.to_mapping())

    def test_rejected_decision_blocks_before_native_load(self):
        declaration, projection = _objects()
        bad_projection = CompilerProtocolProjection(
            family=projection.family,
            task_semantics_sha256=projection.task_semantics_sha256,
            role_effects=projection.role_effects,
            attribute_abi_ownership=projection.attribute_abi_ownership,
            physical_bindings=projection.physical_bindings,
            continuation_policy="ALLOW_PARTIAL",
            actual_executable_sha256=projection.actual_executable_sha256,
            generated_device_source_sha256=projection.generated_device_source_sha256,
            generated_host_source_sha256=projection.generated_host_source_sha256,
        )
        rejected = verify_protocol_contract(declaration, bad_projection)
        self.assertEqual(rejected.verdict, "REJECT")
        materialized = MaterializedProtocolProgram(
            program=SimpleNamespace(
                protocol=SimpleNamespace(family=ProtocolFamily.BOUNDED_RELATION)),
            target=object(), toolchain=object(), identity=object(), backend={},
            compiler_log_sha256=_sha("log"), materialize_seconds=0.0,
            protocol_contract_decision=rejected,
        )
        with patch(
            "rtdsl.v4_callback_lifecycle._load_exact_native_library",
        ) as loader:
            with self.assertRaisesRegex(
                RuntimeError, "PL036_PROTOCOL_CONTRACT_REJECTED",
            ):
                materialized.prepare(SimpleNamespace())
        loader.assert_not_called()

    def test_preaction_file_precedes_results_and_forbids_timing(self):
        path = ROOT / (
            "history/internal_docs/"
            "goal5797_s0_five_mechanism_ablation_preaction_20260823.json")
        value = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(value["mechanisms"]), 5)
        self.assertFalse(value["authorization"]["formal_performance_timing"])
        self.assertFalse(value["authorization"]["goal5798_entry"])
        self.assertEqual(
            value["status"],
            "FROZEN_BEFORE_FIRST_GOAL5797_ATTACK_OR_GPU_CONTROL")


if __name__ == "__main__":
    unittest.main()

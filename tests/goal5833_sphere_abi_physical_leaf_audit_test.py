"""Exhaustive hostile mutations of the populated sphere ABI/physical leaves."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import hashlib
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from goal5833_sphere_callback_leaf_audit_test import _authority  # noqa: E402
from rtdsl import v4_callback_abi as _base_abi  # noqa: E402
from rtdsl.v4_callback_abi import CallbackAbiError  # noqa: E402
from rtdsl.v4_sphere_callback_abi import (  # noqa: E402
    compile_sphere_callback_abi,
    verify_sphere_callback_abi,
)
from rtdsl.v4_sphere_optix_wrapper_codegen import (  # noqa: E402
    generate_trusted_optix_sphere_wrapper_v1,
)
from rtdsl.v4_sphere_physical_schema import (  # noqa: E402
    BuiltinSpherePhysicalSchema,
    SphereCanonicalPlan,
    SpherePhysicalSchemaError,
    SphereTargetProfile,
    verify_builtin_sphere_physical_schema,
)


_SHA256 = re.compile(r"[0-9a-f]{64}")


def _scalar_leaves(value, tokens=()):
    if isinstance(value, dict):
        result = []
        for key, child in value.items():
            result.extend(_scalar_leaves(child, (*tokens, key)))
        return result
    if isinstance(value, (list, tuple)):
        result = []
        for index, child in enumerate(value):
            result.extend(_scalar_leaves(child, (*tokens, index)))
        return result
    return [(tokens, value)]


def _path(tokens) -> str:
    result = ""
    for token in tokens:
        result += f"[{token}]" if isinstance(token, int) else (
            f".{token}" if result else token)
    return result


def _set_leaf(value, tokens, replacement) -> None:
    parent = value
    for token in tokens[:-1]:
        parent = parent[token]
    parent[tokens[-1]] = replacement


def _mutated_scalar(value):
    # Exercise Python's dangerous bool/int equality aliases whenever the
    # original value permits it; otherwise make one same-shape scalar change.
    if type(value) is bool:
        return int(value)
    if type(value) is int:
        return bool(value) if value in (0, 1) else value + 1
    if type(value) is str:
        if _SHA256.fullmatch(value):
            return ("0" if value[0] != "0" else "1") + value[1:]
        return value + "__mutated"
    raise AssertionError(f"unsupported populated scalar {type(value).__name__}")


def _reseal_abi(payload) -> None:
    unsigned = {key: value for key, value in payload.items() if key != "abi_sha256"}
    payload["abi_sha256"] = hashlib.sha256(
        _base_abi._canonical_json(unsigned)).hexdigest()


def _presentational_schema_mutation(schema, tokens, replacement):
    class MutatedPresentation(BuiltinSpherePhysicalSchema):
        def semantic_dict(self):
            payload = super().semantic_dict()
            _set_leaf(payload, tokens, replacement)
            return payload

    return MutatedPresentation(**schema.__dict__)


class Goal5833SphereAbiPhysicalLeafAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.authority, cls.abi, cls.wrapper = _authority()

    def test_all_611_populated_serialized_abi_scalar_occurrences_are_admitted_exactly(self):
        canonical = self.abi.to_dict()
        all_leaves = _scalar_leaves(canonical)
        populated = [(tokens, value) for tokens, value in all_leaves if value is not None]
        self.assertEqual(len(all_leaves), 614)
        self.assertEqual(len(populated), 611)
        self.assertEqual(
            [len(_scalar_leaves(role)) for role in canonical["roles"]],
            [189, 135, 159, 111],
        )

        rejected = 0
        for tokens, value in populated:
            hostile = deepcopy(canonical)
            _set_leaf(hostile, tokens, _mutated_scalar(value))
            if tokens != ("abi_sha256",):
                # Do not let a stale outer digest stand in for the leaf gate.
                _reseal_abi(hostile)
            try:
                decoded = _base_abi.callback_abi_from_dict(hostile)
            except CallbackAbiError:
                rejected += 1
                continue
            with self.assertRaises(CallbackAbiError, msg=_path(tokens)):
                verify_sphere_callback_abi(decoded, self.authority)
            rejected += 1
        self.assertEqual(rejected, 611)

    def test_direct_abi_bool_integer_alias_and_subclass_are_rejected(self):
        role = self.abi.roles[0]
        field = replace(role.inputs[0], readonly=int(role.inputs[0].readonly))
        hostile = replace(
            self.abi,
            roles=(replace(role, inputs=(field, *role.inputs[1:])), *self.abi.roles[1:]),
        )
        # Python/dataclass equality is exactly the hostile condition: 1 == True.
        self.assertEqual(hostile, self.abi)
        self.assertNotEqual(
            _base_abi._canonical_json(hostile.to_dict()),
            _base_abi._canonical_json(self.abi.to_dict()),
        )
        with self.assertRaises(CallbackAbiError):
            verify_sphere_callback_abi(hostile, self.authority)

        class AbiSubclass(_base_abi.CompiledCallbackAbi):
            pass

        with self.assertRaises(CallbackAbiError):
            verify_sphere_callback_abi(AbiSubclass(**self.abi.__dict__), self.authority)

    def test_three_null_any_hit_proof_slots_remain_mandatorily_absent(self):
        canonical = self.abi.to_dict()
        mutations = {
            "any_hit_proof_sha256": "2" * 64,
            "any_hit_proof_kind": (
                "compiler_recognized_commutative_idempotent_reduction_v1"),
            "any_hit_delivery_contract": "order_independent_canonical",
        }
        for key, value in mutations.items():
            hostile = deepcopy(canonical)
            hostile[key] = value
            _reseal_abi(hostile)
            with self.assertRaises(CallbackAbiError, msg=key):
                _base_abi.callback_abi_from_dict(hostile)
        hostile = deepcopy(canonical)
        hostile.update(mutations)
        _reseal_abi(hostile)
        with self.assertRaises(CallbackAbiError):
            _base_abi.callback_abi_from_dict(hostile)

    def test_all_30_physical_schema_semantic_scalar_occurrences_are_closed(self):
        schema = self.authority.schema
        leaves = _scalar_leaves(schema.semantic_dict())
        self.assertEqual(len(leaves), 30)
        self.assertEqual(
            sum(tokens[0] in {"buffers", "hit_channels"} for tokens, _ in leaves),
            10,
        )
        rejected = 0
        for tokens, value in leaves:
            replacement = _mutated_scalar(value)
            if tokens[0] in {"buffers", "hit_channels"}:
                # These ten leaves are fixed compiler-owned declarations, not
                # user-selectable runtime policy.  A subclass must not be able
                # to reseal a different declaration while execution stays fixed.
                hostile = _presentational_schema_mutation(
                    schema, tokens, replacement)
            else:
                hostile = BuiltinSpherePhysicalSchema(**schema.__dict__)
                if tokens[0] == "stable_order":
                    order = list(hostile.stable_order)
                    order[tokens[1]] = replacement
                    object.__setattr__(hostile, "stable_order", tuple(order))
                else:
                    object.__setattr__(hostile, tokens[0], replacement)
            with self.assertRaises(SpherePhysicalSchemaError, msg=_path(tokens)):
                verify_builtin_sphere_physical_schema(
                    self.authority.callback, hostile, target=self.authority.target)
            rejected += 1
        self.assertEqual(rejected, 30)

    def test_all_six_target_leaves_revalidate_and_change_or_reject(self):
        target = self.authority.target
        changes = {
            "provider": ("cuda", False),
            "optix_sdk": ("9.0.1", True),
            "compute_capability": ("9.0", True),
            "native_sha256": ("2" * 64, True),
            "supports_builtin_sphere": (1, False),
            "max_graph_depth": (True, False),
        }
        self.assertEqual(len(_scalar_leaves({
            key: getattr(target, key) for key in target.__dataclass_fields__
        })), 6)
        for field, (value, accepted) in changes.items():
            hostile = SphereTargetProfile(**target.__dict__)
            object.__setattr__(hostile, field, value)
            if not accepted:
                with self.assertRaises(SpherePhysicalSchemaError, msg=field):
                    verify_builtin_sphere_physical_schema(
                        self.authority.callback, self.authority.schema,
                        target=hostile)
                continue
            fresh = verify_builtin_sphere_physical_schema(
                self.authority.callback, self.authority.schema, target=hostile)
            self.assertNotEqual(fresh.target.target_sha256, target.target_sha256)
            self.assertNotEqual(fresh.authority_nonce, self.authority.authority_nonce)
            self.assertNotEqual(
                fresh.canonical_plan.plan_sha256,
                self.authority.canonical_plan.plan_sha256,
            )

    def test_target_subclass_cannot_override_the_bound_identity(self):
        class TargetSubclass(SphereTargetProfile):
            @property
            def target_sha256(self):
                return "0" * 64

        hostile = TargetSubclass(**self.authority.target.__dict__)
        with self.assertRaises(SpherePhysicalSchemaError):
            verify_builtin_sphere_physical_schema(
                self.authority.callback, self.authority.schema, target=hostile)

    def test_all_seven_canonical_plan_leaves_are_exactly_decision_bearing(self):
        plan = self.authority.canonical_plan
        leaves = _scalar_leaves(plan.semantic_dict())
        self.assertEqual(len(leaves), 7)
        for tokens, value in leaves:
            hostile = SphereCanonicalPlan(**plan.__dict__)
            object.__setattr__(hostile, tokens[0], _mutated_scalar(value))
            self.assertNotEqual(hostile, plan, _path(tokens))
            self.assertNotEqual(hostile.plan_sha256, plan.plan_sha256, _path(tokens))
            hostile_authority = replace(
                self.authority, canonical_plan=hostile)
            with self.assertRaises(CallbackAbiError, msg=_path(tokens)):
                compile_sphere_callback_abi(hostile_authority)
            with self.assertRaises(Exception, msg=_path(tokens)):
                generate_trusted_optix_sphere_wrapper_v1(
                    self.authority, hostile, self.abi)


if __name__ == "__main__":
    unittest.main()

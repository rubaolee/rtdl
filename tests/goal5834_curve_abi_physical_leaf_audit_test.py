"""Exhaustive mutation audit for Goal5834 curve ABI/physical leaves."""

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

from goal5834_builtin_curve_public_path_test import _authority  # noqa: E402
from rtdsl import v4_callback_abi as _base_abi  # noqa: E402
from rtdsl.v4_callback_abi import CallbackAbiError  # noqa: E402
from rtdsl.v4_curve_callback_abi import (  # noqa: E402
    compile_curve_callback_abi,
    verify_curve_callback_abi,
)
from rtdsl.v4_curve_optix_wrapper_codegen import (  # noqa: E402
    generate_trusted_optix_curve_wrapper_v1,
)
from rtdsl.v4_curve_physical_schema import (  # noqa: E402
    BuiltinCurvePhysicalSchema,
    CurveCanonicalPlan,
    CurvePhysicalSchemaError,
    CurveTargetProfile,
    verify_builtin_curve_physical_schema,
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
    if type(value) is bool:
        return int(value)
    if type(value) is int:
        return bool(value) if value in (0, 1) else value + 1
    if type(value) is str:
        if _SHA256.fullmatch(value):
            return ("0" if value[0] != "0" else "1") + value[1:]
        return value + "__mutated"
    raise AssertionError(f"unsupported scalar {type(value).__name__}")


def _reseal_abi(payload) -> None:
    unsigned = {
        key: value for key, value in payload.items() if key != "abi_sha256"}
    payload["abi_sha256"] = hashlib.sha256(
        _base_abi._canonical_json(unsigned)).hexdigest()


_NESTED_SCHEMA_FIELDS = {
    ("numeric_admission", "policy_id"): "numeric_policy_id",
    ("numeric_admission", "query_axis_cross_ratio_min_exponent2"):
        "direction_cross_ratio_min_exponent2",
    ("numeric_admission", "segment_distance_ratio_min_exponent2"):
        "contact_separation_min_exponent2",
    ("numeric_admission", "front_entry_endpoint_margin_exponent2"):
        "front_entry_endpoint_margin_exponent2",
    ("numeric_admission", "provider_t_semantics"): "provider_t_semantics",
    ("buffers", "control_points"): "control_points_buffer_contract",
    ("buffers", "widths"): "widths_buffer_contract",
    ("buffers", "segment_indices"): "segment_indices_buffer_contract",
    ("buffers", "application_ids"): "application_ids_buffer_contract",
    ("buffers", "queries"): "queries_buffer_contract",
    ("buffers", "outputs"): "outputs_buffer_contract",
    ("buffers", "status"): "status_buffer_contract",
    ("hit_channels", "t"): "t_hit_channel_contract",
    ("hit_channels", "hit_kind"): "hit_kind_channel_contract",
    ("hit_channels", "primitive_index"):
        "primitive_index_hit_channel_contract",
    ("hit_channels", "application_id"):
        "application_id_hit_channel_contract",
}


class Goal5834CurveAbiPhysicalLeafAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.authority = _authority()
        cls.abi = compile_curve_callback_abi(cls.authority)

    def test_all_611_populated_abi_scalar_occurrences_are_closed(self):
        canonical = self.abi.to_dict()
        leaves = _scalar_leaves(canonical)
        populated = [item for item in leaves if item[1] is not None]
        self.assertEqual((len(leaves), len(populated)), (614, 611))
        self.assertEqual(
            [len(_scalar_leaves(role)) for role in canonical["roles"]],
            [189, 135, 159, 111])
        for tokens, value in populated:
            hostile = deepcopy(canonical)
            _set_leaf(hostile, tokens, _mutated_scalar(value))
            if tokens != ("abi_sha256",):
                _reseal_abi(hostile)
            try:
                decoded = _base_abi.callback_abi_from_dict(hostile)
            except CallbackAbiError:
                continue
            with self.assertRaises(CallbackAbiError, msg=_path(tokens)):
                verify_curve_callback_abi(decoded, self.authority)

    def test_all_40_physical_schema_scalar_occurrences_are_closed(self):
        schema = self.authority.schema
        leaves = _scalar_leaves(schema.semantic_dict())
        self.assertEqual(len(leaves), 40)
        self.assertEqual(
            sum(tokens[0] in {"buffers", "hit_channels"}
                for tokens, _ in leaves), 11)
        self.assertEqual(
            sum(tokens[0] == "numeric_admission" for tokens, _ in leaves), 5)
        rejected = 0
        for tokens, value in leaves:
            replacement = _mutated_scalar(value)
            hostile = BuiltinCurvePhysicalSchema(**schema.__dict__)
            if tokens[0] == "stable_order":
                order = list(hostile.stable_order)
                order[tokens[1]] = replacement
                object.__setattr__(hostile, "stable_order", tuple(order))
            elif tuple(tokens) in _NESTED_SCHEMA_FIELDS:
                object.__setattr__(
                    hostile, _NESTED_SCHEMA_FIELDS[tuple(tokens)], replacement)
            else:
                object.__setattr__(hostile, tokens[0], replacement)
            with self.assertRaises(
                    CurvePhysicalSchemaError, msg=_path(tokens)):
                verify_builtin_curve_physical_schema(
                    self.authority.callback, hostile,
                    target=self.authority.target)
            rejected += 1
        self.assertEqual(rejected, 40)

    def test_all_six_target_leaves_change_identity_or_reject(self):
        target = self.authority.target
        changes = {
            "provider": ("cuda", False),
            "optix_sdk": ("9.0.1", True),
            "compute_capability": ("9.0", True),
            "native_sha256": ("2" * 64, True),
            "supports_builtin_round_linear_curve": (1, False),
            "max_graph_depth": (True, False),
        }
        self.assertEqual(len(_scalar_leaves({
            key: getattr(target, key) for key in target.__dataclass_fields__
        })), 6)
        for field, (value, accepted) in changes.items():
            hostile = CurveTargetProfile(**target.__dict__)
            object.__setattr__(hostile, field, value)
            if not accepted:
                with self.assertRaises(CurvePhysicalSchemaError, msg=field):
                    verify_builtin_curve_physical_schema(
                        self.authority.callback, self.authority.schema,
                        target=hostile)
                continue
            fresh = verify_builtin_curve_physical_schema(
                self.authority.callback, self.authority.schema,
                target=hostile)
            self.assertNotEqual(fresh.target.target_sha256, target.target_sha256)
            self.assertNotEqual(
                fresh.authority_nonce, self.authority.authority_nonce)
            self.assertNotEqual(
                fresh.canonical_plan.plan_sha256,
                self.authority.canonical_plan.plan_sha256)

    def test_target_subclass_cannot_override_bound_identity(self):
        class TargetSubclass(CurveTargetProfile):
            @property
            def target_sha256(self):
                return "0" * 64

        hostile = TargetSubclass(**self.authority.target.__dict__)
        with self.assertRaises(CurvePhysicalSchemaError):
            verify_builtin_curve_physical_schema(
                self.authority.callback, self.authority.schema,
                target=hostile)

    def test_all_seven_canonical_plan_leaves_are_decision_bearing(self):
        plan = self.authority.canonical_plan
        leaves = _scalar_leaves(plan.semantic_dict())
        self.assertEqual(len(leaves), 7)
        for tokens, value in leaves:
            hostile = CurveCanonicalPlan(**plan.__dict__)
            object.__setattr__(hostile, tokens[0], _mutated_scalar(value))
            self.assertNotEqual(hostile, plan, _path(tokens))
            self.assertNotEqual(hostile.plan_sha256, plan.plan_sha256)
            hostile_authority = replace(
                self.authority, canonical_plan=hostile)
            with self.assertRaises(CallbackAbiError, msg=_path(tokens)):
                compile_curve_callback_abi(hostile_authority)
            with self.assertRaises(Exception, msg=_path(tokens)):
                generate_trusted_optix_curve_wrapper_v1(
                    self.authority, hostile, self.abi)


if __name__ == "__main__":
    unittest.main()

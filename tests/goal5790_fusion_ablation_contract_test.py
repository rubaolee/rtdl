from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import replace
import hashlib
import inspect
import json
from pathlib import Path
import unittest

from rtdsl.v4_checked_u64_device_reduction import (
    checked_u64_downstream_operation_identity,
)
from rtdsl.v4_fusion_ablation import (
    CHECKED_U64_PRODUCT_SUM_MECHANISM,
    FusionAblationError,
    FusionVariant,
    SHARED_CONTRACT_FREEZE_FILE_SHA256,
    SHARED_CONTRACT_FREEZE_SHA256,
    TARGET_MATERIALIZATION_AUTHORITY_SCHEMA,
    VerifiedDownstreamOperationRecipe,
    build_checked_u64_product_sum_ablation_plan,
    load_verified_shared_contract_freeze,
    plan_from_mapping,
    verify_fusion_ablation_pair,
    verify_fusion_ablation_plan,
    verify_target_materialization_authority,
)
import rtdsl.v4_fusion_ablation as ablation


ROOT = Path(__file__).parents[1]
FREEZE = (
    ROOT / "history" / "internal_docs" /
    "goal5789_contract_evidence_20260816" /
    "GOAL5789_GOAL5790_SHARED_CONTRACT_FREEZE.json"
)
REFERENCE_NATIVE = (
    "efcc147b3e3dbf06731f424b3883b0a785cb80e227334d27b672dd01ac56feab"
)
NATIVE = "e" * 64  # Deliberately distinct Home-like target native.
BUNDLE = "v4_builtin_triangle_checked_reduction_composed"


def _sha(digit: str) -> str:
    return digit * 64


def _freeze():
    return load_verified_shared_contract_freeze(FREEZE.read_bytes())


def _authority(
    *, native: str = NATIVE, target: str = "4", cupy_version: str = "14.0.1",
):
    target_sha256 = _sha(target)
    on_recipe = checked_u64_downstream_operation_identity(
        FusionVariant.FUSION_ON.value,
        target_identity_sha256=target_sha256,
        cupy_version=cupy_version,
    )
    off_recipe = checked_u64_downstream_operation_identity(
        FusionVariant.FUSION_OFF.value,
        target_identity_sha256=target_sha256,
        cupy_version=cupy_version,
    )
    body = {
        "schema": TARGET_MATERIALIZATION_AUTHORITY_SCHEMA,
        "shared_contract_freeze_sha256": SHARED_CONTRACT_FREEZE_SHA256,
        "execution_source_archive_sha256": _sha("1"),
        "execution_source_tree_sha256": _sha("2"),
        "callback_ir_sha256": _sha("3"),
        "callback_authority_nonce": "goal5790-callback-authority-0001",
        "contract_sha256": _sha("6"),
        "abi_sha256": _sha("7"),
        "provider_identity": "optix",
        "program_bundle_identity": BUNDLE,
        "composed_program_sha256": _sha("c"),
        "cupy_version": cupy_version,
        "fusion_on_downstream_operation_recipe": on_recipe,
        "fusion_off_downstream_operation_recipe": off_recipe,
        "fusion_on_downstream_operation_recipe_sha256": ablation._digest(on_recipe),
        "fusion_off_downstream_operation_recipe_sha256": ablation._digest(off_recipe),
        "native_library_sha256": native,
        "native_payload_sha256": native,
        "target_identity_sha256": target_sha256,
        "materializer_source_sha256": _sha("d"),
        "source_manifest_sha256": _sha("f"),
        "evidence_archive_sha256": _sha("0"),
        "materialization_nonce": f"goal5790-target-{target}-0001",
        "actual_native_rehashed_from_preserved_payload": True,
        "actual_source_tree_recounted_from_preserved_archive": True,
        "cross_target_native_byte_reproducibility_claimed": False,
    }
    body["receipt_sha256"] = hashlib.sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()
    return verify_target_materialization_authority(body)


def _plan(variant: FusionVariant):
    return build_checked_u64_product_sum_ablation_plan(
        _freeze(),
        variant=variant,
        target_materialization=_authority(),
        input_sha256=_sha("5"),
        output_contract_sha256=_sha("6"),
        oracle_sha256=_sha("7"),
        timer_contract_sha256=_sha("8"),
        lifecycle_contract_sha256=_sha("9"),
        value_count=17,
    )


class _ReceiptFlipMapping(Mapping[str, object]):
    """Expose drift only after a verifier has read the receipt twice."""

    def __init__(self, value: dict[str, object]):
        self._value = value
        self._receipt_reads = 0

    def __iter__(self) -> Iterator[str]:
        return iter(self._value)

    def __len__(self) -> int:
        return len(self._value)

    def __getitem__(self, key: str) -> object:
        if key == "receipt_sha256":
            result = self._value[key]
            self._receipt_reads += 1
            return result
        if key == "contract_sha256" and self._receipt_reads >= 2:
            return _sha("a")
        return self._value[key]


class _StatefulRecipe(VerifiedDownstreamOperationRecipe):
    def to_dict(self) -> dict[str, object]:
        value = super().to_dict()
        value["implementation"]["kind"] = "attacker_mutable_recipe"
        return value


class _SplitViewRecipeDict(dict[str, object]):
    """Canonical lookup view with an attacker-controlled JSON items view."""

    def items(self):
        malicious = json.loads(json.dumps(dict(self)))
        malicious["implementation"]["operations"][0] = "cp.min(weights)"
        return malicious.items()


class Goal5790FusionAblationContractTest(unittest.TestCase):
    def test_exact_goal5789_freeze_is_bound_twice(self) -> None:
        authority = _freeze()
        self.assertEqual(authority.file_sha256, SHARED_CONTRACT_FREEZE_FILE_SHA256)
        self.assertEqual(authority.freeze_sha256, SHARED_CONTRACT_FREEZE_SHA256)
        self.assertEqual(authority.reference_native_provenance_sha256,
                         REFERENCE_NATIVE)
        self.assertEqual(authority.program_bundle, BUNDLE)

    def test_target_native_is_receipt_bound_not_cross_target_pinned(self) -> None:
        authority = _authority(native=NATIVE, target="4")
        self.assertNotEqual(authority.native_library_sha256, REFERENCE_NATIVE)
        plan = _plan(FusionVariant.FUSION_ON)
        self.assertEqual(plan.native_library_sha256, NATIVE)
        self.assertEqual(plan.target_materialization_receipt_sha256,
                         authority.receipt_sha256)

        another = _authority(native=_sha("a"), target="5")
        another_plan = build_checked_u64_product_sum_ablation_plan(
            _freeze(), variant=FusionVariant.FUSION_ON,
            target_materialization=another,
            input_sha256=_sha("5"), output_contract_sha256=_sha("6"),
            oracle_sha256=_sha("7"), timer_contract_sha256=_sha("8"),
            lifecycle_contract_sha256=_sha("9"), value_count=17)
        self.assertEqual(another_plan.native_library_sha256, _sha("a"))
        self.assertNotEqual(plan.shared_identity_sha256,
                            another_plan.shared_identity_sha256)

    def test_naked_or_mutated_target_native_cannot_enter_a_plan(self) -> None:
        authority = _authority()
        forged = authority.to_dict()
        forged["native_library_sha256"] = _sha("b")
        with self.assertRaisesRegex(FusionAblationError, "target_native_payload"):
            verify_target_materialization_authority(forged)
        forged = authority.to_dict()
        forged["execution_source_tree_sha256"] = _sha("b")
        with self.assertRaisesRegex(FusionAblationError, "target_authority_digest"):
            verify_target_materialization_authority(forged)
        with self.assertRaisesRegex(FusionAblationError,
                                    "target_materialization_authority"):
            build_checked_u64_product_sum_ablation_plan(
                _freeze(), variant=FusionVariant.FUSION_ON,
                target_materialization=_sha("e"),  # type: ignore[arg-type]
                input_sha256=_sha("5"), output_contract_sha256=_sha("6"),
                oracle_sha256=_sha("7"), timer_contract_sha256=_sha("8"),
                lifecycle_contract_sha256=_sha("9"), value_count=17)

    def test_target_authority_binds_callback_contract_abi_and_recipe_payloads(self):
        authority = _authority()
        portable = authority.to_dict()
        for variant in ("fusion_on", "fusion_off"):
            recipe = portable[f"{variant}_downstream_operation_recipe"]
            independently_rebuilt = hashlib.sha256(json.dumps(
                recipe,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode()).hexdigest()
            self.assertEqual(
                independently_rebuilt,
                portable[f"{variant}_downstream_operation_recipe_sha256"],
            )
            self.assertFalse(
                recipe["implementation"][
                    "opaque_partner_kernel_binary_claimed"
                ]
            )
        for field, replacement in (
            ("callback_authority_nonce", "goal5790-callback-authority-9999"),
            ("contract_sha256", _sha("a")),
            ("abi_sha256", _sha("b")),
            ("cupy_version", "99.0.0"),
        ):
            with self.subTest(field=field):
                mutated = dict(portable)
                mutated[field] = replacement
                with self.assertRaisesRegex(
                    FusionAblationError,
                    "target_authority_digest|downstream_recipe_identity",
                ):
                    verify_target_materialization_authority(mutated)

        # Even a self-consistently re-signed authority cannot replace the
        # compiler-owned structured recipe with an arbitrary lookalike.
        forged = json.loads(json.dumps(portable))
        forged_recipe = forged["fusion_off_downstream_operation_recipe"]
        forged_recipe["implementation"]["operations"][0] = "cp.min(weights)"
        forged["fusion_off_downstream_operation_recipe_sha256"] = (
            ablation._digest(forged_recipe)
        )
        unsigned = dict(forged)
        unsigned.pop("receipt_sha256")
        forged["receipt_sha256"] = ablation._digest(unsigned)
        with self.assertRaisesRegex(
            FusionAblationError, "downstream_recipe_identity"
        ):
            verify_target_materialization_authority(forged)

    def test_plan_binds_new_target_and_recipe_identities(self):
        plan = _plan(FusionVariant.FUSION_ON)
        mutations = (
            replace(plan, callback_authority_nonce="goal5790-callback-other-0001"),
            replace(plan, contract_sha256=_sha("a")),
            replace(plan, abi_sha256=_sha("b")),
            replace(plan, cupy_version="99.0.0"),
        )
        for mutated in mutations:
            with self.subTest(field=next(
                name for name in (
                    "callback_authority_nonce", "contract_sha256",
                    "abi_sha256", "cupy_version",
                ) if getattr(mutated, name) != getattr(plan, name)
            )):
                with self.assertRaises(FusionAblationError):
                    verify_fusion_ablation_plan(mutated)

    def test_stateful_mapping_and_recipe_subclass_fail_closed(self):
        authority = _authority()
        verified = verify_target_materialization_authority(
            _ReceiptFlipMapping(authority.to_dict())
        )
        # A single parser snapshot ensures the returned authority is exactly
        # the object whose receipt was checked, not a later Mapping view.
        self.assertEqual(verified.contract_sha256, authority.contract_sha256)
        self.assertEqual(
            verify_target_materialization_authority(verified.to_dict()),
            verified,
        )

        plan = _plan(FusionVariant.FUSION_ON)
        recipe = plan.fusion_on_downstream_operation_recipe
        stateful = _StatefulRecipe(
            variant=recipe.variant,
            target_identity_sha256=recipe.target_identity_sha256,
            cupy_version=recipe.cupy_version,
            kind=recipe.kind,
            entry=recipe.entry,
            source_sha256=recipe.source_sha256,
            options=recipe.options,
            operations=recipe.operations,
        )
        with self.assertRaisesRegex(
            FusionAblationError, "plan_downstream_recipe_type"
        ):
            verify_fusion_ablation_plan(replace(
                plan, fusion_on_downstream_operation_recipe=stateful
            ))

        portable = authority.to_dict()
        portable["fusion_off_downstream_operation_recipe"] = (
            _SplitViewRecipeDict(
                portable["fusion_off_downstream_operation_recipe"]
            )
        )
        unsigned = dict(portable)
        unsigned.pop("receipt_sha256")
        portable["receipt_sha256"] = ablation._digest(unsigned)
        with self.assertRaisesRegex(
            FusionAblationError, "target_authority_digest"
        ):
            verify_target_materialization_authority(portable)

    def test_any_freeze_byte_mutation_fails_closed(self) -> None:
        value = bytearray(FREEZE.read_bytes())
        value[-2] = ord(" ") if value[-2] != ord(" ") else ord("\t")
        with self.assertRaisesRegex(FusionAblationError, "freeze_file_identity"):
            load_verified_shared_contract_freeze(bytes(value))

    def test_pair_shares_every_non_allowlisted_identity(self) -> None:
        on, off = verify_fusion_ablation_pair(
            _plan(FusionVariant.FUSION_ON),
            _plan(FusionVariant.FUSION_OFF),
        )
        self.assertEqual(on.shared_identity_sha256, off.shared_identity_sha256)
        changed = {
            key for key in on.to_dict()
            if on.to_dict()[key] != off.to_dict()[key]
        }
        self.assertEqual(changed, {
            "variant", "lowering_node", "downstream_operation_recipe_sha256",
            "operation_requirements", "plan_sha256",
        })
        self.assertEqual(on.mechanism_id, CHECKED_U64_PRODUCT_SUM_MECHANISM)
        self.assertFalse(on.executable)

    def test_semantic_or_input_drift_cannot_form_a_pair(self) -> None:
        on = _plan(FusionVariant.FUSION_ON)
        off = _plan(FusionVariant.FUSION_OFF)
        drift = replace(off, input_sha256=_sha("c"))
        with self.assertRaisesRegex(FusionAblationError, "shared_identity|plan_digest"):
            verify_fusion_ablation_pair(on, drift)

    def test_unknown_or_mutated_plan_fails_closed(self) -> None:
        on = _plan(FusionVariant.FUSION_ON)
        with self.assertRaisesRegex(FusionAblationError, "variant"):
            build_checked_u64_product_sum_ablation_plan(
                _freeze(),
                variant="fusion_on",  # type: ignore[arg-type]
                target_materialization=_authority(),
                input_sha256=_sha("5"),
                output_contract_sha256=_sha("6"),
                oracle_sha256=_sha("7"),
                timer_contract_sha256=_sha("8"),
                lifecycle_contract_sha256=_sha("9"),
                value_count=17,
            )
        with self.assertRaisesRegex(FusionAblationError, "frozen_identity"):
            verify_fusion_ablation_plan(replace(on, semantic_request_sha256=_sha("f")))

    def test_same_downstream_recipe_is_not_a_real_ablation(self) -> None:
        portable = _authority().to_dict()
        portable["fusion_off_downstream_operation_recipe_sha256"] = portable[
            "fusion_on_downstream_operation_recipe_sha256"
        ]
        unsigned = dict(portable)
        unsigned.pop("receipt_sha256")
        portable["receipt_sha256"] = hashlib.sha256(json.dumps(
            unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode()).hexdigest()
        with self.assertRaisesRegex(FusionAblationError, "target_downstream_pair"):
            verify_target_materialization_authority(portable)

    def test_portable_mapping_round_trip_and_extra_field_rejection(self) -> None:
        plan = _plan(FusionVariant.FUSION_OFF)
        portable = json.loads(json.dumps(plan.to_dict()))
        self.assertEqual(plan_from_mapping(portable), plan)
        portable["dataset"] = "forbidden"
        with self.assertRaisesRegex(FusionAblationError, "plan_fields"):
            plan_from_mapping(portable)

    def test_registered_operation_sequences_are_exact(self) -> None:
        on = _plan(FusionVariant.FUSION_ON)
        off = _plan(FusionVariant.FUSION_OFF)
        self.assertEqual(
            [item.operation_id for item in on.operation_requirements],
            [
                "checked_summary.kernel_launch",
                "checked_summary.summary_copy_sync",
            ],
        )
        self.assertEqual(
            [item.operation_id for item in off.operation_requirements],
            [
                "maximum_weight.logical_reduce",
                "maximum_weight.scalar_copy_sync",
                "weight_sum.logical_reduce",
                "weight_sum.scalar_copy_sync",
                "weighted_product.materialize",
                "weighted_product_sum.logical_reduce",
                "weighted_product_sum.scalar_copy_sync",
            ],
        )
        counts = {
            kind: sum(item.kind.value == kind for item in off.operation_requirements)
            for kind in {
                "device_materialization", "logical_reduction",
                "host_copy_synchronization",
            }
        }
        self.assertEqual(counts, {
            "device_materialization": 1,
            "logical_reduction": 3,
            "host_copy_synchronization": 3,
        })

    def test_module_has_no_application_or_dataset_selection_surface(self) -> None:
        source = inspect.getsource(ablation).lower()
        for name in (
            "raydb", "librts", "x-hd", "rt-dbscan", "rayjoin",
            "barneshut", "arkade", "rtxrmq", "com-dblp", "cit-patents",
            "livejournal", "paper-reproduction-apps",
        ):
            self.assertNotIn(name, source)
        self.assertNotIn("performance_seconds", source)
        self.assertNotIn("observed_ratio", source)


if __name__ == "__main__":
    unittest.main()

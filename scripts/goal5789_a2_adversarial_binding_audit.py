"""Adversarial audit for the Goal5789-A2 Callback-IR binding.

The audit imports the A2 checker but never the evidence builder or product.
It first replays every frozen successor certificate, then applies certificate-
only, coordinated authority, type-alias, same-family swap, and UNKNOWN-
precedence attacks.  A deliberately rerooted authority control documents the
remaining authority-TCB ceiling rather than pretending to provide tamper-proof
or end-to-end semantic-soundness guarantees.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from scripts import goal5789_a2_independent_compatibility_checker as checker


ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT / "history/internal_docs/goal5789_a2_contract_evidence_20260821"
OUTPUT = A2 / "CALLBACK_BINDING_ADVERSARIAL_MATRIX.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {path}")
    return value


def _pretty(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _seal_certificate(value: dict[str, object]) -> None:
    value["certificate_sha256"] = checker.certificate_digest(value)


def _seal_callback_authority(value: dict[str, object]) -> None:
    value["authority_sha256"] = checker.callback_authority_digest(value)


def _seal_pin(value: dict[str, object]) -> None:
    value["pin_sha256"] = checker.callback_pin_digest(value)


def _seal_nested(value: dict[str, object]) -> None:
    value["authority_sha256"] = checker.v1.nested_authority_digest(value)


def _seal_bundle(value: dict[str, object]) -> None:
    value["authority_sha256"] = checker.authority_digest(value)


def _coherently_relabel_multiplicity(
    certificate: dict[str, object], authority: dict[str, object]
) -> None:
    replacement = "JOINTLY_WRONG_BUT_MUTUALLY_CONSISTENT_MULTIPLICITY"
    contract_id = certificate["semantic_request"]["contract_id"]
    encoding_id = certificate["physical_encoding"]["encoding_id"]
    certificate["semantic_request"]["policy"]["multiplicity"] = replacement
    certificate["physical_encoding"]["guarantees"]["multiplicity"] = replacement
    certificate["canonical_candidates"][0]["guarantees"]["multiplicity"] = replacement
    authority["semantic_authority"]["contracts"][contract_id]["policy"][
        "multiplicity"
    ] = replacement
    authority["physical_authority"]["encodings"][encoding_id]["guarantees"][
        "multiplicity"
    ] = replacement
    _seal_nested(authority["semantic_authority"])
    _seal_nested(authority["physical_authority"])
    _seal_bundle(authority)
    _seal_certificate(certificate)


def _evaluate(
    certificate: Mapping[str, object],
    authority: Mapping[str, object],
    callback_authority: Mapping[str, object],
    pin: Mapping[str, object],
) -> dict[str, object]:
    return checker.evaluate_certificate(certificate, authority, callback_authority, pin)


def _record(
    rows: list[dict[str, object]],
    *,
    attack_id: str,
    expected_verdict: str,
    expected_reference_admission: bool,
    result: Mapping[str, object],
    required_reason_fragment: str | None = None,
) -> None:
    verdict = result["semantic_compatible"]["verdict"]
    reference = result["reference_admission_complete"]
    reasons = list(result["semantic_compatible"]["reasons"])
    passed = verdict == expected_verdict and reference is expected_reference_admission
    if required_reason_fragment is not None:
        passed = passed and any(required_reason_fragment in reason for reason in reasons)
    row = {
        "attack_id": attack_id,
        "expected_semantic_verdict": expected_verdict,
        "actual_semantic_verdict": verdict,
        "expected_reference_admission_complete": expected_reference_admission,
        "actual_reference_admission_complete": reference,
        "required_reason_fragment": required_reason_fragment,
        "reasons": reasons,
        "passed": passed,
    }
    rows.append(row)
    if not passed:
        raise RuntimeError(f"adversarial audit failed: {row}")


def _reroot(
    authority: dict[str, object],
    callback_authority: dict[str, object],
    pin: dict[str, object],
) -> None:
    _seal_callback_authority(callback_authority)
    pin["callback_authority"]["file_sha256"] = checker.file_digest_from_object(callback_authority)
    pin["callback_authority"]["size_bytes"] = len(checker.pretty_json_bytes(callback_authority))
    pin["callback_authority"]["authority_sha256"] = callback_authority["authority_sha256"]
    _seal_pin(pin)
    binding = authority["callback_ir_authority_binding"]
    binding["callback_authority_file_sha256"] = checker.file_digest_from_object(callback_authority)
    binding["callback_authority_sha256"] = callback_authority["authority_sha256"]
    binding["callback_authority_pin_file_sha256"] = checker.file_digest_from_object(pin)
    binding["callback_authority_pin_sha256"] = pin["pin_sha256"]
    _seal_nested(binding)
    _seal_bundle(authority)


def audit(a2_dir: Path = A2) -> dict[str, object]:
    authority = _load(a2_dir / "AUTHORITY_BUNDLE.json")
    callback_authority = _load(a2_dir / "CALLBACK_IR_AUTHORITY.json")
    pin = _load(a2_dir / "CALLBACK_IR_AUTHORITY_PIN.json")
    inventory = _load(a2_dir / "BOUNDED_INVENTORY.json")
    heldout_certificate = _load(a2_dir / "HELD_OUT_RTXRMQ_CERTIFICATE.json")
    heldout_authority = _load(a2_dir / "HELD_OUT_AUTHORITY_BUNDLE.json")
    certificates = {
        row["unit_id"]: _load(a2_dir / "certificates" / f"{row['unit_id']}.json")
        for row in inventory["inventory"]
    }
    rows: list[dict[str, object]] = []

    for inventory_row in inventory["inventory"]:
        unit_id = inventory_row["unit_id"]
        result = _evaluate(certificates[unit_id], authority, callback_authority, pin)
        stored = _load(a2_dir / "results" / f"{unit_id}.json")
        if checker.canonical_bytes(result) != checker.canonical_bytes(stored):
            raise RuntimeError(f"stored successor result drift: {unit_id}")
        _record(
            rows,
            attack_id=f"baseline::{unit_id}",
            expected_verdict=inventory_row["semantic_compatible"],
            expected_reference_admission=bool(inventory_row["reference_admission_complete"]),
            result=result,
        )

    admitted = [
        (unit_id, certificate)
        for unit_id, certificate in certificates.items()
        if certificate["callback_contract"] is not None
    ]
    if len(admitted) != 6:
        raise RuntimeError("A2 adversarial audit requires exact 6 admitted inventory certificates")

    for unit_id, certificate in admitted:
        baseline_callback = certificate["callback_contract"]
        mutations: list[tuple[str, dict[str, object]]] = []
        empty_effects = deepcopy(certificate)
        for role in empty_effects["callback_contract"]["roles"]:
            role["effects"] = []
        mutations.append(("empty_effects", empty_effects))
        for key in ("ir_sha256", "effect_digest"):
            value = deepcopy(certificate)
            value["callback_contract"][key] = hashlib.sha256(
                f"goal5789-a2-hostile::{unit_id}::{key}".encode("utf-8")
            ).hexdigest()
            mutations.append((f"digest::{key}", value))
        for key in (
            "payload_u32_slots",
            "attribute_u32_slots",
            "trace_depth",
            "callable_depth",
            "total_static_iterations",
            "helper_call_depth",
        ):
            for label, replacement in (
                ("different_int", 1 if baseline_callback[key] != 1 else 2),
                ("bool_alias", bool(baseline_callback[key])),
                ("float_alias", float(baseline_callback[key])),
            ):
                value = deepcopy(certificate)
                value["callback_contract"][key] = replacement
                mutations.append((f"resource::{key}::{label}", value))
        for mutation_id, value in mutations:
            _seal_certificate(value)
            result = _evaluate(value, authority, callback_authority, pin)
            _record(
                rows,
                attack_id=f"certificate_only::{unit_id}::{mutation_id}",
                expected_verdict=checker.INCOMPATIBLE,
                expected_reference_admission=False,
                result=result,
                required_reason_fragment="callback_contract",
            )

    by_family: dict[str, list[tuple[str, dict[str, object]]]] = {}
    for unit_id, certificate in admitted:
        by_family.setdefault(certificate["physical_encoding"]["geometry_family"], []).append((unit_id, certificate))
    swap_count = 0
    for family, family_rows in by_family.items():
        for recipient_id, recipient in family_rows:
            for donor_id, donor in family_rows:
                if checker.canonical_bytes(recipient["callback_contract"]) == checker.canonical_bytes(donor["callback_contract"]):
                    continue
                value = deepcopy(recipient)
                value["callback_contract"] = deepcopy(donor["callback_contract"])
                _seal_certificate(value)
                result = _evaluate(value, authority, callback_authority, pin)
                _record(
                    rows,
                    attack_id=f"same_family_swap::{family}::{recipient_id}<-{donor_id}",
                    expected_verdict=checker.INCOMPATIBLE,
                    expected_reference_admission=False,
                    result=result,
                    required_reason_fragment="callback_contract_authority_mismatch",
                )
                swap_count += 1
    if swap_count == 0:
        raise RuntimeError("same-family callback swap matrix was empty")

    unbound = deepcopy(certificates["triangle__com_dblp__rt_1a2"])
    unbound["physical_encoding"]["geometry_family"] = "contradictory_family"
    _seal_certificate(unbound)
    result = _evaluate(unbound, authority, callback_authority, pin)
    _record(
        rows,
        attack_id="unknown_precedence::physical_contradiction_must_not_be_masked",
        expected_verdict=checker.INCOMPATIBLE,
        expected_reference_admission=False,
        result=result,
        required_reason_fragment="gas_geometry_family_mismatch",
    )

    particle = certificates["particle__microfluidics_5000"]
    for key, replacement in (
        ("payload_u32_slots", 2),
        ("attribute_u32_slots", 1),
        ("helper_call_depth", 1),
    ):
        changed_certificate = deepcopy(particle)
        changed_authority = deepcopy(authority)
        changed_callback_authority = deepcopy(callback_authority)
        changed_pin = deepcopy(pin)
        program_sha = changed_certificate["callback_contract"]["authority_program_sha256"]
        changed_certificate["callback_contract"][key] = replacement
        program_row = changed_callback_authority["programs"][program_sha]
        program_row["verified_summary"][key] = replacement
        program_row["callback_contract"][key] = replacement
        _seal_certificate(changed_certificate)
        _reroot(changed_authority, changed_callback_authority, changed_pin)
        result = _evaluate(
            changed_certificate, changed_authority, changed_callback_authority, changed_pin
        )
        _record(
            rows,
            attack_id=f"coordinated_summary_lie::{key}",
            expected_verdict=checker.INCOMPATIBLE,
            expected_reference_admission=False,
            result=result,
            required_reason_fragment="callback_authority_verified_program_mismatch",
        )

    overclaim_certificate = deepcopy(certificates["triangle__com_dblp__rt_2a1"])
    overclaim_authority = deepcopy(authority)
    overclaim_callback_authority = deepcopy(callback_authority)
    overclaim_pin = deepcopy(pin)
    overclaim_callback_authority["claim_boundary"]["semantic_soundness_claimed"] = True
    overclaim_callback_authority["claim_boundary"]["execution_authorized"] = True
    _reroot(overclaim_authority, overclaim_callback_authority, overclaim_pin)
    result = _evaluate(
        overclaim_certificate,
        overclaim_authority,
        overclaim_callback_authority,
        overclaim_pin,
    )
    _record(
        rows,
        attack_id="coordinated_claim_overreach::soundness_and_execution_true",
        expected_verdict=checker.INCOMPATIBLE,
        expected_reference_admission=False,
        result=result,
        required_reason_fragment="callback_authority_claim_boundary_not_exact",
    )

    metadata_certificate = deepcopy(certificates["triangle__com_dblp__rt_2a1"])
    metadata_authority = deepcopy(authority)
    metadata_callback_authority = deepcopy(callback_authority)
    metadata_pin = deepcopy(pin)
    metadata_program_sha = metadata_certificate["callback_contract"][
        "authority_program_sha256"
    ]
    metadata_row = metadata_callback_authority["programs"][metadata_program_sha]
    metadata_row["alias"] = "fabricated_alias"
    metadata_row["compile_entrypoint"] = "attacker.fake:compile"
    metadata_row["selected_constructor_source_paths"] = [
        "src/rtdsl/v4_callback_ir.py"
    ]
    _reroot(metadata_authority, metadata_callback_authority, metadata_pin)
    result = _evaluate(
        metadata_certificate,
        metadata_authority,
        metadata_callback_authority,
        metadata_pin,
    )
    _record(
        rows,
        attack_id="coordinated_producer_metadata_lie::alias_entrypoint_sources",
        expected_verdict=checker.INCOMPATIBLE,
        expected_reference_admission=False,
        result=result,
        required_reason_fragment="callback_authority_program_metadata_exact_identity_mismatch",
    )

    manifest_certificate = deepcopy(certificates["triangle__com_dblp__rt_2a1"])
    manifest_authority = deepcopy(authority)
    manifest_callback_authority = deepcopy(callback_authority)
    manifest_pin = deepcopy(pin)
    manifest_callback_authority["execution_leaf_manifest"]["entries_sha256"] = "0" * 64
    _reroot(manifest_authority, manifest_callback_authority, manifest_pin)
    result = _evaluate(
        manifest_certificate,
        manifest_authority,
        manifest_callback_authority,
        manifest_pin,
    )
    _record(
        rows,
        attack_id="coordinated_leaf_manifest_lie::entries_digest",
        expected_verdict=checker.INCOMPATIBLE,
        expected_reference_admission=False,
        result=result,
        required_reason_fragment="callback_authority_execution_leaf_manifest_identity_mismatch",
    )

    for unit_id, replacement_program_sha in (
        (
            "triangle__com_dblp__rt_2a1",
            "c126a788b5e451fc0d76b4c48610bb2e6d6dbbf22fdb0b1c656deac97babc671",
        ),
        (
            "librts__parks_point_contains",
            "c3a17d90e2c8895f6ec14b0c07bafdc734d7ec233b3397bdc99fd478b9941c26",
        ),
        (
            "particle__microfluidics_5000",
            "92697debe1e25227ec770b4d339c7cd248b16b7185612516841f3986a208ea30",
        ),
    ):
        changed_certificate = deepcopy(certificates[unit_id])
        changed_authority = deepcopy(authority)
        changed_callback_authority = deepcopy(callback_authority)
        changed_pin = deepcopy(pin)
        pair = (
            changed_certificate["semantic_request"]["contract_id"],
            changed_certificate["physical_encoding"]["encoding_id"],
        )
        replacement_contract = changed_callback_authority["programs"][
            replacement_program_sha
        ]["callback_contract"]
        changed_certificate["callback_contract"] = deepcopy(replacement_contract)
        for binding in changed_callback_authority["admitted_bindings"]:
            if (
                binding["semantic_contract_id"],
                binding["physical_encoding_id"],
            ) == pair:
                binding["authority_program_sha256"] = replacement_program_sha
                binding["callback_authority_id"] = replacement_contract[
                    "callback_authority_id"
                ]
                break
        else:
            raise RuntimeError(f"binding substitution target missing: {unit_id}")
        _seal_certificate(changed_certificate)
        _reroot(changed_authority, changed_callback_authority, changed_pin)
        result = _evaluate(
            changed_certificate,
            changed_authority,
            changed_callback_authority,
            changed_pin,
        )
        _record(
            rows,
            attack_id=f"coordinated_pair_program_substitution::{unit_id}",
            expected_verdict=checker.INCOMPATIBLE,
            expected_reference_admission=False,
            result=result,
            required_reason_fragment="callback_authority_admitted_binding_exact_mapping_mismatch",
        )

    changed_heldout_certificate = deepcopy(heldout_certificate)
    changed_heldout_authority = deepcopy(heldout_authority)
    changed_callback_authority = deepcopy(callback_authority)
    changed_pin = deepcopy(pin)
    for binding in changed_callback_authority["admitted_bindings"]:
        if binding["semantic_contract_id"] == "rtxrmq.leftmost_argmin.v1":
            binding["semantic_contract_id"] = "invented.unused.semantic.contract.v1"
            break
    else:
        raise RuntimeError("RTXRMQ binding missing from hostile baseline")
    _reroot(changed_heldout_authority, changed_callback_authority, changed_pin)
    result = _evaluate(
        changed_heldout_certificate,
        changed_heldout_authority,
        changed_callback_authority,
        changed_pin,
    )
    _record(
        rows,
        attack_id="coordinated_pair_program_substitution::rtxrmq_pair_removed_or_invented",
        expected_verdict=checker.INCOMPATIBLE,
        expected_reference_admission=False,
        result=result,
        required_reason_fragment="callback_authority_admitted_binding_exact_mapping_mismatch",
    )

    jointly_wrong_certificate = deepcopy(certificates["triangle__com_dblp__rt_2a1"])
    jointly_wrong_authority = deepcopy(authority)
    _coherently_relabel_multiplicity(jointly_wrong_certificate, jointly_wrong_authority)
    result = _evaluate(
        jointly_wrong_certificate,
        jointly_wrong_authority,
        callback_authority,
        pin,
    )
    _record(
        rows,
        attack_id="tcb_ceiling_control::semantic_and_physical_authorities_jointly_wrong_but_consistent",
        expected_verdict=checker.COMPATIBLE,
        expected_reference_admission=True,
        result=result,
    )

    passed_count = sum(row["passed"] is True for row in rows)
    output: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.callback_binding_adversarial_matrix.v1",
        "matrix_sha256": "",
        "status": "PASS__CALLBACK_CERTIFICATE_SUMMARY_AND_PAIR_PROGRAM_SUBSTITUTIONS_REJECTED__JOINTLY_WRONG_SEMANTIC_PHYSICAL_AUTHORITY_TCB_CEILING_REPRODUCED",
        "case_count": len(rows),
        "passed_count": passed_count,
        "failed_count": len(rows) - passed_count,
        "cases": rows,
        "claim_boundary": {
            "fixed_external_authority_root_callback_drift_rejected": True,
            "full_program_resources_independently_derived": True,
            "callback_authority_claim_boundary_exact_and_fail_closed": True,
            "callback_pair_to_program_mapping_is_fixed_and_substitution_rejected": True,
            "jointly_wrong_semantic_and_physical_authorities_can_remain_mutually_consistent": True,
            "jointly_wrong_authority_detection_claimed": False,
            "semantic_soundness_claimed": False,
            "completeness_claimed": False,
            "generalization_claimed": False,
            "callback_authority_bound_inventory_count": 6,
            "callback_authority_unbound_inventory_count": 9,
        },
        "authorization": {
            "authorizes_goal5793": False,
            "authorizes_entropy_draw": False,
            "authorizes_candidate_selection": False,
            "authorizes_product_change": False,
            "authorizes_gpu": False,
            "authorizes_home": False,
            "authorizes_pod": False,
            "authorizes_worker": False,
            "authorizes_performance_timing": False,
            "authorizes_publication": False,
        },
    }
    output["matrix_sha256"] = checker.digest(
        {key: value for key, value in output.items() if key != "matrix_sha256"}
    )
    return output


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError("A2 adversarial matrix is create-only")
    result = audit()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("xb") as handle:
        handle.write(_pretty(result))
    print(
        json.dumps(
            {
                "file_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
                "matrix_sha256": result["matrix_sha256"],
                "case_count": result["case_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

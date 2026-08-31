from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts import goal5790_static_formal_contract as predecessor
from scripts import goal5791_formal_contract as contract
from scripts import goal5791_trace_record_cost_diagnostic as trace_diagnostic


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_SOURCE_PATHS = {
    "source_authority": (
        ROOT / "history" / "internal_docs"
        / "goal5791_successor_source_authority_v2_20260817.json"
    ),
    "data_authority": (
        ROOT / "history" / "internal_docs"
        / "goal5791_frozen_triangle_data_and_oracle_authority_20260817.json"
    ),
    "runtime_budget_authority": (
        ROOT / "history" / "internal_docs"
        / "goal5791_pre_pod_conservative_runtime_budget_20260817.json"
    ),
    "expected_value_authority": (
        ROOT / "history" / "internal_docs"
        / "goal5790_preregistered_expected_value_and_fallback_20260816.json"
    ),
    "citation_authority": (
        ROOT / "history" / "internal_docs"
        / "goal5791_pre_worker_zero_related_work_and_claim_freeze_20260817.json"
    ),
}


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _sha(label: str) -> str:
    return contract.digest({"fixture_identity": label})


def _nonce(label: str) -> str:
    return contract.digest({"fixture_nonce": label})


def _citation_payload() -> dict[str, object]:
    return {
        "schema": (
            "rtdl.goal5791.pre_worker_zero_related_work_and_claim_freeze.v1"
        ),
        "goal": 5791,
        "status": "FROZEN_FIXTURE__NOT_EXECUTION_AUTHORITY",
        "nearest_adjacent_primary_work": {
            "doi": contract.SIGMETRICS_DOI,
            "attribution": {
                "rt_1a2_algorithm_and_name_owned_by_paper_authors": True,
                "rt_2a1_algorithm_and_name_owned_by_paper_authors": True,
                "graph_to_bvh_geometry_mapping_owned_by_paper_authors": True,
                "graph_to_ray_mapping_owned_by_paper_authors": True,
                "goal5791_invents_or_selects_any_of_these": False,
            },
        },
        "goal5791_experiment_claim_freeze": {
            "paper_algorithm": contract.PAPER_ALGORITHM,
            "paper_algorithm_is_fixed_not_selected": True,
            "rt_1a2_included": False,
            "particle_included": False,
            "author_binary_arm_included": False,
            "only_allowlisted_variant": contract.MECHANISM_ID,
            "maximum_matrix": {
                "independent_rows": 6,
                "balanced_pairs_per_row": 8,
                "arms_per_pair": 2,
                "maximum_fresh_parent_pid_workers": 96,
                "cross_dataset_lifecycle_or_row_compensation": False,
            },
        },
        "authorization": {
            "authorizes_pod": False,
            "authorizes_create_only_target_prepare": False,
            "authorizes_formal_worker_zero": False,
            "authorizes_registered_timing": False,
        },
    }


def _recipe(
    variant: str, *, target_identity_sha256: str, cupy_version: str,
) -> dict[str, object]:
    operation_ids = (
        contract.FUSION_OFF_OPERATION_IDS
        if variant == contract.FUSION_OFF
        else contract.FUSION_ON_OPERATION_IDS
    )
    implementation = (
        {
            "kind": "trusted_cupy_operation_graph",
            "operations": list(contract.ACTUAL_FUSION_OFF_CUPY_OPERATIONS),
            "opaque_partner_kernel_binary_claimed": False,
        }
        if variant == contract.FUSION_OFF else {
            "kind": "compiler_owned_rawkernel_recipe",
            "entry": contract.ACTUAL_FUSION_ON_ENTRY,
            "source_sha256": _sha("fusion-on-source"),
            "options": list(contract.ACTUAL_FUSION_ON_OPTIONS),
            "opaque_partner_kernel_binary_claimed": False,
        }
    )
    actual_recipe = {
        "schema": "rtdl.v4.checked_u64_downstream_operation_identity.v1",
        "variant": variant,
        "target_identity_sha256": target_identity_sha256,
        "cupy_version": cupy_version,
        "implementation": implementation,
    }
    claim_wrapper = {
        "variant": variant,
        "mechanism_id": contract.MECHANISM_ID,
        "allowed_delta_id": contract.ALLOWED_DELTA_ID,
        "operation_ids": list(operation_ids),
    }
    return {
        "actual_recipe": actual_recipe,
        "actual_recipe_sha256": contract.digest(actual_recipe),
        "claim_wrapper": claim_wrapper,
        "claim_wrapper_sha256": contract.digest(claim_wrapper),
    }


def _target_binding() -> dict[str, object]:
    hashes = {
        field: _sha("target:" + field)
        for field in contract.TARGET_HASH_SLOTS
    }
    versions = {
        field: f"fixture-{field}"
        for field in contract.TARGET_VERSION_SLOTS
    }
    recipes = {
        variant: _recipe(
            variant,
            target_identity_sha256=hashes["target_identity_sha256"],
            cupy_version=versions["cupy_version"],
        )
        for variant in contract.VARIANTS
    }
    hashes["semantic_request_sha256"] = contract.SEMANTIC_REQUEST_SHA256
    hashes["physical_encoding_sha256"] = contract.PHYSICAL_ENCODING_SHA256
    hashes["fusion_off_recipe_sha256"] = recipes[
        contract.FUSION_OFF]["actual_recipe_sha256"]
    hashes["fusion_on_recipe_sha256"] = recipes[
        contract.FUSION_ON]["actual_recipe_sha256"]
    nonces = {
        field: _nonce("target:" + field)
        for field in contract.TARGET_NONCE_SLOTS
    }
    program_bundle = contract.provider_program_bundle_digest_record(
        hashes, nonces,
    )
    hashes["provider_program_bundle_sha256"] = program_bundle["sha256"]
    value = {
        "schema": contract.TARGET_BINDING_SCHEMA,
        "goal": 5791,
        "status": contract.TARGET_BINDING_STATUS,
        "hashes": hashes,
        "nonces": nonces,
        "versions": versions,
        "recipes": recipes,
        "derived_digests": {
            "provider_program_bundle": program_bundle,
        },
        "cache_policy": deepcopy(contract.CACHE_POLICY),
    }
    return {**value, "binding_sha256": contract.digest(value)}


def _record(path: Path, root: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": contract.file_sha256(path),
        "bytes": path.stat().st_size,
    }


def _preexecution_authority(
    root: Path, *, with_target: bool = False,
) -> tuple[Path, dict[str, object]]:
    authority_dir = root / "authority_inputs"
    authority_dir.mkdir(parents=True)
    role_paths: dict[str, Path] = {}
    for role in contract.AUTHORITY_ROLES:
        path = authority_dir / f"{role}.json"
        path.write_bytes(AUTHORITY_SOURCE_PATHS[role].read_bytes())
        role_paths[role] = path
    target = _target_binding() if with_target else None
    body = {
        "schema": contract.PREEXECUTION_AUTHORITY_SCHEMA,
        "goal": 5791,
        "status": (
            contract.POSTPREPARE_STATUS if with_target
            else contract.PRETARGET_STATUS
        ),
        "formal_contract_sha256": contract.contract_sha256(),
        "schedule_sha256": contract.schedule_sha256(),
        "authority_records": {
            role: _record(role_paths[role], root)
            for role in contract.AUTHORITY_ROLES
        },
        "dataset_input_sha256": {
            dataset_id: contract.DATA_AUTHORITY_DATASETS[dataset_id]["sha256"]
            for dataset_id in contract.DATASET_IDS
        },
        "oracle_authority_sha256": {
            dataset_id: contract.DATA_AUTHORITY_DATASETS[dataset_id][
                "oracle_authority_sha256"
            ]
            for dataset_id in contract.DATASET_IDS
        },
        "target_materialization_binding": target,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "authorization": {
            "authorizes_pod": False,
            "authorizes_target_prepare": False,
            "authorizes_formal_workers": False,
            "authorizes_registered_timing": False,
        },
    }
    value = {**body, "authority_sha256": contract.digest(body)}
    path = root / "GOAL5791_PREEXECUTION_AUTHORITY.json"
    _write_json(path, value)
    return path, value


def _resign_authority(value: dict[str, object]) -> None:
    unsigned = dict(value)
    unsigned.pop("authority_sha256", None)
    value["authority_sha256"] = contract.digest(unsigned)


def _resign_target(value: dict[str, object]) -> None:
    target = value["target_materialization_binding"]
    assert isinstance(target, dict)
    unsigned = dict(target)
    unsigned.pop("binding_sha256", None)
    target["binding_sha256"] = contract.digest(unsigned)
    _resign_authority(value)


def _owner_formal_authority(
    root: Path,
    preexecution_path: Path,
    preexecution: dict[str, object],
) -> tuple[Path, dict[str, object]]:
    target = preexecution["target_materialization_binding"]
    assert isinstance(target, dict)
    endpoint = contract.pod_endpoint_identity_record(
        ssh_user="root", host="192.0.2.57", port=24579,
    )
    body = {
        "schema": contract.OWNER_FORMAL_EXECUTION_AUTHORITY_SCHEMA,
        "goal": 5791,
        "status": contract.OWNER_FORMAL_EXECUTION_STATUS,
        "formal_contract_sha256": contract.contract_sha256(),
        "schedule_sha256": contract.schedule_sha256(),
        "preexecution_authority_file_sha256": contract.file_sha256(
            preexecution_path
        ),
        "target_materialization_binding_sha256": target["binding_sha256"],
        "formal_identity_sha256": target["hashes"][
            "formal_identity_sha256"
        ],
        "runtime_budget_authority_sha256": preexecution[
            "authority_records"
        ]["runtime_budget_authority"]["sha256"],
        "runtime_file_sha256": _sha("formal-runtime-file"),
        "runtime_sha256": _sha("formal-runtime-seal"),
        "owner_authorization_nonce": _nonce("owner-formal-authority"),
        "independent_row_count": 6,
        "formal_worker_count": 96,
        "resource_confirmation": {
            "owner_confirmed_uninterrupted_window_hours": 7.0,
            "confirmed_free_disk_bytes": 25_000_000_000,
            "confirmed_before_formal_worker_zero": True,
            "formal_output_parent_resolved_path": "/root",
            "formal_output_parent_free_bytes_observed_at_authority_creation": (
                30_000_000_000),
            "minimum_required_free_disk_bytes": 20_000_000_000,
        },
        "execution_target": {
            "target_materialization_root": (
                "/root/goal5791_fixture_materialization"),
            "create_only_formal_output_root": (
                "/root/goal5791_fixture_formal_output"),
            "controller_incomplete_staging_root": (
                "/root/.goal5791_fixture_formal_output.goal5791_incomplete"),
            "target_materialization_root_observed_existing_and_bound_at_authority_creation": True,
            "formal_output_root_observed_absent_at_authority_creation": True,
            "controller_incomplete_staging_root_observed_absent_at_authority_creation": True,
            "preexisting_or_shared_formal_output_root_allowed": False,
            "pod_endpoint": endpoint,
        },
        "execution_policy": deepcopy(contract.FORMAL_EXECUTION_POLICY),
        "authorization": deepcopy(contract.FORMAL_AUTHORIZATION),
    }
    value = {**body, "authority_sha256": contract.digest(body)}
    path = root / "GOAL5791_OWNER_FORMAL_EXECUTION_AUTHORITY.json"
    _write_json(path, value)
    return path, value


def _resign_owner_authority(value: dict[str, object]) -> None:
    unsigned = dict(value)
    unsigned.pop("authority_sha256", None)
    value["authority_sha256"] = contract.digest(unsigned)


class Goal5791FormalContractTest(unittest.TestCase):
    def test_successor_contract_is_six_rows_and_96_pair_parity_workers(self) -> None:
        rows = contract.statistical_rows()
        workers = contract.schedule()
        self.assertEqual(len(rows), 6)
        self.assertEqual(len(workers), 96)
        self.assertEqual(
            [row["row_id"] for row in rows],
            [row["row_id"] for row in predecessor.statistical_rows()],
        )
        self.assertEqual(
            [row["bootstrap_seed"] for row in rows],
            [57_900_000 + index for index in range(6)],
        )
        self.assertEqual([row["row_index"] for row in rows], list(range(6)))
        self.assertEqual(
            {row["paper_algorithm"] for row in rows}, {"RT-2A1"})
        self.assertEqual(len({row["worker_index"] for row in workers}), 96)
        self.assertTrue(all(row["fresh_parent_pid_required"] for row in workers))
        # Global execution is round-major: one adjacent OFF/ON pair for every
        # frozen row, then the next pair round with reversed arm order.
        self.assertEqual(
            [item["pair_index"] for item in workers[:12]], [0] * 12)
        self.assertEqual(
            [item["row_id"] for item in workers[:12:2]],
            [row["row_id"] for row in rows],
        )
        self.assertEqual(
            [item["pair_index"] for item in workers[12:24]], [1] * 12)
        self.assertEqual(
            tuple(item["variant"] for item in workers[:2]),
            (contract.FUSION_OFF, contract.FUSION_ON),
        )
        self.assertEqual(
            tuple(item["variant"] for item in workers[12:14]),
            (contract.FUSION_ON, contract.FUSION_OFF),
        )
        for row in rows:
            cohort = [item for item in workers if item["row_id"] == row["row_id"]]
            self.assertEqual(len(cohort), 16)
            observed_orders = []
            for pair_index in range(8):
                pair = sorted(
                    (item for item in cohort if item["pair_index"] == pair_index),
                    key=lambda item: item["order_ordinal"],
                )
                observed_orders.append(tuple(item["variant"] for item in pair))
            self.assertEqual(
                observed_orders.count(
                    (contract.FUSION_OFF, contract.FUSION_ON)), 4)
            self.assertEqual(
                observed_orders.count(
                    (contract.FUSION_ON, contract.FUSION_OFF)), 4)

    def test_goal_scope_statistics_and_claim_boundary_are_frozen(self) -> None:
        value = contract.contract_document()
        self.assertEqual(value["goal"], 5791)
        self.assertEqual(value["schema"], contract.SCHEMA)
        scope = value["scientific_scope"]
        self.assertTrue(scope["triangle_weighted_rt2a1_only"])
        self.assertEqual(scope["rt1a2_rows"], 0)
        self.assertEqual(scope["particle_rows"], 0)
        self.assertEqual(scope["v2_v3_author_or_cuda_arms"], 0)
        mechanism_scope = scope["mechanism_scope_decision"]
        self.assertEqual(mechanism_scope, contract.MECHANISM_SCOPE_DECISION)
        self.assertEqual(
            mechanism_scope["causally_tested_mechanism_family_count"], 1)
        self.assertFalse(mechanism_scope["particle_included_in_goal5791"])
        self.assertFalse(
            mechanism_scope[
                "old_two_mechanism_success_criterion_controls_current_submission"
            ]
        )
        statistics = value["statistics"]
        self.assertEqual(
            statistics["ratio"], "fusion_off_seconds / fusion_on_seconds")
        self.assertEqual(statistics["greater_than_one_favors"], "fusion_on")
        self.assertEqual(statistics["bootstrap_draws"], 10_000)
        self.assertEqual(statistics["bootstrap_ci_indices"], [249, 9749])
        self.assertIsNone(statistics["numeric_speedup_floor"])
        self.assertFalse(
            statistics["cross_dataset_lifecycle_or_row_compensation_allowed"])
        claim = value["claim_and_governance"]
        self.assertEqual(claim["sigmetrics_doi"], "10.1145/3727108")
        self.assertTrue(
            claim["rt1a2_rt2a1_and_graph_to_rt_mapping_owned_by_paper_authors"])
        self.assertFalse(claim["goal5791_invents_or_selects_paper_algorithm"])
        self.assertFalse(claim["author_binary_or_implementation_compared"])
        self.assertFalse(
            claim["retry_resume_replacement_tuning_row_drop_or_relabel_allowed"])
        paper_outcomes = claim["paper_outcome_consequence_contract"]
        self.assertEqual(
            paper_outcomes, contract.PAPER_OUTCOME_CONSEQUENCE_CONTRACT)
        self.assertTrue(paper_outcomes["frozen_before_stage_b_worker_zero"])
        self.assertTrue(
            paper_outcomes[
                "paper_clear_winning_row_count_uses_mechanism_performance_statement_eligible"
            ]
        )
        self.assertEqual(
            paper_outcomes["published_paper_outcome_fields"],
            [
                "paper_clear_winning_row_count",
                "paper_clear_winning_row_ids",
                "ci_clear_win_trace_cost_inconclusive_count",
                "ci_clear_win_trace_cost_inconclusive_row_ids",
                "paper_outcome_consequence_selection",
            ],
        )
        self.assertEqual(
            paper_outcomes["paper_outcome_branch_selection"],
            {
                "paper_clear_winning_row_count_equals_0": (
                    "zero_clear_winning_rows"
                ),
                "paper_clear_winning_row_count_between_1_and_5": (
                    "mixed_one_through_five_clear_winning_rows"
                ),
                "paper_clear_winning_row_count_equals_6": (
                    "all_six_clear_winning_rows"
                ),
            },
        )
        self.assertEqual(
            paper_outcomes["ci_clear_win_but_trace_bound_not_small"]
            ["paper_classification"],
            "trace_cost_inconclusive",
        )
        self.assertFalse(
            paper_outcomes["zero_clear_winning_rows"]
            ["compiler_fusion_performance_claim_allowed"]
        )
        self.assertFalse(
            paper_outcomes["mixed_one_through_five_clear_winning_rows"]
            ["abstract_or_title_may_compress_result_to_fusion_wins"]
        )
        self.assertFalse(
            paper_outcomes["all_six_clear_winning_rows"]
            ["particle_causal_claim_allowed"]
        )
        self.assertFalse(
            paper_outcomes[
                "new_benchmark_rows_or_particle_ablation_added_after_outcome_allowed"
            ]
        )
        review_path = ROOT / contract.PROJECT_STATE_REVIEW_PATH
        self.assertEqual(
            contract.file_sha256(review_path),
            contract.PROJECT_STATE_REVIEW_FILE_SHA256,
        )
        unknown_path = ROOT / (
            "history/internal_docs/"
            "goal5792_unknown_lane_classification_work_authority_20260819.json"
        )
        unknown = json.loads(unknown_path.read_text(encoding="utf-8"))
        unknown_unsigned = dict(unknown)
        unknown_seal = unknown_unsigned.pop("authority_sha256")
        self.assertEqual(unknown_seal, contract.digest(unknown_unsigned))
        self.assertEqual(len(unknown["unknown_rows"]), 9)
        self.assertEqual(
            {row["reason"] for row in unknown["unknown_rows"]},
            {"MISSING_INDEPENDENT_SEMANTIC_AUTHORITY"},
        )
        self.assertFalse(
            unknown["classification_boundary"]
            ["current_evidence_establishes_principled_undecidability_for_any_row"]
        )
        cache = value["identity_and_fairness"]["cache_policy"]
        self.assertEqual(
            cache["cold_definition"],
            "fresh_parent_process_and_empty_private_cupy_recipe_cache__"
            "not_cold_operating_system_page_cache_cuda_driver_jit_cache_or_"
            "optix_disk_cache",
        )
        self.assertEqual(cache["cold_claim_excludes"], [
            "operating_system_page_cache",
            "cuda_driver_jit_cache",
            "optix_disk_cache",
        ])
        self.assertTrue(
            cache["controller_rehashes_all_scheduled_inputs_before_worker_zero"])
        self.assertTrue(
            cache["preworker_full_rehash_can_warm_operating_system_page_cache"])
        self.assertFalse(
            cache["operating_system_page_cache_controlled_or_dropped"])
        self.assertFalse(cache["cuda_driver_jit_cache_controlled_or_isolated"])
        self.assertFalse(cache["optix_disk_cache_controlled_or_isolated"])
        self.assertTrue(
            cache["same_cohort_abba_symmetry_is_page_cache_mitigation_not_control"])
        self.assertTrue(
            cache["round_major_abba_is_uncontrolled_cache_mitigation_not_control"])
        self.assertTrue(cache["paper_must_disclose_page_cache_boundary"])
        self.assertTrue(cache["cache_receipts_preserved"])
        self.assertFalse(cache["cache_payloads_are_authoritative_evidence"])
        self.assertTrue(
            cache[
                "successful_cohort_cache_payloads_removed_after_validation_before_publication"
            ]
        )
        source_admission = value["identity_and_fairness"][
            "source_admission_policy"
        ]
        self.assertEqual(source_admission, contract.SOURCE_ADMISSION_POLICY)
        self.assertTrue(
            source_admission[
                "controller_full_rehash_and_exact_set_before_worker_zero"
            ]
        )
        self.assertTrue(
            source_admission[
                "every_worker_full_rehash_and_exact_set_before_product_import"
            ]
        )
        self.assertFalse(
            source_admission[
                "extra_missing_symlink_reparse_or_special_paths_allowed"
            ]
        )
        self.assertFalse(
            source_admission["same_host_malicious_root_race_excluded"]
        )
        environment = value["identity_and_fairness"][
            "formal_worker_environment_contract"
        ]
        self.assertEqual(
            environment, contract.FORMAL_WORKER_ENVIRONMENT_CONTRACT)
        self.assertEqual(environment["lc_all"], "C.UTF-8")
        self.assertEqual(environment["ld_preload"], "")
        self.assertEqual(
            environment["dynamic_keys"],
            ["CUPY_CACHE_DIR", "NUMBA_CACHE_DIR"],
        )
        self.assertEqual(len(environment["frozen_keys"]), 14)
        self.assertIn("LC_ALL", environment["frozen_keys"])
        self.assertNotIn("LC_CTYPE", environment["frozen_keys"])
        self.assertTrue(environment["exact_live_key_set_required"])
        self.assertFalse(environment["ambient_environment_inherited"])
        self.assertFalse(
            environment[
                "python_locale_coercion_or_injected_lc_ctype_allowed"
            ]
        )
        fairness = value["identity_and_fairness"]
        self.assertEqual(
            fairness["formal_output_layout_contract"],
            contract.FORMAL_OUTPUT_LAYOUT_CONTRACT,
        )
        self.assertEqual(
            fairness["controller_bootstrap_observation_contract"],
            contract.CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT,
        )
        self.assertEqual(
            fairness["immutable_control_file_observation_contract"],
            contract.IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT,
        )
        self.assertEqual(
            fairness["no_gpu_product_process_state_observation_contract"],
            contract.NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT,
        )
        self.assertEqual(
            fairness["target_runtime_admission_contract"],
            contract.TARGET_RUNTIME_ADMISSION_CONTRACT,
        )
        self.assertEqual(
            fairness["resource_admission_contract"],
            contract.RESOURCE_ADMISSION_CONTRACT,
        )
        self.assertEqual(
            contract.FORMAL_OUTPUT_LAYOUT_CONTRACT[
                "minimum_required_free_disk_bytes"],
            20_000_000_000,
        )
        self.assertTrue(
            contract.CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT[
                "stdlib_environment_and_entrypoint_gate_precedes_shared_imports"
            ]
        )
        markers = contract.NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT[
            "forbidden_dso_map_markers"]
        self.assertIn("/libnvrtc-builtins.so", markers)
        self.assertIn("/libnvidia-rtcore.so", markers)
        self.assertIn("/libnvptxcompiler", markers)
        segment_input = value["contracts"]["segment_plan_input"]
        self.assertEqual(segment_input, contract.SEGMENT_PLAN_INPUT_CONTRACT)
        self.assertFalse(segment_input["descriptor_only_input_identity_allowed"])
        self.assertEqual(
            segment_input["formal_source_input"],
            "selected_frozen_dataset_input_sha256",
        )

    def test_target_values_are_slots_not_guessed_identities(self) -> None:
        value = contract.contract_document()
        self.assertFalse(value["target_derived_values_filled_by_this_contract"])
        self.assertEqual(
            set(value["required_authority_hash_slots"]),
            set(contract.AUTHORITY_ROLES),
        )
        self.assertEqual(
            value["required_authority_file_sha256"],
            contract.AUTHORITY_FILE_SHA256,
        )
        self.assertEqual(
            set(value["required_target_materialization_hash_slots"]),
            set(contract.TARGET_HASH_SLOTS),
        )
        self.assertEqual(
            set(value["required_target_materialization_nonce_slots"]),
            set(contract.TARGET_NONCE_SLOTS),
        )
        self.assertNotIn("callback_authority_nonce", contract.TARGET_HASH_SLOTS)
        self.assertNotIn("target_evidence_nonce", contract.TARGET_HASH_SLOTS)
        bundle = value["provider_program_bundle_digest_contract"]
        self.assertEqual(
            bundle["source_hash_slots"],
            list(contract.PROVIDER_PROGRAM_BUNDLE_SOURCE_HASH_SLOTS),
        )
        self.assertEqual(
            bundle["source_nonce_slots"],
            list(contract.PROVIDER_PROGRAM_BUNDLE_SOURCE_NONCE_SLOTS),
        )
        self.assertFalse(bundle["opaque_identity_string_accepted_as_digest"])
        self.assertIn("cupy_version", value["required_target_version_slots"])
        boundary = value["authority_boundary"]
        self.assertTrue(boundary["separate_owner_formal_execution_authority_required"])
        for key, item in boundary.items():
            if key.startswith("base_contract_authorizes_"):
                self.assertFalse(item, key)

    def test_timer_phase_accounting_and_two_phase_seal_are_exact(self) -> None:
        cold = {
            "loading": 0.1,
            "preparation": 0.2,
            "prewarm": 0.0,
            "execute": 0.3,
            "close": 0.4,
        }
        prepared = {
            "loading": 0.1,
            "preparation": 0.2,
            "prewarm": 0.25,
            "execute": 0.3,
            "close": 0.4,
        }
        def sequence(values, *, gaps):
            cursor = 1_000_000_000
            rows = []
            for index, name in enumerate(
                ("loading", "preparation", "prewarm", "execute", "close")
            ):
                if index:
                    cursor += gaps[index - 1]
                duration = round(values[name] * 1_000_000_000)
                rows.append({
                    "phase": name,
                    "started_ns": cursor,
                    "ended_ns": cursor + duration,
                    "seconds": values[name],
                })
                cursor += duration
            return rows

        cold_sequence = sequence(cold, gaps=[10_000_000] * 4)
        prepared_sequence = sequence(prepared, gaps=[10_000_000] * 4)
        cold_registered = (
            cold_sequence[-1]["ended_ns"]
            - cold_sequence[0]["started_ns"]
        ) / 1_000_000_000.0
        contract.validate_phase_accounting(
            contract.COLD, cold, cold_registered, cold_sequence)
        contract.validate_phase_accounting(
            contract.PREPARED, prepared, 0.3, prepared_sequence)
        bad_prepared = dict(prepared)
        bad_prepared["prewarm"] = 0.0
        with self.assertRaises(contract.Goal5791ContractError):
            contract.validate_phase_accounting(
                contract.PREPARED, bad_prepared, 0.3, prepared_sequence)
        with self.assertRaises(contract.Goal5791ContractError):
            contract.validate_phase_accounting(
                contract.COLD, cold, sum(cold.values()), cold_sequence)
        bad_cold = dict(cold)
        bad_cold["prewarm"] = 0.01
        with self.assertRaises(contract.Goal5791ContractError):
            contract.validate_phase_accounting(
                contract.COLD, bad_cold, cold_registered, cold_sequence)
        overlapping = [dict(row) for row in cold_sequence]
        overlapping[2]["started_ns"] = overlapping[1]["ended_ns"] - 1
        with self.assertRaises(contract.Goal5791ContractError):
            contract.validate_phase_accounting(
                contract.COLD, cold, cold_registered, overlapping)
        timer = contract.timer_contract(contract.PREPARED)
        self.assertEqual(
            timer["registered_endpoint"],
            "one_continuous_first_post_preparation_measured_execute_interval",
        )
        self.assertTrue(timer["registered_endpoint_is_one_continuous_interval"])
        self.assertFalse(timer["registered_phase_seconds_are_summed"])
        self.assertEqual(timer["registered_phases"], ["execute"])
        self.assertIn(
            "cpu_deterministic_segment_descriptor_pass",
            timer["preparation_required_work"],
        )
        self.assertIn(
            "deep_admission_of_every_single_use_execution_token",
            timer["preparation_required_work"],
        )
        self.assertIn(
            "native_traversal_audit_capture", timer["execute_included_work"])
        self.assertIn(
            "constant_time_pre_admitted_single_use_execution_token_binding",
            timer["execute_included_work"],
        )
        self.assertEqual(
            set(timer["execute_forbidden_work"]),
            set(contract.EXECUTE_FORBIDDEN_WORK),
        )
        execute_control = timer["execute_control_contract"]
        self.assertEqual(
            execute_control["timer_interval"],
            "one_continuous_interval_without_pause_or_restart",
        )
        self.assertFalse(
            execute_control[
                "deep_plan_authority_recipe_or_operation_contract_verification_allowed"
            ]
        )
        self.assertTrue(execute_control["constant_time_token_binding_required"])
        trace = timer["trace_instrumentation_contract"]
        self.assertTrue(trace["trace_capture_inside_execute_timer"])
        self.assertTrue(
            trace["instrumentation_policy_identical_by_declared_operation_semantics"])
        self.assertEqual(
            trace["expected_success_event_count"],
            {contract.FUSION_OFF: 7, contract.FUSION_ON: 2},
        )
        self.assertFalse(
            trace["subtract_correct_or_pause_timer_for_trace_cost_allowed"])
        self.assertTrue(
            trace["cpu_only_diagnostic_required_before_stage_b_worker_zero"])
        self.assertTrue(trace["cpu_only_diagnostic_completed_and_frozen"])
        self.assertEqual(trace["per_event_record_cost_bound_ns"], 12_202)
        self.assertEqual(
            trace["five_extra_event_differential_bound_per_segment_ns"],
            61_010,
        )
        self.assertEqual(trace["small_relative_max_fraction"], 0.01)
        self.assertEqual(
            trace["small_relative_comparison_arithmetic"],
            "exact_registered_phase_interval_nanoseconds_with_fractional_"
            "median_and_rational_less_equal_comparison_before_float_"
            "presentation",
        )
        self.assertTrue(
            trace["ci_clear_win_requires_small_relative_rule_for_paper_claim"])
        self.assertFalse(
            trace["diagnostic_may_change_row_statistic_ci_threshold_or_verdict"])
        self.assertEqual(
            trace["measured_claim"],
            "end_to_end_compiler_runtime_lowering_including_evidence_overhead",
        )
        self.assertFalse(trace["pure_device_kernel_timing_claimed"])
        self.assertTrue(
            trace["every_result_row_must_publish_diagnostic_bound"])
        self.assertTrue(trace["paper_must_disclose_diagnostic_measurement_host"])
        self.assertFalse(
            trace["diagnostic_measurement_environment"]
            ["measured_on_formal_target_host"]
        )
        self.assertFalse(trace["stage_a_target_host_cpu_diagnostic_rerun_required"])
        diagnostic_path = ROOT / contract.TRACE_COST_DIAGNOSTIC_AUTHORITY_PATH
        diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8"))
        diagnostic_unsigned = dict(diagnostic)
        diagnostic_seal = diagnostic_unsigned.pop("diagnostic_sha256")
        self.assertEqual(
            contract.file_sha256(diagnostic_path),
            contract.TRACE_COST_DIAGNOSTIC_AUTHORITY_FILE_SHA256,
        )
        self.assertEqual(
            diagnostic_seal,
            contract.TRACE_COST_DIAGNOSTIC_AUTHORITY_SHA256,
        )
        self.assertEqual(diagnostic_seal, contract.digest(diagnostic_unsigned))
        self.assertEqual(
            diagnostic["operation_ids"][contract.FUSION_OFF],
            [name for name, _kind in trace_diagnostic.FUSION_OFF_OPERATIONS],
        )
        self.assertEqual(
            diagnostic["operation_ids"][contract.FUSION_ON],
            [name for name, _kind in trace_diagnostic.FUSION_ON_OPERATIONS],
        )
        self.assertEqual(
            diagnostic["per_event_record_cost_bound_ns"],
            trace["per_event_record_cost_bound_ns"],
        )
        self.assertEqual(
            diagnostic["five_extra_event_differential_bound_per_segment_ns"],
            trace["five_extra_event_differential_bound_per_segment_ns"],
        )
        presentation = contract.contract_document()["result_presentation"]
        self.assertEqual(
            presentation["public_lifecycle_labels"][contract.COLD],
            "cold_process_warm_system",
        )
        self.assertEqual(
            presentation["public_lifecycle_labels"][contract.PREPARED],
            "prepared",
        )
        self.assertEqual(
            contract.result_row_id("com_dblp", contract.COLD),
            "com_dblp__cold_process_warm_system",
        )
        self.assertEqual(
            presentation["independent_recount_external_review_status"],
            contract.INDEPENDENT_RECOUNT_REVIEW_STATUS,
        )
        self.assertIn(
            "receipt_json_serialization",
            timer["evidence_seal_work_outside_registered_timer"],
        )
        self.assertTrue(timer["evidence_sealed_after_registered_endpoint_stops"])
        self.assertTrue(
            timer["prepared_loading_preparation_prewarm_and_close_reported_separately"])
        self.assertFalse(timer["prepared_work_called_free"])

        cache = contract.CACHE_POLICY
        self.assertTrue(cache["cold_cache_initially_empty"])
        self.assertFalse(cache["shared_cache_between_workers_or_measured_arms"])
        self.assertTrue(
            cache["cold_only_selected_recipe_first_compile_and_jit_inside_execute"])
        self.assertFalse(cache["cold_preparation_may_compile_selected_recipe"])
        self.assertEqual(
            cache["prepared_neutral_recipe_prewarm_order"],
            [contract.FUSION_OFF, contract.FUSION_ON],
        )
        self.assertTrue(
            cache["prepared_same_fresh_worker_prewarms_both_recipes"])
        self.assertTrue(
            cache["prepared_private_cache_contains_both_neutral_prewarm_recipes"])
        self.assertTrue(
            cache["prepared_each_recipe_launches_synchronizes_and_frees"])

    def test_operation_contract_is_exact_two_versus_seven(self) -> None:
        off = contract.expected_operation_contract(contract.FUSION_OFF)
        on = contract.expected_operation_contract(contract.FUSION_ON)
        self.assertEqual(off["successful_event_count"], 7)
        self.assertEqual(on["successful_event_count"], 2)
        self.assertEqual(off["operation_ids"], list(contract.FUSION_OFF_OPERATION_IDS))
        self.assertEqual(on["operation_ids"], list(contract.FUSION_ON_OPERATION_IDS))
        self.assertFalse(off["hardware_or_opaque_cupy_kernel_introspection_claimed"])
        self.assertFalse(on["hardware_or_opaque_cupy_kernel_introspection_claimed"])

    def test_real_predecessor_and_citation_authorities_revalidate(self) -> None:
        contract.validate_predecessor_contract(ROOT)
        contract.validate_source_authority(
            AUTHORITY_SOURCE_PATHS["source_authority"])
        data = contract.validate_data_authority(
            AUTHORITY_SOURCE_PATHS["data_authority"])
        contract.validate_runtime_budget_authority(
            AUTHORITY_SOURCE_PATHS["runtime_budget_authority"])
        contract.validate_expected_value_authority(
            AUTHORITY_SOURCE_PATHS["expected_value_authority"])
        citation = AUTHORITY_SOURCE_PATHS["citation_authority"]
        value = contract.validate_citation_authority(citation)
        self.assertEqual(
            value["nearest_adjacent_primary_work"]["doi"],
            contract.SIGMETRICS_DOI,
        )
        self.assertEqual(
            {
                dataset_id: data["datasets"][dataset_id]["sha256"]
                for dataset_id in contract.DATASET_IDS
            },
            {
                dataset_id: contract.DATA_AUTHORITY_DATASETS[dataset_id]["sha256"]
                for dataset_id in contract.DATASET_IDS
            },
        )

    def test_pretarget_authority_loads_but_cannot_satisfy_target_gate(self) -> None:
        preregistration_path = ROOT / (
            "history/internal_docs/goal5791_preregistration_v9_20260820.json"
        )
        preregistration = json.loads(
            preregistration_path.read_text(encoding="utf-8"))
        preregistration_unsigned = dict(preregistration)
        preregistration_seal = preregistration_unsigned.pop(
            "preregistration_sha256")
        self.assertEqual(
            contract.file_sha256(preregistration_path),
            "4878e666695e513e47c2adad65869a1cde2640396b6afdcbcd1f493e8cc1495a",
        )
        self.assertEqual(
            preregistration_seal, contract.digest(preregistration_unsigned))
        self.assertEqual(
            preregistration["formal_contract_sha256"],
            contract.contract_sha256(),
        )
        frozen_pretarget_path = ROOT / (
            "history/internal_docs/"
            "goal5791_pretarget_preexecution_authority_v9_20260820.json"
        )
        resolved_history = (ROOT / "history").resolve()
        validation_root = (
            resolved_history.parent
            if resolved_history != ROOT / "history" else ROOT
        )
        frozen = contract.load_preexecution_authority(
            frozen_pretarget_path,
            repository_root=validation_root,
            require_target_binding=False,
        )
        self.assertIsNone(frozen["target_materialization_binding"])
        self.assertEqual(
            contract.file_sha256(frozen_pretarget_path),
            "46fdb549f8397b361871a8dc1d5a6e7d6995903c9e0f1ba60ed2a7804ff0cfc1",
        )
        successor_path = ROOT / (
            "history/internal_docs/"
            "goal5791_paper_outcome_consequence_selection_"
            "successor_authority_20260820.json"
        )
        successor = json.loads(successor_path.read_text(encoding="utf-8"))
        successor_unsigned = dict(successor)
        successor_seal = successor_unsigned.pop("authority_sha256")
        self.assertEqual(
            contract.file_sha256(successor_path),
            "b38251247b6408ca3b1b34b51fd8b22c2cc079f80e3f28fb14b124106b5957ac",
        )
        self.assertEqual(successor_seal, contract.digest(successor_unsigned))
        self.assertEqual(
            successor["v9_formal_freeze"]["formal_contract_sha256"],
            contract.contract_sha256(),
        )
        self.assertEqual(
            successor["v9_formal_freeze"][
                "paper_outcome_consequence_contract_sha256"
            ],
            contract.digest(contract.PAPER_OUTCOME_CONSEQUENCE_CONTRACT),
        )
        self.assertEqual(
            successor["v9_preexecution_freeze"][
                "preregistration_file_sha256"
            ],
            contract.file_sha256(preregistration_path),
        )
        self.assertEqual(
            successor["v9_preexecution_freeze"]["pretarget_file_sha256"],
            contract.file_sha256(frozen_pretarget_path),
        )
        self.assertEqual(
            set(successor["paper_outcome_mechanical_policy"]),
            {
                "row_eligibility",
                "small_relative_arithmetic",
                "paper_clear_winning_row_count_equals_0",
                "paper_clear_winning_row_count_between_1_and_5",
                "paper_clear_winning_row_count_equals_6",
                "primary_evaluator_rebuilds_from_raw_workers",
                "independent_recount_rebuilds_from_raw_workers_without_primary_selection",
                "controller_rebuilds_from_all_96_raw_workers",
                "published_result_copies_only_a_mechanically_revalidated_selection",
                "ci_clear_win_count_remains_a_distinct_pure_statistical_count",
                "zero_one_through_five_and_six_branches_are_attack_tested",
                "exact_0p01_boundary_and_just_above_boundary_are_attack_tested",
                "jointly_resigned_primary_recount_and_result_wrong_branch_is_rejected",
            },
        )
        self.assertTrue(all(
            value is False
            for value in successor["authorization"].values()
        ))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path, _ = _preexecution_authority(root)
            value = contract.load_preexecution_authority(
                path, repository_root=root)
            self.assertIsNone(value["target_materialization_binding"])
            with self.assertRaises(contract.Goal5791ContractError):
                contract.load_preexecution_authority(
                    path, repository_root=root, require_target_binding=True)

    def test_postprepare_authority_strictly_binds_target_and_recipes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path, _ = _preexecution_authority(root, with_target=True)
            value = contract.load_preexecution_authority(
                path, repository_root=root, require_target_binding=True)
            target = value["target_materialization_binding"]
            self.assertIsInstance(target, dict)
            self.assertEqual(
                target["hashes"]["fusion_off_recipe_sha256"],
                target["recipes"]["fusion_off"]["actual_recipe_sha256"],
            )
            self.assertNotEqual(
                target["recipes"]["fusion_off"]["actual_recipe_sha256"],
                target["recipes"]["fusion_off"]["claim_wrapper_sha256"],
            )
            bundle = target["derived_digests"]["provider_program_bundle"]
            self.assertEqual(
                target["hashes"]["provider_program_bundle_sha256"],
                bundle["sha256"],
            )
            self.assertEqual(
                bundle,
                contract.provider_program_bundle_digest_record(
                    target["hashes"], target["nonces"],
                ),
            )
            self.assertFalse(value["authorization"]["authorizes_formal_workers"])

    def test_nonces_are_typed_separately_and_bundle_derivation_is_strict(self) -> None:
        def malformed_nonce(value):
            value["target_materialization_binding"]["nonces"][
                "callback_authority_nonce"
            ] = "a" * 63

        def placeholder_nonce(value):
            value["target_materialization_binding"]["nonces"][
                "target_evidence_nonce"
            ] = "0" * 64

        def derived_source_drift(value):
            record = value["target_materialization_binding"][
                "derived_digests"
            ]["provider_program_bundle"]
            record["source_bindings"]["source_hashes"][
                "native_library_sha256"
            ] = _sha("unbound-native")
            record["sha256"] = contract.digest(record["source_bindings"])
            value["target_materialization_binding"]["hashes"][
                "provider_program_bundle_sha256"
            ] = record["sha256"]

        def opaque_bundle_identity(value):
            target = value["target_materialization_binding"]
            target["derived_digests"]["provider_program_bundle"] = {
                "sha256": _sha("opaque-identity-string")
            }
            target["hashes"]["provider_program_bundle_sha256"] = _sha(
                "opaque-identity-string"
            )

        for name, mutation in (
            ("malformed nonce", malformed_nonce),
            ("placeholder nonce", placeholder_nonce),
            ("derived source drift", derived_source_drift),
            ("opaque bundle identity", opaque_bundle_identity),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                path, value = _preexecution_authority(root, with_target=True)
                mutation(value)
                _resign_target(value)
                _write_json(path, value)
                with self.assertRaises(contract.Goal5791ContractError):
                    contract.load_preexecution_authority(
                        path, repository_root=root, require_target_binding=True)

    def test_owner_formal_authority_binds_stage_a_and_exactly_once_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            preexecution_path, preexecution = _preexecution_authority(
                root, with_target=True,
            )
            owner_path, owner = _owner_formal_authority(
                root, preexecution_path, preexecution,
            )
            loaded = contract.load_owner_formal_execution_authority(
                owner_path,
                preexecution_authority_path=preexecution_path,
                repository_root=root,
            )
            self.assertEqual(loaded, owner)
            snapshot_loaded = contract.load_owner_formal_execution_authority(
                owner_path,
                preexecution_authority=preexecution,
                preexecution_authority_file_sha256=contract.file_sha256(
                    preexecution_path
                ),
            )
            self.assertEqual(snapshot_loaded, owner)
            from scripts import goal5791_formal_worker as formal_worker
            worker_context = formal_worker._load_authority_context(
                repository_root=root,
                preexecution_path=preexecution_path,
                formal_authority_path=owner_path,
            )
            self.assertEqual(worker_context.formal, owner)
            self.assertEqual(loaded["formal_worker_count"], 96)
            self.assertEqual(loaded["independent_row_count"], 6)
            self.assertTrue(
                loaded["execution_policy"][
                    "each_worker_index_executes_exactly_once"
                ]
            )
            self.assertEqual(
                loaded["execution_policy"]["per_worker_timeout_seconds"],
                1_800,
            )
            for prohibited in ("retry_allowed", "resume_allowed", "replacement_allowed"):
                self.assertFalse(loaded["execution_policy"][prohibited])
            target = preexecution["target_materialization_binding"]
            self.assertNotIn("formal_execution_authority_sha256", target)
            self.assertNotIn(
                loaded["authority_sha256"],
                json.dumps(target, sort_keys=True),
            )

    def test_resigned_owner_nonce_count_authorization_and_target_drift_fail(self) -> None:
        def nonce_drift(value):
            value["owner_authorization_nonce"] = "0" * 64

        def count_drift(value):
            value["formal_worker_count"] = 95

        def authorization_drift(value):
            value["authorization"]["authorizes_registered_timing"] = False

        def target_drift(value):
            value["target_materialization_binding_sha256"] = _sha(
                "other-target-binding"
            )

        def retry_drift(value):
            value["execution_policy"]["retry_allowed"] = True

        def endpoint_drift(value):
            value["execution_target"]["pod_endpoint"]["port"] += 1

        def resource_drift(value):
            value["resource_confirmation"][
                "owner_confirmed_uninterrupted_window_hours"
            ] = 6.99

        def materialization_output_overlap(value):
            value["execution_target"]["create_only_formal_output_root"] = (
                "/root/goal5791_fixture_materialization/formal_output")

        def staging_derivation_drift(value):
            value["execution_target"]["controller_incomplete_staging_root"] = (
                "/root/goal5791_fixture_other_staging")

        def authority_disk_observation_drift(value):
            value["resource_confirmation"][
                "formal_output_parent_free_bytes_observed_at_authority_creation"
            ] = 24_999_999_999

        def minimum_disk_drift(value):
            value["resource_confirmation"][
                "minimum_required_free_disk_bytes"] = 19_999_999_999

        def resource_parent_drift(value):
            value["resource_confirmation"][
                "formal_output_parent_resolved_path"] = "/tmp"

        def legacy_root_field(value):
            value["execution_target"]["create_only_remote_root"] = (
                "/root/goal5791_legacy")

        for name, mutation in (
            ("nonce", nonce_drift),
            ("count", count_drift),
            ("authorization", authorization_drift),
            ("target", target_drift),
            ("retry", retry_drift),
            ("endpoint", endpoint_drift),
            ("resource", resource_drift),
            ("materialization_output_overlap", materialization_output_overlap),
            ("staging_derivation", staging_derivation_drift),
            ("authority_disk_observation", authority_disk_observation_drift),
            ("minimum_disk", minimum_disk_drift),
            ("resource_parent", resource_parent_drift),
            ("legacy_root_field", legacy_root_field),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                preexecution_path, preexecution = _preexecution_authority(
                    root, with_target=True,
                )
                owner_path, owner = _owner_formal_authority(
                    root, preexecution_path, preexecution,
                )
                mutation(owner)
                _resign_owner_authority(owner)
                _write_json(owner_path, owner)
                with self.assertRaises(contract.Goal5791ContractError):
                    contract.load_owner_formal_execution_authority(
                        owner_path,
                        preexecution_authority_path=preexecution_path,
                        repository_root=root,
                    )

    def test_authority_files_hashes_paths_roles_and_seal_fail_closed(self) -> None:
        mutations = {}

        def missing_role(value):
            del value["authority_records"]["runtime_budget_authority"]

        mutations["missing role"] = missing_role

        def unsafe_path(value):
            value["authority_records"]["source_authority"]["path"] = "../source"

        mutations["unsafe path"] = unsafe_path

        def placeholder_hash(value):
            value["authority_records"]["data_authority"]["sha256"] = "0" * 64

        mutations["placeholder hash"] = placeholder_hash

        def wrong_hash(value):
            value["authority_records"]["expected_value_authority"]["sha256"] = _sha(
                "wrong-file")

        mutations["wrong file hash"] = wrong_hash

        def reused_path(value):
            value["authority_records"]["runtime_budget_authority"] = deepcopy(
                value["authority_records"]["source_authority"])

        mutations["reused role path"] = reused_path

        def target_work(value):
            value["formal_worker_count"] = 1

        mutations["preexisting worker"] = target_work

        def input_map_drift(value):
            value["dataset_input_sha256"]["com_dblp"] = _sha("wrong-input")

        mutations["input map differs from data authority"] = input_map_drift

        def oracle_map_drift(value):
            value["oracle_authority_sha256"]["cit_patents"] = _sha(
                "wrong-oracle"
            )

        mutations["oracle map differs from data authority"] = oracle_map_drift

        for name, mutation in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                path, value = _preexecution_authority(root)
                mutation(value)
                _resign_authority(value)
                _write_json(path, value)
                with self.assertRaises(contract.Goal5791ContractError):
                    contract.load_preexecution_authority(path, repository_root=root)

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path, value = _preexecution_authority(root)
            value["schedule_sha256"] = _sha("wrong-schedule")
            _write_json(path, value)  # deliberately not resigned
            with self.assertRaises(contract.Goal5791ContractError):
                contract.load_preexecution_authority(path, repository_root=root)

    def test_resigned_reauthored_role_files_cannot_replace_frozen_authorities(self) -> None:
        for role in contract.AUTHORITY_ROLES:
            with self.subTest(role=role), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                path, authority = _preexecution_authority(root)
                record = authority["authority_records"][role]
                role_path = root.joinpath(*Path(record["path"]).parts)
                payload = json.loads(role_path.read_text(encoding="utf-8"))
                payload["goal"] = 9_999
                _write_json(role_path, payload)
                record["sha256"] = contract.file_sha256(role_path)
                record["bytes"] = role_path.stat().st_size
                _resign_authority(authority)
                _write_json(path, authority)
                with self.assertRaises(contract.Goal5791ContractError):
                    contract.load_preexecution_authority(
                        path, repository_root=root,
                    )

    def test_resigned_target_identity_recipe_cache_and_semantics_drift_fail(self) -> None:
        def placeholder_identity(value):
            value["target_materialization_binding"]["hashes"][
                "native_library_sha256"] = "0" * 64

        def recipe_payload_drift(value):
            target = value["target_materialization_binding"]
            recipe = target["recipes"][contract.FUSION_OFF]
            recipe["claim_wrapper"]["operation_ids"] = list(
                reversed(recipe["claim_wrapper"]["operation_ids"]))
            recipe["claim_wrapper_sha256"] = contract.digest(
                recipe["claim_wrapper"]
            )

        def cache_drift(value):
            value["target_materialization_binding"]["cache_policy"][
                "shared_cache_between_workers_or_measured_arms"] = True

        def semantic_drift(value):
            value["target_materialization_binding"]["hashes"][
                "semantic_request_sha256"] = _sha("other-semantics")

        for name, mutation in (
            ("placeholder identity", placeholder_identity),
            ("recipe drift", recipe_payload_drift),
            ("cache drift", cache_drift),
            ("semantic drift", semantic_drift),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                path, value = _preexecution_authority(root, with_target=True)
                mutation(value)
                _resign_target(value)
                _write_json(path, value)
                with self.assertRaises(contract.Goal5791ContractError):
                    contract.load_preexecution_authority(
                        path, repository_root=root, require_target_binding=True)

    def test_resigned_citation_doi_ownership_and_authorization_drift_fail(self) -> None:
        for name, mutation in (
            (
                "doi",
                lambda value: value["nearest_adjacent_primary_work"].__setitem__(
                    "doi", "10.0000/not-the-paper"),
            ),
            (
                "ownership",
                lambda value: value["nearest_adjacent_primary_work"][
                    "attribution"].__setitem__(
                        "goal5791_invents_or_selects_any_of_these", True),
            ),
            (
                "authorization",
                lambda value: value["authorization"].__setitem__(
                    "authorizes_formal_worker_zero", True),
            ),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                path, authority = _preexecution_authority(root)
                citation_record = authority["authority_records"]["citation_authority"]
                citation_path = root.joinpath(
                    *Path(citation_record["path"]).parts)
                citation = json.loads(citation_path.read_text(encoding="utf-8"))
                mutation(citation)
                _write_json(citation_path, citation)
                citation_record["sha256"] = contract.file_sha256(citation_path)
                citation_record["bytes"] = citation_path.stat().st_size
                _resign_authority(authority)
                _write_json(path, authority)
                with self.assertRaises(contract.Goal5791ContractError):
                    contract.load_preexecution_authority(path, repository_root=root)

    def test_selection_logic_is_pair_parity_only(self) -> None:
        source = Path(contract.__file__).read_text(encoding="utf-8")
        start = source.index("def variant_order(")
        end = source.index("\n\ndef schedule(", start)
        function = source[start:end]
        tree = ast.parse(function)
        comparisons = [
            ast.unparse(node)
            for node in ast.walk(tree)
            if isinstance(node, ast.Compare)
        ]
        self.assertIn("pair_index % 2 == 0", comparisons)
        lowered = function.lower()
        for forbidden in (
            "dataset", "timing", "result", "speed", "application", "paper",
        ):
            self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()

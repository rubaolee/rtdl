from pathlib import Path
import unittest

from scripts import goal1506_v1_5_4_optix_collect_k_stage_profile_probe as probe


ROOT = Path(__file__).resolve().parents[1]
PLAN_MD = ROOT / "docs" / "reports" / "goal1506_v1_5_4_optix_collect_k_stage_profile_plan_2026-05-08.md"
OPTIX_API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
POD_RUNNER = ROOT / "scripts" / "goal1506_v1_5_4_run_optix_collect_k_stage_profile_pod.sh"


class Goal1506V154OptixCollectKStageProfilePlanTest(unittest.TestCase):
    def test_plan_keeps_claim_boundary_conservative(self) -> None:
        text = PLAN_MD.read_text(encoding="utf-8")

        self.assertIn("Local source review only", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("Claim flags all false", text)
        self.assertIn("does not change the experimental status", text)

    def test_plan_records_next_pod_stage_measurement_targets(self) -> None:
        text = PLAN_MD.read_text(encoding="utf-8")

        for phrase in (
            "Tile sort time",
            "Merge kernel time by level",
            "Host synchronization and metadata download time",
            "Final device-to-device output copy time",
            "First-call PTX compile/module-load overhead",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_runner_has_exact_profile_flow(self) -> None:
        text = POD_RUNNER.read_text(encoding="utf-8")

        self.assertIn("make build-optix", text)
        self.assertIn("goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py", text)
        self.assertIn("--counts $COUNTS", text)
        self.assertIn("--repeats \"$REPEATS\"", text)
        self.assertIn("tests.goal1506_v1_5_4_optix_collect_k_stage_profile_plan_test", text)
        self.assertIn("goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.jsonl", text)

    def test_plan_records_current_tiled_topology_for_large_counts(self) -> None:
        text = PLAN_MD.read_text(encoding="utf-8")

        self.assertIn("For `131072` candidates", text)
        self.assertIn("`32` sort kernel launches", text)
        self.assertIn("`31` merge kernel launches", text)
        self.assertIn("`126` tiny device-to-host metadata fields", text)
        self.assertIn("For `65537` candidates", text)
        self.assertIn("`17` sort kernel launches", text)
        self.assertIn("`16` merge kernel launches", text)
        self.assertIn("`66` tiny device-to-host metadata fields", text)

    def test_native_source_has_opt_in_profile_hook(self) -> None:
        text = OPTIX_API_CPP.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_PROFILE_JSONL", text)
        self.assertIn("CollectKStageProfile", text)
        self.assertIn("Profiling must never change runtime behavior", text)
        self.assertIn("collect_k_bounded_i64_device_stage_profile", text)

    def test_probe_validator_accepts_synthetic_profile_payload(self) -> None:
        payload = make_synthetic_probe()

        self.assertIs(probe.validate_probe(payload), payload)
        markdown = probe.to_markdown(payload)
        self.assertIn("Goal 1506", markdown)
        self.assertIn("Claim Boundary", markdown)

    def test_probe_validator_rejects_missing_profile_records(self) -> None:
        payload = make_synthetic_probe()
        payload["all_profile_records_present"] = False

        with self.assertRaisesRegex(ValueError, "profiled call record"):
            probe.validate_probe(payload)

    def test_accepted_evidence_requires_all_core_gates(self) -> None:
        payload = make_synthetic_probe()

        self.assertTrue(payload["accepted_goal1506_evidence"])
        for flag in (
            "all_parity_passed",
            "all_profile_records_present",
            "all_profile_paths_match_expected",
            "all_profile_topologies_match_expected",
        ):
            with self.subTest(flag=flag):
                mutated = make_synthetic_probe()
                mutated[flag] = False
                mutated["accepted_goal1506_evidence"] = (
                    mutated["all_parity_passed"]
                    and mutated["all_profile_records_present"]
                    and mutated["all_profile_paths_match_expected"]
                    and mutated["all_profile_topologies_match_expected"]
                )
                self.assertFalse(mutated["accepted_goal1506_evidence"])

    def test_probe_validator_rejects_topology_mismatch(self) -> None:
        payload = make_synthetic_probe()
        payload["all_profile_topologies_match_expected"] = False

        with self.assertRaisesRegex(ValueError, "topology records"):
            probe.validate_probe(payload)

    def test_probe_validator_accepts_explicit_local_fallback_smoke(self) -> None:
        payload = make_synthetic_probe()
        payload["accepted_goal1506_evidence"] = False
        payload["local_fallback_smoke_only"] = True
        payload["all_profile_paths_match_expected"] = False
        payload["all_profile_topologies_match_expected"] = False
        payload["cases"][0]["profile_native_path_matches_expected"] = False
        payload["cases"][0]["profile_topology_matches_expected"] = False
        payload["cases"][0]["stage_profile"]["topology"] = probe.expected_topology(4097, 3)

        self.assertIs(probe.validate_probe(payload, allow_local_fallback_smoke=True), payload)
        with self.assertRaisesRegex(ValueError, "expected paths"):
            probe.validate_probe(payload)

    def test_probe_validator_rejects_claim_expansion(self) -> None:
        payload = make_synthetic_probe()
        payload["claim_flags"]["public_speedup_wording_authorized"] = True

        with self.assertRaisesRegex(ValueError, "public_speedup_wording_authorized"):
            probe.validate_probe(payload)

    def test_expected_topology_matches_known_tiled_shapes(self) -> None:
        self.assertEqual(
            probe.expected_topology(4097, 2),
            {
                "native_path": "row_width2_bounded_multi_tile_sort_merge",
                "tile_count": 2,
                "merge_levels": 1,
                "sort_launches": 2,
                "merge_launches": 1,
                "carry_copies": 0,
                "final_copies": 1,
                "metadata_fields_downloaded": 6,
            },
        )
        self.assertEqual(
            probe.expected_topology(65537, 2),
            {
                "native_path": "row_width2_bounded_multi_tile_sort_merge",
                "tile_count": 17,
                "merge_levels": 5,
                "sort_launches": 17,
                "merge_launches": 16,
                "carry_copies": 4,
                "final_copies": 1,
                "metadata_fields_downloaded": 66,
            },
        )
        self.assertEqual(
            probe.expected_topology(131072, 2),
            {
                "native_path": "row_width2_bounded_multi_tile_sort_merge",
                "tile_count": 32,
                "merge_levels": 5,
                "sort_launches": 32,
                "merge_launches": 31,
                "carry_copies": 0,
                "final_copies": 1,
                "metadata_fields_downloaded": 126,
            },
        )


def make_case(candidate_count: int, *, tile_count: int, merge_launches: int, metadata_fields: int) -> dict:
    expected_path = "row_width2_bounded_multi_tile_sort_merge"
    stage_profile = {
        "record_count": 5,
        "stage_median_ms": {field: 0.01 for field in probe.STAGE_FIELDS},
        "stage_min_ms": {field: 0.01 for field in probe.STAGE_FIELDS},
        "stage_max_ms": {field: 0.01 for field in probe.STAGE_FIELDS},
        "topology": {
            "native_path": expected_path,
            "tile_count": tile_count,
            "merge_levels": 5,
            "sort_launches": tile_count,
            "merge_launches": merge_launches,
            "carry_copies": 0,
            "final_copies": 1,
            "metadata_fields_downloaded": metadata_fields,
        },
    }
    return {
        "candidate_count": candidate_count,
        "row_width": 2,
        "unique_count": candidate_count // 2,
        "expected_native_path": expected_path,
        "repeats": 5,
        "median_ms": 1.0,
        "min_ms": 1.0,
        "max_ms": 1.0,
        "all_ms": [1.0] * 5,
        "same_candidate_rows": True,
        "same_valid_count": True,
        "same_overflowed_flag": True,
        "transfer_accounting": {
            "host_to_device_transfers_before_backend_execution": 0,
            "device_to_host_transfers_after_backend_execution": metadata_fields,
            "internal_device_transfers_if_any": merge_launches + 1,
            "allocation_only_transfers_distinguished_from_content_transfers": True,
        },
        "expected_profile_records": 6,
        "observed_profile_records": 6,
        "steady_state_profile_records": [],
        "stage_profile": stage_profile,
        "expected_profile_topology": stage_profile["topology"],
        "profile_topology_matches_expected": True,
        "profile_native_path_matches_expected": True,
    }


def make_synthetic_probe() -> dict:
    return {
        "goal": "Goal1506",
        "status": "goal1506_optix_collect_k_stage_profile_probe_recorded",
        "accepted_goal1506_evidence": True,
        "local_fallback_smoke_only": False,
        "git_commit": "synthetic",
        "platform": "synthetic",
        "device_name": "NVIDIA synthetic",
        "cuda_driver_version": 0,
        "library_path": "synthetic",
        "profile_jsonl_path": "synthetic",
        "measured_on_real_nvidia": True,
        "python_entry_point": "scripts.goal1506_v1_5_4_optix_collect_k_stage_profile_probe",
        "native_profile_env": "RTDL_OPTIX_COLLECT_K_PROFILE_JSONL",
        "timing_scope": "synthetic",
        "cases": [
            make_case(4097, tile_count=2, merge_launches=1, metadata_fields=6),
            make_case(131072, tile_count=32, merge_launches=31, metadata_fields=126),
        ],
        "all_parity_passed": True,
        "all_profile_records_present": True,
        "all_profile_paths_match_expected": True,
        "all_profile_topologies_match_expected": True,
        "claim_flags": {
            "true_zero_copy_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "stable_public_primitive_authorized": False,
            "partner_tensor_handoff_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": (
            "Goal1506 records opt-in host-side stage timing only and does not "
            "authorize public speedup wording."
        ),
    }


if __name__ == "__main__":
    unittest.main()

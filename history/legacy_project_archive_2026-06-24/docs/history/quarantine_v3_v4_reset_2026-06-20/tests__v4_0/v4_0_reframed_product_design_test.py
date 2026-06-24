from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts import run_test_matrix
from scripts.v4_0_current_front_door_claim_boundary_scan import scan as scan_v4_front_door_claims
from scripts.v4_0_source_tree_runtime_preflight import build_payload as build_source_tree_runtime_preflight


ROOT = Path(__file__).resolve().parents[1]
REFRAMING_NOTE = (
    ROOT
    / "docs"
    / "reviews"
    / "v4_reframing_note_rt_core_operator_for_python_gpu_ecosystem_2026-06-19.md"
)
CODEX_RESPONSE = (
    ROOT / "docs" / "reviews" / "codex_v4_reframing_ingestion_response_2026-06-19.md"
)
ROUTE_CONSENSUS = (
    ROOT / "docs" / "reviews" / "codex_v4_m1_route_consensus_2026-06-19.md"
)
DESIGN = ROOT / "docs" / "engineering" / "rtdl_v4_0_design_review_packet_2026-06-19.md"
ACTIVE_ABI_NOTE = ROOT / "docs" / "engineering" / "rtdl_v4_0_active_abi_slice_2026-06-19.md"
M1_STATUS = ROOT / "docs" / "engineering" / "rtdl_v4_0_m1_experimental_status_2026-06-19.md"
M8_PACKET = ROOT / "docs" / "engineering" / "rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md"
PRE_M8_BOUNDARY = ROOT / "docs" / "engineering" / "rtdl_v4_0_pre_m8_boundary_2026-06-19.md"
SOURCE_TREE_RUNTIME_STORY = (
    ROOT / "docs" / "engineering" / "rtdl_v4_0_source_tree_runtime_story_2026-06-19.md"
)
NEXT_STEP_CONSENSUS = (
    ROOT / "docs" / "reviews" / "codex_v4_next_step_pre_m8_dlpack_3ai_consensus_2026-06-19.md"
)
M8_NEXT_STEP_CONSENSUS = (
    ROOT / "docs" / "reviews" / "codex_v4_after_runtime_preflight_m8_next_step_2ai_consensus_2026-06-19.md"
)
M8_INTERNAL_REVIEW = ROOT / "docs" / "reviews" / "codex_v4_m8_internal_2ai_critical_review_2026-06-19.md"
PACKAGE_RUNTIME_TIEBREAKER = (
    ROOT / "docs" / "reviews" / "codex_v4_package_runtime_tiebreaker_2026-06-19.md"
)
AFTER_EDITABLE_INSTALL_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_v4_after_editable_install_m8_external_review_consensus_2026-06-19.md"
)
RC_BLOCKERS = (
    ROOT / "docs" / "engineering" / "rtdl_v4_0_release_candidate_blockers_2026-06-19.json"
)
CLAIM_SCAN_REPORT = (
    ROOT / "docs" / "reports" / "v4_0_current_front_door_claim_boundary_scan_2026-06-19.json"
)
SOURCE_TREE_RUNTIME_PREFLIGHT_REPORT = (
    ROOT / "docs" / "reports" / "v4_0_source_tree_runtime_preflight_2026-06-19.json"
)
EDITABLE_INSTALL_REPORT = (
    ROOT / "docs" / "reports" / "v4_0_editable_install_runtime_probe_2026-06-19.json"
)
FINAL_VALIDATION_REPORT = (
    ROOT / "docs" / "reports" / "v4_0_m8_final_validation_bundle_2026-06-19.json"
)
ACTIVE_README = ROOT / "src" / "v4" / "README.md"
V4_OPERATOR = ROOT / "src" / "rtdsl" / "v4_0_device_array_operator.py"
RELEASE_POSITIONING = (
    ROOT / "docs" / "reviews" / "codex_v4_m1_release_positioning_2ai_consensus_2026-06-19.md"
)
BENCHMARK_REPORT = ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_cupy_benchmark_probe_2026-06-19.json"
NO_HOST_STAGE_REPORT = ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_cupy_no_host_stage_probe_2026-06-19.json"
FRONT_PAGE = ROOT / "README.md"
DOCS_INDEX = ROOT / "docs" / "README.md"
RELEASE_REPORTS_INDEX = ROOT / "docs" / "release_reports" / "README.md"
VERSION = ROOT / "VERSION"
PYPROJECT = ROOT / "pyproject.toml"


def _compact(text: str) -> str:
    return " ".join(text.split())


class V40ReframedProductDesignTest(unittest.TestCase):
    def test_reframing_note_carries_missing_rt_core_lane_pitch(self) -> None:
        note = REFRAMING_NOTE.read_text(encoding="utf-8")

        for token in (
            "The pitch: the missing RT-core lane",
            "CUDA cores",
            "Tensor cores",
            "RT cores",
            "RTDL is the missing RT-core lane for the Python GPU ecosystem",
            "Python actors only",
            "full public multi-language C ABI and SDK packaging are V4.x",
            "Phase 1",
            "Python device-array RT-core operator",
        ):
            self.assertIn(token, note)

    def test_design_packet_leads_with_python_gpu_product_not_c_abi_product(self) -> None:
        design = DESIGN.read_text(encoding="utf-8")
        compact = _compact(design)

        for token in (
            "Product Pitch: The Missing RT-Core Lane",
            "positions RTDL as the missing RT-core lane for the Python GPU ecosystem",
            "V4.0 is Python actors only",
            "CuPy, Numba, Triton, PyTorch",
            "There is no C++ host in current V4.0 scope",
            "The C ABI remains real, but it is the basement under that Python product",
            "Phase 1: Python Device-Array RT-Core Operator",
            "Phase 2: C ABI Substrate Hardening",
            "Phase 3: Non-Python Hosts And SDK Packaging",
            "Under the current Python-only V4.0 scope decision, this phase is V4.x",
            "M2: Python Device-Array Intake",
            "M3: First Python RT-Core Operator Route",
            "fixed_radius_count_threshold_2d",
            "fixed-size `query_ids`, `neighbor_counts`, and `threshold_flags`",
            "M4: Zero-Copy Evidence Packet",
            "M5: C ABI Substrate Hardening",
            "Non-Python Host V4.x Path",
        ):
            self.assertIn(token, compact)

        for stale in (
            "Phase 1: CPU Host Route",
            "Phase 4: CUDA Device-Buffer Route",
            "M2: C ABI 0.2 Control Plane",
            "M3: First Real Query Route",
            "Scope decision made: non-Python hosts are either V4.0 goals or V4.x goals",
            "Are non-Python hosts (C++/Rust/PyTorch-C++) V4.0 goals",
        ):
            self.assertNotIn(stale, compact)

    def test_scope_decision_moves_public_non_python_sdk_to_v4_x(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (DESIGN, ACTIVE_ABI_NOTE, CODEX_RESPONSE)
        )

        for token in (
            "V4.0 is Python actors only",
            "non-Python hosts are V4.x",
            "public multi-language C ABI",
            "generated C/C++/Rust",
            "pkg-config/CMake",
        ):
            self.assertIn(token, combined)

        self.assertIn(
            "full public multi-language C ABI packaging is V4.x",
            CODEX_RESPONSE.read_text(encoding="utf-8"),
        )

    def test_m1_route_consensus_freezes_fixed_radius_count_threshold(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (DESIGN, ROUTE_CONSENSUS, ACTIVE_ABI_NOTE, ACTIVE_README, V4_OPERATOR)
        )
        compact = _compact(combined)

        for token in (
            "fixed_radius_count_threshold_2d",
            "not variable-length neighbor rows",
            "caller-owned CUDA point columns",
            "query_ids",
            "neighbor_counts",
            "threshold_flags",
            "propagate through fixed-radius prepare and query",
            "caller_stream_supported_synchronous",
            "Ray/triangle any-hit is not rejected",
            "V4_0_M1_ROUTE_ID",
            "run_v4_fixed_radius_count_threshold_2d",
        ):
            self.assertIn(token, compact)

        self.assertNotIn("First product route: Fixed-radius neighbors, ray/triangle any-hit", compact)

    def test_active_v4_abi_slice_is_substrate_not_product_headline(self) -> None:
        active_note = ACTIVE_ABI_NOTE.read_text(encoding="utf-8")
        readme = ACTIVE_README.read_text(encoding="utf-8")

        for text in (active_note, readme):
            compact = _compact(text)
            self.assertIn("Phase 2 substrate", compact)
            self.assertIn("not the Phase 1 V4.0 product proof", compact)

        self.assertIn("not the V4.0 product headline", active_note)
        self.assertIn("not the V4.0 headline", _compact(readme))

    def test_m1_status_packet_records_experimental_not_current_release_position(self) -> None:
        status = M1_STATUS.read_text(encoding="utf-8")
        consensus = RELEASE_POSITIONING.read_text(encoding="utf-8")
        engineering_index = (ROOT / "docs" / "engineering" / "README.md").read_text(encoding="utf-8")

        for token in (
            "superseded pre-release engineering evidence",
            "V4.0.0 is now the current source-tree release",
            "Latest validated source-tree head:",
            "Clean cross-stream prepare/query event-wait evidence commit:",
            "`48ce1f9725613f746cea9ba0de438ae0ee830ca3`",
            "fixed_radius_count_threshold_2d",
            "Zero-copy device-column handoff with no observed host staging of named columns",
            "Same-stream producer -> RTDL prepare/query -> consumer ordering is validated",
            "Numba `DeviceNDArray` via CUDA Array Interface",
            "DLPack bridge wrapper smoke",
            "DLPack capsule probe",
            "V4.0 is the current release",
            "blocked",
            "Release-candidate blocker manifest",
            "v4_release_candidate",
            "Source-tree runtime story",
        ):
            self.assertIn(token, status)

        self.assertIn("Do not promote V4.0", consensus)
        self.assertIn("Keep `v3.0.2` as the current source-tree release", consensus)
        self.assertIn("RTDL V4.0 M1 Experimental Status", engineering_index)
        self.assertIn("RTDL V4.0 M8 Release-Candidate Evidence Packet", engineering_index)
        self.assertIn("RTDL V4.0 Release-Candidate Blockers", engineering_index)
        self.assertIn("RTDL V4.0 Pre-M8 Boundary", engineering_index)
        self.assertIn("RTDL V4.0 Source-Tree Runtime Story", engineering_index)
        self.assertIn("RTDL V4.0 M8 Internal 2-AI Critical Review", engineering_index)
        self.assertIn("RTDL V4.0 After Runtime Preflight M8 Consensus", engineering_index)

    def test_source_tree_runtime_preflight_authorizes_only_checkout_runtime(self) -> None:
        payload = build_source_tree_runtime_preflight()
        self.assertTrue(payload["ok"])
        self.assertEqual("pass", payload["status"])

        self.assertTrue(payload["pyproject"]["source_tree_identity_ok"])
        self.assertEqual("rtdl-source-tree", payload["pyproject"]["name"])
        self.assertEqual("4.0.0", payload["pyproject"]["version"])
        self.assertFalse(payload["pyproject"]["v4_distribution_artifact"])

        self.assertTrue(payload["source_tree_import_smoke"]["ok"])
        self.assertTrue(payload["source_tree_import_smoke"]["from_checkout_src"])
        self.assertTrue(payload["source_tree_doctor"]["ok"])

        check_names = {item["name"] for item in payload["source_tree_doctor"]["checks"]}
        self.assertIn("optional module torch", check_names)
        self.assertTrue(payload["test_matrix_policy"]["v4_active_group_present"])
        self.assertTrue(payload["test_matrix_policy"]["v4_release_candidate_group_present"])
        self.assertTrue(payload["test_matrix_policy"]["v4_current_group_present"])
        self.assertTrue(payload["test_matrix_policy"]["v4_release_candidate_gate_non_authorizing"])
        self.assertIn(
            "PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v4_release_candidate",
            payload["supported_source_tree_commands"],
        )
        self.assertIn(
            "PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v4_current",
            payload["supported_source_tree_commands"],
        )

        for item in payload["required_paths"]:
            self.assertTrue(item["exists"], item["path"])

        self.assertTrue(payload["claim_boundaries"]["source_tree_runtime_wording_authorized"])
        for key in (
            "v4_package_install_authorized",
            "pypi_authorized",
            "wheel_authorized",
            "stable_sdk_authorized",
            "generated_bindings_authorized",
        ):
            self.assertFalse(payload["claim_boundaries"][key], key)
        self.assertTrue(payload["claim_boundaries"]["v4_current_front_door_authorized"])

    def test_source_tree_runtime_preflight_report_is_tracked_as_m1_evidence(self) -> None:
        self.assertTrue(SOURCE_TREE_RUNTIME_PREFLIGHT_REPORT.exists())
        report = json.loads(SOURCE_TREE_RUNTIME_PREFLIGHT_REPORT.read_text(encoding="utf-8"))

        self.assertEqual("v4_0_source_tree_runtime_preflight_2026-06-19", report["report_id"])
        self.assertEqual("pass", report["status"])
        self.assertTrue(report["ok"])
        self.assertTrue(report["git"]["head"])
        self.assertTrue(report["pyproject"]["source_tree_identity_ok"])
        self.assertTrue(report["test_matrix_policy"]["v4_active_group_present"])
        self.assertTrue(report["test_matrix_policy"]["v4_release_candidate_group_present"])
        self.assertTrue(report["test_matrix_policy"].get("v4_current_group_present", True))
        self.assertTrue(report["test_matrix_policy"]["v4_release_candidate_gate_non_authorizing"])
        self.assertIn(
            "PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v4_release_candidate",
            report["supported_source_tree_commands"],
        )
        if report["platform"]["system"] == "Linux":
            self.assertTrue(report["v4_m1_gpu_runtime"]["all_required_for_v4_m1_gpu_runtime_present"])
        else:
            self.assertFalse(report["v4_m1_gpu_runtime"]["all_required_for_v4_m1_gpu_runtime_present"])
        self.assertTrue(report["claim_boundaries"]["source_tree_runtime_wording_authorized"])
        self.assertFalse(report["claim_boundaries"]["v4_package_install_authorized"])
        self.assertFalse(report["claim_boundaries"]["pypi_authorized"])
        self.assertFalse(report["claim_boundaries"]["wheel_authorized"])
        self.assertFalse(report["claim_boundaries"]["stable_sdk_authorized"])

    def test_pre_m8_boundary_keeps_release_candidate_aura_blocked(self) -> None:
        boundary = PRE_M8_BOUNDARY.read_text(encoding="utf-8")
        compact_boundary = _compact(boundary)
        consensus = NEXT_STEP_CONSENSUS.read_text(encoding="utf-8")

        for token in (
            "superseded pre-M8 boundary stub, not a release approval",
            "pre-promotion",
            "narrow legacy DLPack capsule intake",
            "PyTorch CUDA tensors with a compatibility matrix",
            "Use the M8 packet as the critical-review input",
            "release approval",
            "Not Yet Authorized",
        ):
            self.assertIn(token, compact_boundary)

        for token in (
            "Adopt the narrow hybrid",
            "real `__dlpack__` capsule intake",
            "consume-once and deleter-once tests",
            "PyTorch route evidence",
            "Claims That Stay Blocked",
        ):
            self.assertIn(token, consensus)

        m8_consensus = M8_NEXT_STEP_CONSENSUS.read_text(encoding="utf-8")
        for token in (
            "M8 release-candidate packet",
            "External critical review",
            "Package/runtime story closure",
            "Public contract freeze",
            "does not authorize",
            "full PyTorch",
            "public true-zero-copy",
            "public speedup",
        ):
            self.assertIn(token, m8_consensus)

    def test_m8_release_candidate_packet_is_review_ready_but_non_authorizing(self) -> None:
        packet = M8_PACKET.read_text(encoding="utf-8")
        compact = _compact(packet)

        for token in (
            "superseded release-candidate evidence packet",
            "Implementation evidence baseline: `bbc43984b74dee7d52c059b295c5eaade0813096`",
            "First M8 packet/gate commit: `0273d4cba5e38afee099573b0ac47f2f883c1067`",
            "External review request commit: `eba6f4b6e49152d8da4e545477a1cb125f6bab43`",
            "Post-review action validation commit: `66e6529859a1bac63ce2a72527dc5942e301143d`",
            "Final release-candidate commit: `758111f08b6b2b79f073ec7c3880137df8f08116`",
            "Release-candidate readiness was true",
            "pre-promotion evidence for the V4.0.0 release",
            "OptiX-backed Python GPU operator direction",
            "one CUDA device per route invocation",
            "multi-GPU runtime behavior is not a V4.0 claim",
            "fixed_radius_count_threshold_2d",
            "rtdsl.prepare_v4_fixed_radius_count_threshold_2d",
            "rtdsl.run_v4_fixed_radius_count_threshold_2d",
            "CuPy CUDA arrays",
            "Numba `DeviceNDArray`",
            "legacy DLPack capsules",
            "PyTorch detached contiguous CUDA tensors",
            "same-stream producer -> RTDL -> consumer ordering is validated",
            "native prepare and query calls still synchronize before returning",
            "async/nonblocking completion is not claimed",
            "Source-tree runtime preflight",
            "Front-door claim scan",
            "DLPack capsule probe",
            "PyTorch CUDA tensor probe",
            "M8 next-step consensus",
            "M8 internal critical review",
            "Editable install hygiene probe",
            "Package/runtime tie-breaker",
            "Final validation bundle",
            "Linux validation on `192.168.1.20`",
            "`scripts/run_test_matrix.py --group v4_active`: 73 tests, pass",
            "`scripts/run_test_matrix.py --group v4_release_candidate`: 73 tests, pass as a non-authorizing review gate",
            "`scripts/v4_0_editable_install_runtime_probe.py --system-site-packages --run-v4-smoke`: pass",
            "`venv --without-pip` plus `pip --python`",
            "This M8 packet does not authorize",
            "V4.0 as the current release",
            "package install, PyPI, wheel, or stable SDK wording",
            "public true-zero-copy",
            "public speedup",
            "Full PyTorch/Numba/DLPack surfaces",
            "Review Request",
        ):
            self.assertIn(token, compact)

        for stale in (
            "V4.0 is the current user release",
            "stable SDK is authorized",
            "public true-zero-copy is authorized",
        ):
            self.assertNotIn(stale, compact)

    def test_release_candidate_gate_remains_blocked_until_m8_packet(self) -> None:
        blockers = json.loads(RC_BLOCKERS.read_text(encoding="utf-8"))
        blocking_by_id = {entry["id"]: entry for entry in blockers["blockers"]}
        evidence_by_id = {entry["id"]: entry for entry in blockers["evidence_ready"]}

        self.assertEqual(
            "v4_0_0_current_source_tree_release_published_with_bounded_claims",
            blockers["status"],
        )
        self.assertTrue(blockers["release_candidate_ready"])
        self.assertEqual("v4.0.0", blockers["current_release"])
        self.assertEqual("v3.0.2", blockers["previous_release"])
        self.assertEqual("current_source_tree_python_gpu_operator_release", blockers["v4_position"])
        self.assertEqual("v4_current", blockers["current_gate"])
        self.assertEqual(
            "758111f08b6b2b79f073ec7c3880137df8f08116",
            blockers["latest_validated_implementation_head"],
        )
        self.assertEqual(
            "758111f08b6b2b79f073ec7c3880137df8f08116",
            blockers["latest_validated_package_runtime_hygiene_head"],
        )
        self.assertEqual(
            "758111f08b6b2b79f073ec7c3880137df8f08116",
            blockers["latest_validated_external_review_guard_head"],
        )
        self.assertEqual(
            {
                "implementation_evidence_baseline": "bbc43984b74dee7d52c059b295c5eaade0813096",
                "first_packet_gate_commit": "0273d4cba5e38afee099573b0ac47f2f883c1067",
                "external_review_request_commit": "eba6f4b6e49152d8da4e545477a1cb125f6bab43",
                "post_review_action_validation_commit": "66e6529859a1bac63ce2a72527dc5942e301143d",
                "claude_external_review_record_commit": "e7c3f83b81eba8b78e530850cf92e0321ef49a30",
                "final_release_candidate_commit": "758111f08b6b2b79f073ec7c3880137df8f08116",
                "policy": (
                    "final_release_candidate_commit is assigned after a fresh full validation bundle; "
                    "front-door, package, zero-copy, async, and speedup claims remain separately "
                    "blocked unless explicitly closed."
                ),
            },
            blockers["m8_review_baseline_commits"],
        )
        self.assertEqual(71, blockers["latest_validated_m1_implementation_v4_active_tests"])
        self.assertEqual(
            "48ce1f9725613f746cea9ba0de438ae0ee830ca3",
            blockers["latest_validated_m1_cross_stream_evidence_commit"],
        )
        self.assertEqual(
            53,
            blockers["latest_validated_m1_cross_stream_v4_active_tests"],
        )
        self.assertEqual(85, blockers["current_source_tree_v4_active_tests"])
        self.assertEqual(85, blockers["current_source_tree_v4_release_candidate_tests"])
        self.assertEqual(
            "retained_as_review_gate; current release validation uses v4_current plus the Linux M1 release gate",
            blockers["v4_release_candidate_gate_policy"],
        )
        self.assertIn("v4_release_candidate", run_test_matrix.TEST_GROUPS)
        self.assertIn("v4_current", run_test_matrix.TEST_GROUPS)

        for blocker_id in (
            "public_true_zero_copy",
            "async_completion",
            "public_speedup",
            "rtx_rt_core_speed_evidence",
            "full_pytorch_partner_surface",
            "full_dlpack_capsule_route_evidence",
            "full_numba_partner_surface",
            "package_install_runtime_story",
            "multi_gpu_runtime_evidence",
            "stable_sdk_public_c_abi",
        ):
            self.assertIn(blocker_id, blocking_by_id)
            self.assertIs(blocking_by_id[blocker_id]["closed"], False)
        self.assertTrue(blocking_by_id["front_door_docs_switch"]["closed"])
        self.assertIn("m8_internal_2ai_critical_review", evidence_by_id)
        self.assertEqual(
            "docs/reviews/codex_v4_m8_internal_2ai_critical_review_2026-06-19.md",
            evidence_by_id["m8_internal_2ai_critical_review"]["path"],
        )
        self.assertIn("cuda_array_interface_device_identity_contract", evidence_by_id)
        self.assertIn(
            "Multi-GPU runtime claims remain blocked",
            evidence_by_id["cuda_array_interface_device_identity_contract"]["note"],
        )
        self.assertIn("package_runtime_tiebreaker", evidence_by_id)
        self.assertEqual(
            "docs/reviews/codex_v4_package_runtime_tiebreaker_2026-06-19.md",
            evidence_by_id["package_runtime_tiebreaker"]["path"],
        )
        self.assertIn("editable_install_runtime_probe", evidence_by_id)
        self.assertEqual(
            "docs/reports/v4_0_editable_install_runtime_probe_2026-06-19.json",
            evidence_by_id["editable_install_runtime_probe"]["path"],
        )
        self.assertIn("final_validation_bundle", evidence_by_id)
        self.assertIn("current_head_linux_gpu_m1_release_gate", evidence_by_id)
        self.assertEqual(
            "docs/reports/v4_0_m8_final_validation_bundle_2026-06-19.json",
            evidence_by_id["final_validation_bundle"]["path"],
        )
        self.assertEqual(
            "docs/reports/v4_0_m1_linux_gpu_release_gate_2026-06-19.json",
            evidence_by_id["current_head_linux_gpu_m1_release_gate"]["path"],
        )
        self.assertEqual(
            "scripts/v4_0_m1_linux_gpu_release_gate.py",
            evidence_by_id["current_head_linux_gpu_m1_release_gate"]["runner"],
        )
        self.assertIn("after_editable_install_external_review_consensus", evidence_by_id)
        self.assertEqual(
            "docs/reviews/codex_v4_after_editable_install_m8_external_review_consensus_2026-06-19.md",
            evidence_by_id["after_editable_install_external_review_consensus"]["path"],
        )
        self.assertTrue(blocking_by_id["m8_release_candidate_packet"]["closed"])
        self.assertTrue(blocking_by_id["cross_stream_event_wait"]["closed"])
        self.assertTrue(blocking_by_id["pytorch_route_evidence"]["closed"])
        self.assertTrue(blocking_by_id["claim_boundary_scan"]["closed"])
        self.assertEqual(
            "final_validation_passed_release_candidate_ready_not_front_door",
            blocking_by_id["m8_release_candidate_packet"]["current_preflight"]["status"],
        )
        self.assertEqual(
            "docs/engineering/rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md",
            blocking_by_id["m8_release_candidate_packet"]["current_preflight"]["evidence"],
        )
        self.assertEqual(
            "docs/reports/v4_0_m8_final_validation_bundle_2026-06-19.json",
            blocking_by_id["m8_release_candidate_packet"]["current_preflight"]["final_validation"],
        )
        self.assertIn(
            "experimental source-tree release candidate",
            blocking_by_id["m8_release_candidate_packet"]["current_preflight"]["reason"],
        )
        self.assertEqual(
            "closed_fixed_radius_m1_prepare_ready_event_wait",
            blocking_by_id["cross_stream_event_wait"]["current_preflight"]["status"],
        )
        self.assertEqual(
            "docs/reports/v4_0_m1_fixed_radius_cupy_stream_ordering_probe_2026-06-19.json",
            blocking_by_id["cross_stream_event_wait"]["current_preflight"]["evidence"],
        )
        cross_stream_evidence = "\n".join(
            blocking_by_id["cross_stream_event_wait"]["current_preflight"]["native_source_evidence"]
        )
        self.assertIn("prepare-ready CUDA event", cross_stream_evidence)
        self.assertIn("waits on the prepare-ready event", cross_stream_evidence)
        self.assertIn("synchronizes the query stream", cross_stream_evidence)
        self.assertIn(
            "does not authorize async execution",
            blocking_by_id["cross_stream_event_wait"]["current_preflight"]["reason"],
        )
        self.assertEqual(
            "closed_fixed_radius_m1_pytorch_cuda_tensor_compatibility_matrix",
            blocking_by_id["pytorch_route_evidence"]["current_preflight"]["status"],
        )
        self.assertEqual(
            "docs/reports/v4_0_m1_fixed_radius_pytorch_cuda_tensor_probe_2026-06-19.json",
            blocking_by_id["pytorch_route_evidence"]["current_preflight"]["evidence"],
        )
        self.assertIn(
            "not a full PyTorch partner surface",
            blocking_by_id["pytorch_route_evidence"]["current_preflight"]["reason"],
        )
        self.assertEqual(
            "m1_pytorch_cuda_tensor_compatibility_matrix_ready_but_full_surface_wording_blocked",
            blocking_by_id["full_pytorch_partner_surface"]["current_preflight"]["status"],
        )
        self.assertEqual(
            "docs/reports/v4_0_m1_fixed_radius_pytorch_cuda_tensor_probe_2026-06-19.json",
            blocking_by_id["full_pytorch_partner_surface"]["current_preflight"]["evidence"],
        )
        self.assertIn(
            "arbitrary PyTorch tensor layouts",
            blocking_by_id["full_pytorch_partner_surface"]["current_preflight"]["reason"],
        )
        self.assertEqual(
            "fixed_radius_m1_legacy_dlpack_capsule_route_ready_but_full_framework_neutral_blocked",
            blocking_by_id["full_dlpack_capsule_route_evidence"]["current_preflight"]["status"],
        )
        self.assertEqual(
            "docs/reports/v4_0_m1_fixed_radius_dlpack_capsule_probe_2026-06-19.json",
            blocking_by_id["full_dlpack_capsule_route_evidence"]["current_preflight"]["evidence"],
        )
        self.assertIn(
            "not arbitrary framework-neutral DLPack support",
            blocking_by_id["full_dlpack_capsule_route_evidence"]["current_preflight"]["reason"],
        )
        rtx_preflight = blocking_by_id["rtx_rt_core_speed_evidence"]["current_preflight"]
        self.assertEqual("blocked_rtx_hardware_access_unavailable", rtx_preflight["status"])
        self.assertIn("RT-core or RTX speedup wording", rtx_preflight["reason"])
        attempted_hosts = {entry["host"]: entry for entry in rtx_preflight["attempted_hosts"]}
        self.assertEqual(
            "Permission denied (publickey,password).",
            attempted_hosts["157.157.221.29"]["result"],
        )
        self.assertIn("GTX 1070", attempted_hosts["192.168.1.20"]["result"])
        self.assertEqual(
            "m1_devicearray_route_evidence_ready_but_full_surface_wording_blocked",
            blocking_by_id["full_numba_partner_surface"]["current_preflight"]["status"],
        )
        self.assertEqual(
            "docs/reports/v4_0_m1_fixed_radius_numba_partner_surface_probe_2026-06-19.json",
            blocking_by_id["full_numba_partner_surface"]["current_preflight"]["evidence"],
        )
        self.assertEqual(
            "source_tree_runtime_and_editable_install_hygiene_passed_but_package_flow_blocked",
            blocking_by_id["package_install_runtime_story"]["current_preflight"]["status"],
        )
        self.assertEqual(
            "docs/reports/v4_0_source_tree_runtime_preflight_2026-06-19.json",
            blocking_by_id["package_install_runtime_story"]["current_preflight"]["evidence"],
        )
        self.assertEqual(
            "758111f08b6b2b79f073ec7c3880137df8f08116",
            blocking_by_id["package_install_runtime_story"]["current_preflight"]["validation_commit"],
        )
        self.assertEqual(
            "docs/reports/v4_0_editable_install_runtime_probe_2026-06-19.json",
            blocking_by_id["package_install_runtime_story"]["current_preflight"][
                "editable_install_evidence"
            ],
        )
        self.assertEqual(
            "stdlib_venv_without_pip_targeted_by_system_pip",
            blocking_by_id["package_install_runtime_story"]["current_preflight"][
                "venv_creation_method"
            ],
        )
        self.assertEqual(
            "docs/reviews/codex_v4_package_runtime_tiebreaker_2026-06-19.md",
            blocking_by_id["package_install_runtime_story"]["current_preflight"]["consensus"],
        )
        self.assertIn(
            "not a V4 wheel, PyPI artifact, V4 distribution artifact",
            blocking_by_id["package_install_runtime_story"]["current_preflight"]["reason"],
        )
        self.assertEqual(
            "closed_by_claude_external_review_final_validation_passed",
            blocking_by_id["external_release_candidate_review"]["current_preflight"]["status"],
        )
        self.assertTrue(blocking_by_id["external_release_candidate_review"]["closed"])
        self.assertEqual(
            "docs/reviews/codex_v4_after_editable_install_m8_external_review_consensus_2026-06-19.md",
            blocking_by_id["external_release_candidate_review"]["current_preflight"]["consensus"],
        )
        self.assertEqual(
            "docs/reviews/codex_v4_m8_external_ai_access_attempt_2026-06-19.md",
            blocking_by_id["external_release_candidate_review"]["current_preflight"][
                "access_attempt"
            ],
        )
        self.assertEqual(
            "docs/reviews/claude_v4_0_m8_external_review_2026-06-19.md",
            blocking_by_id["external_release_candidate_review"]["current_preflight"][
                "external_review"
            ],
        )
        self.assertIn(
            "No feature expansion or front-door switch is authorized",
            blocking_by_id["external_release_candidate_review"]["current_preflight"]["reason"],
        )
        self.assertEqual(
            "single_gpu_device_identity_contract_guarded_multi_gpu_runtime_not_claimed",
            blocking_by_id["multi_gpu_runtime_evidence"]["current_preflight"]["status"],
        )
        self.assertIn(
            "fails closed when fixed-radius columns disagree on CUDA device",
            blocking_by_id["multi_gpu_runtime_evidence"]["current_preflight"]["reason"],
        )
        self.assertEqual(
            "docs/reports/v4_0_current_front_door_claim_boundary_scan_2026-06-19.json",
            blocking_by_id["claim_boundary_scan"]["evidence"],
        )

    def test_m8_internal_review_records_required_actions_without_release_approval(self) -> None:
        review = M8_INTERNAL_REVIEW.read_text(encoding="utf-8")
        compact = _compact(review)

        for token in (
            "accepted review input; actions required before release-candidate readiness",
            "accept the M8 packet as a critical-review baseline",
            "reject calling V4.0 release-candidate ready today",
            "`v4_release_candidate` must remain a non-authorizing review gate",
            "final RC decision needs one explicit candidate commit",
            "source-tree-only",
            "CUDA device identity",
            "avoid implying RTX/RT-core speed authority",
            "Refresh the blocker manifest status from pre-M8 to M8-review-baseline",
            "Add device-id preservation/fail-closed tests",
            "V4.0 current-release/front-door promotion",
        ):
            self.assertIn(token, compact)

    def test_v4_source_tree_runtime_story_blocks_package_wording(self) -> None:
        story = SOURCE_TREE_RUNTIME_STORY.read_text(encoding="utf-8")
        compact = _compact(story)

        for token in (
            "source-tree runtime story only",
            "not a V4 distribution artifact",
            "PYTHONPATH=src:.",
            "scripts/v4_0_source_tree_runtime_preflight.py --require-v4-gpu-runtime",
            "docs/reports/v4_0_source_tree_runtime_preflight_2026-06-19.json",
            "docs/reviews/codex_v4_package_runtime_tiebreaker_2026-06-19.md",
            "docs/reports/v4_0_editable_install_runtime_probe_2026-06-19.json",
            "working directory outside the repository",
            "make build-optix",
            "package_install_runtime_story` remains open",
            "Closing it requires a V4 package flow",
            "package install",
            "PyPI",
            "wheel support",
            "stable SDK",
        ):
            self.assertIn(token, compact)

    def test_package_runtime_tiebreaker_keeps_editable_install_narrow(self) -> None:
        tiebreaker = PACKAGE_RUNTIME_TIEBREAKER.read_text(encoding="utf-8")
        compact = _compact(tiebreaker)

        for token in (
            "accepted tie-breaker decision, not release approval",
            "Adopt the narrow middle path",
            "Implement clean editable-install hygiene validation now",
            "Keep `package_install_runtime_story` open",
            "Do not authorize package install, PyPI, wheel, stable SDK",
            "Editable install validation is a source-tree hygiene gate, not package release evidence",
            "working directory outside the repository",
            "PYTHONPATH",
            "rtdl-source-tree",
            "Claims Still Blocked",
        ):
            self.assertIn(token, compact)

        report = json.loads(EDITABLE_INSTALL_REPORT.read_text(encoding="utf-8"))
        self.assertTrue(report["ok"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(
            "e7c3f83b81eba8b78e530850cf92e0321ef49a30",
            report["git"]["head"],
        )
        self.assertTrue(report["system_site_packages"])
        self.assertEqual(
            "stdlib_venv_without_pip_targeted_by_system_pip",
            report["venv_creation_method"],
        )
        self.assertFalse(report["inspection"]["pythonpath_present"])
        self.assertEqual("rtdl-source-tree", report["inspection"]["package"]["distribution_name"])
        self.assertIn(report["inspection"]["package"]["version"], {"3.0.2", "4.0.0"})
        self.assertTrue(report["inspection"]["package"]["module_loaded_from_checkout_editable"])
        self.assertTrue(report["inspection"]["package"]["module_under_repo_src"])
        self.assertIn(report["inspection"]["native_library"]["status"], {"found", "missing"})

        claim_boundaries = report["claim_boundaries"]
        self.assertTrue(claim_boundaries["editable_source_tree_install_hygiene_evidence"])
        for blocked_claim in (
            "generated_binding_package_claim_authorized",
            "package_install_claim_authorized",
            "pypi_claim_authorized",
            "stable_sdk_claim_authorized",
            "v4_distribution_artifact",
            "wheel_claim_authorized",
        ):
            self.assertFalse(claim_boundaries[blocked_claim])
        if report["inspection"]["package"]["version"] == "4.0.0":
            self.assertTrue(claim_boundaries["v4_current_front_door_authorized"])
        else:
            self.assertFalse(claim_boundaries["v4_current_front_door_authorized"])

        if report["platform"]["system"] == "Linux":
            self.assertTrue(report["run_v4_smoke"])
            self.assertEqual("found", report["inspection"]["native_library"]["status"])
            self.assertTrue(report["inspection"]["native_library"]["under_repo_build"])
            self.assertEqual("pass", report["inspection"]["v4_smoke"]["status"])
            self.assertEqual(
                {
                    "query_ids": [1, 2, 3],
                    "neighbor_counts": [1, 1, 0],
                    "threshold_flags": [1, 1, 0],
                },
                report["inspection"]["v4_smoke"]["observed"],
            )
            self.assertTrue(report["inspection"]["v4_smoke"]["caller_stream_handle_nonzero"])
            self.assertTrue(report["inspection"]["v4_smoke"]["native_synchronized_before_return"])
            self.assertFalse(report["inspection"]["v4_smoke"]["public_true_zero_copy_authorized"])
        else:
            self.assertFalse(report["run_v4_smoke"])
            self.assertEqual("not_run", report["inspection"]["v4_smoke"]["status"])

        probe_source = (ROOT / "scripts" / "v4_0_editable_install_runtime_probe.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("blocked_missing_native_library", probe_source)
        self.assertIn('"native_async_claim_authorized": False', probe_source)
        self.assertIn('"async_claim_authorized": False', probe_source)

    def test_final_validation_bundle_assigns_experimental_release_candidate(self) -> None:
        report = json.loads(FINAL_VALIDATION_REPORT.read_text(encoding="utf-8"))
        commands = {entry["name"]: entry for entry in report["commands"]}

        self.assertEqual("v4_0_m8_final_validation_bundle_2026-06-19", report["report_id"])
        self.assertEqual("pass", report["status"])
        self.assertTrue(report["ok"])
        self.assertEqual("192.168.1.20", report["host"])
        self.assertEqual(
            "758111f08b6b2b79f073ec7c3880137df8f08116",
            report["validated_commit"],
        )
        for command_name in (
            "build_optix",
            "source_tree_runtime_preflight",
            "editable_install_runtime_probe",
            "v4_active",
            "v4_release_candidate",
            "claim_boundary_scan",
            "git_diff_check",
            "clean_worktree",
        ):
            self.assertEqual("pass", commands[command_name]["status"], command_name)
        self.assertEqual(73, commands["v4_active"]["tests"])
        self.assertEqual(73, commands["v4_release_candidate"]["tests"])
        self.assertTrue(report["release_decision"]["release_candidate_ready"])
        self.assertEqual("v3.0.2", report["release_decision"]["current_user_release_remains"])
        self.assertFalse(report["release_decision"]["front_door_switch_authorized"])
        for key, value in report["claim_boundaries"].items():
            self.assertFalse(value, key)

    def test_after_editable_install_consensus_requires_external_review_next(self) -> None:
        consensus = AFTER_EDITABLE_INSTALL_CONSENSUS.read_text(encoding="utf-8")
        compact = _compact(consensus)

        for token in (
            "accepted 2-AI next-step consensus, not release approval",
            "release_candidate_ready` remains false",
            "external M8 critical review, not more implementation",
            "accept baseline, accept with blockers, or reject",
            "Do not pursue these before the external review verdict",
            "another route",
            "public true-zero-copy wording",
            "PyPI, wheel, stable SDK, or generated bindings",
            "front-door docs switch",
            "keep `release_candidate_ready` false",
        ):
            self.assertIn(token, compact)

    def test_current_front_door_claim_scan_closes_only_scan_blocker(self) -> None:
        payload = scan_v4_front_door_claims(ROOT)
        report = json.loads(CLAIM_SCAN_REPORT.read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertFalse(payload["findings"])
        self.assertEqual("pass", report["status"])
        self.assertFalse(report["findings"])
        self.assertGreater(len(report["accepted_negative_occurrences"]), 0)
        self.assertEqual("v4.0.0", report["front_door"]["current_version"])
        self.assertTrue(report["front_door"]["v4_0_0_release_package_exists"])
        self.assertIn("README.md", report["public_files_scanned"])
        self.assertIn("src/v4/README.md", report["public_files_scanned"])
        self.assertIn(
            "docs/engineering/rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md",
            report["public_files_scanned"],
        )
        self.assertIn(
            "docs/reviews/claude_v4_0_m8_external_review_2026-06-19.md",
            report["public_files_scanned"],
        )
        self.assertIn("tutorials/v4_0/README.md", report["public_files_scanned"])
        self.assertIn("examples/v4_0/getting_started/README.md", report["public_files_scanned"])
        self.assertTrue(
            any(
                occurrence["phrase"].lower() == "zero-copy"
                for occurrence in report["accepted_negative_occurrences"]
            )
        )
        self.assertTrue(report["claim_boundaries"]["v4_current_release_claim_authorized"])
        self.assertTrue(report["claim_boundaries"]["v4_release_package_claim_authorized"])
        self.assertTrue(report["claim_boundaries"]["fixed_radius_m1_python_gpu_operator_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["stable_v4_sdk_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["public_true_zero_copy_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["pytorch_route_claim_authorized"])

    def test_release_front_door_is_v4_while_m1_claim_flags_stay_bounded(self) -> None:
        benchmark = json.loads(BENCHMARK_REPORT.read_text(encoding="utf-8"))
        no_host_stage = json.loads(NO_HOST_STAGE_REPORT.read_text(encoding="utf-8"))

        blocked_flags = (
            benchmark["claim_boundaries"]["public_speedup_claim_authorized"],
            benchmark["claim_boundaries"]["rt_core_speedup_claim_authorized"],
            benchmark["claim_boundaries"]["v4_true_zero_copy_claim_authorized"],
            benchmark["claim_boundaries"]["async_claim_authorized"],
            no_host_stage["claim_boundaries"]["public_speedup_claim_authorized"],
            no_host_stage["claim_boundaries"]["rt_core_speedup_claim_authorized"],
            no_host_stage["claim_boundaries"]["v4_true_zero_copy_claim_authorized"],
            no_host_stage["claim_boundaries"]["async_claim_authorized"],
        )
        self.assertEqual((False,) * len(blocked_flags), blocked_flags)

        front_page = FRONT_PAGE.read_text(encoding="utf-8")
        docs_index = DOCS_INDEX.read_text(encoding="utf-8")
        release_reports = RELEASE_REPORTS_INDEX.read_text(encoding="utf-8")
        pyproject = PYPROJECT.read_text(encoding="utf-8")

        self.assertEqual("v4.0.0", VERSION.read_text(encoding="utf-8").strip())
        self.assertIn('version = "4.0.0"', pyproject)
        self.assertIn("current V4.0.0 source-tree RTDL surface", front_page)
        self.assertIn("RTDL V4.0.0 is the active source-tree", docs_index)
        self.assertIn("RTDL V4.0.0 Release Package", release_reports)
        self.assertTrue((ROOT / "docs" / "release_reports" / "v4_0_0").exists())

    def test_v4_active_matrix_includes_design_reframing_gate(self) -> None:
        modules = run_test_matrix.group_modules("v4_active")
        self.assertIn("tests.v4_0_active_abi_control_plane_test", modules)
        self.assertIn("tests.v4_0_reframed_product_design_test", modules)
        self.assertIn("tests.v4_0_m1_linux_gpu_release_gate_test", modules)
        release_modules = run_test_matrix.group_modules("v4_release_candidate")
        self.assertEqual(modules, release_modules)
        self.assertEqual(modules, run_test_matrix.group_modules("v4_current"))
        self.assertIn("tests.v4_0_m1_fixed_radius_route_test", modules)
        self.assertIn("tests.v4_0_user_tutorials_test", modules)


if __name__ == "__main__":
    unittest.main()

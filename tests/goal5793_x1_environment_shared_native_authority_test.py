from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tarfile
import unittest

from scripts import goal5793_x1_build_environment_shared_native_authority as builder
from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]
SUPERSEDED_V2 = (
    ROOT
    / "history/internal_docs/goal5793_x1_environment_shared_native_authority_v2_20260822.json"
)
SUPERSEDED_V1 = (
    ROOT
    / "history/internal_docs/goal5793_x1_environment_shared_native_authority_20260822.json"
)
BUILDER = ROOT / "scripts/goal5793_x1_build_environment_shared_native_authority.py"


class EnvironmentSharedNativeAuthorityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.actual = builder.build_authority()
        cls.rebuilt = builder.build_authority()

    def test_dry_build_is_deterministic_and_seal_rederives(self) -> None:
        self.assertEqual(
            canonical_json_bytes(self.actual), canonical_json_bytes(self.rebuilt)
        )
        self.assertEqual(
            self.actual["authority_sha256"],
            seal_document(
                self.actual,
                seal_field="authority_sha256",
                domain="rtdl.goal5793.x1.environment_shared_native_authority",
                version=4,
            ),
        )

    def test_every_frozen_file_rehashes(self) -> None:
        for record in self.actual["frozen_files"].values():
            path = ROOT / record["path"]
            self.assertEqual(path.stat().st_size, record["bytes"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["sha256"])

    def test_incomplete_environment_blocks_execution_without_hidden_activity(self) -> None:
        self.assertEqual(
            self.actual["status"],
            "BLOCKS_EXAM_EXECUTION__EXACT_ENVIRONMENT_INCOMPLETE",
        )
        self.assertEqual(len(self.actual["missing_required_exact_identities"]), 11)
        self.assertFalse(self.actual["scope"]["authorizes_exam_execution"])
        self.assertFalse(self.actual["claim_boundary"]["exact_environment_ready"])
        self.assertFalse(self.actual["claim_boundary"]["shared_native_execution_ready"])
        self.assertFalse(self.actual["claim_boundary"]["candidate_specific_native_allowed"])
        for field in (
            "gpu_probe_count",
            "native_build_count",
            "network_call_count",
            "candidate_execution_count",
            "registered_timing_count",
        ):
            self.assertEqual(self.actual["scope"][field], 0)

    def test_real_native_is_one_shared_frozen_byte_identity_but_not_ready(self) -> None:
        shared = self.actual["shared_native"]
        self.assertEqual(
            shared["sha256"],
            "713d33734cdd6b1ad9be7852fc4af18e4ed138ae1080f1fd15638ef1b874dfe1",
        )
        self.assertEqual(
            shared["policy"],
            "ONE_EXACT_NATIVE_FOR_ALL_EXAMS__NO_CANDIDATE_SPECIFIC_BUILD",
        )
        self.assertEqual(
            shared["build_id_policy"],
            "TIME_DERIVED_EXISTING_ID__INELIGIBLE_FOR_X1_EXECUTION",
        )
        self.assertIn(
            "non-time-derived embedded native build identity",
            self.actual["missing_required_exact_identities"],
        )

    def test_ready_counterfeit_does_not_validate_under_frozen_seal(self) -> None:
        forged = deepcopy(self.actual)
        forged["status"] = "READY"
        forged["claim_boundary"]["exact_environment_ready"] = True
        forged["claim_boundary"]["shared_native_execution_ready"] = True
        self.assertNotEqual(
            forged["authority_sha256"],
            seal_document(
                forged,
                seal_field="authority_sha256",
                domain="rtdl.goal5793.x1.environment_shared_native_authority",
                version=4,
            ),
        )

    def test_v1_v2_are_preserved_and_unwritten_v3_is_noncontrolling(self) -> None:
        v1 = json.loads(SUPERSEDED_V1.read_text(encoding="utf-8"))
        v2 = json.loads(SUPERSEDED_V2.read_text(encoding="utf-8"))
        self.assertFalse(v1["scope"]["ambient_library_search_used"])
        self.assertEqual(
            hashlib.sha256(SUPERSEDED_V2.read_bytes()).hexdigest(),
            self.actual["supersedes"]["file_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(SUPERSEDED_V1.read_bytes()).hexdigest(),
            v2["supersedes"]["file_sha256"],
        )
        self.assertFalse(self.actual["supersedes"]["controlling"])
        resolution = self.actual["dynamic_library_resolution"]
        self.assertTrue(resolution["rtdl_native_top_level_path_explicit"])
        self.assertFalse(resolution["ambient_search_absence_claimed"])
        self.assertIn("NOT_PROVEN", resolution["nvrtc"])
        self.assertEqual(
            resolution["native_transitive_dependencies"]["status"],
            "AMBIENT_RESOLUTION_PRESENT__BLOCKING",
        )
        self.assertFalse(self.actual["unwritten_dry_predecessor"]["formal_history_file_created"])
        self.assertFalse(self.actual["unwritten_dry_predecessor"]["controlling"])

    def test_inspection_is_archive_member_bound_and_callback_abi_not_optix_abi(self) -> None:
        archive = (
            ROOT
            / "history/internal_docs/goal5791_stage_a_v15_rtx4000ada_20260821/"
            "TARGET_MATERIALIZATION_EVIDENCE.tar.gz"
        )
        external = (
            ROOT
            / "history/internal_docs/goal5791_stage_a_v15_rtx4000ada_20260821/"
            "TARGET_PROGRAM_INSPECTION.json"
        ).read_bytes()
        with tarfile.open(archive, "r:gz") as handle:
            member = handle.extractfile("TARGET_PROGRAM_INSPECTION.json")
            self.assertIsNotNone(member)
            archived = member.read()
        self.assertEqual(external, archived)
        self.assertEqual(len(archived), 5060)
        self.assertEqual(
            hashlib.sha256(archived).hexdigest(),
            "c2ba693c9dab69806b5f8f8182833ea92148eeaebc66e570bc960d56748690a0",
        )
        self.assertEqual(self.actual["optix"]["sdk_abi_exact_authority"]["value"], 105)
        self.assertEqual(
            self.actual["compiled_program"]["callback_abi_sha256"],
            "eb7dc1311987aebada95363630d9f81422f590550a7974e3f3ad261201307036",
        )
        self.assertNotIn("abi_sha256", self.actual["optix"])

    def test_optix_header_archive_reconstructs_exact_sdk_abi(self) -> None:
        optix = self.actual["optix"]
        self.assertEqual(optix["header_archive"]["bytes"], 95765)
        self.assertEqual(
            optix["header_archive"]["sha256"],
            "7fae86ce3dca2fbc2a47be075f02465cf6ee9d9eafd204234f2882fbdeebee54",
        )
        self.assertEqual(optix["header_tree"]["regular_file_count"], 14)
        self.assertEqual(len(optix["header_tree"]["rows"]), 14)
        self.assertEqual(optix["optix_version_macro"], 90000)
        self.assertEqual(optix["sdk_abi_exact_authority"]["value"], 105)
        self.assertTrue(self.actual["claim_boundary"]["optix_header_tree_and_sdk_abi_recovered"])

    def test_linker_and_runtime_boundaries_are_partial_not_upgraded(self) -> None:
        linker = self.actual["host_toolchain"]["linker"]
        self.assertEqual(linker["path"], "/usr/bin/ld")
        self.assertEqual(
            linker["declared_target_sha256"],
            "5b674ea1d7017c2929f3c52c43487478bb240ecdd7197a25cce3813a70329a5c",
        )
        self.assertEqual(linker["exact_argv"][0], "/usr/bin/ld")
        self.assertFalse(linker["bytes_preserved_for_independent_rehash"])
        self.assertFalse(linker["version_preserved"])
        self.assertEqual(linker["status"], "PARTIAL__BLOCKING")
        for name in ("libcuda", "libstdcxx", "glibc"):
            self.assertIn("BLOCKING", self.actual["runtime_libraries"][name]["status"])

    def test_preserved_elf_proves_ambient_resolution_structure(self) -> None:
        elf = self.actual["shared_native"]["elf_dynamic_identity_recomputed_from_preserved_bytes"]
        self.assertEqual(
            elf["gnu_build_id"],
            "d3c7850f6d77f7021fdd47187da7aa906e073bcf",
        )
        self.assertEqual(
            elf["dt_needed"],
            [
                "libcuda.so.1",
                "libnvrtc.so.12",
                "libstdc++.so.6",
                "libm.so.6",
                "libgcc_s.so.1",
                "libc.so.6",
                "ld-linux-x86-64.so.2",
            ],
        )
        self.assertEqual(elf["rpath"], [])
        self.assertEqual(elf["runpath"], [])
        resolution = self.actual["dynamic_library_resolution"]["native_transitive_dependencies"]
        self.assertTrue(resolution["ambient_or_default_loader_resolution_structurally_used"])
        self.assertFalse(resolution["exact_dependency_bytes_complete"])
        self.assertTrue(self.actual["claim_boundary"]["ambient_resolution_was_used"])

    def test_geos_not_used_proof_is_narrow_and_does_not_cover_candidates(self) -> None:
        geos = self.actual["runtime_libraries"]["geos"]
        self.assertGreater(geos["native_header_probe_count"], 0)
        self.assertEqual(geos["successful_header_open_count"], 0)
        self.assertEqual(geos["successful_ptx_libgeos_open_count"], 0)
        self.assertFalse(geos["successful_link_argv_contains_lgeos_c"])
        self.assertFalse(geos["future_candidate_or_oracle_use_ruled_out"])
        self.assertTrue(
            self.actual["claim_boundary"]["geos_not_used_claim_is_shared_native_producer_only"]
        )

    def test_execution_and_base_source_identities_are_not_conflated(self) -> None:
        source = self.actual["source"]
        self.assertEqual(source["execution"]["source_file_count_excluding_manifest"], 952)
        self.assertEqual(
            source["execution"]["source_manifest_file_sha256"],
            "bf7f77d97f005c3ea283e0d8a185635508fb71c317d2d1382ee2bb92d999c10c",
        )
        self.assertEqual(source["base"]["source_file_count_excluding_manifest"], 729)
        self.assertEqual(
            source["base"]["source_manifest_sha256"],
            "d538a1ddaa79768feb9c8845077c069e444151d5aa76a59f50bd55922933b9c5",
        )

    def test_trace_mechanically_yields_exact_argv_and_time_build_id(self) -> None:
        argv = self.actual["cuda"]["top_level_build_argv_authority"]["exact_argv"]
        self.assertEqual(argv[0], "/usr/local/cuda-12.8/bin/nvcc")
        self.assertIn("-arch=sm_89", argv)
        self.assertIn(
            '-DRTDL_OPTIX_BUILD_ID="20260821T031637397083302"', argv
        )
        self.assertEqual(
            self.actual["shared_native"]["embedded_build_id_observed_in_frozen_trace"],
            "20260821T031637397083302",
        )

    def test_builder_has_no_probe_build_network_or_subprocess_surface(self) -> None:
        tree = ast.parse(BUILDER.read_text(encoding="utf-8"))
        imported = set()
        called = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called.add(node.func.attr)
        self.assertTrue(
            {"subprocess", "socket", "urllib", "requests", "cupy", "numba"}.isdisjoint(
                imported
            )
        )
        self.assertTrue(
            {"run", "Popen", "check_call", "check_output", "system"}.isdisjoint(called)
        )


if __name__ == "__main__":
    unittest.main()

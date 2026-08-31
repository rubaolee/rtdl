from __future__ import annotations

import ast
from copy import deepcopy
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import tempfile
import tarfile
import types
import unittest
from unittest import mock

from scripts import goal5791_home_clean_validate as home
from scripts import goal5791_independent_home_recount as recount
from scripts import goal5791_independent_portable_audit as portable_audit
from scripts import goal5791_open_upload_staging as staging_helper
from scripts import goal5791_target_prepare as target
from scripts import goal5791_build_owner_authority as owner_builder
from scripts import goal5791_build_portable_source as source_builder
from scripts import goal5791_build_pre_pod_bundle as bundle_builder
from scripts import goal5791_cpu_test_gate as cpu_test_gate
from scripts import goal5791_formal_contract as formal_contract


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_RECORD = {
    "source": staging_helper.FIRST_ENTRY_STDIN_BOOTSTRAP_SOURCE,
    "source_sha256": staging_helper.FIRST_ENTRY_STDIN_BOOTSTRAP_SOURCE_SHA256,
    "actual_source_rehashed_from_proc_cmdline_before_helper_exec": True,
    "honest_owner_exact_ssh_command_is_operational_tcb": True,
}


def _joint_delivery_fixture(*, bundle_sha256: str = "1" * 64) \
        -> dict[str, object]:
    return {
        "joint_bundle_audit_receipt_file_sha256": "3" * 64,
        "joint_bundle_audit_receipt_sha256": "4" * 64,
        "independent_portable_auditor_sha256": (
            target.TRUSTED_INDEPENDENT_PORTABLE_AUDITOR_SHA256),
        "bundle_sha256": bundle_sha256,
        "bundle_twin_sha256": bundle_sha256,
        "bundle_twin_byte_identical": True,
        "home_evidence_sha256": "5" * 64,
        "home_evidence_twin_sha256": "5" * 64,
        "home_evidence_twin_byte_identical": True,
        "strict_joint_audit_passed": True,
        "home_independent_raw_recount_reexecuted_and_byte_identical": True,
    }


def _canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        ) + "\n"
    ).encode("utf-8")


def _manifest_rows(payloads: dict[str, bytes]) -> list[dict[str, object]]:
    return [
        {
            "path": name,
            "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        for name, data in sorted(payloads.items())
    ]


def _first_entry_observation(
    *, helper_sha256: str, helper_size_bytes: int,
    python_sha256: str = "9" * 64,
) -> dict[str, object]:
    return {
        "schema": staging_helper.FIRST_ENTRY_OBSERVATION_SCHEMA,
        "bootstrap_source_sha256": (
            staging_helper.FIRST_ENTRY_STDIN_BOOTSTRAP_SOURCE_SHA256),
        "bootstrap_source_verified_before_helper_exec": True,
        "observed_staging_helper_size_bytes": helper_size_bytes,
        "observed_staging_helper_sha256": helper_sha256,
        "staging_helper_verified_before_exec": True,
        "python_executable_path": "/usr/bin/python3",
        "python_executable_sha256": python_sha256,
        "python_version": "3.12.3",
        "python_identity_verified_before_root_creation": True,
    }


class Goal5791PortableHomeHarnessTest(unittest.TestCase):
    def test_v3_prereg_pretarget_lineage_is_append_only_terminal(self) -> None:
        prereg = ROOT / (
            "history/internal_docs/goal5791_preregistration_v3_20260817.json")
        pretarget = ROOT / (
            "history/internal_docs/"
            "goal5791_pretarget_preexecution_authority_v3_20260817.json")
        authority_path = ROOT / (
            "history/internal_docs/"
            "goal5791_v3_prereg_pretarget_terminal_supersession_authority_"
            "20260817.json")
        self.assertEqual(
            hashlib.sha256(prereg.read_bytes()).hexdigest(),
            "03a031afbcc6c532a666b7fdc6e426a0a1c66b15d2e5c6abf52b8adf3ef65e86",
        )
        self.assertEqual(
            hashlib.sha256(pretarget.read_bytes()).hexdigest(),
            "2ea28b4b4ebdf28d69a99dff29e402188e9b7ec12d9ca5b4553d08c6d37ee4ad",
        )
        authority = json.loads(authority_path.read_text(encoding="utf-8"))
        claimed = authority.pop("authority_sha256")
        self.assertEqual(
            claimed,
            hashlib.sha256(json.dumps(
                authority, sort_keys=True, separators=(",", ":"),
                ensure_ascii=False, allow_nan=False,
            ).encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            authority["status"],
            "TERMINAL_SUPERSEDED__NEVER_EXECUTABLE_OR_CANDIDATE",
        )
        self.assertTrue(all(
            value is False for value in authority["authorization"].values()))
        self.assertEqual(
            authority["execution_facts"]["formal_worker_count_executed"], 0)
        self.assertIn(
            authority_path.relative_to(ROOT).as_posix(),
            source_builder.OVERLAY_PATHS,
        )

    def test_v1_source_build_timeout_is_terminal_zero_output(self) -> None:
        terminal_path = ROOT / (
            "history/internal_docs/"
            "goal5791_portable_source_v1_zero_output_terminal_20260817.json")
        report_path = terminal_path.with_suffix(".md")
        value = json.loads(terminal_path.read_text(encoding="utf-8"))
        unsigned = dict(value)
        claimed = unsigned.pop("terminal_authority_sha256")
        self.assertEqual(claimed, portable_audit._digest(unsigned))
        self.assertEqual(
            value["status"],
            "TERMINAL_ZERO_OUTPUT__CPU_SUITE_TIMEOUT_BEFORE_PUBLICATION",
        )
        self.assertEqual(
            value["failure"]["exception_class"], "subprocess.TimeoutExpired")
        self.assertEqual(
            value["attempt_identity"]["cpu_test_timeout_seconds"], 600)
        self.assertFalse(value["failure"]["claim_111_tests_passed"])
        self.assertTrue(all(
            item is False for item in value["authorization"].values()))
        self.assertTrue(all(
            not record["exists"]
            for record in value["output_facts"].values()))
        self.assertEqual(source_builder.CPU_TEST_TIMEOUT_SECONDS, 1_200)
        self.assertTrue(source_builder.CANONICAL_OUTPUT_PATH.endswith(
            "goal5791_portable_source_v26_20260820.tar.gz"))
        self.assertTrue(source_builder.CANONICAL_TWIN_PATH.endswith(
            "goal5791_portable_source_v26_twin_20260820.tar.gz"))
        self.assertTrue(source_builder.CANONICAL_RECEIPT_PATH.endswith(
            "goal5791_portable_source_v26_build_receipt_20260820.json"))
        for path in (terminal_path, report_path):
            self.assertIn(path.relative_to(ROOT).as_posix(),
                          source_builder.OVERLAY_PATHS)
        portable_audit._validate_v1_zero_output_terminal({
            portable_audit.V1_ZERO_OUTPUT_TERMINAL_MEMBER:
                terminal_path.read_bytes(),
        })
        mutated = deepcopy(value)
        mutated["failure"]["claim_111_tests_passed"] = True
        body = dict(mutated)
        body.pop("terminal_authority_sha256")
        mutated["terminal_authority_sha256"] = portable_audit._digest(body)
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError, "terminal lineage",
        ):
            portable_audit._validate_v1_zero_output_terminal({
                portable_audit.V1_ZERO_OUTPUT_TERMINAL_MEMBER:
                    _canonical_json_bytes(mutated),
            })
        v2_terminal_path = ROOT / portable_audit.V2_ZERO_OUTPUT_TERMINAL_MEMBER
        v2_report_path = (
            ROOT / portable_audit.V2_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER)
        v2 = json.loads(v2_terminal_path.read_text(encoding="utf-8"))
        v2_unsigned = dict(v2)
        v2_claimed = v2_unsigned.pop("terminal_authority_sha256")
        self.assertEqual(v2_claimed, portable_audit._digest(v2_unsigned))
        self.assertEqual(v2["suite_outcome"], {
            "error_count": 8,
            "failure_count": 1,
            "reported_test_count": 112,
            "reported_unittest_seconds": 639.576,
            "result": "FAILED",
            "timeout_expired": False,
        })
        self.assertEqual(len(v2["failure_cases"]), 9)
        self.assertTrue(all(
            item is False for item in v2["authorization"].values()))
        self.assertTrue(all(
            item["exists"] is False
            for item in v2["output_facts"].values()))
        portable_audit._validate_v2_zero_output_terminal({
            portable_audit.V2_ZERO_OUTPUT_TERMINAL_MEMBER:
                v2_terminal_path.read_bytes(),
            portable_audit.V2_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER:
                v2_report_path.read_bytes(),
        })
        for path in (v2_terminal_path, v2_report_path):
            self.assertIn(
                path.relative_to(ROOT).as_posix(), source_builder.OVERLAY_PATHS)
        v2_mutated = deepcopy(v2)
        v2_mutated["failure_cases"][0]["missing_relative_path"] = "other"
        v2_body = dict(v2_mutated)
        v2_body.pop("terminal_authority_sha256")
        v2_mutated["terminal_authority_sha256"] = portable_audit._digest(v2_body)
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError, "v2 zero-output",
        ):
            portable_audit._validate_v2_zero_output_terminal({
                portable_audit.V2_ZERO_OUTPUT_TERMINAL_MEMBER:
                    _canonical_json_bytes(v2_mutated),
                portable_audit.V2_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER:
                    v2_report_path.read_bytes(),
            })
        successor_path = (
            ROOT / portable_audit.DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_MEMBER)
        successor_report_path = (
            ROOT /
            portable_audit.DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_REPORT_MEMBER)
        successor_payloads = {
            portable_audit.DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_MEMBER:
                successor_path.read_bytes(),
            portable_audit.DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_REPORT_MEMBER:
                successor_report_path.read_bytes(),
            **{
                name: (ROOT / name).read_bytes()
                for name in (
                    "scripts/goal5791_formal_contract.py",
                    "scripts/goal5791_formal_controller.py",
                    "scripts/goal5791_formal_evaluate.py",
                    "scripts/goal5791_formal_independent_recount.py",
                    "scripts/goal5791_formal_worker.py",
                )
            },
        }
        successor = json.loads(successor_path.read_text(encoding="utf-8"))
        successor_unsigned = dict(successor)
        successor_claimed = successor_unsigned.pop("authority_sha256")
        self.assertEqual(
            successor_claimed, portable_audit._digest(successor_unsigned))
        self.assertEqual(
            successor["test_gate"]["workspace_discovered_test_count"], 112)
        self.assertEqual(
            successor["test_gate"]["clean_selected_test_count"], 106)
        self.assertTrue(all(
            item is False for item in successor["authorization"].values()))
        portable_audit._validate_dual_cpu_gate_successor_authority(
            successor_payloads)
        successor_mutations = []
        for field, replacement in (
            ("resolution.clean_gate_coverage_is_not_reduced", False),
            ("test_gate.cpu_test_gate_helper_sha256", "0" * 64),
            (
                "test_gate.cpu_test_gate_helper_sha256",
                hashlib.sha256(
                    (ROOT / portable_audit.CPU_TEST_GATE_MEMBER).read_bytes()
                ).hexdigest(),
            ),
            ("test_gate.operational_timeout_watchdog_uses_host_clock", False),
            ("work_plan.sha256", "0" * 64),
            ("authorization.authorizes_v3_source_build", True),
        ):
            mutated_successor = deepcopy(successor)
            parent_name, child_name = field.split(".")
            mutated_successor[parent_name][child_name] = replacement
            successor_mutations.append(mutated_successor)
        excluded_mutation = deepcopy(successor)
        excluded_mutation["test_gate"][
            "clean_external_only_excluded_test_ids"] = (
                excluded_mutation["test_gate"][
                    "clean_external_only_excluded_test_ids"][:-1])
        successor_mutations.append(excluded_mutation)
        for successor_mutated in successor_mutations:
            successor_body = dict(successor_mutated)
            successor_body.pop("authority_sha256")
            successor_mutated["authority_sha256"] = portable_audit._digest(
                successor_body)
            with self.assertRaisesRegex(
                portable_audit.IndependentPortableAuditError,
                "dual CPU-gate successor",
            ):
                portable_audit._validate_dual_cpu_gate_successor_authority({
                    **successor_payloads,
                    portable_audit.DUAL_CPU_GATE_SUCCESSOR_AUTHORITY_MEMBER:
                        _canonical_json_bytes(successor_mutated),
                })
        v3_terminal_path = ROOT / portable_audit.V3_ZERO_OUTPUT_TERMINAL_MEMBER
        v3_terminal_report_path = (
            ROOT / portable_audit.V3_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER)
        v3_terminal_payloads = {
            portable_audit.V3_ZERO_OUTPUT_TERMINAL_MEMBER:
                v3_terminal_path.read_bytes(),
            portable_audit.V3_ZERO_OUTPUT_TERMINAL_REPORT_MEMBER:
                v3_terminal_report_path.read_bytes(),
        }
        portable_audit._validate_v3_zero_output_terminal(v3_terminal_payloads)
        v3_terminal = json.loads(
            v3_terminal_path.read_text(encoding="utf-8"))
        v3_mutated = deepcopy(v3_terminal)
        v3_mutated["authorization"]["authorizes_retry_of_v3"] = True
        v3_body = dict(v3_mutated)
        v3_body.pop("terminal_authority_sha256")
        v3_mutated["terminal_authority_sha256"] = portable_audit._digest(
            v3_body)
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError,
            "v3 zero-output terminal",
        ):
            portable_audit._validate_v3_zero_output_terminal({
                **v3_terminal_payloads,
                portable_audit.V3_ZERO_OUTPUT_TERMINAL_MEMBER:
                    _canonical_json_bytes(v3_mutated),
            })
        v4_authority_path = (
            ROOT / portable_audit.V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_MEMBER)
        v4_authority_report_path = (
            ROOT /
            portable_audit.V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_REPORT_MEMBER)
        v4_authority = json.loads(
            v4_authority_path.read_text(encoding="utf-8"))
        v4_payloads = {
            portable_audit.V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_MEMBER:
                v4_authority_path.read_bytes(),
            portable_audit.V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_REPORT_MEMBER:
                v4_authority_report_path.read_bytes(),
            portable_audit.CPU_TEST_GATE_MEMBER:
                (ROOT / portable_audit.CPU_TEST_GATE_MEMBER).read_bytes(),
            **v3_terminal_payloads,
            **{
                row["path"]: (ROOT / row["path"]).read_bytes()
                for row in v4_authority["missing_controlling_predecessors"]
            },
        }
        portable_audit._validate_v4_clean_failure_successor_authority(
            v4_payloads)
        self.assertEqual(
            len(v4_authority["missing_controlling_predecessors"]), 4)
        self.assertEqual(
            v4_authority["temporary_v3_diagnostic"][
                "other_selected_tests_passed"],
            105,
        )
        for field, replacement in (
            ("resolution.clean_selected_test_count_remains_106", False),
            ("temporary_v3_diagnostic.other_selected_tests_passed", 104),
            ("test_gate_successor.cpu_test_gate_helper_schema", "v1"),
            (
                "test_gate_successor.cpu_test_gate_helper_sha256",
                portable_audit.V3_CPU_TEST_GATE_HELPER_SHA256,
            ),
            ("authorization.authorizes_v4_source_build", True),
        ):
            mutated = deepcopy(v4_authority)
            parent_name, child_name = field.split(".")
            mutated[parent_name][child_name] = replacement
            body = dict(mutated)
            body.pop("authority_sha256")
            mutated["authority_sha256"] = portable_audit._digest(body)
            with self.assertRaisesRegex(
                portable_audit.IndependentPortableAuditError,
                "v4 clean-failure successor",
            ):
                portable_audit._validate_v4_clean_failure_successor_authority({
                    **v4_payloads,
                    portable_audit.V4_CLEAN_FAILURE_SUCCESSOR_AUTHORITY_MEMBER:
                        _canonical_json_bytes(mutated),
                })
        v15_path = ROOT / portable_audit.STAGE_A_V15_SUCCESSOR_AUTHORITY_MEMBER
        v15_report_path = (
            ROOT / portable_audit.STAGE_A_V15_SUCCESSOR_AUTHORITY_REPORT_MEMBER)
        v15_payloads = {
            portable_audit.STAGE_A_V15_SUCCESSOR_AUTHORITY_MEMBER:
                v15_path.read_bytes(),
            portable_audit.STAGE_A_V15_SUCCESSOR_AUTHORITY_REPORT_MEMBER:
                v15_report_path.read_bytes(),
            portable_audit.STAGE_A_V1_TERMINAL_MEMBER:
                (ROOT / portable_audit.STAGE_A_V1_TERMINAL_MEMBER).read_bytes(),
            portable_audit.STAGE_A_V2_TERMINAL_MEMBER:
                (ROOT / portable_audit.STAGE_A_V2_TERMINAL_MEMBER).read_bytes(),
            portable_audit.STAGE_A_V2_OPEN_RECEIPT_MEMBER:
                (ROOT / portable_audit.STAGE_A_V2_OPEN_RECEIPT_MEMBER).read_bytes(),
            "scripts/goal5791_open_upload_staging.py": (
                ROOT / "scripts/goal5791_open_upload_staging.py").read_bytes(),
            "scripts/goal5791_target_prepare.py": (
                ROOT / "scripts/goal5791_target_prepare.py").read_bytes(),
        }
        portable_audit._validate_stage_a_v15_successor_authority(v15_payloads)
        v15_mutated = json.loads(v15_path.read_text(encoding="utf-8"))
        v15_mutated["authorization"]["authorizes_stage_a"] = True
        v15_body = dict(v15_mutated)
        v15_body.pop("authority_sha256")
        v15_mutated["authority_sha256"] = portable_audit._digest(v15_body)
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError,
            "endpoint-record v15 successor",
        ):
            portable_audit._validate_stage_a_v15_successor_authority({
                **v15_payloads,
                portable_audit.STAGE_A_V15_SUCCESSOR_AUTHORITY_MEMBER:
                    _canonical_json_bytes(v15_mutated),
            })

        v25_governance_members = (
            portable_audit.APPEND_ONLY_CORRECTION_AUTHORITY_MEMBER,
            portable_audit.APPEND_ONLY_CORRECTION_AUTHORITY_REPORT_MEMBER,
            portable_audit.PAPER_OUTCOME_SUCCESSOR_AUTHORITY_MEMBER,
            portable_audit.PAPER_OUTCOME_SUCCESSOR_AUTHORITY_REPORT_MEMBER,
            portable_audit.PREREGISTRATION_V8_MEMBER,
            portable_audit.PRETARGET_V8_MEMBER,
            portable_audit.PREREGISTRATION_V9_MEMBER,
            portable_audit.PRETARGET_V9_MEMBER,
            portable_audit.OWNER_REVIEW_ABSORPTION_MEMBER,
            portable_audit.SMALL_RELATIVE_ABSORPTION_MEMBER,
            portable_audit.CORRECTION_FORMAL_V1_TERMINAL_MEMBER,
            portable_audit.V25_SUPPORT_CHAIN_TERMINAL_MEMBER,
            portable_audit.V25_SUPPORT_CHAIN_TERMINAL_REPORT_MEMBER,
            "scripts/goal5791_formal_contract.py",
            "scripts/goal5791_formal_worker.py",
            "scripts/goal5791_formal_controller.py",
            "scripts/goal5791_formal_evaluate.py",
            "scripts/goal5791_formal_independent_recount.py",
        )
        v25_payloads = {
            name: (ROOT / name).read_bytes()
            for name in v25_governance_members
        }
        portable_audit._validate_v25_governance_successors(v25_payloads)
        for member, field_path in (
            (
                portable_audit.APPEND_ONLY_CORRECTION_AUTHORITY_MEMBER,
                ("authorization", "authorizes_formal_worker_zero"),
            ),
            (
                portable_audit.PAPER_OUTCOME_SUCCESSOR_AUTHORITY_MEMBER,
                ("authorization", "authorizes_formal_worker_zero"),
            ),
        ):
            mutated = json.loads(v25_payloads[member])
            mutated[field_path[0]][field_path[1]] = True
            body = dict(mutated)
            body.pop("authority_sha256")
            mutated["authority_sha256"] = portable_audit._digest(body)
            with self.assertRaisesRegex(
                portable_audit.IndependentPortableAuditError, "v25",
            ):
                portable_audit._validate_v25_governance_successors({
                    **v25_payloads,
                    member: _canonical_json_bytes(mutated),
                })

        resigned_v8_preregistration = json.loads(
            v25_payloads[portable_audit.PREREGISTRATION_V8_MEMBER])
        resigned_v8_preregistration["status"] = (
            "ATTACKER_RESIGNED_HISTORICAL_SUPPORT")
        preregistration_body = dict(resigned_v8_preregistration)
        preregistration_body.pop("preregistration_sha256")
        resigned_v8_preregistration["preregistration_sha256"] = (
            portable_audit._digest(preregistration_body))
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError,
            "preregistration v8|exact file identity",
        ):
            portable_audit._validate_v25_governance_successors({
                **v25_payloads,
                portable_audit.PREREGISTRATION_V8_MEMBER:
                    _canonical_json_bytes(resigned_v8_preregistration),
            })

        resigned_v8_pretarget = json.loads(
            v25_payloads[portable_audit.PRETARGET_V8_MEMBER])
        resigned_v8_pretarget["status"] = (
            "ATTACKER_RESIGNED_HISTORICAL_SUPPORT")
        pretarget_body = dict(resigned_v8_pretarget)
        pretarget_body.pop("authority_sha256")
        resigned_v8_pretarget["authority_sha256"] = portable_audit._digest(
            pretarget_body)
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError,
            "pretarget v8|exact file identity",
        ):
            portable_audit._validate_v25_governance_successors({
                **v25_payloads,
                portable_audit.PRETARGET_V8_MEMBER:
                    _canonical_json_bytes(resigned_v8_pretarget),
            })

        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError,
            "v25 governance successor exact file identity",
        ):
            portable_audit._validate_v25_governance_successors({
                **v25_payloads,
                portable_audit.PREREGISTRATION_V8_MEMBER:
                    v25_payloads[portable_audit.PRETARGET_V8_MEMBER],
                portable_audit.PRETARGET_V8_MEMBER:
                    v25_payloads[portable_audit.PREREGISTRATION_V8_MEMBER],
            })

        resigned_absorption = json.loads(
            v25_payloads[portable_audit.SMALL_RELATIVE_ABSORPTION_MEMBER])
        resigned_absorption["status"] = "ATTACKER_RESIGNED_SUPPORT"
        absorption_body = dict(resigned_absorption)
        absorption_body.pop("absorption_sha256")
        resigned_absorption["absorption_sha256"] = portable_audit._digest(
            absorption_body)
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError,
            "exact file identity|predecessor absorption",
        ):
            portable_audit._validate_v25_governance_successors({
                **v25_payloads,
                portable_audit.SMALL_RELATIVE_ABSORPTION_MEMBER:
                    _canonical_json_bytes(resigned_absorption),
            })

        resigned_formal_v1_terminal = json.loads(
            v25_payloads[
                portable_audit.CORRECTION_FORMAL_V1_TERMINAL_MEMBER])
        resigned_formal_v1_terminal["status"] = "ATTACKER_RESIGNED_SUPPORT"
        terminal_body = dict(resigned_formal_v1_terminal)
        terminal_body.pop("terminal_sha256")
        resigned_formal_v1_terminal["terminal_sha256"] = (
            portable_audit._digest(terminal_body))
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError,
            "exact file identity|correction formal-v1 terminal",
        ):
            portable_audit._validate_v25_governance_successors({
                **v25_payloads,
                portable_audit.CORRECTION_FORMAL_V1_TERMINAL_MEMBER:
                    _canonical_json_bytes(resigned_formal_v1_terminal),
            })

    def test_home_shape_is_exact_four_small_plus_six_bounded(self) -> None:
        self.assertEqual(home.PREFIX_EDGE_RECORD_COUNT, 262_144)
        self.assertEqual(set(home.REAL_DATASETS), {
            "com-dblp", "cit-Patents", "soc-LiveJournal1",
        })
        self.assertEqual(len(recount.EXPECTED_LANES), 10)
        self.assertEqual(
            len([name for name in recount.EXPECTED_LANES
                 if name.startswith("small__")]),
            4,
        )
        self.assertEqual(
            len([name for name in recount.EXPECTED_LANES
                 if name.startswith("bounded_real__")]),
            6,
        )
        self.assertEqual(
            recount.EXPECTED_CACHE_POLICY, formal_contract.CACHE_POLICY)

    def test_home_clean_extractor_is_standalone_and_regular_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            good = root / "good.tar.gz"
            good.write_bytes(source_builder._archive({
                "src/kept.py": b"print('kept')\n",
            }))
            self.assertEqual(
                home._safe_extract_source(good, root / "good"),
                ["src/kept.py"],
            )
            malicious_bytes = io.BytesIO()
            with gzip.GzipFile(
                fileobj=malicious_bytes, mode="wb", filename="", mtime=0,
            ) as compressed:
                with tarfile.open(fileobj=compressed, mode="w") as archive:
                    directory = tarfile.TarInfo("src")
                    directory.type = tarfile.DIRTYPE
                    archive.addfile(directory)
            malicious = root / "directory-member.tar.gz"
            malicious.write_bytes(malicious_bytes.getvalue())
            with self.assertRaisesRegex(RuntimeError, "directory member"):
                home._safe_extract_source(malicious, root / "bad")
        source = (ROOT / "scripts/goal5791_home_clean_validate.py").read_text(
            encoding="utf-8")
        self.assertIn("executing Goal5791 Home validator differs", source)
        self.assertIn("imported outside frozen source", source)
        for selector in (
            "CUDA_VISIBLE_DEVICES", "NVIDIA_VISIBLE_DEVICES",
            "NUMBA_DISABLE_CUDA", "NUMBA_ENABLE_CUDASIM",
            "NUMBA_CUDA_NVVM", "NUMBA_CUDA_LIBDEVICE",
            "NUMBA_CACHE_DIR", "CUPY_CACHE_DIR", "CUDA_CACHE_PATH",
            "OPTIX_CACHE_PATH",
            "RTDL_V4_FORMAL_LEAF_CACHE",
        ):
            self.assertIn(selector, source)
        self.assertIn('numba_cache_root = root / "numba_cache"', source)
        self.assertIn('env["NUMBA_CACHE_DIR"] = str(numba_cache_root)', source)

    def test_independent_recount_freezes_two_versus_seven(self) -> None:
        self.assertEqual(recount.ON_IDS, (
            "checked_summary.kernel_launch",
            "checked_summary.summary_copy_sync",
        ))
        self.assertEqual(len(recount.OFF_IDS), 7)
        source = (ROOT / "scripts/goal5791_independent_home_recount.py").read_text(
            encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertFalse(any(name.startswith((
            "rtdsl", "cupy", "numpy", "numba",
            "scripts.goal5791_formal_",
            "scripts.goal5791_home_",
        )) for name in imports))
        identity = {
            "schema": "rtdl.goal5790.ptx_program_identity.v1",
            "composed": {"ptx_sha256": "1" * 64},
        }
        self.assertEqual(
            {recount._digest(lane["ptx_program_identity"]) for lane in (
                {"ptx_program_identity": identity},
                {"ptx_program_identity": dict(identity)},
            )},
            {recount._digest(identity)},
        )
        self.assertIn(
            '_digest(lane["ptx_program_identity"])', source)
        self.assertNotIn(
            'lane["ptx_program_identity_sha256"]', source)

    def test_independent_home_oracle_reconstructs_raw_simple_graph(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            edge = Path(temporary) / "fixture.edge"
            # K4 plus reversed duplicates and self loops remains four simple
            # undirected triangles.
            rows = [
                (0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3),
                (1, 0), (3, 3), (2, 2),
            ]
            edge.write_bytes(b"".join(struct.pack("<ii", *row) for row in rows))
            self.assertEqual(recount._triangle_count(edge), 4)
        self.assertEqual(
            recount.INPUT_AUTHORITIES[("small", "four_vertex_clique")],
            {
                "filename": "small__four_vertex_clique.edge",
                "sha256": (
                    "2f7f2b2d4f994e6abd593b71f5e28fe65b71d59e34f4134ad2037e5d037f746d"
                ),
                "bytes": 48,
                "triangle_count": 4,
            },
        )

    def test_independent_home_plan_reconstructs_production_seals(self) -> None:
        from rtdsl.v4_fusion_ablation import (
            FusionVariant,
            build_checked_u64_product_sum_ablation_plan,
            load_verified_shared_contract_freeze,
        )
        from tests.goal5790_fusion_ablation_contract_test import (
            FREEZE, _authority,
        )

        descriptor = {
            "schema": "rtdl.goal5791.rt2a1_segment_descriptor.v1",
            "segment_id": 0,
            "partition": {
                "source_begin": 0, "source_end": 4,
                "oversized_source_part": 0, "global_segment_id": 0,
            },
            "relation_count": 6, "primitive_count": 6, "query_count": 5,
            "host_geometry_bytes": 796, "maximum_weight": 2,
            "weight_sum": 6, "paper_algorithm": "RT-2A1",
            "gpu_touched": False,
        }
        authority = _authority()
        freeze = load_verified_shared_contract_freeze(FREEZE.read_bytes())
        source_input_sha256 = "5" * 64
        plan_input_binding = {
            "schema": "rtdl.goal5791.segment_plan_input.v1",
            "source_input_sha256": source_input_sha256,
            "segment_descriptor_sha256": recount._digest(descriptor),
            "formal_input": False,
        }
        output_contract = {
            "schema": "rtdl.goal5791.home_output_contract.v1",
            "paper_algorithm": "RT-2A1",
            "result": "exact_u64_triangle_count",
            "overflow": "fail_closed_before_wraparound",
        }
        oracle_contract = {
            "schema": "rtdl.goal5791.home_bounded_oracle.v1",
            "dataset": "fixture",
            "edge_file_sha256": source_input_sha256,
            "expected_triangle_count": 4,
            "authority": "independent_stdlib_simple_undirected_triangle_recount",
        }
        timer_contract = {
            "schema": "rtdl.goal5791.home_zero_elapsed_observation.v1",
            "elapsed_value_count": 0,
            "clock_sample_count": 0,
            "home_performance_observation_created": False,
            "home_performance_diagnostic_used": False,
            "token_admission_before_device_geometry": True,
            "device_iterator_closed_before_evidence_seal": True,
        }
        lifecycle_contract = {
            "schema": "rtdl.goal5791.home_lifecycle.v1",
            "lifecycle": "cold",
            "prepared_neutral_prewarm_order": [],
            "formal_worker": False,
        }
        for variant in (FusionVariant.FUSION_ON, FusionVariant.FUSION_OFF):
            plan = build_checked_u64_product_sum_ablation_plan(
                freeze, variant=variant, target_materialization=authority,
                input_sha256=recount._digest(plan_input_binding),
                output_contract_sha256=recount._digest(output_contract),
                oracle_sha256=recount._digest(oracle_contract),
                timer_contract_sha256=recount._digest(timer_contract),
                lifecycle_contract_sha256=recount._digest(lifecycle_contract),
                value_count=descriptor["query_count"],
            )
            lane = {
                "variant": variant.value,
                "dataset": "fixture",
                "lifecycle": "cold",
                "edge_file_sha256": source_input_sha256,
                "expected_triangle_count": 4,
                "execution_source_archive_sha256": (
                    plan.execution_source_archive_sha256),
                "execution_source_tree_sha256": plan.execution_source_tree_sha256,
                "native_library_sha256": plan.native_library_sha256,
                "target_materialization_receipt_sha256": (
                    plan.target_materialization_receipt_sha256),
            }
            self.assertEqual(
                recount._verify_plan(
                    plan.to_dict(), lane=lane, descriptor=descriptor,
                    plan_input_binding=plan_input_binding),
                plan.to_dict(),
            )
            legacy_plan = build_checked_u64_product_sum_ablation_plan(
                freeze, variant=variant, target_materialization=authority,
                input_sha256=recount._digest(descriptor),
                output_contract_sha256=recount._digest(output_contract),
                oracle_sha256=recount._digest(oracle_contract),
                timer_contract_sha256=recount._digest(timer_contract),
                lifecycle_contract_sha256=recount._digest(lifecycle_contract),
                value_count=descriptor["query_count"],
            )
            with self.assertRaisesRegex(
                recount.RecountError, "plan identity",
            ):
                recount._verify_plan(
                    legacy_plan.to_dict(), lane=lane, descriptor=descriptor,
                    plan_input_binding=plan_input_binding,
                )
            wrong_source_binding = {
                **plan_input_binding,
                "source_input_sha256": "a" * 64,
            }
            with self.assertRaisesRegex(
                recount.RecountError, "input binding",
            ):
                recount._verify_plan(
                    plan.to_dict(), lane=lane, descriptor=descriptor,
                    plan_input_binding=wrong_source_binding,
                )

    def test_home_worker_uses_only_token_entry_for_device_execution(self) -> None:
        source = (ROOT / "scripts/goal5791_home_token_validation.py").read_text(
            encoding="utf-8")
        tree = ast.parse(source)
        execute_calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "execute_segment_unsealed"
        ]
        self.assertEqual(len(execute_calls), 2)
        for call in execute_calls:
            names = {keyword.arg for keyword in call.keywords}
            self.assertIn("fusion_execution_token", names)
            self.assertIn("segment_ordinal", names)
            self.assertIn("segment_descriptor_sha256", names)
            self.assertNotIn("fusion_ablation_plan", names)
            self.assertNotIn("operation_execution_nonce", names)
        admit_calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "admit_fusion_execution_token"
        ]
        self.assertEqual(len(admit_calls), 2)
        for call in admit_calls:
            names = {keyword.arg for keyword in call.keywords}
            self.assertIn("plan_input_binding_sha256", names)
        for forbidden in (
            "time.monotonic", "time.perf_counter", "diagnostic_elapsed",
            "home_elapsed_values_are_diagnostic_only",
        ):
            self.assertNotIn(forbidden, source)
        functional = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_functional"
        )
        self.assertTrue(any(
            isinstance(node, ast.ImportFrom)
            and node.module == "scripts.goal5791_formal_contract"
            and any(alias.name == "CACHE_POLICY" for alias in node.names)
            for node in ast.walk(functional)
        ))
        self.assertIn('"elapsed_value_count": 0', source)
        self.assertIn('"clock_sample_count": 0', source)
        self.assertIn('"home_performance_observation_created": False', source)
        self.assertIn('"home_performance_diagnostic_used": False', source)
        self.assertIn('"loading_complete_before_preparation": True', source)
        self.assertIn('"seal_after_device_iterator_close": True', source)
        self.assertIn("registered_performance_timing_count\": 0", source)

    def test_home_zero_elapsed_gate_rejects_resigned_fields(self) -> None:
        home_sources = [
            (ROOT / "scripts/goal5791_home_token_validation.py").read_text(
                encoding="utf-8"),
            (ROOT / "scripts/goal5791_independent_home_recount.py").read_text(
                encoding="utf-8"),
            (ROOT / "scripts/goal5791_home_clean_validate.py").read_text(
                encoding="utf-8"),
        ]
        for source in home_sources:
            for forbidden in (
                "time.monotonic", "time.perf_counter", "diagnostic_elapsed",
                "home_elapsed_values_are_diagnostic_only",
            ):
                self.assertNotIn(forbidden, source)
        clean = {
            "elapsed_value_count": 0,
            "clock_sample_count": 0,
            "home_performance_observation_created": False,
            "home_performance_diagnostic_used": False,
            "inherited_producer": {"elapsed_values_recorded": False},
            "timer_contract_sha256": hashlib.sha256(
                _canonical_json_bytes({
                    "schema": "rtdl.goal5791.home_zero_elapsed_observation.v1",
                    "elapsed_value_count": 0,
                    "clock_sample_count": 0,
                    "home_performance_observation_created": False,
                    "home_performance_diagnostic_used": False,
                    "token_admission_before_device_geometry": True,
                    "device_iterator_closed_before_evidence_seal": True,
                }).rstrip(b"\n")
            ).hexdigest(),
        }
        self.assertEqual(
            clean["timer_contract_sha256"],
            "8839b4654141b4f18ef61db948889656705a8878bdd4a4292457a17e73193967",
        )
        portable_audit._reject_home_performance_observations(
            clean, label="clean")
        home._reject_home_performance_observations(clean, label="clean")
        target._reject_home_performance_observations(clean, label="clean")
        bundle_builder._reject_home_performance_observations(
            clean, label="clean")
        bundle_builder._reject_home_performance_observations(
            {**clean, "cpu_test_timeout_seconds": 1_200},
            label="source_receipt",
        )
        bundle_builder._reject_home_performance_observations(
            {
                **clean,
                "overlay_sha256": {
                    "tests/goal5791_pretimer_exact_member.py": "a" * 64,
                },
            },
            label="SOURCE_BASE_AND_OVERLAY_AUTHORITY.json",
        )
        for source_gate in (
            portable_audit._reject_home_performance_observations,
            target._reject_home_performance_observations,
        ):
            source_gate(
                {
                    **clean,
                    "cpu_test_timeout_seconds": 1_200,
                    "overlay_sha256": {
                        "tests/goal5791_pretimer_exact_member.py": "a" * 64,
                    },
                },
                label="SOURCE_BASE_AND_OVERLAY_AUTHORITY.json",
            )
        for source_gate, source_error in (
            (portable_audit._reject_home_performance_observations,
             portable_audit.IndependentPortableAuditError),
            (target._reject_home_performance_observations,
             target.PrepareError),
        ):
            for source_attack in (
                {"cpu_test_timeout_seconds": 600},
                {"cpu_test_timeout_seconds": True},
                {"overlay_sha256": {}},
                {"overlay_sha256": {"pretimer.py": "g" * 64}},
            ):
                with self.assertRaises(source_error):
                    source_gate(
                        {**clean, **source_attack},
                        label="SOURCE_BASE_AND_OVERLAY_AUTHORITY.json",
                    )
        for operational_timeout_attack in (600, True, 1_200.0, "1200"):
            with self.assertRaises(bundle_builder.BundleError):
                bundle_builder._reject_home_performance_observations(
                    {
                        **clean,
                        "cpu_test_timeout_seconds": operational_timeout_attack,
                    },
                    label="source_receipt",
                )
        for overlay_digest_attack in ({}, {"pretimer.py": True}, {
                "pretimer.py": "g" * 64}):
            with self.assertRaises(bundle_builder.BundleError):
                bundle_builder._reject_home_performance_observations(
                    {**clean, "overlay_sha256": overlay_digest_attack},
                    label="SOURCE_BASE_AND_OVERLAY_AUTHORITY.json",
                )
        attacks = (
            {**clean, "elapsed_value_count": 1},
            {**clean, "clock_sample_count": 1},
            {**clean, "elapsed_value_count": False},
            {**clean, "elapsed_value_count": 0.0},
            {**clean, "elapsed_value_count": "0"},
            {**clean, "clock_sample_count": False},
            {**clean, "clock_sample_count": 0.0},
            {**clean, "clock_sample_count": "0"},
            {**clean, "home_performance_observation_created": True},
            {**clean, "home_performance_diagnostic_used": True},
            {**clean, "diagnostic_elapsed_seconds": 0.0},
            {**clean, "resigned": {"phase_elapsed_seconds": 0.0}},
            {**clean, "inherited_producer": {"elapsed_values_recorded": True}},
            {**clean, "clock_started_ns": 0},
            {**clean, "duration_seconds": False},
            {**clean, "timing_seconds": 0},
            {**clean, "perf_counter_ns": 0},
            {**clean, "latency_ms": 0},
            {**clean, "timer_contract_sha256": "a" * 64},
        )
        gates = (
            (portable_audit._reject_home_performance_observations,
             portable_audit.IndependentPortableAuditError),
            (home._reject_home_performance_observations, RuntimeError),
            (target._reject_home_performance_observations,
             target.PrepareError),
            (bundle_builder._reject_home_performance_observations,
             bundle_builder.BundleError),
        )
        for attack in attacks:
            for gate, error in gates:
                with self.assertRaises(error):
                    gate(attack, label="resigned")

    def test_bundle_outer_member_set_rejects_resigned_extras(self) -> None:
        exact_names = set(bundle_builder.EXPECTED_BUNDLE_OUTER_MEMBERS)
        self.assertEqual(exact_names, target.EXPECTED_BUNDLE_OUTER_MEMBERS)
        self.assertEqual(
            exact_names, portable_audit.EXPECTED_BUNDLE_OUTER_MEMBERS)
        exact = {name: b"payload" for name in exact_names}
        bundle_builder._require_exact_bundle_member_set(exact)
        target._require_exact_bundle_member_set(exact)
        portable_audit._require_exact_bundle_member_set(exact)
        for extra in (
            "OWNER_TARGET_PREPARE_AUTHORITY.json",
            "EXTRA.txt",
            "DATA/disguised_as_text.txt",
        ):
            resigned = {**exact, extra: b"fully resigned extra"}
            # A manifest row and hash for the extra cannot enlarge the frozen
            # outer set.  The membership gate runs independently of signatures.
            manifest_value = {
                "schema": "rtdl.goal5791.pre_pod_bundle.v3",
                "payloads": [
                    {"path": name, "size_bytes": len(data),
                     "sha256": hashlib.sha256(data).hexdigest()}
                    for name, data in sorted(resigned.items())
                    if name != "BUNDLE_MANIFEST.json"
                ],
            }
            resigned["BUNDLE_MANIFEST.json"] = (
                json.dumps(manifest_value, sort_keys=True) + "\n"
            ).encode()
            with self.assertRaises(bundle_builder.BundleError):
                bundle_builder._require_exact_bundle_member_set(resigned)
            with self.assertRaises(target.PrepareError):
                target._require_exact_bundle_member_set(resigned)
            with self.assertRaises(
                portable_audit.IndependentPortableAuditError,
            ):
                portable_audit._require_exact_bundle_member_set(resigned)

    def test_private_paths_and_renamed_binary_magics_are_rejected(self) -> None:
        for name in (
            ".Codex/token.txt",
            "src/__PyCache__/module.pyc",
            "Build/output.txt",
        ):
            with self.assertRaises(RuntimeError):
                source_builder._normalized(name)
            with self.assertRaises(
                portable_audit.IndependentPortableAuditError,
            ):
                portable_audit._name(name, source=True)
        renamed_blobs = (
            b"\xcf\xfa\xed\xfe" + b"x" * 16,
            b"PK\x05\x06" + b"\x00" * 18,
            b"7z\xbc\xaf'\x1c" + b"x" * 16,
            b"Rar!\x1a\x07\x00" + b"x" * 16,
            b"Rar!\x1a\x07\x01\x00" + b"x" * 16,
            b"\xa7\x0d\x0d\x0a" + b"x" * 16,
            b"\xcb\x0d\x0d\x0a" + b"x" * 16,
        )
        for blob in renamed_blobs:
            self.assertIsNotNone(source_builder._blob_kind(blob))
            self.assertIsNotNone(portable_audit._blob_kind(blob))

    def test_v4_successor_lineage_is_nonexecuting_and_self_sealed(self) -> None:
        path = ROOT / (
            "history/internal_docs/"
            "goal5791_v4_successor_lineage_authority_20260817.json"
        )
        value = json.loads(path.read_text(encoding="utf-8"))
        claimed = value.pop("authority_sha256")
        self.assertEqual(
            claimed,
            hashlib.sha256(_canonical_json_bytes(value).rstrip(b"\n")).hexdigest(),
        )
        self.assertTrue(all(
            item is False for item in value["authorization"].values()))
        self.assertEqual(value["execution_facts"]["formal_worker_count_executed"], 0)
        self.assertEqual(value["execution_facts"]["home_execution_count"], 0)
        self.assertEqual(value["execution_facts"]["pod_connection_count"], 0)
        replacements = value["superseded_preliminary_clauses"]["replacements"]
        self.assertEqual(len(replacements), 3)
        text = _canonical_json_bytes(replacements).decode("utf-8")
        self.assertIn("exactly two reviewed product deltas", text)
        self.assertIn("zero clocks", text)
        self.assertIn("57900000 + row_index", text)
        self.assertIn(
            path.relative_to(ROOT).as_posix(), source_builder.OVERLAY_PATHS)
        self.assertEqual(
            set(source_builder.OVERLAY_PATHS),
            set(portable_audit.EXPECTED_SOURCE_OVERLAY_PATHS),
        )

    def test_hostile_minimal_home_evidence_exploit_is_rejected(self) -> None:
        # Regression for the independently reproduced exploit that used a
        # truncated source, arbitrary native bytes, empty RAW records, and
        # locally re-signed manifests.
        fake_source_payloads = {
            "src/rtdsl/v4_operation_evidence.py": b"# forged\n",
            "src/rtdsl/v4_triangle_reduction_device_runtime.py": b"# forged\n",
        }
        fake_source_payloads[portable_audit.SOURCE_MANIFEST] = (
            _canonical_json_bytes({
                "schema": portable_audit.SOURCE_SCHEMA,
                "files": _manifest_rows(fake_source_payloads),
            })
        )
        fake_source = source_builder._archive(fake_source_payloads)
        payloads = {
            name: b"{}\n" for name in portable_audit.EXPECTED_HOME_RAW_MEMBERS
        }
        payloads.update({
            name: b"x" for name in portable_audit.EXPECTED_HOME_INPUT_MEMBERS
        })
        payloads.update({
            "EXECUTION_SOURCE.tar.gz": fake_source,
            "TARGET_NATIVE/librtdl_optix.so": b"not-an-elf",
            "TARGET_MATERIALIZATION_AUTHORITY.json": b"{}\n",
            "TARGET_MATERIALIZATION_EVIDENCE.tar.gz": source_builder._archive({
                "placeholder.txt": b"forged",
            }),
            "TARGET_PROGRAM_INSPECTION.json": b"{}\n",
            "SOURCE_MANIFEST.json": b"{}\n",
            "FUNCTIONAL_RECOUNT.json": b"{}\n",
        })
        manifest = {
            "schema": portable_audit.HOME_EVIDENCE_SCHEMA,
            "status": "PASS__10_OF_10_TOKEN_ONLY_HOME_EVIDENCE",
            "files": _manifest_rows(payloads),
            "exact_lane_count": 10,
            "behavioral_true_optix_lane_count": 10,
            "token_only_lane_count": 10,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "elapsed_value_count": 0,
            "clock_sample_count": 0,
            "home_performance_observation_created": False,
            "home_performance_diagnostic_used": False,
            "pod_used": False,
        }
        payloads["EVIDENCE_MANIFEST.json"] = _canonical_json_bytes(manifest)
        forged = source_builder._archive(payloads)
        with self.assertRaises(portable_audit.IndependentPortableAuditError):
            portable_audit.audit_home_evidence(forged)

    def test_hostile_exact_member_bundle_exploit_is_rejected(self) -> None:
        # Regression for the exact-outer-set, fully re-signed attack that used
        # a truncated source, empty receipts/Home chain/semantic authority,
        # and attacker-controlled README text.
        fake_source_payloads = {
            "src/rtdsl/v4_operation_evidence.py": b"# forged\n",
            "src/rtdsl/v4_triangle_reduction_device_runtime.py": b"# forged\n",
        }
        fake_source_payloads[portable_audit.SOURCE_MANIFEST] = (
            _canonical_json_bytes({
                "schema": portable_audit.SOURCE_SCHEMA,
                "files": _manifest_rows(fake_source_payloads),
            })
        )
        fake_source = source_builder._archive(fake_source_payloads)
        payloads = {
            name: b"{}\n"
            for name in portable_audit.EXPECTED_BUNDLE_OUTER_MEMBERS
            if name != "BUNDLE_MANIFEST.json"
        }
        payloads["SOURCE.tar.gz"] = fake_source
        payloads["README.md"] = b"attacker-controlled authorization text\n"
        manifest = {
            "schema": portable_audit.BUNDLE_SCHEMA,
            "payloads": _manifest_rows(payloads),
            "source_is_only_nested_container": True,
            "contains_real_scale_data": False,
            "contains_wheelhouse": False,
            "contains_optix_headers": False,
            "contains_prebuilt_target_native": False,
            "contains_owner_prepare_authority": False,
            "contains_owner_formal_authority": False,
            "formal_worker_count_executed": 0,
            "registered_performance_timing_count": 0,
            "elapsed_value_count": 0,
            "clock_sample_count": 0,
            "home_performance_observation_created": False,
            "home_performance_diagnostic_used": False,
            "source_archive_sha256": hashlib.sha256(fake_source).hexdigest(),
        }
        payloads["BUNDLE_MANIFEST.json"] = _canonical_json_bytes(manifest)
        forged = source_builder._archive(payloads)
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError, "source",
        ):
            portable_audit.audit_bundle(
                forged, home_evidence=b"equal-placeholder",
                home_evidence_twin=b"equal-placeholder",
            )

    def test_strict_bundle_audit_requires_external_home_evidence_pair(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError,
            "requires external Home evidence and twin",
        ):
            portable_audit.audit_bundle(b"not-read-without-pair")
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError,
            "requires external Home evidence and twin",
        ):
            portable_audit.audit_bundle(
                b"not-read-without-pair", home_evidence=b"one")
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError,
            "evidence/twin bytes differ",
        ):
            portable_audit.audit_bundle(
                b"not-read-after-mismatch", home_evidence=b"one",
                home_evidence_twin=b"two",
            )

    def test_home_materialization_mints_valid_fresh_nonce(self) -> None:
        from rtdsl.v4_fusion_ablation import (
            verify_target_materialization_authority,
        )
        from tests.goal5790_fusion_ablation_contract_test import _authority

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            freeze_path = source / home.SHARED_FREEZE_MEMBER
            freeze_path.parent.mkdir(parents=True)
            freeze_path.write_bytes((ROOT / home.SHARED_FREEZE_MEMBER).read_bytes())
            materializer = source / "scripts/goal5791_home_clean_validate.py"
            materializer.parent.mkdir(parents=True, exist_ok=True)
            materializer.write_bytes((
                ROOT / "scripts/goal5791_home_clean_validate.py").read_bytes())
            manifest_path = source / home.SOURCE_MANIFEST_MEMBER
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_bytes(b"{}\n")
            source_archive = root / "SOURCE.tar.gz"
            native = root / "librtdl_optix.so"
            evidence = root / "EVIDENCE.tar.gz"
            source_archive.write_bytes(b"source")
            native.write_bytes(b"native")
            evidence.write_bytes(b"evidence")
            fixture = _authority().to_dict()
            inspection = {
                name: fixture[name] for name in (
                    "callback_ir_sha256", "callback_authority_nonce",
                    "contract_sha256", "abi_sha256",
                    "program_bundle_identity", "composed_program_sha256",
                    "cupy_version",
                    "fusion_on_downstream_operation_recipe",
                    "fusion_off_downstream_operation_recipe",
                    "fusion_on_downstream_operation_recipe_sha256",
                    "fusion_off_downstream_operation_recipe_sha256",
                    "target_identity_sha256",
                )
            }
            kwargs = {
                "source_archive": source_archive,
                "source_manifest": {"source_tree_sha256": "9" * 64},
                "source": source,
                "native": native,
                "inspection": inspection,
                "target_evidence": evidence,
            }
            first = home._target_authority(**kwargs)
            second = home._target_authority(**kwargs)
            for value in (first, second):
                nonce = value["materialization_nonce"]
                self.assertEqual(len(nonce), 64)
                self.assertTrue(all(character in "0123456789abcdef"
                                    for character in nonce))
                unsigned = dict(value)
                claimed = unsigned.pop("receipt_sha256")
                self.assertEqual(home._digest(unsigned), claimed)
                self.assertEqual(
                    verify_target_materialization_authority(value).receipt_sha256,
                    claimed,
                )
            self.assertNotEqual(
                first["materialization_nonce"], second["materialization_nonce"])

    def test_portable_clean_set_rejects_extra_pyc(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "kept.py").write_bytes(b"print('kept')\n")
            expected = {"kept.py": b"print('kept')\n"}
            self.assertTrue(source_builder._audit_extracted_exact_set(
                root, expected)["regular_file_set_exact"])
            cache = root / "__pycache__"
            cache.mkdir()
            (cache / "attacker.pyc").write_bytes(b"not-real-bytecode")
            with self.assertRaisesRegex(RuntimeError, "file/directory set"):
                source_builder._audit_extracted_exact_set(root, expected)
            (cache / "attacker.pyc").unlink()
            with self.assertRaisesRegex(RuntimeError, "file/directory set"):
                source_builder._audit_extracted_exact_set(root, expected)

    def test_independent_portable_auditor_rejects_directory_and_link_members(self) -> None:
        for kind in ("directory", "symlink"):
            with self.subTest(kind=kind):
                raw = io.BytesIO()
                with gzip.GzipFile(
                    fileobj=raw, mode="wb", filename="", mtime=0,
                ) as compressed:
                    with tarfile.open(fileobj=compressed, mode="w") as archive:
                        member = tarfile.TarInfo("src/attack")
                        if kind == "directory":
                            member.type = tarfile.DIRTYPE
                        else:
                            member.type = tarfile.SYMTYPE
                            member.linkname = "../escape"
                        archive.addfile(member)
                with self.assertRaises(
                    portable_audit.IndependentPortableAuditError,
                ):
                    portable_audit._archive(
                        raw.getvalue(), label="attack", source=True)
        source = (
            ROOT / "scripts/goal5791_independent_portable_audit.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            node.module or "" for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        } | {
            alias.name for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertFalse(any(
            name.startswith("scripts.goal5791_build_portable_source")
            for name in imported
        ))

    def test_target_source_set_rejects_extra_pyc(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            kept = root / "src/kept.py"
            kept.parent.mkdir(parents=True)
            kept.write_bytes(b"print('kept')\n")
            manifest = {
                "files": [{
                    "path": "src/kept.py",
                    "size_bytes": kept.stat().st_size,
                    "sha256": hashlib.sha256(kept.read_bytes()).hexdigest(),
                }],
            }
            manifest_path = root / target.SOURCE_MANIFEST_MEMBER
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(json.dumps(manifest) + "\n")
            manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            self.assertTrue(target._audit_exact_source_set(
                root, manifest, manifest_file_sha256=manifest_sha,
                require_read_only=False,
            )["regular_file_set_exact"])
            cache = root / "__pycache__"
            cache.mkdir()
            (cache / "attacker.pyc").write_bytes(b"not-real-bytecode")
            with self.assertRaisesRegex(target.PrepareError, "directory set"):
                target._audit_exact_source_set(
                    root, manifest, manifest_file_sha256=manifest_sha,
                    require_read_only=False,
                )

    def test_target_prepare_external_upload_and_data_scope_are_exact(self) -> None:
        terminal_path = ROOT / (
            "history/internal_docs/"
            "goal5791_stage_a_v8_target_producer_observation_terminal_"
            "20260820.json")
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        terminal_body = dict(terminal)
        terminal_seal = terminal_body.pop("terminal_sha256")
        self.assertEqual(portable_audit._digest(terminal_body), terminal_seal)
        self.assertEqual(terminal["observed_numpy_version"], "2.4.4")
        self.assertEqual(
            terminal["stale_target_prepare_expected_numpy_version"],
            "2.2.6")
        self.assertEqual(terminal["functional_smoke_count"], 0)
        self.assertEqual(terminal["formal_worker_count"], 0)
        self.assertEqual(
            terminal["registered_performance_timing_count"], 0)
        self.assertFalse(terminal["authorizes_stage_a_successor"])
        self.assertFalse(terminal["authorizes_stage_b"])

        self.assertEqual(target.EXPECTED_DATA_SHA256, (
            "f186cd28a5ae767f968eaa1372cd66285934be430bceb77ff14c6cf94e33e6eb"))
        self.assertEqual(target.EXPECTED_WHEELHOUSE_SHA256, (
            "d0c0f75365a78792cf0c2f548e0bdd144f0ad7175e0d8f83efcf335eb3b311f3"))
        self.assertEqual(target.EXPECTED_OPTIX_HEADERS_SHA256, (
            "7fae86ce3dca2fbc2a47be075f02465cf6ee9d9eafd204234f2882fbdeebee54"))
        self.assertEqual(target.EXPECTED_TARGET_DEPENDENCY_IDENTITY, {
            "python": "3.12.3", "numba": "0.65.1", "numpy": "2.4.4",
            "llvmlite": "0.47.0", "cupy": "14.0.1",
            "cuda_runtime_int": 12090,
        })
        self.assertEqual(set(target.EXPECTED_DATA), {
            "com_dblp", "cit_patents", "soc_livejournal1",
        })
        self.assertFalse(any(
            "barnes" in record["member"].lower()
            for record in target.EXPECTED_DATA.values()
        ))

    def test_target_producer_audit_binds_actual_paths_and_rejects_foreign(self) -> None:
        replay_path = ROOT / (
            "history/internal_docs/goal5791_stage_a_v8_failure_evidence_"
            "20260820/TARGET_PTX_PRODUCER_OBSERVATION.json")
        replay = json.loads(replay_path.read_text(encoding="utf-8"))
        self.assertEqual(
            target._validate_target_producer_observation_fields(
                replay, cuda=Path("/usr/local/cuda-12.8")),
            {
                "python": "3.12.3", "numba": "0.65.1",
                "numpy": "2.4.4", "cupy": "14.0.1",
                "llvmlite": "0.47.0",
            },
        )
        stale = deepcopy(replay)
        stale["numpy"] = "2.2.6"
        with self.assertRaisesRegex(
            target.PrepareError, "producer observation drifted",
        ):
            target._validate_target_producer_observation_fields(
                stale, cuda=Path("/usr/local/cuda-12.8"))

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cuda = root / "cuda"
            nvvm = cuda / "nvvm/lib64/libnvvm.so.4"
            libdevice = cuda / "nvvm/libdevice/libdevice.10.bc"
            nvrtc = cuda / "lib64/libnvrtc.so.12"
            builtins = cuda / "lib64/libnvrtc-builtins.so.12.8"
            for path in (nvvm, libdevice, nvrtc, builtins):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(path.name.encode())
            trace = root / "trace.log"
            trace.write_text("synthetic\n", encoding="utf-8")
            observation = {
                "schema": "rtdl.goal5791.target_ptx_producer_observation.v1",
                "python": "3.12.3", "numba": "0.65.1",
                "numpy": "2.4.4", "cupy": "14.0.1",
                "llvmlite": "0.47.0", "cuda_home": cuda.as_posix(),
                "cuda_path": cuda.as_posix(),
                "numba_selected_nvvm_by": "CUDA_HOME",
                "numba_selected_nvvm_path": str(nvvm.resolve()),
                "numba_selected_nvvm_sha256": target._sha(nvvm),
                "numba_selected_libdevice_by": "CUDA_HOME",
                "numba_selected_libdevice_path": str(libdevice.resolve()),
                "numba_selected_libdevice_sha256": target._sha(libdevice),
                "numba_probe_ptx_directives": {
                    "version": "8.5", "target": "sm_89", "address_size": "64",
                },
                "loaded_nvvm_paths": [str(nvvm.resolve())],
                "loaded_nvvm_sha256": {
                    str(nvvm.resolve()): target._sha(nvvm),
                },
                "cupy_nvrtc_runtime_version": [12, 8],
                "nvrtc_probe_output": 5791,
                "loaded_nvrtc_family_paths": sorted((
                    str(nvrtc.resolve()), str(builtins.resolve()))),
                "loaded_nvrtc_family_sha256": {
                    str(nvrtc.resolve()): target._sha(nvrtc),
                    str(builtins.resolve()): target._sha(builtins),
                },
                "private_cupy_cache_initially_empty": True,
                "unique_pid_bearing_nvrtc_source": True,
                "cache_payload_is_not_authoritative_evidence": True,
                "application_input_used": False,
                "elapsed_values_recorded": False,
                "registered_performance_timing_created": False,
            }
            expected = {path.resolve() for path in (
                nvvm, libdevice, nvrtc, builtins)}
            with mock.patch.object(
                target, "_successful_absolute_trace_paths",
                return_value=expected,
            ):
                audit = target._audit_target_producer_observation(
                    observation, trace=trace, cuda=cuda)
            self.assertEqual(audit["foreign_successful_producer_opens"], [])
            foreign = root / "foreign/libnvrtc.so.12"
            foreign.parent.mkdir()
            foreign.write_bytes(b"foreign")
            with mock.patch.object(
                target, "_successful_absolute_trace_paths",
                return_value=expected | {foreign.resolve()},
            ), self.assertRaisesRegex(target.PrepareError, "foreign producer"):
                target._audit_target_producer_observation(
                    observation, trace=trace, cuda=cuda)

            nvcc = cuda / "bin/nvcc"
            host = root / "usr/bin/x86_64-linux-gnu-gcc-12"
            nvcc.parent.mkdir()
            host.parent.mkdir(parents=True)
            nvcc.write_bytes(b"nvcc")
            host.write_bytes(b"gcc")
            with mock.patch.object(
                target, "_successful_absolute_trace_paths",
                return_value={nvcc.resolve(), host.resolve()},
            ):
                build = target._audit_native_build_trace(trace, nvcc=nvcc)
            self.assertEqual(
                build["host_compiler_executed_paths"], [str(host.resolve())])

    def test_target_trace_parser_handles_real_strace_argument_positions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            opened = Path(
                "/opt/goal5791/cuda-12.8/nvvm/libdevice/"
                "libdevice.10.bc")
            benign_pyc = Path(
                "/opt/goal5791/venv/lib/python3.12/site-packages/numba/"
                "cuda/cudadrv/__pycache__/libs.cpython-312.pyc")
            failed = Path("/opt/goal5791/missing/libnvrtc.so.12")
            nvcc = Path("/opt/goal5791/cuda-12.8/bin/nvcc")
            split = Path(
                "/opt/goal5791/cuda-12.8/lib64/"
                "libnvrtc-builtins.so.12.8")
            trace = root / "real-default-strace.log"
            trace.write_text(
                "[pid 5791] openat(AT_FDCWD, "
                + json.dumps(opened.as_posix())
                + ", O_RDONLY|O_CLOEXEC) = 3\n"
                + "5791 openat(AT_FDCWD, "
                + json.dumps(benign_pyc.as_posix())
                + ", O_RDONLY|O_CLOEXEC) = 4\n"
                + "5791 openat(AT_FDCWD, "
                + json.dumps(failed.as_posix())
                + ", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file)\n"
                + "[pid 5792] openat(AT_FDCWD, "
                + json.dumps(split.as_posix())
                + ", O_RDONLY|O_CLOEXEC <unfinished ...>\n"
                + "[pid 5792] <... openat resumed>) = 5\n"
                + "[pid 5791] execve("
                + json.dumps(nvcc.as_posix())
                + ", [\"nvcc\"], 0x7fff) = 0\n",
                encoding="utf-8",
            )
            self.assertEqual(
                target._successful_absolute_trace_paths(trace, "openat"),
                {opened.resolve(), benign_pyc.resolve(), split.resolve()},
            )
            self.assertEqual(
                target._successful_absolute_trace_paths(trace, "execve"),
                {nvcc.resolve()},
            )
            self.assertNotIn(
                benign_pyc.resolve(),
                {path for path in target._successful_absolute_trace_paths(
                    trace, "openat") if target._is_cuda_producer_binary(path)},
            )
            with self.assertRaisesRegex(ValueError, "unsupported traced syscall"):
                target._successful_absolute_trace_paths(trace, "statx")

    def test_target_build_environment_overrides_poisoned_producer_ambient(self) -> None:
        poisoned = {
            "PATH": "/poison/bin",
            "CUDA_HOME": "/poison/cuda-home",
            "CUDA_PATH": "/poison/cuda-path",
            "NUMBA_CUDA_NVVM": "/poison/libnvvm.so",
            "NUMBA_CUDA_LIBDEVICE": "/poison/libdevice.bc",
            "CUDA_VISIBLE_DEVICES": "poison",
            "NVIDIA_VISIBLE_DEVICES": "poison",
            "NUMBA_DISABLE_CUDA": "1",
            "NUMBA_ENABLE_CUDASIM": "1",
            "CUDA_CACHE_PATH": "/poison/cuda-cache",
            "OPTIX_CACHE_PATH": "/poison/optix-cache",
            "CUPY_CACHE_DIR": "/poison/cupy-cache",
            "NUMBA_CACHE_DIR": "/poison/numba-cache",
            "RTDL_V4_FORMAL_LEAF_CACHE_DIR": "/poison/leaf-cache",
            "RTDL_V4_FORMAL_LEAF_CACHE_ATTACK": "poison",
            "LD_PRELOAD": "/poison/preload.so",
        }
        source = Path("/frozen/source")
        venv = Path("/fresh/venv")
        cuda = Path("/frozen/cuda-12.8")
        optix = Path("/frozen/optix-9")
        numba_cache = Path("/fresh/disposable-numba-cache")
        value = target._target_build_environment(
            poisoned, source=source, venv=venv, cuda=cuda,
            optix_root=optix, numba_cache_root=numba_cache,
        )
        self.assertEqual(value["CUDA_HOME"], str(cuda))
        self.assertEqual(value["CUDA_PATH"], str(cuda))
        self.assertEqual(value["RTDL_V4_CUDA_PREFIX"], str(cuda))
        self.assertEqual(value["RTDL_V4_OPTIX_PREFIX"], str(optix))
        self.assertEqual(value["NUMBA_CACHE_DIR"], str(numba_cache))
        self.assertEqual(
            value["PATH"].split(os.pathsep)[:2],
            [str(venv / "bin"), str(cuda / "bin")],
        )
        self.assertFalse(any(
            name in value for name in (
                "NUMBA_CUDA_NVVM", "NUMBA_CUDA_LIBDEVICE",
                "CUDA_VISIBLE_DEVICES", "NVIDIA_VISIBLE_DEVICES",
                "NUMBA_DISABLE_CUDA", "NUMBA_ENABLE_CUDASIM",
                "CUDA_CACHE_PATH", "OPTIX_CACHE_PATH",
                "CUPY_CACHE_DIR", "RTDL_V4_FORMAL_LEAF_CACHE_DIR",
                "RTDL_V4_FORMAL_LEAF_CACHE_ATTACK", "LD_PRELOAD",
            )
        ))

        # Exercise the actual subprocess/environment boundary that failed
        # Stage-A v11.  The probe models Numba's cache-root selection: the
        # subprocess must place cache material outside the writable source.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            real_source = root / "source"
            source_module_root = real_source / "src"
            source_module_root.mkdir(parents=True)
            (source_module_root / "goal5791_numba_cache_probe.py").write_text(
                "import os\n"
                "from pathlib import Path\n"
                "cache = Path(os.environ.get('NUMBA_CACHE_DIR', "
                "Path(__file__).parent / '__pycache__'))\n"
                "cache.mkdir(parents=True, exist_ok=True)\n"
                "(cache / 'cache-probe').write_bytes(b'probe')\n",
                encoding="utf-8",
            )
            external_numba_cache = root / "external_numba_cache"
            external_numba_cache.mkdir()
            actual_env = target._target_build_environment(
                dict(os.environ), source=real_source,
                venv=Path(sys.executable).parent.parent,
                cuda=root / "cuda", optix_root=root / "optix",
                numba_cache_root=external_numba_cache,
            )
            completed = subprocess.run(
                [sys.executable, "-c",
                 "import goal5791_numba_cache_probe"],
                cwd=real_source, env=actual_env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=120, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                [path.relative_to(real_source).as_posix()
                 for path in real_source.rglob("__pycache__")],
                [],
            )
            self.assertEqual(
                [path.relative_to(real_source).as_posix()
                 for path in real_source.rglob("*.pyc")],
                [],
            )
            self.assertTrue(any(external_numba_cache.rglob("*")))

    def test_target_evidence_preserves_exact_dependency_wheelhouse_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wheelhouse = root / "wheelhouse.tar.gz"
            wheelhouse.write_bytes(b"exact-wheelhouse-container-bytes")
            expected = hashlib.sha256(wheelhouse.read_bytes()).hexdigest()
            with mock.patch.object(
                target, "EXPECTED_WHEELHOUSE_SHA256", expected,
            ):
                preserved = target._preserved_dependency_wheelhouse(wheelhouse)
            evidence = root / "evidence.tar.gz"
            evidence.write_bytes(target._deterministic_archive({
                "DEPENDENCY_WHEELHOUSE.tar.gz": preserved,
            }))
            payloads = target._read_regular_archive(evidence)
            self.assertEqual(
                set(payloads), {"DEPENDENCY_WHEELHOUSE.tar.gz"})
            self.assertEqual(
                hashlib.sha256(
                    payloads["DEPENDENCY_WHEELHOUSE.tar.gz"]
                ).hexdigest(),
                expected,
            )
            rooted_archive = root / "root-directory-member.tar.gz"
            with tarfile.open(rooted_archive, "w:gz") as archive:
                root_member = tarfile.TarInfo(".")
                root_member.type = tarfile.DIRTYPE
                root_member.mode = 0o755
                archive.addfile(root_member)
                payload = b"wheel-bytes"
                wheel_member = tarfile.TarInfo("wheel.whl")
                wheel_member.size = len(payload)
                wheel_member.mode = 0o444
                archive.addfile(wheel_member, io.BytesIO(payload))
            self.assertEqual(
                target._read_regular_archive(rooted_archive),
                {"wheel.whl": b"wheel-bytes"},
            )
        source = (ROOT / "scripts/goal5791_target_prepare.py").read_text(
            encoding="utf-8")
        self.assertIn('"raw_composed_ptx_bytes_preserved": False', source)
        self.assertIn('"independent_raw_ptx_reparse_supported": False', source)

    def test_owner_stage_a_generator_self_seals_zero_worker_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base_python = root / "python3.12"
            base_python.write_bytes(b"fixture-python")
            endpoint = target._pod_endpoint_identity_record(
                ssh_user="root", host="192.0.2.91", port=25791)
            self.assertEqual(
                staging_helper._endpoint(
                    ssh_user="root", host="192.0.2.91", port=25791),
                endpoint,
            )
            remote_root = Path("/tmp/goal5791_owner_authority_fixture")
            remote_staging_root = Path(
                "/tmp/goal5791_owner_authority_staging_fixture")
            required_target = {
                "gpu_name": "NVIDIA RTX 4000 Ada Generation",
                "gpu_uuid": "GPU-fixture",
                "driver_version": "580.fixture",
                "compute_capability": "8.9",
                "cuda_toolkit_version": "12.8",
                "optix_sdk_version": "9.0.0",
                "base_python_executable_path": "/usr/bin/python3",
                "base_python_executable_sha256": target._sha(base_python),
                "base_python_version": "3.12.3",
            }
            value = owner_builder._stage_a_authority(
                bundle_sha256="1" * 64, source_sha256="2" * 64,
                data_sha256=target.EXPECTED_DATA_SHA256,
                wheelhouse_sha256=target.EXPECTED_WHEELHOUSE_SHA256,
                optix_headers_sha256=target.EXPECTED_OPTIX_HEADERS_SHA256,
                pretarget_file_sha256="3" * 64,
                formal_contract_sha256="4" * 64,
                schedule_sha256="5" * 64,
                runtime_budget_file_sha256="6" * 64,
                token_amendment_sha256="7" * 64,
                required_target=required_target,
                first_entry_stdin_bootstrap=BOOTSTRAP_RECORD,
                materialization_root=str(remote_root),
                upload_staging_root=str(remote_staging_root),
                endpoint=endpoint,
                resource={
                    "owner_confirmed_prepare_window_hours": 1.0,
                    "confirmed_free_disk_bytes": 20_000_000_000,
                    "confirmed_before_target_materialization_root_creation": True,
                },
                nonce="8" * 64,
                joint_delivery_audit=_joint_delivery_fixture(),
            )
            authority = root / "OWNER_STAGE_A.json"
            authority.write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            loaded = target._validate_owner(
                authority, bundle_sha="1" * 64, source_sha="2" * 64,
                materialization_root=str(remote_root),
                upload_staging_root=str(remote_staging_root),
                gpu={
                    "gpu_name": required_target["gpu_name"],
                    "gpu_uuid": required_target["gpu_uuid"],
                    "driver_version": required_target["driver_version"],
                    "compute_capability": required_target[
                        "compute_capability"],
                },
                base_python_sha256=target._sha(base_python),
                base_python_version="3.12.3",
                base_python_path="/usr/bin/python3",
                pod_endpoint=endpoint,
            )
            self.assertEqual(loaded["authority_sha256"], value["authority_sha256"])
            self.assertEqual(
                loaded["paid_transaction_justification"],
                target.STAGE_A_THIRD_POD_JUSTIFICATION,
            )
            self.assertEqual(
                loaded["paid_transaction_justification"][
                    "paid_transaction_ordinal_if_stage_a_is_authorized"
                ],
                3,
            )
            self.assertTrue(
                loaded["paid_transaction_justification"][
                    "third_transaction_is_cost_of_correction_not_scope_creep"
                ]
            )
            attacked = json.loads(json.dumps(value))
            attacked["paid_transaction_justification"][
                "paid_transaction_ordinal_if_stage_a_is_authorized"
            ] = 2
            attacked_unsigned = dict(attacked)
            attacked_unsigned.pop("authority_sha256", None)
            attacked["authority_sha256"] = formal_contract.digest(
                attacked_unsigned
            )
            authority.write_text(
                json.dumps(attacked, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(PermissionError):
                target._validate_owner(
                    authority, bundle_sha="1" * 64, source_sha="2" * 64,
                    materialization_root=str(remote_root),
                    upload_staging_root=str(remote_staging_root),
                    gpu={
                        "gpu_name": required_target["gpu_name"],
                        "gpu_uuid": required_target["gpu_uuid"],
                        "driver_version": required_target["driver_version"],
                        "compute_capability": required_target[
                            "compute_capability"],
                    },
                    base_python_sha256=target._sha(base_python),
                    base_python_version="3.12.3",
                    base_python_path="/usr/bin/python3",
                    pod_endpoint=endpoint,
                )
            authority.write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            home_small_chain = {
                "home_evidence_sha256": "5" * 64,
                "home_evidence_twin_sha256": "5" * 64,
                "home_evidence_twin_byte_identical": True,
            }
            outer_small_chain = {
                target.HOME_FUNCTIONAL_CLOSURE_MEMBER: _canonical_json_bytes(
                    home_small_chain),
            }
            manifest_small_chain = {
                "home_evidence_sha256": "5" * 64,
                "home_evidence_twin_sha256": "5" * 64,
            }
            target._crossbind_owner_joint_home_chain(
                loaded, outer=outer_small_chain, manifest=manifest_small_chain)
            self.assertFalse(
                loaded["authorization"]["authorizes_formal_worker_zero"])
            mutated = deepcopy(value)
            mutated["authorization"]["authorizes_formal_worker_zero"] = True
            unsigned = dict(mutated)
            unsigned.pop("authority_sha256")
            mutated["authority_sha256"] = target._digest(unsigned)
            authority.write_text(
                json.dumps(mutated, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(PermissionError, "authorization"):
                target._validate_owner(
                    authority, bundle_sha="1" * 64, source_sha="2" * 64,
                    materialization_root=str(remote_root),
                    upload_staging_root=str(remote_staging_root),
                    gpu={
                        "gpu_name": required_target["gpu_name"],
                        "gpu_uuid": required_target["gpu_uuid"],
                        "driver_version": required_target["driver_version"],
                        "compute_capability": required_target[
                            "compute_capability"],
                    },
                    base_python_sha256=target._sha(base_python),
                    base_python_version="3.12.3",
                    base_python_path="/usr/bin/python3",
                    pod_endpoint=endpoint,
                )
            mutated = deepcopy(value)
            mutated["joint_delivery_audit"]["strict_joint_audit_passed"] = False
            unsigned = dict(mutated)
            unsigned.pop("authority_sha256")
            mutated["authority_sha256"] = target._digest(unsigned)
            authority.write_text(
                json.dumps(mutated, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(PermissionError, "joint delivery"):
                target._validate_owner(
                    authority, bundle_sha="1" * 64, source_sha="2" * 64,
                    materialization_root=str(remote_root),
                    upload_staging_root=str(remote_staging_root),
                    gpu={
                        "gpu_name": required_target["gpu_name"],
                        "gpu_uuid": required_target["gpu_uuid"],
                        "driver_version": required_target["driver_version"],
                        "compute_capability": required_target[
                            "compute_capability"],
                    },
                    base_python_sha256=target._sha(base_python),
                    base_python_version="3.12.3",
                    base_python_path="/usr/bin/python3",
                    pod_endpoint=endpoint,
                )
            mutated = deepcopy(value)
            mutated["joint_delivery_audit"]["home_evidence_sha256"] = "6" * 64
            mutated["joint_delivery_audit"]["home_evidence_twin_sha256"] = (
                "6" * 64)
            unsigned = dict(mutated)
            unsigned.pop("authority_sha256")
            mutated["authority_sha256"] = target._digest(unsigned)
            authority.write_text(
                json.dumps(mutated, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            loaded = target._validate_owner(
                authority, bundle_sha="1" * 64, source_sha="2" * 64,
                materialization_root=str(remote_root),
                upload_staging_root=str(remote_staging_root),
                gpu={
                    "gpu_name": required_target["gpu_name"],
                    "gpu_uuid": required_target["gpu_uuid"],
                    "driver_version": required_target["driver_version"],
                    "compute_capability": required_target[
                        "compute_capability"],
                },
                base_python_sha256=target._sha(base_python),
                base_python_version="3.12.3",
                base_python_path="/usr/bin/python3",
                pod_endpoint=endpoint,
            )
            with self.assertRaisesRegex(PermissionError, "small-chain"):
                target._crossbind_owner_joint_home_chain(
                    loaded, outer=outer_small_chain,
                    manifest=manifest_small_chain)

    def test_owner_generator_has_explicit_separate_stage_b_mode(self) -> None:
        owner_builder._admit_loaded_generator_modules()
        source = (
            ROOT / "scripts/goal5791_build_owner_authority.py"
        ).read_text(encoding="utf-8")
        target_source = (
            ROOT / "scripts/goal5791_target_prepare.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'required=True, choices=("target-prepare", "formal")', source)
        self.assertIn("build_stage_a(args.request.resolve()", source)
        self.assertIn("build_stage_b(args.request.resolve()", source)
        self.assertIn("runtime_file_sha256", source)
        self.assertIn("runtime_sha256", source)
        self.assertIn("prepared_claimed != contract.digest", source)
        self.assertIn("len(contract.schedule())", source)
        self.assertIn("inputs[\"runtime\"].stat().st_mode & 0o222", source)
        stage_a_source = source[
            source.index("def build_stage_a("):
            source.index("def _validate_stage_a_lineage(")
        ]
        self.assertLess(
            stage_a_source.index("_write_create_only(output, value)"),
            stage_a_source.index("target_prepare._validate_owner("),
        )
        self.assertLess(
            stage_a_source.index("target_prepare._validate_owner("),
            stage_a_source.index("_seal_validated_authority(output)"),
        )
        stage_b_source = source[
            source.index("def build_stage_b("):
            source.index("def main()")
        ]
        self.assertLess(
            stage_b_source.index("_write_create_only(output, value)"),
            stage_b_source.index(
                "contract.load_owner_formal_execution_authority("),
        )
        self.assertLess(
            stage_b_source.index(
                "contract.load_owner_formal_execution_authority("),
            stage_b_source.index("_seal_validated_authority(output)"),
        )
        self.assertNotIn(
            "from scripts import goal5791_build_owner_authority", target_source)
        self.assertNotIn("build_stage_b(", target_source)
        with tempfile.TemporaryDirectory() as temporary:
            authority = Path(temporary) / "OWNER_AUTHORITY.json"
            owner_builder._write_create_only(authority, {"fixture": True})
            try:
                owner_builder._seal_validated_authority(authority)
                self.assertTrue(authority.is_file())
                self.assertFalse(authority.is_symlink())
                self.assertEqual(authority.stat().st_mode & 0o222, 0)
                authority.chmod(authority.stat().st_mode | 0o200)
                with self.assertRaisesRegex(
                    owner_builder.OwnerAuthorityError, "not a regular",
                ):
                    owner_builder._require_read_only_authority(authority)
            finally:
                authority.chmod(authority.stat().st_mode | 0o600)

    def test_stage_a_joint_external_delivery_audit_is_recomputed_and_bound(
        self,
    ) -> None:
        bundle = b"frozen-bundle"
        evidence = b"frozen-Home-evidence"
        audit_body = {
            "schema": "rtdl.goal5791.joint_bundle_home_evidence_audit.v1",
            "goal": 5791,
            "status": (
                "PASS__STRICT_JOINT_BUNDLE_AND_EXTERNAL_HOME_EVIDENCE_AUDIT"),
            "home_independent_raw_recount_reexecuted_and_byte_identical": True,
        }
        audit_receipt = {
            **audit_body,
            "receipt_sha256": portable_audit._digest(audit_body),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = {
                "bundle": root / "bundle.tar.gz",
                "bundle_twin": root / "bundle-twin.tar.gz",
                "home_evidence": root / "home.tar.gz",
                "home_evidence_twin": root / "home-twin.tar.gz",
                "joint_bundle_audit_receipt": root / "JOINT_AUDIT.json",
            }
            inputs["bundle"].write_bytes(bundle)
            inputs["bundle_twin"].write_bytes(bundle)
            inputs["home_evidence"].write_bytes(evidence)
            inputs["home_evidence_twin"].write_bytes(evidence)
            inputs["joint_bundle_audit_receipt"].write_text(
                json.dumps(audit_receipt, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            expected = {
                "joint_bundle_audit_receipt_file_sha256": target._sha(
                    inputs["joint_bundle_audit_receipt"]),
                "joint_bundle_audit_receipt_sha256": audit_receipt[
                    "receipt_sha256"],
                "independent_portable_auditor_sha256": target._sha(
                    ROOT / "scripts/goal5791_independent_portable_audit.py"),
                "bundle_sha256": target._sha_bytes(bundle),
                "bundle_twin_sha256": target._sha_bytes(bundle),
                "bundle_twin_byte_identical": True,
                "home_evidence_sha256": target._sha_bytes(evidence),
                "home_evidence_twin_sha256": target._sha_bytes(evidence),
                "home_evidence_twin_byte_identical": True,
                "strict_joint_audit_passed": True,
                "home_independent_raw_recount_reexecuted_and_byte_identical": True,
            }
            with mock.patch.object(
                portable_audit, "joint_bundle_audit_receipt",
                return_value=audit_receipt,
            ) as recompute:
                self.assertEqual(
                    owner_builder._joint_delivery_audit_record(
                        inputs=inputs, expected=expected),
                    expected,
                )
                recompute.assert_called_once_with(
                    bundle=bundle, bundle_twin=bundle,
                    home_evidence=evidence, home_evidence_twin=evidence,
                )

                changed = {**audit_receipt, "goal": 5790}
                inputs["joint_bundle_audit_receipt"].write_text(
                    json.dumps(changed, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    owner_builder.OwnerAuthorityError, "differs",
                ):
                    owner_builder._joint_delivery_audit_record(
                        inputs=inputs, expected=expected)

                inputs["joint_bundle_audit_receipt"].write_text(
                    json.dumps(audit_receipt, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                inputs["bundle_twin"].write_bytes(b"different-bundle")
                with self.assertRaisesRegex(
                    owner_builder.OwnerAuthorityError, "twins differ",
                ):
                    owner_builder._joint_delivery_audit_record(
                        inputs=inputs, expected=expected)

                inputs["bundle_twin"].write_bytes(bundle)
                false_expected = {
                    **expected, "strict_joint_audit_passed": False}
                with self.assertRaisesRegex(
                    owner_builder.OwnerAuthorityError, "identity drifted",
                ):
                    owner_builder._joint_delivery_audit_record(
                        inputs=inputs, expected=false_expected)

                inputs["joint_bundle_audit_receipt"].unlink()
                with self.assertRaises(owner_builder.OwnerAuthorityError):
                    owner_builder._joint_delivery_audit_record(
                        inputs=inputs, expected=expected)

    def test_local_stage_a_generator_cannot_claim_remote_root_observation(
        self,
    ) -> None:
        source = (
            ROOT / "scripts/goal5791_build_owner_authority.py"
        ).read_text(encoding="utf-8")
        target_source = (
            ROOT / "scripts/goal5791_target_prepare.py"
        ).read_text(encoding="utf-8")
        protocol = (
            ROOT / "history/internal_docs/"
            "goal5791_owner_authority_request_protocol_20260817.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("Path(remote_root).exists()", source)
        self.assertNotIn("Path(remote_root).is_symlink()", source)
        self.assertNotIn('"pretarget", "base_python"', source)
        self.assertIn(
            '"base_python_executable_sha256", "base_python_version"',
            source,
        )
        self.assertIn("not os.path.lexists(root)", target_source)
        self.assertIn("if os.path.lexists(root):", target_source)
        self.assertIn(
            '"target_materialization_root_observed_absent_before_creation"',
            target_source,
        )
        self.assertIn(
            "materialization_root_absence_observed_at_entry", target_source)
        self.assertIn("local Windows or Linux path", protocol)
        self.assertIn("is not evidence about that target", protocol)
        # A POSIX target spelling remains byte-exact when the local generator
        # self-validates it; it is never converted through a Windows Path.
        endpoint = target._pod_endpoint_identity_record(
            ssh_user="root", host="192.0.2.91", port=25791)
        with tempfile.TemporaryDirectory() as temporary:
            authority = Path(temporary) / "OWNER_STAGE_A.json"
            required_target = {
                "gpu_name": "NVIDIA RTX 4000 Ada Generation",
                "gpu_uuid": "GPU-fixture",
                "driver_version": "580.fixture",
                "compute_capability": "8.9",
                "cuda_toolkit_version": "12.8",
                "optix_sdk_version": "9.0.0",
                "base_python_executable_path": "/usr/bin/python3",
                "base_python_executable_sha256": "9" * 64,
                "base_python_version": "3.12.3",
            }
            value = owner_builder._stage_a_authority(
                bundle_sha256="1" * 64, source_sha256="2" * 64,
                data_sha256=target.EXPECTED_DATA_SHA256,
                wheelhouse_sha256=target.EXPECTED_WHEELHOUSE_SHA256,
                optix_headers_sha256=target.EXPECTED_OPTIX_HEADERS_SHA256,
                pretarget_file_sha256="3" * 64,
                formal_contract_sha256="4" * 64,
                schedule_sha256="5" * 64,
                runtime_budget_file_sha256="6" * 64,
                token_amendment_sha256="7" * 64,
                required_target=required_target,
                first_entry_stdin_bootstrap=BOOTSTRAP_RECORD,
                materialization_root="/tmp/goal5791-remote-only",
                upload_staging_root="/tmp/goal5791-staging-only",
                endpoint=endpoint,
                resource={
                    "owner_confirmed_prepare_window_hours": 1.0,
                    "confirmed_free_disk_bytes": 20_000_000_000,
                    "confirmed_before_target_materialization_root_creation": True,
                },
                nonce="8" * 64,
                joint_delivery_audit=_joint_delivery_fixture(),
            )
            authority.write_text(
                json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
            loaded = target._validate_owner(
                authority, bundle_sha="1" * 64, source_sha="2" * 64,
                materialization_root="/tmp/goal5791-remote-only",
                upload_staging_root="/tmp/goal5791-staging-only",
                gpu={
                    name: required_target[name] for name in (
                        "gpu_name", "gpu_uuid", "driver_version",
                        "compute_capability")
                },
                base_python_sha256="9" * 64,
                base_python_version="3.12.3",
                base_python_path="/usr/bin/python3", pod_endpoint=endpoint,
            )
            self.assertEqual(
                loaded["execution_target"]["target_materialization_root"],
                "/tmp/goal5791-remote-only",
            )

    def test_upload_staging_exact_set_receipt_and_extra_pyc_attack(self) -> None:
        self.assertEqual(
            staging_helper.STAGED_UPLOAD_RELATIVE_PATHS,
            target.STAGED_UPLOAD_RELATIVE_PATHS,
        )
        self.assertEqual(
            staging_helper.CLEANUP_DISPOSITION,
            target.UPLOAD_STAGING_CLEANUP_DISPOSITION,
        )
        self.assertIn(
            "scripts/goal5791_open_upload_staging.py",
            source_builder.OVERLAY_PATHS,
        )
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            staging = parent / "goal5791-upload-staging"
            work = parent / "goal5791-target-work"
            staging.mkdir()
            owner_sha = "a" * 64
            helper_sha = "b" * 64
            helper_size = 5791
            required_target = {
                "base_python_executable_path": "/usr/bin/python3",
                "base_python_executable_sha256": "9" * 64,
                "base_python_version": "3.12.3",
            }
            endpoint = target._pod_endpoint_identity_record(
                ssh_user="root", host="192.0.2.91", port=25791)
            staged_paths = {}
            for label, relative in target.STAGED_UPLOAD_RELATIVE_PATHS.items():
                path = staging / relative
                path.write_bytes((label + "\n").encode("utf-8"))
                staged_paths[label] = path
            receipt_body = {
                "schema": target.UPLOAD_STAGING_RECEIPT_SCHEMA,
                "goal": 5791,
                "status": target.UPLOAD_STAGING_RECEIPT_STATUS,
                "owner_target_prepare_authority_file_sha256": owner_sha,
                "bootstrap_source_sha256": BOOTSTRAP_RECORD["source_sha256"],
                "bootstrap_source_verified_before_helper_exec": True,
                "staging_helper_source_sha256": helper_sha,
                "observed_staging_helper_size_bytes": helper_size,
                "staging_helper_verified_before_exec": True,
                "python_executable_path": "/usr/bin/python3",
                "python_executable_sha256": "9" * 64,
                "python_version": "3.12.3",
                "python_identity_verified_before_root_creation": True,
                "upload_staging_root": str(staging),
                "target_materialization_root": str(work),
                "pod_endpoint": endpoint,
                "both_roots_observed_absent_before_staging_creation": True,
                "upload_staging_root_created_create_only": True,
                "target_materialization_root_created_by_staging_helper": False,
                "expected_uploaded_relative_paths": (
                    target.STAGED_UPLOAD_RELATIVE_PATHS),
                "upload_staging_cleanup_disposition": (
                    target.UPLOAD_STAGING_CLEANUP_DISPOSITION),
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
            }
            receipt = {
                **receipt_body, "receipt_sha256": target._digest(receipt_body)}
            receipt_path = staging / target.UPLOAD_STAGING_RECEIPT_NAME
            receipt_path.write_text(
                json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
            all_paths = list(staged_paths.values()) + [receipt_path]
            try:
                for path in all_paths:
                    path.chmod(path.stat().st_mode & ~0o222)
                identity = target._validate_upload_staging(
                    staging_root=staging, materialization_root=work,
                    staged_paths=staged_paths,
                    owner_authority_sha256=owner_sha,
                    staging_helper_sha256=helper_sha,
                    staging_helper_size_bytes=helper_size,
                    first_entry_stdin_bootstrap=BOOTSTRAP_RECORD,
                    required_target=required_target,
                    pod_endpoint=endpoint,
                )
                self.assertTrue(identity["exact_regular_file_set"])
                self.assertEqual(len(identity["staged_inputs"]), 7)
                with self.assertRaisesRegex(
                    target.PrepareError, "receipt drifted",
                ):
                    target._validate_upload_staging(
                        staging_root=staging, materialization_root=work,
                        staged_paths=staged_paths,
                        owner_authority_sha256=owner_sha,
                        staging_helper_sha256="c" * 64,
                        staging_helper_size_bytes=helper_size,
                        first_entry_stdin_bootstrap=BOOTSTRAP_RECORD,
                        required_target=required_target,
                        pod_endpoint=endpoint,
                    )
                wrong_bootstrap = dict(BOOTSTRAP_RECORD)
                wrong_bootstrap["source_sha256"] = "d" * 64
                with self.assertRaisesRegex(
                    target.PrepareError, "receipt drifted",
                ):
                    target._validate_upload_staging(
                        staging_root=staging, materialization_root=work,
                        staged_paths=staged_paths,
                        owner_authority_sha256=owner_sha,
                        staging_helper_sha256=helper_sha,
                        staging_helper_size_bytes=helper_size,
                        first_entry_stdin_bootstrap=wrong_bootstrap,
                        required_target=required_target,
                        pod_endpoint=endpoint,
                    )
                extra = staging / "injected.pyc"
                extra.write_bytes(b"not allowed")
                extra.chmod(extra.stat().st_mode & ~0o222)
                all_paths.append(extra)
                with self.assertRaisesRegex(
                    target.PrepareError, "exact file set",
                ):
                    target._validate_upload_staging(
                        staging_root=staging, materialization_root=work,
                        staged_paths=staged_paths,
                        owner_authority_sha256=owner_sha,
                        staging_helper_sha256=helper_sha,
                        staging_helper_size_bytes=helper_size,
                        first_entry_stdin_bootstrap=BOOTSTRAP_RECORD,
                        required_target=required_target,
                        pod_endpoint=endpoint,
                    )
                extra.chmod(extra.stat().st_mode | 0o600)
                extra.unlink()
                all_paths.remove(extra)
                writable = staged_paths["bundle"]
                writable.chmod(writable.stat().st_mode | 0o200)
                with self.assertRaisesRegex(
                    target.PrepareError, "remains writable",
                ):
                    target._validate_upload_staging(
                        staging_root=staging, materialization_root=work,
                        staged_paths=staged_paths,
                        owner_authority_sha256=owner_sha,
                        staging_helper_sha256=helper_sha,
                        staging_helper_size_bytes=helper_size,
                        first_entry_stdin_bootstrap=BOOTSTRAP_RECORD,
                        required_target=required_target,
                        pod_endpoint=endpoint,
                    )
                writable.chmod(writable.stat().st_mode & ~0o222)
            finally:
                for path in all_paths:
                    if path.exists():
                        path.chmod(path.stat().st_mode | 0o600)

    def test_first_entry_bootstrap_rejects_wrong_or_truncated_bytes_before_exec(
        self,
    ) -> None:
        source = staging_helper.FIRST_ENTRY_STDIN_BOOTSTRAP_SOURCE
        source_bytes = source.encode("utf-8")
        executable = os.path.abspath(sys.executable)
        executable_sha = hashlib.sha256(Path(executable).read_bytes()).hexdigest()

        def execute(
            helper_bytes: bytes, *, expected_bootstrap_sha: str | None = None,
            expected_helper_sha: str | None = None,
            expected_python_sha: str | None = None,
        ) -> None:
            command_line = b"\0".join((
                executable.encode(), b"-c", source_bytes, b"",
            ))

            class FakePath:
                def __init__(self, spelling: str) -> None:
                    if spelling != "/proc/self/cmdline":
                        raise AssertionError(spelling)

                def read_bytes(self) -> bytes:
                    return command_line

            fake_pathlib = types.ModuleType("pathlib")
            fake_pathlib.Path = FakePath
            old_argv = sys.argv
            old_stdin = sys.stdin
            try:
                sys.argv = [
                    "-c",
                    expected_bootstrap_sha or hashlib.sha256(
                        source_bytes).hexdigest(),
                    expected_helper_sha or hashlib.sha256(
                        helper_bytes).hexdigest(),
                    executable,
                    expected_python_sha or executable_sha,
                    platform.python_version(),
                ]
                sys.stdin = types.SimpleNamespace(buffer=io.BytesIO(helper_bytes))
                with mock.patch.dict(sys.modules, {"pathlib": fake_pathlib}):
                    namespace: dict[str, object] = {}
                    exec(
                        compile(source, "<bootstrap-test>", "exec"),
                        namespace, namespace,
                    )
            finally:
                sys.argv = old_argv
                sys.stdin = old_stdin

        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "helper-executed"
            full_helper = (
                f"with open({str(marker)!r}, 'w', encoding='utf-8') as stream:\n"
                "    stream.write('yes')\n"
            ).encode("utf-8")
            execute(full_helper)
            self.assertEqual(marker.read_text(encoding="utf-8"), "yes")
            marker.unlink()

            with self.assertRaisesRegex(SystemExit, "93"):
                execute(
                    full_helper[:-1],
                    expected_helper_sha=hashlib.sha256(full_helper).hexdigest(),
                )
            self.assertFalse(marker.exists())

            with self.assertRaisesRegex(SystemExit, "92"):
                execute(full_helper, expected_bootstrap_sha="1" * 64)
            self.assertFalse(marker.exists())

            with self.assertRaisesRegex(SystemExit, "94"):
                execute(full_helper, expected_python_sha="2" * 64)
            self.assertFalse(marker.exists())

        self.assertLess(
            source.index("actual_bootstrap_sha != expected_bootstrap_sha"),
            source.index("exec(compile(helper"),
        )
        self.assertLess(
            source.index("actual_helper_sha != expected_helper_sha"),
            source.index("exec(compile(helper"),
        )
        wrong_observation = _first_entry_observation(
            helper_sha256="3" * 64, helper_size_bytes=10)
        wrong_observation["bootstrap_source_sha256"] = "4" * 64
        with self.assertRaisesRegex(
            staging_helper.UploadStagingError, "bootstrap observation",
        ):
            staging_helper._first_entry_observation(wrong_observation)

    def test_page_cache_scope_uses_only_shared_long_field_names(self) -> None:
        expected_scope = (
            "uncontrolled_same_cohort_balanced_pair_parity_interleaving")
        self.assertEqual(
            formal_contract.CACHE_POLICY[
                "operating_system_page_cache_scope"],
            expected_scope,
        )
        self.assertEqual(
            recount.EXPECTED_CACHE_POLICY[
                "operating_system_page_cache_scope"],
            expected_scope,
        )
        for relative in (
            "scripts/goal5791_target_prepare.py",
            "scripts/goal5791_home_clean_validate.py",
            "scripts/goal5791_independent_home_recount.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn('"os_page_cache_', source)
            self.assertNotIn("warm_os_page_cache", source)
            self.assertIn("operating_system_page_cache_scope", source)

    def test_stage_a_capacity_and_stage_b_split_root_schema_are_explicit(
        self,
    ) -> None:
        target_source = (
            ROOT / "scripts/goal5791_target_prepare.py"
        ).read_text(encoding="utf-8")
        owner_source = (
            ROOT / "scripts/goal5791_build_owner_authority.py"
        ).read_text(encoding="utf-8")
        self.assertIn("shutil.disk_usage(materialization_parent).free", target_source)
        self.assertIn('nvidia_smi = Path("/usr/bin/nvidia-smi")', target_source)
        self.assertIn(
            '"target_materialization_resource_admission_sha256"',
            target_source,
        )
        self.assertIn(
            '"TARGET_MATERIALIZATION_RESOURCE_ADMISSION.json"',
            target_source,
        )
        for name in (
            "target_materialization_root",
            "create_only_formal_output_root",
            "controller_incomplete_staging_root",
            "target_materialization_root_observed_existing_and_bound_at_authority_creation",
            "formal_output_root_observed_absent_at_authority_creation",
            "controller_incomplete_staging_root_observed_absent_at_authority_creation",
            "preexisting_or_shared_formal_output_root_allowed",
            "formal_output_parent_resolved_path",
            "formal_output_parent_free_bytes_observed_at_authority_creation",
            "minimum_required_free_disk_bytes",
        ):
            self.assertIn(f'"{name}"', owner_source)
        self.assertIn("shutil.disk_usage(formal_output_parent).free", owner_source)
        self.assertIn("os.path.lexists(formal_output_path)", owner_source)
        self.assertIn("os.path.lexists(controller_staging_path)", owner_source)
        self.assertNotIn('"create_only_remote_root"', owner_source)
        self.assertNotIn('"create_only_remote_root"', target_source)

        home_source = (
            ROOT / "scripts/goal5791_home_clean_validate.py"
        ).read_text(encoding="utf-8")
        self.assertIn('nvidia_smi = Path("/usr/bin/nvidia-smi")', home_source)
        bundle_source = (
            ROOT / "scripts/goal5791_build_pre_pod_bundle.py"
        ).read_text(encoding="utf-8")
        self.assertIn("canonical_readme", bundle_source)
        runbook = bundle_builder._readme(
            source_sha256="1" * 64, source_tree_sha256="2" * 64,
        ).decode("utf-8")
        self.assertIn("launched with `env -i`", runbook)
        self.assertIn("through `/usr/bin/nvidia-smi`", runbook)
        for forbidden in (
            "three_roots_are_distinct_same_parent_siblings",
            "formal_output_or_staging_inside_materialization_allowed",
            "target_materialization_root_preexists_for_bound_stage_a",
            "controller_staging_root_observed_absent_at_authority_creation",
        ):
            self.assertNotIn(f'"{forbidden}"', owner_source)

    def test_target_prepare_freezes_minimal_worker_environment(self) -> None:
        source = (ROOT / "scripts/goal5791_target_prepare.py").read_text(
            encoding="utf-8")
        tree = ast.parse(source)
        assignment = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and any(
                isinstance(item, ast.Name) and item.id == "formal_environment"
                for item in node.targets
            ):
                assignment = node.value
                break
        self.assertIsInstance(assignment, ast.Dict)
        assert isinstance(assignment, ast.Dict)
        ordered_keys = [ast.literal_eval(key) for key in assignment.keys]
        keys = set(ordered_keys)
        self.assertEqual(keys, {
            "PYTHONPATH", "PATH", "PYTHONHASHSEED",
            "PYTHONDONTWRITEBYTECODE", "PYTHONNOUSERSITE",
            "LC_ALL",
            "CUDA_HOME", "CUDA_PATH", "LD_LIBRARY_PATH", "LD_PRELOAD",
            "RTDL_OPTIX_LIB", "RTDL_OPTIX_LIBRARY",
            "RTDL_V4_CUDA_PREFIX", "RTDL_V4_OPTIX_PREFIX",
        })
        self.assertNotIn("CUPY_CACHE_DIR", keys)
        self.assertEqual(
            ordered_keys,
            formal_contract.FORMAL_WORKER_ENVIRONMENT_CONTRACT["frozen_keys"],
        )
        self.assertIn('"LD_PRELOAD": ""', source)
        self.assertIn('"LC_ALL": "C.UTF-8"', source)
        self.assertIn("formal_environment_locale_probe.log", source)
        self.assertIn(
            'contract.FORMAL_EXECUTION_POLICY[\n        "per_worker_timeout_seconds"]',
            source,
        )
        self.assertIn(
            'frozen_runtime_budget["formal_conservative_budget_seconds"]',
            source,
        )
        self.assertIn('"llvmlite_version": identity["llvmlite"]', source)

    def test_target_prepare_cannot_create_stage_b_or_formal_workers(self) -> None:
        target_path = ROOT / "scripts/goal5791_target_prepare.py"
        source = target_path.read_text(encoding="utf-8")
        target_tree = ast.parse(source)

        def assigned_dict_keys(tree: ast.AST, name: str) -> set[str]:
            matches: list[set[str]] = []
            for node in ast.walk(tree):
                if not isinstance(node, ast.Assign) or not any(
                    isinstance(candidate, ast.Name) and candidate.id == name
                    for candidate in node.targets
                ) or not isinstance(node.value, ast.Dict):
                    continue
                keys = {
                    key.value for key in node.value.keys
                    if isinstance(key, ast.Constant)
                    and isinstance(key.value, str)
                }
                matches.append(keys)
            self.assertEqual(len(matches), 1, name)
            return matches[0]

        target_hash_keys = assigned_dict_keys(target_tree, "hashes")
        runtime_body_keys = assigned_dict_keys(target_tree, "runtime_body")
        receipt_body_keys = assigned_dict_keys(target_tree, "receipt_body")
        self.assertEqual(target_hash_keys, set(formal_contract.TARGET_HASH_SLOTS))
        self.assertNotIn("prepared_identity_record", target_hash_keys)
        self.assertIn("prepared_identity_record", receipt_body_keys)

        runtime_field_sets: list[set[str]] = []
        for relative_path, assignment in (
            ("scripts/goal5791_formal_worker.py", "_RUNTIME_KEYS"),
            ("scripts/goal5791_formal_evaluate.py", "RUNTIME_FIELDS"),
            ("scripts/goal5791_formal_independent_recount.py", "RUNTIME_FIELDS"),
        ):
            tree = ast.parse((ROOT / relative_path).read_text(encoding="utf-8"))
            values: list[set[str]] = []
            for node in ast.walk(tree):
                if not isinstance(node, ast.Assign) or not any(
                    isinstance(candidate, ast.Name)
                    and candidate.id == assignment
                    for candidate in node.targets
                ) or not isinstance(node.value, ast.Set):
                    continue
                values.append({
                    item.value for item in node.value.elts
                    if isinstance(item, ast.Constant)
                    and isinstance(item.value, str)
                })
            self.assertEqual(len(values), 1, relative_path)
            runtime_field_sets.append(values[0])
        expected_runtime_keys = runtime_body_keys | {"runtime_sha256"}
        self.assertEqual(runtime_field_sets, [expected_runtime_keys] * 3)

        prepared_record_keys = (
            assigned_dict_keys(target_tree, "prepared_identity_preimage")
            | assigned_dict_keys(target_tree, "prepared_identity_record")
        )
        self.assertEqual(prepared_record_keys, {
            "schema", "runtime_identity_sha256",
            "target_materialization_authority_sha256",
            "target_evidence_archive_sha256",
            "target_functional_summary_sha256",
            "owner_prepare_authority_sha256",
            "upload_staging_identity_sha256", "prepared_identity_sha256",
        })
        self.assertEqual(target.PRETARGET_AUTHORITY_MEMBER, (
            "history/internal_docs/"
            "goal5791_pretarget_preexecution_authority_v9_20260820.json"
        ))
        self.assertNotIn("OWNER_FORMAL_EXECUTION_AUTHORITY_SCHEMA", source)
        self.assertNotIn("load_owner_formal_execution_authority", source)
        self.assertIn("source_archive, runtime_path,", source)
        self.assertIn(
            '"owner_stage_b_must_pin_exact_runtime_file_and_runtime_sha256": True',
            source,
        )
        self.assertIn('"runtime_reseal_after_owner_stage_b_allowed": False', source)
        self.assertIn('"owner_stage_b_formal_authority_created": False', source)
        self.assertIn('"formal_worker_count": 0', source)
        self.assertIn('"registered_performance_timing_count": 0', source)

    def test_owner_preflight_failure_precedes_any_bundle_parse_or_exec(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "untrusted_bundle.tar.gz"
            bundle.write_bytes(b"attacker-controlled executable payload")
            parse = mock.Mock(side_effect=AssertionError(
                "bundle parser ran before owner preflight"))
            execute = mock.Mock(side_effect=AssertionError(
                "bundle auditor executed before owner preflight"))
            with mock.patch.object(
                target, "_validate_owner_prebundle",
                side_effect=PermissionError("owner pin rejected"),
            ), mock.patch.object(target, "_validate_bundle", parse), \
                    mock.patch.object(target, "_load_bundle_auditor", execute):
                with self.assertRaisesRegex(PermissionError, "owner pin"):
                    target._owner_pinned_bundle_admission(
                        authority=root / "bad-owner.json",
                        bundle=bundle,
                        materialization_root=root / "materialization",
                        upload_staging_root=root / "staging",
                        pod_endpoint={"host": "invalid"},
                    )
            parse.assert_not_called()
            execute.assert_not_called()

    def test_wrong_embedded_auditor_is_rejected_before_exec(self) -> None:
        trusted_bytes = (
            ROOT / "scripts/goal5791_independent_portable_audit.py"
        ).read_bytes()
        self.assertEqual(
            hashlib.sha256(trusted_bytes).hexdigest(),
            target.TRUSTED_INDEPENDENT_PORTABLE_AUDITOR_SHA256,
        )
        self.assertEqual(
            portable_audit.FORMAL_CONTRACT_FILE_SHA256,
            hashlib.sha256(
                (ROOT / "scripts/goal5791_formal_contract.py").read_bytes()
            ).hexdigest(),
        )
        self.assertEqual(
            portable_audit.FORMAL_CONTRACT_SHA256,
            formal_contract.contract_sha256(),
        )
        with mock.patch("builtins.exec") as execute:
            with self.assertRaisesRegex(target.PrepareError, "not trusted"):
                target._load_bundle_auditor(
                    b"raise SystemExit('attacker-controlled bundle Python')\n")
        execute.assert_not_called()

    def test_target_pre_root_source_audit_is_pure_memory(self) -> None:
        frozen_manifest_path = ROOT.joinpath(
            *source_builder.NEW_MANIFEST.split("/"))
        if frozen_manifest_path.is_file():
            frozen_manifest = json.loads(
                frozen_manifest_path.read_text(encoding="utf-8"))
            payloads = {}
            for row in frozen_manifest["files"]:
                name = row["path"]
                path = ROOT.joinpath(*name.split("/"))
                data = path.read_bytes()
                self.assertEqual(len(data), row["size_bytes"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), row["sha256"])
                payloads[name] = data
            base_manifest = json.loads(
                payloads[source_builder.PRESERVED_BASE_MANIFEST_MEMBER])
        else:
            base = source_builder._read_archive(
                source_builder.BASE_SOURCE.read_bytes())
            base_manifest = source_builder._verify_base(base)
            payloads = dict(base)
            preserved = payloads.pop(source_builder.BASE_MANIFEST)
            payloads[source_builder.PRESERVED_BASE_MANIFEST_MEMBER] = preserved
            for name in source_builder.OVERLAY_PATHS:
                payloads[name] = ROOT.joinpath(*name.split("/")).read_bytes()
            payloads[source_builder.BUILDER_MEMBER] = (
                ROOT / source_builder.BUILDER_MEMBER).read_bytes()
        rows = source_builder._canonical_rows(payloads)
        manifest = (json.dumps({
            "schema": "rtdl.goal5791.portable_source_manifest.v1",
            "goal": 5791,
            "status": "PORTABLE_SOURCE_FROZEN__HOME_REQUALIFICATION_REQUIRED",
            "base_source_archive_sha256": source_builder.BASE_SOURCE_SHA256,
            "base_source_manifest_sha256": source_builder.BASE_MANIFEST_SHA256,
            "base_source_tree_sha256": source_builder.BASE_TREE_SHA256,
            "base_source_file_count_excluding_manifest": base_manifest[
                "file_count_excluding_this_manifest"],
            "old_source_manifest_removed": source_builder.BASE_MANIFEST,
            "product_delta_paths": sorted(source_builder.PRODUCT_DELTA),
            "product_delta": source_builder.PRODUCT_DELTA,
            "nonproduct_overlay_count_including_builder": (
                len(source_builder.OVERLAY_PATHS) + 2
                - len(source_builder.PRODUCT_DELTA)),
            "deep_blob_audit": source_builder._deep_audit(payloads),
            "manifest_is_non_self_referential": True,
            "file_count_excluding_this_manifest": len(rows),
            "source_tree_sha256": source_builder._tree_sha(rows),
            "home_or_target_execution_count": 0,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "files": rows,
        }, indent=2, sort_keys=True) + "\n").encode("utf-8")
        archive = source_builder._archive({
            **payloads, source_builder.NEW_MANIFEST: manifest,
        })
        overlay_hashes = {
            name: hashlib.sha256(payloads[name]).hexdigest()
            for name in source_builder.OVERLAY_PATHS
        }
        with mock.patch.object(
            portable_audit, "_frozen_builder_overlay_contract",
            return_value=(
                tuple(source_builder.OVERLAY_PATHS), overlay_hashes,
                source_builder.BUILDER_MEMBER,
                source_builder.PRESERVED_BASE_MANIFEST_MEMBER,
            ),
        ), mock.patch.object(
            portable_audit.tempfile, "TemporaryDirectory",
            side_effect=AssertionError("pre-root filesystem write attempted"),
        ):
            summary = portable_audit.audit_source(
                archive, perform_clean_extraction=False)
        self.assertEqual(
            summary["clean_extraction"]["regular_file_count"],
            len(payloads) + 1,
        )
        target_source = (ROOT / "scripts/goal5791_target_prepare.py").read_text(
            encoding="utf-8")
        self.assertIn("perform_clean_extraction=False", target_source)

    def test_home_ptx_producer_observation_is_exact_and_authority_bound(
        self,
    ) -> None:
        authority = json.loads((ROOT / (
            "history/internal_docs/"
            "goal5790_frozen_home_machine_authority_20260816.json"
        )).read_text(encoding="utf-8"))
        observation = {
            "schema": "rtdl.goal5790.home_ptx_producer_observation.v1",
            **portable_audit.HOME_QUALIFICATION_DEPENDENCY_IDENTITY,
            "cuda_home": authority["cuda_toolkit_resolved_path"],
            "cuda_path": authority["cuda_toolkit_resolved_path"],
            "numba_selected_nvvm_by": "CUDA_HOME",
            "numba_selected_nvvm_path": authority["cuda_nvvm_resolved_path"],
            "numba_selected_nvvm_sha256": authority["cuda_nvvm_sha256"],
            "numba_selected_libdevice_by": "CUDA_HOME",
            "numba_selected_libdevice_path": authority[
                "cuda_libdevice_resolved_path"],
            "numba_selected_libdevice_sha256": authority[
                "cuda_libdevice_sha256"],
            "numba_probe_ptx_sha256": "1" * 64,
            "numba_probe_ptx_directives": {
                "version": "8.2", "target": "sm_61", "address_size": "64",
            },
            "loaded_nvvm_paths": [authority["cuda_nvvm_resolved_path"]],
            "cupy_nvrtc_runtime_version": authority[
                "cuda_nvrtc_runtime_version"],
            "nvrtc_probe_source_sha256": "2" * 64,
            "nvrtc_probe_output": 5790,
            "loaded_nvrtc_family_paths": sorted((
                authority["cuda_nvrtc_resolved_path"],
                authority["cuda_nvrtc_builtins_resolved_path"],
            )),
            "elapsed_values_recorded": False,
            "application_input_used": False,
            "registered_performance_timing_created": False,
        }
        portable_audit._validate_home_ptx_producer_observation(
            observation, home_authority=authority)
        target_observation = deepcopy(observation)
        target_observation["numba_probe_ptx_sha256"] = "3" * 64
        target_observation["nvrtc_probe_source_sha256"] = "4" * 64
        self.assertEqual(
            home._target_bound_producer_observation(
                observation,
                {"ptx_producer_observation": target_observation},
            ),
            target_observation,
        )
        stable_drift = deepcopy(target_observation)
        stable_drift["cuda_home"] = "/foreign/cuda"
        with self.assertRaisesRegex(RuntimeError, "stable identity"):
            home._target_bound_producer_observation(
                observation,
                {"ptx_producer_observation": stable_drift},
            )
        harness_source = (
            ROOT / "scripts/goal5791_home_clean_validate.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            '"ptx_producer_observation": target_producer_observation',
            harness_source,
        )
        self.assertIn(
            "json.dumps(\n                target_producer_observation",
            harness_source,
        )
        for mutation in (
            {**observation, "extra": False},
            {**observation, "loaded_nvvm_paths": []},
            {**observation, "nvrtc_probe_output": 5791},
        ):
            with self.assertRaisesRegex(
                portable_audit.IndependentPortableAuditError,
                "producer observation",
            ):
                portable_audit._validate_home_ptx_producer_observation(
                    mutation, home_authority=authority)

        expected_producers = {
            "/cuda/lib/libnvrtc.so.12.2.140",
            "/cuda/lib/libnvrtc-builtins.so.12.2.140",
            "/cuda/lib/libnvvm.so.4.0.0",
            "/cuda/nvvm/libdevice/libdevice.10.bc",
        }

        def trace(paths: set[str]) -> bytes:
            return "".join(
                f'openat(AT_FDCWD, "{path}", O_RDONLY) = 3\n'
                for path in sorted(paths)
            ).encode("utf-8")

        loader_alias = "/cuda/lib/libnvrtc-builtins.so.12.2"
        accepted_trace = trace(expected_producers | {loader_alias})
        self.assertEqual(
            portable_audit._validate_home_trace_producer_opens(
                accepted_trace, expected_producers=expected_producers),
            {
                "successful_exact_producer_opens": sorted(expected_producers),
                "foreign_successful_producer_opens": [],
                "trace_sha256": hashlib.sha256(accepted_trace).hexdigest(),
            },
        )
        for rejected_paths in (
            expected_producers - {
                "/cuda/lib/libnvrtc-builtins.so.12.2.140"},
            expected_producers | {"/foreign/lib/libnvrtc.so.11"},
            expected_producers | {"/cuda/lib/libnvrtc-builtins.so.11"},
        ):
            with self.assertRaisesRegex(
                portable_audit.IndependentPortableAuditError,
                "producer-open exact/alias set",
            ):
                portable_audit._validate_home_trace_producer_opens(
                    trace(rejected_paths),
                    expected_producers=expected_producers,
                )

    def test_resigned_source_receipt_governance_fields_are_rejected(
        self,
    ) -> None:
        discovered = cpu_test_gate._flatten(
            unittest.defaultTestLoader.loadTestsFromNames(
                cpu_test_gate.WORKSPACE_CPU_TEST_MODULES))
        full_ids = [item.id() for item in discovered]
        excluded = list(
            cpu_test_gate.CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS)
        clean_ids = [item for item in full_ids if item not in set(excluded)]

        def gate(scope: str) -> dict[str, object]:
            selected = full_ids if scope == "workspace" else clean_ids
            empty_outcomes = {
                "failures": [], "errors": [], "skipped": [],
                "expectedFailures": [], "unexpectedSuccesses": [],
            }
            return {
                "schema": cpu_test_gate.SCHEMA,
                "scope": scope,
                "python_role": "current_interpreter",
                "entrypoint": source_builder.CPU_TEST_GATE_MEMBER,
                "workspace_test_modules": list(
                    cpu_test_gate.WORKSPACE_CPU_TEST_MODULES),
                "workspace_test_module_count": 11,
                "workspace_test_modules_sha256": (
                    cpu_test_gate.WORKSPACE_CPU_TEST_MODULES_SHA256),
                "discovered_workspace_test_ids": full_ids,
                "discovered_workspace_test_count": len(full_ids),
                "discovered_workspace_test_ids_sha256": (
                    cpu_test_gate.EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256),
                "excluded_external_only_test_ids": excluded,
                "excluded_external_only_test_count": 6,
                "excluded_external_only_test_ids_sha256": (
                    cpu_test_gate.
                    CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256),
                "selected_test_ids": selected,
                "selected_test_count": len(selected),
                "selected_test_ids_sha256": portable_audit._digest(selected),
                "environment_contract": cpu_test_gate.ENVIRONMENT_CONTRACT,
                "test_result": {
                    "testsRun": len(selected),
                    "failures": 0,
                    "errors": 0,
                    "skipped": 0,
                    "expectedFailures": 0,
                    "unexpectedSuccesses": 0,
                },
                "outcome_test_ids": empty_outcomes,
                "outcome_test_ids_sha256": portable_audit._digest(
                    empty_outcomes),
                "failure_test_ids": [],
                "error_test_ids": [],
                "failure_exception_summaries": [],
                "error_exception_summaries": [],
                "success": True,
                "reported_elapsed_value_count": 0,
                "test_or_scientific_clock_sample_count": 0,
                "registered_performance_timing_count": 0,
                "operational_timeout_watchdog_uses_host_clock": True,
                "operational_watchdog_clock_not_persisted_or_registered": True,
            }

        try:
            raise AssertionError(
                f"False is not true : "
                f"{ROOT / 'history/internal_docs/missing.json'}")
        except AssertionError:
            stable_summary = cpu_test_gate._stable_exception_summary(
                root=ROOT, test_id=clean_ids[0], outcome="failure",
                error=sys.exc_info())
        self.assertEqual(
            stable_summary["summary"],
            "False is not true : <SOURCE_ROOT>/history/internal_docs/missing.json",
        )
        failed_clean = gate("clean")
        failed_outcomes = deepcopy(failed_clean["outcome_test_ids"])
        failed_outcomes["failures"] = [clean_ids[0]]
        failed_clean.update({
            "outcome_test_ids": failed_outcomes,
            "outcome_test_ids_sha256": portable_audit._digest(
                failed_outcomes),
            "failure_test_ids": [clean_ids[0]],
            "failure_exception_summaries": [stable_summary],
            "test_result": {
                **failed_clean["test_result"], "failures": 1,
            },
            "success": False,
        })
        source_builder._validate_cpu_test_gate_result(
            failed_clean, scope="clean", require_success=False)
        with self.assertRaisesRegex(RuntimeError, "identity/result"):
            source_builder._validate_cpu_test_gate_result(
                failed_clean, scope="clean", require_success=True)
        with mock.patch.object(
            source_builder.subprocess, "run",
            return_value=types.SimpleNamespace(
                returncode=1,
                stdout=json.dumps(failed_clean, sort_keys=True) + "\n",
            ),
        ):
            with self.assertRaisesRegex(
                RuntimeError, "failure_test_ids=.*test_resigned",
            ):
                source_builder._cpu_test_gate(ROOT, scope="clean")
        with mock.patch.object(
            source_builder.subprocess, "run",
            return_value=types.SimpleNamespace(
                returncode=0,
                stdout=json.dumps(failed_clean, sort_keys=True) + "\n",
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "identity/result"):
                source_builder._cpu_test_gate(ROOT, scope="clean")
        successful_clean = gate("clean")
        with mock.patch.object(
            source_builder.subprocess, "run",
            return_value=types.SimpleNamespace(
                returncode=1,
                stdout=json.dumps(successful_clean, sort_keys=True) + "\n",
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "exit/result drifted"):
                source_builder._cpu_test_gate(ROOT, scope="clean")
        foreign_failure = deepcopy(failed_clean)
        foreign_failure["outcome_test_ids"]["failures"] = [excluded[0]]
        foreign_failure["outcome_test_ids_sha256"] = portable_audit._digest(
            foreign_failure["outcome_test_ids"])
        foreign_failure["failure_test_ids"] = [excluded[0]]
        foreign_failure["failure_exception_summaries"][0]["test_id"] = (
            excluded[0])
        with self.assertRaisesRegex(RuntimeError, "outcome IDs"):
            source_builder._validate_cpu_test_gate_result(
                foreign_failure, scope="clean", require_success=False)
        overlap = deepcopy(failed_clean)
        overlap["outcome_test_ids"]["errors"] = [clean_ids[0]]
        overlap["outcome_test_ids_sha256"] = portable_audit._digest(
            overlap["outcome_test_ids"])
        overlap["error_test_ids"] = [clean_ids[0]]
        overlap["error_exception_summaries"] = [{
            **stable_summary, "outcome": "error",
        }]
        overlap["test_result"]["errors"] = 1
        with self.assertRaisesRegex(RuntimeError, "classes overlap"):
            source_builder._validate_cpu_test_gate_result(
                overlap, scope="clean", require_success=False)
        private_summary = deepcopy(failed_clean)
        private_summary["failure_exception_summaries"][0]["summary"] = (
            "C:/Users/private/AppData/Local/Temp/leak")
        with self.assertRaisesRegex(RuntimeError, "outcome evidence"):
            source_builder._validate_cpu_test_gate_result(
                private_summary, scope="clean", require_success=False)

        builder_bytes = (
            ROOT / source_builder.BUILDER_MEMBER).read_bytes()
        helper_bytes = (
            ROOT / source_builder.CPU_TEST_GATE_MEMBER).read_bytes()
        receipt = {
            "goal": 5791,
            "schema": "rtdl.goal5791.portable_source_build_receipt.v26",
            "base_source_archive_path": (
                portable_audit.BASE_SOURCE_ARCHIVE_PATH),
            "output_path": portable_audit.CANONICAL_SOURCE_OUTPUT_PATH,
            "twin_path": portable_audit.CANONICAL_SOURCE_TWIN_PATH,
            "cpu_test_timeout_seconds": 1_200,
            "cpu_test_gate_helper_member": source_builder.CPU_TEST_GATE_MEMBER,
            "cpu_test_gate_helper_sha256": hashlib.sha256(
                helper_bytes).hexdigest(),
            "workspace_cpu_test_gate_result": gate("workspace"),
            "clean_cpu_test_gate_result": gate("clean"),
            "reported_elapsed_value_count": 0,
            "test_or_scientific_clock_sample_count": 0,
            "operational_timeout_watchdog_uses_host_clock": True,
            "operational_watchdog_clock_not_persisted_or_registered": True,
        }
        portable_audit._validate_source_receipt_governance(
            receipt, builder_bytes=builder_bytes, helper_bytes=helper_bytes)
        source_payloads = {
            source_builder.BUILDER_MEMBER: builder_bytes,
            source_builder.CPU_TEST_GATE_MEMBER: helper_bytes,
        }
        bundle_builder._validate_source_cpu_gate_binding(
            receipt, source_payloads=source_payloads)
        fake_auditor = types.SimpleNamespace(
            _validate_source_receipt_governance=lambda value, **kwargs: (
                portable_audit._validate_source_receipt_governance(
                    value, **kwargs)))
        target._validate_source_cpu_gate_binding(
            source_receipt=receipt, source_payloads=source_payloads,
            auditor=fake_auditor,
        )
        with self.assertRaises(target.PrepareError):
            target._validate_source_cpu_gate_binding(
                source_receipt=receipt,
                source_payloads={
                    **source_payloads,
                    source_builder.BUILDER_MEMBER: b"re-signed-builder",
                },
                auditor=fake_auditor,
            )
        clean = receipt["clean_cpu_test_gate_result"]
        workspace = receipt["workspace_cpu_test_gate_result"]
        mutations = [
            {**receipt, "goal": 5790},
            {**receipt, "base_source_archive_path": "other-base.tar.gz"},
            {**receipt, "output_path": "C:/Users/private/source.tar.gz"},
            {**receipt, "twin_path": ".Codex/source-twin.tar.gz"},
            {**receipt, "cpu_test_timeout_seconds": 600},
            {**receipt, "cpu_test_timeout_seconds": True},
            {
                **receipt,
                "workspace_cpu_test_gate_result": {
                    **workspace, "scope": "clean",
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean,
                    "excluded_external_only_test_ids": excluded[:-1],
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean,
                    "excluded_external_only_test_ids": (
                        excluded[:-1] + [full_ids[2]]),
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean,
                    "excluded_external_only_test_ids": (
                        excluded + [full_ids[2]]),
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean, "selected_test_count": 112,
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean,
                    "test_result": {
                        **clean["test_result"], "testsRun": 112,
                    },
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean,
                    "test_result": {
                        **clean["test_result"], "skipped": 1,
                    },
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean,
                    "test_result": {
                        **clean["test_result"], "expectedFailures": 1,
                    },
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean,
                    "test_result": {
                        **clean["test_result"], "failures": 1,
                    },
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean,
                    "test_result": {
                        **clean["test_result"], "errors": True,
                    },
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean,
                    "test_result": {
                        **clean["test_result"], "unexpectedSuccesses": 1,
                    },
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean,
                    "outcome_test_ids": {
                        **clean["outcome_test_ids"],
                        "failures": [clean_ids[0]],
                    },
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean, "outcome_test_ids_sha256": "0" * 64,
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean, "failure_test_ids": [clean_ids[0]],
                },
            },
            {
                **receipt,
                "clean_cpu_test_gate_result": {
                    **clean,
                    "failure_exception_summaries": [stable_summary],
                },
            },
            {
                **receipt,
                "operational_timeout_watchdog_uses_host_clock": False,
            },
            {
                **receipt,
                "reported_elapsed_value_count": 0.0,
            },
        ]
        for mutation in mutations:
            with self.assertRaises(
                portable_audit.IndependentPortableAuditError):
                portable_audit._validate_source_receipt_governance(
                    mutation, builder_bytes=builder_bytes,
                    helper_bytes=helper_bytes)
        for mutation in mutations:
            with self.assertRaises(bundle_builder.BundleError):
                bundle_builder._validate_source_cpu_gate_binding(
                    mutation, source_payloads=source_payloads)
            with self.assertRaises(target.PrepareError):
                target._validate_source_cpu_gate_binding(
                    source_receipt=mutation, source_payloads=source_payloads,
                    auditor=fake_auditor)
        with self.assertRaises(
            portable_audit.IndependentPortableAuditError):
            portable_audit._validate_source_receipt_governance(
                receipt, builder_bytes=builder_bytes,
                helper_bytes=helper_bytes + b"\n# re-signed")
        with tempfile.TemporaryDirectory() as temporary:
            fake_root = Path(temporary)
            fake_base = fake_root / "base.tar.gz"
            fake_builder = fake_root / "builder.py"
            fake_helper = fake_root / "helper.py"
            fake_test = fake_root / "test.py"
            fake_base.write_bytes(b"frozen-base")
            fake_builder.write_bytes(b"frozen-builder")
            fake_helper.write_bytes(b"frozen-helper")
            fake_test.write_bytes(b"frozen-test")
            expected_overlay = {
                "helper.py": hashlib.sha256(b"frozen-helper").hexdigest(),
                "test.py": hashlib.sha256(b"frozen-test").hexdigest(),
            }
            with mock.patch.multiple(
                source_builder,
                ROOT=fake_root,
                BASE_SOURCE=fake_base,
                BASE_SOURCE_BYTES=len(b"frozen-base"),
                BASE_SOURCE_SHA256=hashlib.sha256(b"frozen-base").hexdigest(),
                BUILDER_MEMBER="builder.py",
                OVERLAY_PATHS=("helper.py", "test.py"),
                EXPECTED_OVERLAY_SHA256=expected_overlay,
            ):
                for attacked, original in (
                    (fake_helper, b"frozen-helper"),
                    (fake_test, b"frozen-test"),
                ):
                    base_bytes, overlays, builder, identities = (
                        source_builder._verified_workspace_input_snapshot())
                    previous = attacked.stat()
                    attacked.write_bytes(b"temporary-attacker-bytes")
                    attacked.write_bytes(original)
                    os.utime(
                        attacked,
                        ns=(previous.st_atime_ns, previous.st_mtime_ns + 1_000_000),
                    )
                    with self.assertRaisesRegex(
                        RuntimeError, "changed across the full CPU gate",
                    ):
                        source_builder._assert_workspace_input_snapshot_unchanged(
                            base_bytes=base_bytes,
                            overlays=overlays,
                            builder=builder,
                            identities=identities,
                        )
        portable_audit._require_goal_5791(
            {"goal": 5791}, label="independent source audit")
        with self.assertRaisesRegex(
            portable_audit.IndependentPortableAuditError, "Goal identity",
        ):
            portable_audit._require_goal_5791(
                {"goal": 5790}, label="independent source audit")


if __name__ == "__main__":
    unittest.main()

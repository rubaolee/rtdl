from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

from scripts import goal5809_portable_two_app_pilot_bundle as portable
from scripts import goal5809_execution_identity as execution_identity


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history" / "internal_docs"
ARCHIVE = DOCS / "goal5806_triangle_product_projection_evidence_20260826.tar.gz"
TARGET = DOCS / "goal5806_same_source_postimport_target_20260826.json"
GOAL5807_ARCHIVE = (
    DOCS / "goal5807_provider_ready_formal_v2_20260827_0112.tar.gz")
GOAL5807_PILOT_SOURCE = ROOT / "scripts/goal5807_provider_ready_pilot.py"


def _write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _manifest(root: Path) -> dict[str, object]:
    rows = []
    for path in sorted(
            (row for row in root.rglob("*") if row.is_file()),
            key=lambda row: row.relative_to(root).as_posix().encode()):
        rows.append({
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": portable._sha(path),
        })
    body = {
        "schema": portable.SCHEMA,
        "status": "COMPLETE__DIAGNOSTIC_PORTABLE_TWO_APP_PILOT_PAYLOAD",
        "direct_arm_count": 0,
        "host_language_control_present": False,
        "design_attribution_authorized": False,
        "frozen_lineage": {},
        "scope": {
            "nonformal_pilot_only": True,
            "diagnostic_only": True,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "claim_authorized": False,
            "may_replace_goal5806_or_goal5807": False,
            "goal5806_is_primary_preregistered_performance_authority": True,
            "goal5807_is_diagnostic_decomposition_only": True,
            "goal5809_split_phases_are_prospective_diagnosis_only": True,
            "goal5809_may_retroactively_fix_predecessor_result": False,
            "descriptive_ratio_computation_authorized": True,
            "inferential_or_threshold_ratio_claim_authorized": False,
            "direct_arm_count": 0,
            "host_language_control_present": False,
            "design_attribution_authorized": False,
        },
        "claim_authority": portable._claim_authority_manifest(),
        "cell_matrix": [
            {"first_app": task, "arm_order": order}
            for task, order in portable.CELL_SPECS
        ],
        "files": rows,
    }
    return {**body, "bundle_manifest_sha256": portable._digest(body)}


class Goal5809PortableBundleTest(unittest.TestCase):
    def test_bundle_verifier_rejects_every_unmanifested_file_and_directory(
            self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            root.mkdir()
            _write(root / "payload/declared.bin", b"declared")
            manifest = _manifest(root)
            _write(root / "BUNDLE_MANIFEST.json", portable._pretty(manifest))
            self.assertEqual(
                portable._verify_bundle(root)["bundle_manifest_sha256"],
                manifest["bundle_manifest_sha256"])

            extra = root / "payload/unmanifested.bin"
            extra.write_bytes(b"not listed")
            with self.assertRaisesRegex(
                    RuntimeError,
                    "portable_bundle_unmanifested_or_missing_members"):
                portable._verify_bundle(root)
            extra.unlink()

            (root / "unexpected_empty_directory").mkdir()
            with self.assertRaisesRegex(
                    RuntimeError,
                    "portable_bundle_unmanifested_or_missing_members"):
                portable._verify_bundle(root)

    def test_external_review_closure_withdraws_goal5807_and_restores_goal5806(
            self) -> None:
        defaults = portable._defaults(ROOT)
        review_payload = defaults["review"].read_bytes()
        closure_payload = defaults["closure"].read_bytes()
        result_payload = defaults["goal5806_result"].read_bytes()
        self.assertEqual(
            portable._sha_bytes(review_payload),
            portable.GOAL5807_REVIEW_SHA256)
        self.assertEqual(
            portable._sha_bytes(closure_payload),
            portable.GOAL5807_CLOSURE_SHA256)
        closure = portable._require_goal5807_closure(
            closure_payload,
            review_payload=review_payload,
            goal5806_result_payload=result_payload)
        absorption = closure["goal5807_absorption"]
        self.assertEqual(absorption["thresholded_claim_count_authorized"], 0)
        self.assertFalse(absorption["requested_claim_ceiling_authorized"])
        self.assertEqual(
            len(absorption["withdrawn_thresholded_pass_rulings"]), 4)
        self.assertEqual(
            closure["goal5806_primary_performance_authority"][
                "authority_role"],
            "PRIMARY_PREREGISTERED_PERFORMANCE_AUTHORITY")
        self.assertFalse(closure["phase_crosswalk"][
            "goal5809_split_phases_may_retroactively_fix_goal5806_or_goal5807"])
        self.assertFalse(
            closure["goal5809_authority"]["design_attribution_authorized"])
        self.assertTrue(closure["goal5809_authority"][
            "descriptive_ratio_computation_authorized"])
        self.assertFalse(closure["goal5809_authority"][
            "inferential_or_threshold_ratio_claim_authorized"])

    def test_claim_authority_bundle_set_embeds_review_closure_and_primary_sources(
            self) -> None:
        payloads = {
            "goal5807_contract": b"contract",
            "goal5807_result": b"historical-result",
            "goal5807_review": b"controlling-review",
            "goal5807_closure": b"controlling-closure",
            "goal5806_result": b"primary-result",
            "goal5806_technical_report": b"primary-report",
            "goal5806_cfr": b"primary-cfr",
            "goal5806_evaluation": b"absolute-values",
            "goal5806_recount": b"independent-recount",
            "goal5807_reconciliation_json": b"phase-reconciliation",
            "goal5807_reconciliation_report": b"phase-report",
            "goal5807_reconciliation_absorption": b"phase-absorption",
            "goal5809_claim_authority_addendum": b"controlling-addendum",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = portable._write_claim_authority_bundle_files(
                root, payloads=payloads)
            self.assertEqual(len(paths), 13)
            self.assertEqual(
                (root / "frozen/review_goal5807_provider_ready_"
                 "formal_result.md").read_bytes(),
                b"controlling-review")
            self.assertEqual(
                (root / "frozen/goal5807_external_review_absorption_and_"
                 "goal5809_claim_authority_closure.json").read_bytes(),
                b"controlling-closure")
            self.assertEqual(
                (root / "frozen/goal5806_primary_performance_result.json"
                 ).read_bytes(),
                b"primary-result")
            self.assertEqual(
                (root / "frozen/goal5806_primary_formal_evaluation.json"
                 ).read_bytes(),
                b"absolute-values")
            self.assertEqual(
                (root / "frozen/goal5807_postreview_absolute_phase_"
                 "reconciliation.json").read_bytes(),
                b"phase-reconciliation")
            self.assertEqual(
                (root / "frozen/goal5807_postreview_absolute_phase_"
                 "reconciliation_absorption_and_goal5809_entry.json"
                 ).read_bytes(),
                b"phase-absorption")
            self.assertEqual(
                (root / "frozen/goal5809_detached_reconciliation_and_"
                 "goal5806_claim_ceiling_addendum.json").read_bytes(),
                b"controlling-addendum")

    def test_controlling_addendum_narrows_goal5806_claims(self) -> None:
        defaults = portable._defaults(ROOT)
        payload = defaults[
            "goal5809_claim_authority_addendum"].read_bytes()
        self.assertEqual(
            portable._sha_bytes(payload),
            portable.GOAL5809_CLAIM_AUTHORITY_ADDENDUM_SHA256)
        value = portable._require_goal5809_claim_authority_addendum(
            payload,
            closure_payload=defaults["closure"].read_bytes(),
            reconciliation_absorption_payload=defaults[
                "goal5807_reconciliation_absorption"].read_bytes(),
            goal5806_archive_payload_sha256=portable._sha(ARCHIVE),
            goal5807_archive_payload=GOAL5807_ARCHIVE.read_bytes(),
            goal5807_pilot_source_payload=GOAL5807_PILOT_SOURCE.read_bytes(),
        )
        correction = value[
            "goal5806_primary_performance_authority_correction"]
        self.assertFalse(correction[
            "no_measurable_steady_state_cost_claim_authorized"])
        triangle = next(
            row for row in correction["steady_e2e"]
            if row["task"] == "triangle")
        self.assertEqual(
            triangle["ratio_rtdl_over_pyoptix"],
            1.0293902805249933)
        self.assertGreater(triangle["ci95_low"], 1.0)
        process_cold = value["goal5806_full_process_cold_disposition"]
        self.assertEqual(process_cold[
            "thresholded_claim_count_authorized"], 0)
        self.assertTrue(process_cold[
            "historical_pass_literals_are_inoperative_for_claims"])
        for mutate in (
                lambda row: row[
                    "goal5806_primary_performance_authority_correction"
                ].__setitem__(
                    "no_measurable_steady_state_cost_claim_authorized", True),
                lambda row: row[
                    "goal5806_full_process_cold_disposition"
                ].__setitem__("thresholded_claim_count_authorized", 2)):
            hostile = copy.deepcopy(value)
            hostile.pop("claim_authority_addendum_sha256")
            mutate(hostile)
            hostile["claim_authority_addendum_sha256"] = \
                portable._digest(hostile)
            with self.assertRaisesRegex(
                    RuntimeError, "claim-authority addendum differs"):
                portable._require_goal5809_claim_authority_addendum(
                    portable._pretty(hostile),
                    closure_payload=defaults["closure"].read_bytes(),
                    reconciliation_absorption_payload=defaults[
                        "goal5807_reconciliation_absorption"].read_bytes(),
                    goal5806_archive_payload_sha256=portable._sha(ARCHIVE),
                    goal5807_archive_payload=GOAL5807_ARCHIVE.read_bytes(),
                    goal5807_pilot_source_payload=(
                        GOAL5807_PILOT_SOURCE.read_bytes()),
                )

    def test_detached_reconciliation_roots_run_bundled_four_tests(self) \
            -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            root.mkdir()
            portable._copy_source_closure(ROOT, root)
            portable._write_detached_reconciliation_roots(
                root,
                goal5806_archive=ARCHIVE,
                goal5807_archive_payload=GOAL5807_ARCHIVE.read_bytes(),
                goal5807_pilot_source_payload=(
                    GOAL5807_PILOT_SOURCE.read_bytes()))
            environment = dict(os.environ)
            environment["PYTHONPATH"] = os.pathsep.join((
                str(root / "source/src"), str(root / "source")))
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            result = subprocess.run(
                [
                    sys.executable, "-m", "unittest",
                    "source.tests.goal5809_goal5806_goal5807_"
                    "phase_reconciliation_test",
                ],
                cwd=root,
                env=environment,
                capture_output=True,
                check=False,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Ran 4 tests", result.stderr)

    def test_raw_reconciliation_closes_two_review_findings_not_direct(self) \
            -> None:
        defaults = portable._defaults(ROOT)
        reconciliation_payload = defaults[
            "goal5807_reconciliation_json"].read_bytes()
        absorption_payload = defaults[
            "goal5807_reconciliation_absorption"].read_bytes()
        self.assertEqual(
            portable._sha_bytes(reconciliation_payload),
            portable.GOAL5807_RECONCILIATION_JSON_SHA256)
        self.assertEqual(
            portable._sha_bytes(absorption_payload),
            portable.GOAL5807_RECONCILIATION_ABSORPTION_SHA256)
        reconciliation = portable._require_goal5807_reconciliation(
            reconciliation_payload)
        self.assertFalse(
            reconciliation["reconciliation"]["same_named_prepare_boundary"])
        absorption = portable._require_goal5807_reconciliation_absorption(
            absorption_payload,
            reconciliation_payload=reconciliation_payload)
        dispositions = absorption["external_review_finding_disposition"]
        self.assertEqual(
            dispositions["p1_absolute_times"]["status"],
            "CLOSED_BY_RAW_ARCHIVE_RECONSTRUCTION")
        self.assertEqual(
            dispositions["p1_prepare_reconciliation"]["status"],
            "CLOSED_BY_RAW_ARCHIVE_RECONSTRUCTION")
        self.assertEqual(
            dispositions["p1_direct_arm"]["status"],
            "OPEN_FOR_ANY_FORMAL_DESIGN_ATTRIBUTION_OR_PAPER_SUCCESSOR")
        self.assertFalse(absorption["goal5809_entry"][
            "old_bundle_authorized_for_execution_or_delivery"])
        manifest_authority = portable._claim_authority_manifest()
        self.assertEqual(
            manifest_authority["goal5807_review_p1_absolute_times"],
            "CLOSED_BY_RAW_ARCHIVE_RECONSTRUCTION")
        self.assertEqual(
            manifest_authority["goal5807_review_p1_prepare_reconciliation"],
            "CLOSED_BY_RAW_ARCHIVE_RECONSTRUCTION")
        self.assertEqual(
            manifest_authority["goal5807_review_p1_direct_arm"],
            "OPEN_FOR_ANY_FORMAL_DESIGN_ATTRIBUTION_OR_PAPER_SUCCESSOR")
        self.assertFalse(manifest_authority[
            "old_bundle_authorized_for_execution_or_delivery"])

    def test_clean_source_closure_imports_new_bulk_helper_and_worker(self) \
            -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "portable"
            portable._copy_source_closure(ROOT, copied)
            bulk = copied / "source/experiments/goal5809_pyoptix_bulk_input.py"
            self.assertTrue(bulk.is_file())
            reconciliation_script = copied / (
                "source/scripts/goal5809_reconcile_goal5806_goal5807_phases.py")
            reconciliation_test = copied / (
                "source/tests/goal5809_goal5806_goal5807_"
                "phase_reconciliation_test.py")
            self.assertEqual(
                portable._sha(reconciliation_script),
                portable.GOAL5807_RECONCILIATION_SCRIPT_SHA256)
            self.assertEqual(
                portable._sha(reconciliation_test),
                portable.GOAL5807_RECONCILIATION_TEST_SHA256)
            environment = dict(os.environ)
            environment["PYTHONPATH"] = os.pathsep.join((
                str(copied / "source/src"), str(copied / "source")))
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            result = subprocess.run(
                [
                    sys.executable, "-c",
                    "from experiments import goal5809_pyoptix_bulk_input as b; "
                    "from scripts import goal5809_pyoptix_two_app_pilot as w; "
                    "assert b.RELATION_PACKING_SCHEMA.endswith('.v1'); "
                    "assert callable(w._preload_runtime)",
                ],
                cwd=copied,
                env=environment,
                capture_output=True,
                check=False,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            help_result = subprocess.run(
                [
                    sys.executable,
                    str(copied / "source/scripts/"
                        "goal5809_two_app_pilot_controller.py"),
                    "--help",
                ],
                cwd=copied,
                env=environment,
                capture_output=True,
                check=False,
                text=True,
            )
            self.assertEqual(help_result.returncode, 0, help_result.stderr)
            self.assertIn(
                "--execution-identity-manifest", help_result.stdout)
            self.assertIn(
                "--expected-execution-identity-manifest-sha256",
                help_result.stdout)

    def test_real_goal5806_archive_is_not_a_complete_two_arm_bundle(self) \
            -> None:
        result = portable._inspect_archive(ARCHIVE, TARGET)
        self.assertEqual(
            result["status"],
            "INSUFFICIENT__EXACT_EXTERNAL_CUSTODY_BYTES_REQUIRED")
        self.assertEqual(result["missing_exact_products"], [
            "matched_ptx",
            "relation_compaction_cubin",
            "runtime_manifest",
            "target_observation",
        ])
        self.assertFalse(
            result["portable_two_arm_bundle_buildable_from_archive_alone"])
        present = result["present_and_rehashed"]
        self.assertEqual(
            present["native_library"]["sha256"],
            "a8ac65e2c5ebecf558f4df7d4df1fc210b41c2e39f199301f0ed852147a68daa")
        self.assertEqual(
            present["relation_artifact"]["sha256"],
            "f595ed08850ac187fe1560d584197beceb854cb716030b3e07f6745673e7b07c")
        self.assertEqual(
            present["triangle_artifact"]["sha256"],
            "a96ddb9eb88fdee6a2fc3d8bd01b036dc59bac882c0ad07336c151329fedd335")

    def test_real_goal5806_candidate_native_proof_and_trust_cross_link(self) \
            -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = json.loads(TARGET.read_text(encoding="utf-8"))
            with tarfile.open(ARCHIVE, "r:gz") as archive:
                candidate_payload = portable._archive_member_bytes(
                    archive, portable.ARCHIVE_MEMBERS["candidate_manifest"])
                candidate = json.loads(candidate_payload)
                for role in ("trust_root", "trust_head", "trust_package"):
                    path = root / f"{role}.json"
                    _write(path, portable._archive_member_bytes(
                        archive, portable.ARCHIVE_MEMBERS[role]))
                    target["files"][role]["path"] = str(path.resolve())
                proof = root / portable.PAYLOAD_PATHS["proof"]
                _write(proof, portable._archive_member_bytes(
                    archive, portable.ARCHIVE_MEMBERS["proof"]))
            result = portable._validate_goal5806_successor_tuple(
                bundle_root=root,
                staged_target=target,
                staged_candidate=candidate,
            )
            self.assertTrue(result["candidate_native_cross_link"])
            self.assertTrue(result["candidate_proof_cross_link"])
            self.assertTrue(result[
                "trust_head_package_root_cross_link"])

    def _synthetic_bundle(self, root: Path) -> dict[str, object]:
        _write(
            root / "frozen/goal5806_target_manifest.json",
            TARGET.read_bytes())
        with tarfile.open(ARCHIVE, "r:gz") as archive:
            candidate = portable._archive_member_bytes(
                archive, portable.ARCHIVE_MEMBERS["candidate_manifest"])
        _write(root / "frozen/goal5806_candidate_manifest.json", candidate)
        candidate_value = json.loads(candidate)
        for relative in portable.PAYLOAD_PATHS.values():
            _write(root / relative, b"synthetic-present-product")
        for relative in (
                *portable.SOURCE_FILES,
                "src/rtdsl/__init__.py",
                "src/rtdsl/v4_rtdlexe.py",
                "src/rtdsl/physical_execution_provenance.py"):
            _write(
                root / "source" / relative,
                f"synthetic source: {relative}\n".encode())
        for task in ("relation", "triangle"):
            row = candidate_value["candidates"][task]
            _write(
                root / "payload/products/candidates/artifacts" /
                Path(row["artifact_path"]).name,
                f"{task}-artifact".encode())
            _write(
                root / "payload/products/candidates" /
                f"{task}.authority.json",
                f"{task}-authority".encode())
        manifest = _manifest(root)
        _write(root / "BUNDLE_MANIFEST.json", portable._pretty(manifest))
        return manifest

    def test_materialize_changes_paths_and_only_derived_target_identity(self) \
            -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            root.mkdir()
            self._synthetic_bundle(root)
            staging = Path(temporary) / "staging"
            live_initializer = Path(temporary) / "live/optix/__init__.py"
            live_extension = Path(temporary) / "live/optix/_optix.so"
            _write(live_initializer, b"synthetic optix initializer")
            _write(live_extension, b"synthetic optix extension")
            combined = Path(temporary) / "combined_runtime"
            clean_python = combined / "venv/bin/python"
            (combined / "venv/lib/python3.12/site-packages").mkdir(
                parents=True)
            _write(clean_python, b"synthetic controlled python")
            predecessor = {
                "manifest_sha256": "9" * 64,
                "files": {
                    "pyoptix_initializer": {
                        "bytes": live_initializer.stat().st_size,
                        "sha256": portable._sha(live_initializer),
                    },
                    "pyoptix_extension": {
                        "bytes": live_extension.stat().st_size,
                        "sha256": portable._sha(live_extension),
                    },
                    "clean_python": {
                        "path": str(clean_python.resolve()),
                        "bytes": clean_python.stat().st_size,
                        "sha256": portable._sha(clean_python),
                    },
                },
                "pyoptix": {
                    "distribution_version": "9.1.0",
                    "optix_api_version": "9.0.0",
                },
                "build_provenance": {
                    "combined_runtime_path_projection": {
                        "root_path": str(combined.resolve()),
                        "clean_python_relative": "venv/bin/python",
                        "site_packages_relative": (
                            "venv/lib/python3.12/site-packages"),
                    },
                },
                "target_observation": {
                    "loader_environment": {
                        "LD_LIBRARY_PATH": None,
                        "LD_PRELOAD": None,
                    },
                },
            }
            live = {
                "initializer_path": live_initializer.resolve(),
                "extension_path": live_extension.resolve(),
                "distribution_version": "9.1.0",
                "api_version": "9.0.0",
            }
            with mock.patch.object(
                    portable, "_validate_predecessor_runtime_manifest",
                    return_value=predecessor), mock.patch.object(
                    portable, "_validate_goal5806_successor_tuple",
                    return_value={"all_cross_links": True}), \
                    mock.patch.object(
                    portable, "_resolve_live_pyoptix", return_value=live), \
                    mock.patch.object(
                        portable.importlib.metadata, "version",
                        return_value="9.1.0"):
                authority = portable._materialize(argparse.Namespace(
                    bundle_root=root,
                    staging_root=staging,
                ))

            self.assertFalse(
                authority["scope"]["staged_target_is_frozen_goal5806_target"])
            self.assertEqual(authority["scope"]["formal_worker_count"], 0)
            self.assertEqual(
                authority["scope"]["registered_performance_timing_count"], 0)
            self.assertFalse(
                authority["scope"]["paper_or_performance_claim_authorized"])
            self.assertTrue(authority["scope"][
                "successor_execution_identity_is_path_local"])
            self.assertNotEqual(
                authority["staged_target"]["file_sha256"],
                portable.GOAL5806_TARGET_FILE_SHA256)
            self.assertNotEqual(
                authority["staged_target"]["semantic_sha256"],
                portable.GOAL5806_TARGET_SEMANTIC_SHA256)

            frozen_target = json.loads(TARGET.read_text(encoding="utf-8"))
            staged_target = json.loads(
                (staging / "target_manifest.json").read_text(encoding="utf-8"))
            for name in portable.TARGET_FILE_NAMES:
                self.assertTrue(Path(staged_target["files"][name]["path"]).is_absolute())
                if name != "candidate_manifest":
                    self.assertEqual(
                        staged_target["files"][name]["bytes"],
                        frozen_target["files"][name]["bytes"])
                    self.assertEqual(
                        staged_target["files"][name]["sha256"],
                        frozen_target["files"][name]["sha256"])

            frozen_candidate = json.loads((
                root / "frozen/goal5806_candidate_manifest.json"
            ).read_text(encoding="utf-8"))
            staged_candidate = json.loads((
                staging / "candidate_manifest.json"
            ).read_text(encoding="utf-8"))
            self.assertEqual(
                portable._candidate_nonpath_projection(staged_candidate),
                portable._candidate_nonpath_projection(frozen_candidate))
            run_script = (
                staging / "run_pilot_matrix.sh").read_text(encoding="utf-8")
            self.assertEqual(
                run_script.count("goal5809_two_app_pilot_controller.py"), 4)
            self.assertEqual(
                run_script.count("goal5809_portable_two_app_pilot_bundle.py"),
                1)
            self.assertLess(
                run_script.index("goal5809_portable_two_app_pilot_bundle.py"),
                run_script.index("goal5809_two_app_pilot_controller.py"))
            self.assertNotIn("python3 ", run_script)
            self.assertIn(" -I -S -B -P -c ", run_script)
            self.assertIn("unset PYTHONPATH PYTHONHOME LD_PRELOAD", run_script)
            for task, order in portable.CELL_SPECS:
                self.assertIn(f"--first-app {task} --arm-order {order}", run_script)
            self.assertEqual(
                run_script.count("--execution-identity-manifest"), 4)
            execution_identity = json.loads((
                staging / "execution_identity_manifest.json"
            ).read_text(encoding="utf-8"))
            self.assertIn(
                "goal5809_pyoptix_bulk_input_source",
                execution_identity["required_file_roles"])
            self.assertIn(
                "rtdlexe_module", execution_identity["required_file_roles"])
            self.assertTrue(execution_identity[
                "predecessor_runtime_manifest"]["dependency_source_only"])

    def test_exact_external_product_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "wrong.ptx"
            path.write_bytes(b"wrong")
            with self.assertRaisesRegex(RuntimeError, "frozen_product_mismatch"):
                portable._require_file(
                    path, expected_bytes=9009,
                    expected_sha256="b" * 64, label="matched_ptx")

    def test_predecessor_and_target_ptx_from_different_lineages_reject(self) \
            -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = json.loads(TARGET.read_text(encoding="utf-8"))
            with tarfile.open(ARCHIVE, "r:gz") as archive:
                candidate = json.loads(portable._archive_member_bytes(
                    archive,
                    portable.ARCHIVE_MEMBERS["candidate_manifest"]))
            runtime_files = {}
            for runtime_role, target_role in {
                    "matched_ptx": "matched_ptx",
                    "compaction_cubin": "relation_compaction_cubin",
                    "native_library": "native_library",
                    "target_observation_receipt": "target_observation",
                    "trust_root": "trust_root",
                    "trust_head": "trust_head",
                    "trust_package": "trust_package",
            }.items():
                runtime_files[runtime_role] = {
                    "bytes": target["files"][target_role]["bytes"],
                    "sha256": target["files"][target_role]["sha256"],
                }
            for task in ("relation", "triangle"):
                for kind in ("artifact", "authority"):
                    runtime_files[f"{task}_{kind}"] = {
                        "sha256": candidate["candidates"][task][
                            f"{kind}_sha256"],
                    }
            runtime_files["callback_proof"] = {
                "sha256": candidate["proof_sha256"],
            }
            runtime_files["pyoptix_initializer"] = {}
            runtime_files["pyoptix_extension"] = {}
            runtime_files["matched_ptx"]["sha256"] = "8" * 64
            body = {
                "schema": "rtdl.goal5802.target_runtime_manifest.v2",
                "status": "PREPARED_UNTIMED__FORMAL_EXECUTION_LOCKED",
                "registered_performance_timing_count": 0,
                "formal_worker_zero": False,
                "files": runtime_files,
                "pyoptix": {
                    "distribution_version": "9.1.0",
                    "optix_api_version": "9.0.0",
                },
            }
            runtime = {**body, "manifest_sha256": portable._digest(body)}
            path = root / "runtime.json"
            path.write_bytes(portable._pretty(runtime))
            with self.assertRaisesRegex(
                    RuntimeError, "Goal5809_mixed_target_lineage"):
                portable._validate_predecessor_runtime_manifest(
                    path,
                    expected_file_sha256=portable._sha(path),
                    staged_target=target,
                )

    def _write_collection_cells(
        self, root: Path, *, bad_cell: str | None = None,
    ) -> None:
        root.mkdir(parents=True)
        custody = root / "staging_custody"
        custody.mkdir()
        candidate_path = custody / "candidate_manifest.json"
        _write(candidate_path, portable._pretty({"synthetic": "candidate"}))
        target_body = {
            "files": {
                "candidate_manifest": {
                    "bytes": candidate_path.stat().st_size,
                    "sha256": portable._sha(candidate_path),
                },
            },
        }
        target = {
            **target_body,
            "target_manifest_sha256": portable._digest(target_body),
        }
        target_path = custody / "target_manifest.json"
        _write(target_path, portable._pretty(target))

        identity_files = {}
        for role in sorted(execution_identity.REQUIRED_BASE_FILE_ROLES):
            path = custody / "identity_files" / role
            _write(path, (role + "\n").encode())
            identity_files[role] = {
                "path": str(path.resolve()),
                "bytes": path.stat().st_size,
                "sha256": portable._sha(path),
                "provenance": "SYNTHETIC_TEST",
            }
        identity_body = {
            "schema": portable.EXECUTION_IDENTITY_SCHEMA,
            "status": portable.EXECUTION_IDENTITY_STATUS,
            "scope": {
                "claim_authorized": False,
                "formal_worker_count": 0,
                "nonformal_pilot_only": True,
                "registered_performance_timing_count": 0,
            },
            "predecessor_runtime_manifest": {
                "dependency_source_only": True,
                "is_goal5809_execution_identity": False,
            },
            "pyoptix": {
                "api_version": "9.0.0",
                "distribution_name": "pyoptix",
                "distribution_version": "9.1.0",
                "extension_module": "optix._optix",
                "extension_role": "pyoptix_extension",
                "initializer_module": "optix",
                "initializer_role": "pyoptix_initializer",
            },
            "required_file_roles": sorted(identity_files),
            "files": identity_files,
        }
        identity = {
            **identity_body,
            "execution_identity_sha256": portable._digest(identity_body),
        }
        identity_path = custody / "execution_identity_manifest.json"
        _write(identity_path, portable._pretty(identity))
        bundle_body = {
            "schema": portable.SCHEMA,
            "files": [],
            "scope": {"nonformal_pilot_only": True},
        }
        bundle = {
            **bundle_body,
            "bundle_manifest_sha256": portable._digest(bundle_body),
        }
        _write(custody / "BUNDLE_MANIFEST.json", portable._pretty(bundle))
        authority_body = {
            "schema": portable.STAGING_SCHEMA,
            "staged_target": {
                "file_sha256": portable._sha(target_path),
                "semantic_sha256": target["target_manifest_sha256"],
            },
            "successor_execution_identity": {
                "file_sha256": portable._sha(identity_path),
                "semantic_sha256": identity["execution_identity_sha256"],
            },
        }
        authority = {
            **authority_body,
            "staging_authority_sha256": portable._digest(authority_body),
        }
        _write(
            custody / "staging_authority.json", portable._pretty(authority))
        preflight_body = {
            "schema": portable.PREFLIGHT_SCHEMA,
            "status": (
                "COMPLETE__DIAGNOSTIC_READY_FOR_NONFORMAL_FOUR_CELL_PILOT"),
            "scope": {
                "diagnostic_pilot_only": True,
                "nonformal_diagnostic": True,
                "formal_evidence": False,
                "paper_evidence": False,
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
                "claim_authorized": False,
                "direct_arm_count": 0,
                "host_language_control_present": False,
                "design_attribution_authorized": False,
            },
            "environment": {
                "gpu_name": "NVIDIA RTX A4500",
                "compute_capability": [8, 6],
                "native_library_load": "PASS",
            },
            "bundle_manifest_sha256": bundle["bundle_manifest_sha256"],
            "staging_authority_sha256": authority[
                "staging_authority_sha256"],
            "staged_target_file_sha256": portable._sha(target_path),
            "staged_target_semantic_sha256": target[
                "target_manifest_sha256"],
            "successor_execution_identity": {
                "manifest_file_sha256": portable._sha(identity_path),
                "semantic_sha256": identity["execution_identity_sha256"],
                "files_rehashed": True,
                "rtdl_loaded_identity": {
                    "rtdl_loaded_identity_verified": True,
                },
                "pyoptix_loaded_identity": {
                    "pyoptix_loaded_identity_verified": True,
                },
            },
        }
        preflight = {
            **preflight_body,
            "preflight_sha256": portable._digest(preflight_body),
        }
        _write(root / "preflight_receipt.json", portable._pretty(preflight))
        for first_app, arm_order in portable.CELL_SPECS:
            cell_name = f"{first_app}-first__{arm_order}"
            cell = root / cell_name
            cell.mkdir(parents=True)
            children = {}
            for index, arm in enumerate(("rtdl", "pyoptix")):
                child_body = {
                    "schema": ({
                        "rtdl": (
                            "rtdl.goal5809.runtime_session_two_app_pilot.v2"),
                        "pyoptix": (
                            "rtdl.goal5809.pyoptix_two_app_pilot.v2"),
                    }[arm]),
                    "status": ({
                        "rtdl": (
                            "COMPLETE__DIAGNOSTIC_TWO_APPLICATION_"
                            "RUNTIME_SESSION_PILOT"),
                        "pyoptix": (
                            "COMPLETE__DIAGNOSTIC_IDIOMATIC_PYOPTIX_"
                            "TWO_APPLICATION_PILOT"),
                    }[arm]),
                    "process_pid": 100 + index,
                    "formal_worker_count": 0,
                    "registered_performance_timing_count": 0,
                }
                child = {
                    **child_body,
                    "pilot_sha256": portable._digest(child_body),
                }
                child_path = cell / f"{arm}.json"
                _write(child_path, portable._pretty(child))
                children[arm] = {
                    "arm": arm,
                    "pid": 100 + index,
                    "output_path": str(child_path.resolve()),
                    "output_bytes": child_path.stat().st_size,
                    "output_sha256": portable._sha(child_path),
                }
            body = {
                "schema": (
                    "rtdl.goal5809.two_app_fresh_process_controller.v2"),
                "status": (
                    "COMPLETE__DIAGNOSTIC_TWO_ARM_TWO_APPLICATION_"
                    "FRESH_PROCESS_PILOT"),
                "formal_worker_count": 0,
                "registered_performance_timing_count": (
                    1 if cell_name == bad_cell else 0),
                "execution": {
                    "first_app": first_app,
                    "arm_order": (
                        ["rtdl", "pyoptix"] if arm_order == "rtdl-first"
                        else ["pyoptix", "rtdl"]),
                },
                "target": {
                    "file_sha256": portable._sha(target_path),
                    "semantic_sha256": target["target_manifest_sha256"],
                },
                "execution_identity": {
                    "manifest_file_sha256": portable._sha(identity_path),
                    "execution_identity_sha256": identity[
                        "execution_identity_sha256"],
                },
                "children": children,
            }
            row = {**body, "controller_sha256": portable._digest(body)}
            path = root / cell_name / "summary.json"
            path.write_bytes(portable._pretty(row))

    def test_collection_requires_all_four_nonformal_cells(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "outputs"
            self._write_collection_cells(root)
            archive = Path(temporary) / "outputs.tar.gz"
            with mock.patch.object(
                    execution_identity.importlib.metadata,
                    "version", return_value="9.1.0"):
                result = portable._collect(argparse.Namespace(
                    outputs_root=root,
                    output_archive=archive,
                ))
            self.assertEqual(len(result["cells"]), 4)
            self.assertEqual(result["scope"]["formal_worker_count"], 0)
            self.assertEqual(
                result["scope"]["registered_performance_timing_count"], 0)
            self.assertTrue(archive.is_file())

    def test_collection_rejects_registered_timing_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "outputs"
            self._write_collection_cells(
                root, bad_cell="triangle-first__pyoptix-first")
            with mock.patch.object(
                    execution_identity.importlib.metadata,
                    "version", return_value="9.1.0"):
                with self.assertRaisesRegex(
                        RuntimeError, "escaped non-formal"):
                    portable._collect(argparse.Namespace(
                        outputs_root=root,
                        output_archive=None,
                    ))

    def test_collection_rejects_tampered_or_wrong_gpu_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "outputs"
            self._write_collection_cells(root)
            preflight = json.loads((
                root / "preflight_receipt.json").read_text(encoding="utf-8"))
            preflight["environment"]["gpu_name"] = "NVIDIA RTX 4000 Ada"
            (root / "preflight_receipt.json").write_bytes(
                portable._pretty(preflight))
            with self.assertRaisesRegex(
                    RuntimeError, "exact A4500 preflight receipt differs"):
                portable._collect(argparse.Namespace(
                    outputs_root=root,
                    output_archive=None,
                ))

    def test_collection_rejects_child_file_changed_after_controller_seal(self) \
            -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "outputs"
            self._write_collection_cells(root)
            child = root / "relation-first__rtdl-first/rtdl.json"
            child.write_bytes(child.read_bytes() + b" ")
            with mock.patch.object(
                    execution_identity.importlib.metadata,
                    "version", return_value="9.1.0"):
                with self.assertRaisesRegex(
                        RuntimeError, "child file differs"):
                    portable._collect(argparse.Namespace(
                        outputs_root=root,
                        output_archive=None,
                    ))


if __name__ == "__main__":
    unittest.main()

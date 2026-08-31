from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import goal5802_verify_preformal_runtime_dual_untimed as validator


def _sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _named_sha(label: str) -> str:
    return _sha_bytes(label.encode("utf-8"))


class Goal5802PreformalRuntimeDualValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

        required_sources = (
            validator.PYOPTIX_SCALAR_SOURCE,
            validator.GOAL5800_SOURCE,
            "experiments/goal5802_premeasurement/direct_scalar_worker.cpp",
            ("experiments/goal5802_premeasurement/"
             "matched_device_semantic_capacity.cu"),
            ("experiments/goal5802_premeasurement/"
             "relation_semantic_compaction.cu"),
            "experiments/goal5802_premeasurement/independent_recount.py",
            "scripts/goal5802_build_header_projection_untimed.py",
            "scripts/goal5802_nvrtc_compile_child.py",
            "scripts/goal5802_prepare_matched_ptx_untimed.py",
            validator.THIS_VALIDATOR_SOURCE,
        )
        self.source_rows: list[dict[str, object]] = []
        self.source_sha: dict[str, str] = {}
        for index, relative in enumerate(required_sources):
            path = self.root.joinpath(*Path(relative).parts)
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = f"source-{index}-{relative}\n".encode("utf-8")
            path.write_bytes(payload)
            sha256 = _sha_bytes(payload)
            self.source_sha[relative] = sha256
            self.source_rows.append({
                "path": relative, "bytes": len(payload), "sha256": sha256})

        self.product = {
            "wheel_sha256": _named_sha("wheel"),
            "native_sha256": _named_sha("native"),
            "trust_root_sha256": _named_sha("trust-root"),
            "trust_head_sha256": _named_sha("trust-head"),
            "trust_package_sha256": _named_sha("trust-package"),
            "relation_artifact_sha256": _named_sha("relation-artifact"),
            "relation_authority_sha256": _named_sha("relation-authority"),
            "triangle_artifact_sha256": _named_sha("triangle-artifact"),
            "triangle_authority_sha256": _named_sha("triangle-authority"),
            "rtdsl_init_sha256": _named_sha("init"),
            "rtdlexe_module_sha256": _named_sha("rtdlexe"),
            "rtdsl_package_file_count": 37,
            "rtdsl_package_tree_sha256": _named_sha("package-tree"),
            "relation_deployment_id": "relation-deployment",
            "triangle_deployment_id": "triangle-deployment",
            "relation_executable_identity_sha256": _named_sha(
                "relation-executable"),
            "triangle_executable_identity_sha256": _named_sha(
                "triangle-executable"),
            "source_commit": "1" * 40,
            "source_tree": "2" * 40,
        }
        self.freeze: dict[str, object] = {
            "schema": "rtdl.goal5802.local_premeasurement_freeze.v3",
            "status": (
                "FROZEN_LOCAL_PREMEASUREMENT__FORMAL_WORKER_ZERO_LOCKED"),
            "authorization": {
                "formal_worker_zero": False,
                "registered_gpu_timing": False,
                "pod_execution": False,
            },
            "registered_performance_timing_count": 0,
            "source_manifest": self.source_rows,
            "product_binding": self.product,
            "freeze_sha256": _named_sha("freeze-self"),
        }

        self.kat_paths: dict[str, Path] = {}
        for role in (
                "pyoptix_operation_kat", "direct_operation_kat",
                "rtdl_operation_kat"):
            path = self.root / f"{role}.json"
            path.write_text("{}\n", encoding="utf-8")
            self.kat_paths[role] = path

        product_roles = {
            "rtdl_wheel": "wheel_sha256",
            "native_library": "native_sha256",
            "trust_root": "trust_root_sha256",
            "trust_head": "trust_head_sha256",
            "trust_package": "trust_package_sha256",
            "relation_artifact": "relation_artifact_sha256",
            "relation_authority": "relation_authority_sha256",
            "triangle_artifact": "triangle_artifact_sha256",
            "triangle_authority": "triangle_authority_sha256",
            "rtdsl_init": "rtdsl_init_sha256",
            "rtdlexe_module": "rtdlexe_module_sha256",
        }
        files: dict[str, dict[str, object]] = {
            role: {
                "path": str(self.root / role),
                "path_kind": "REGULAR_FILE",
                "bytes": 1,
                "sha256": self.product[key],
            }
            for role, key in product_roles.items()
        }
        source_roles = {
            "direct_scalar_source": (
                "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"),
            "device_source": (
                "experiments/goal5802_premeasurement/"
                "matched_device_semantic_capacity.cu"),
            "compaction_source": (
                "experiments/goal5802_premeasurement/"
                "relation_semantic_compaction.cu"),
        }
        for role, relative in source_roles.items():
            source = self.root.joinpath(*Path(relative).parts)
            files[role] = {
                "path": str(source),
                "path_kind": "REGULAR_FILE",
                "bytes": source.stat().st_size,
                "sha256": self.source_sha[relative],
            }
        for role, path in self.kat_paths.items():
            files[role] = {
                "path": str(path), "path_kind": "REGULAR_FILE",
                "bytes": path.stat().st_size, "sha256": _sha_bytes(
                    path.read_bytes()),
            }
        self.runtime: dict[str, object] = {
            "schema": "rtdl.goal5802.target_runtime_manifest.v2",
            "status": "PREPARED_UNTIMED__FORMAL_EXECUTION_LOCKED",
            "files": files,
            "directories": {
                "rtdsl_package": {
                    "path": str(self.root / "rtdsl"),
                    "file_count": self.product["rtdsl_package_file_count"],
                    "payload_bytes": 999,
                    "tree_sha256": self.product[
                        "rtdsl_package_tree_sha256"],
                },
            },
            "deployment_ids": {
                "relation": self.product["relation_deployment_id"],
                "triangle": self.product["triangle_deployment_id"],
            },
            "pyoptix": {
                "goal5800_v7_source_sha256": self.source_sha[
                    validator.GOAL5800_SOURCE],
            },
            "target_observation": {
                "gpu_name": "synthetic RTX",
                "compute_capability": "8.9",
                "driver_version": "synthetic",
            },
            "target_policy": {"synthetic": True},
            "architecture_contract": {"ptx_target": "sm_89"},
            "build_provenance": {"synthetic": True},
            "formal_preflight_contract": {
                "required_before_worker_zero": True},
            "registered_performance_timing_count": 0,
            "formal_worker_zero": False,
            "manifest_sha256": _named_sha("runtime-self"),
        }
        self.freeze_path = self.root / "freeze.json"
        self.runtime_path = self.root / "runtime.json"
        self.freeze_path.write_text(
            json.dumps(self.freeze, sort_keys=True), encoding="utf-8")
        self.runtime_path.write_text(
            json.dumps(self.runtime, sort_keys=True), encoding="utf-8")

    def _all_validation_mocks(self):
        return (
            mock.patch.object(validator.contract, "validate_freeze"),
            mock.patch.object(
                validator.runtime_manifest, "validate_runtime_manifest"),
            mock.patch.object(
                validator.runtime_manifest,
                "validate_pyoptix_operation_kat"),
            mock.patch.object(
                validator.runtime_manifest, "validate_direct_operation_kat"),
            mock.patch.object(
                validator.runtime_manifest, "validate_rtdl_operation_kat"),
            mock.patch.object(
                validator.independent_recount, "_validate_freeze_bytes"),
            mock.patch.object(
                validator.independent_recount, "_validate_runtime_bytes"),
        )

    def test_pass_requires_both_validators_and_binds_complete_projection(self):
        patches = self._all_validation_mocks()
        with patches[0] as main_freeze, patches[1] as main_runtime, \
                patches[2] as py_kat, patches[3] as direct_kat, \
                patches[4] as rtdl_kat, patches[5] as independent_freeze, \
                patches[6] as independent_runtime:
            receipt = validator.build_pass_receipt(
                root=self.root, freeze_path=self.freeze_path,
                runtime_path=self.runtime_path)

        main_freeze.assert_called_once()
        main_runtime.assert_called_once()
        py_kat.assert_called_once()
        direct_kat.assert_called_once()
        rtdl_kat.assert_called_once()
        independent_freeze.assert_called_once()
        independent_runtime.assert_called_once()
        independent_call = independent_runtime.call_args.kwargs
        self.assertEqual(
            independent_call["expected_pyoptix_scalar_source_sha256"],
            self.source_sha[validator.PYOPTIX_SCALAR_SOURCE])
        self.assertEqual(
            independent_call["expected_rtdl_executable_identities"], {
                "relation": self.product[
                    "relation_executable_identity_sha256"],
                "triangle": self.product[
                    "triangle_executable_identity_sha256"],
            })
        self.assertEqual(receipt["schema"], validator.PASS_SCHEMA)
        self.assertEqual(receipt["status"], validator.PASS_STATUS)
        self.assertEqual(receipt["product_binding"], self.product)
        self.assertEqual(
            receipt["runtime_identity_projection"]["target_observation"],
            self.runtime["target_observation"])
        self.assertTrue(receipt["validation_paths_exact_projection_equal"])
        self.assertFalse(receipt["execution_authority_consumed"])
        self.assertTrue(receipt["live_worker_zero_preflight_still_required"])
        self.assertFalse(receipt["preserved_runtime_operation_kats_reexecuted"])
        self.assertEqual(receipt["retry_count"], 0)
        self.assertEqual(receipt["replacement_count"], 0)
        self.assertEqual(receipt["formal_worker_count"], 0)
        self.assertEqual(receipt["registered_performance_timing_count"], 0)
        unsigned = dict(receipt)
        observed = unsigned.pop("receipt_sha256")
        self.assertEqual(observed, validator._digest(unsigned))

    def test_independent_runtime_rejection_cannot_be_hidden_by_primary_pass(self):
        patches = self._all_validation_mocks()
        with patches[0], patches[1], patches[2], patches[3], patches[4], \
                patches[5], patches[6] as independent_runtime:
            independent_runtime.side_effect = RuntimeError(
                "hostile independent rejection")
            with self.assertRaisesRegex(
                    RuntimeError, "hostile independent rejection"):
                validator.build_pass_receipt(
                    root=self.root, freeze_path=self.freeze_path,
                    runtime_path=self.runtime_path)

    def test_every_product_and_source_mapping_leaf_changes_the_verdict(self):
        product_roles = (
            "rtdl_wheel", "native_library", "trust_root", "trust_head",
            "trust_package", "relation_artifact", "relation_authority",
            "triangle_artifact", "triangle_authority", "rtdsl_init",
            "rtdlexe_module")
        frozen_sources = validator._rebuild_frozen_sources_independently(
            self.freeze, self.root)
        kat_patches = self._all_validation_mocks()[2:5]
        with kat_patches[0], kat_patches[1], kat_patches[2]:
            for role in product_roles:
                with self.subTest(path="product", role=role):
                    changed = copy.deepcopy(self.runtime)
                    changed["files"][role]["sha256"] = _named_sha(
                        "mutated-" + role)
                    with self.assertRaisesRegex(
                            RuntimeError, "frozen-product"):
                        validator._primary_link_projection(
                            self.freeze, changed)
                    with self.assertRaisesRegex(
                            RuntimeError, "frozen-product"):
                        validator._independent_link_projection(
                            self.freeze, changed, frozen_sources)

            for role in (
                    "direct_scalar_source", "device_source",
                    "compaction_source"):
                with self.subTest(path="source", role=role):
                    changed = copy.deepcopy(self.runtime)
                    changed["files"][role]["sha256"] = _named_sha(
                        "mutated-" + role)
                    with self.assertRaisesRegex(
                            RuntimeError, "frozen-source"):
                        validator._primary_link_projection(
                            self.freeze, changed)
                    with self.assertRaisesRegex(
                            RuntimeError, "frozen-source"):
                        validator._independent_link_projection(
                            self.freeze, changed, frozen_sources)

            changed = copy.deepcopy(self.runtime)
            changed["pyoptix"]["goal5800_v7_source_sha256"] = _named_sha(
                "mutated-goal5800")
            with self.assertRaisesRegex(RuntimeError, "Goal5800"):
                validator._primary_link_projection(self.freeze, changed)
            with self.assertRaisesRegex(RuntimeError, "Goal5800"):
                validator._independent_link_projection(
                    self.freeze, changed, frozen_sources)

    def test_package_and_both_deployment_mappings_change_the_verdict(self):
        frozen_sources = validator._rebuild_frozen_sources_independently(
            self.freeze, self.root)
        kat_patches = self._all_validation_mocks()[2:5]
        with kat_patches[0], kat_patches[1], kat_patches[2]:
            for field, value in (
                    ("file_count", 38),
                    ("tree_sha256", _named_sha("mutated-tree"))):
                changed = copy.deepcopy(self.runtime)
                changed["directories"]["rtdsl_package"][field] = value
                with self.assertRaisesRegex(RuntimeError, "package"):
                    validator._primary_link_projection(self.freeze, changed)
                with self.assertRaisesRegex(RuntimeError, "package"):
                    validator._independent_link_projection(
                        self.freeze, changed, frozen_sources)
            for family in ("relation", "triangle"):
                changed = copy.deepcopy(self.runtime)
                changed["deployment_ids"][family] = "mutated-" + family
                with self.assertRaisesRegex(RuntimeError, "deployment"):
                    validator._primary_link_projection(self.freeze, changed)
                with self.assertRaisesRegex(RuntimeError, "deployment"):
                    validator._independent_link_projection(
                        self.freeze, changed, frozen_sources)

    def test_frozen_source_rebuild_rejects_one_byte_drift(self):
        validator._rebuild_frozen_sources_independently(
            self.freeze, self.root)
        relative = validator.PYOPTIX_SCALAR_SOURCE
        source = self.root.joinpath(*Path(relative).parts)
        payload = source.read_bytes()
        source.write_bytes(bytes([payload[0] ^ 1]) + payload[1:])
        with self.assertRaisesRegex(RuntimeError, "source bytes differ"):
            validator._rebuild_frozen_sources_independently(
                self.freeze, self.root)

    def test_any_execution_or_timing_lock_drift_rejects(self):
        mutations = (
            ("freeze-formal", lambda freeze, runtime:
             freeze["authorization"].__setitem__("formal_worker_zero", True)),
            ("freeze-timing", lambda freeze, runtime:
             freeze.__setitem__("registered_performance_timing_count", 1)),
            ("runtime-worker", lambda freeze, runtime:
             runtime.__setitem__("formal_worker_zero", True)),
            ("runtime-timing", lambda freeze, runtime:
             runtime.__setitem__("registered_performance_timing_count", 1)),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                freeze = copy.deepcopy(self.freeze)
                runtime = copy.deepcopy(self.runtime)
                mutate(freeze, runtime)
                with self.assertRaisesRegex(RuntimeError, "execution lock"):
                    validator._validate_zero_locks(freeze, runtime)

    def test_failure_is_create_only_sealed_and_authorizes_nothing(self):
        bad_freeze = self.root / "bad-freeze.json"
        bad_freeze.write_text("[]\n", encoding="utf-8")
        output = self.root / "failure.json"
        exit_code = validator.run(
            root=self.root, freeze_path=bad_freeze,
            runtime_path=self.runtime_path, output=output)
        self.assertEqual(exit_code, 1)
        result = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(result["schema"], validator.FAILURE_SCHEMA)
        self.assertEqual(result["status"], validator.FAILURE_STATUS)
        self.assertFalse(result["execution_authority_consumed"])
        self.assertFalse(result["formal_execution_authorized"])
        self.assertFalse(result["same_transaction_retry_allowed"])
        self.assertFalse(result["result_conditioned_replacement_allowed"])
        self.assertEqual(result["formal_worker_count"], 0)
        self.assertEqual(result["clock_read_count"], 0)
        self.assertEqual(result["gpu_kernel_launch_count"], 0)
        unsigned = dict(result)
        observed = unsigned.pop("receipt_sha256")
        self.assertEqual(observed, validator._digest(unsigned))

    def test_existing_output_is_never_overwritten(self):
        output = self.root / "existing.json"
        output.write_bytes(b"owner bytes\n")
        with self.assertRaises(FileExistsError):
            validator.run(
                root=self.root, freeze_path=self.freeze_path,
                runtime_path=self.runtime_path, output=output)
        self.assertEqual(output.read_bytes(), b"owner bytes\n")

    def test_source_has_no_execution_authority_worker_or_clock_entrypoint(self):
        source = inspect.getsource(validator)
        for forbidden in (
                "--execution-authority", "execute_formal(",
                "from experiments.goal5802_premeasurement import controller",
                "import subprocess", "perf_counter", "monotonic(",
                "time.time(", "datetime.now("):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)
        for required in (
                'parser.add_argument("--root"',
                'parser.add_argument("--freeze"',
                'parser.add_argument("--runtime-manifest"',
                'parser.add_argument("--output"'):
            self.assertIn(required, source)


if __name__ == "__main__":
    unittest.main()

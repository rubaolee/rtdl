from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

import numpy  # Keep the extension loaded across sys.modules patch snapshots.

from experiments.goal5805_successor.protocol import digest, file_record
from experiments import goal5809_pyoptix_bulk_input as bulk_input
from scripts import goal5809_runtime_session_two_app_pilot as pilot


class _Clock:
    def __init__(self) -> None:
        self.value = 1_000_000

    def __call__(self) -> int:
        self.value += 100
        return self.value


class _Prepared:
    def __init__(self, task: str, events: list[str], *, wrong: bool) -> None:
        self.task = task
        self.events = events
        self.wrong = wrong
        self.close_count = 0

    def execute(self, _batch: object, *, include_diagnostics: bool) -> object:
        self.events.append(f"execute:{self.task}:{include_diagnostics}")
        if self.task == "relation":
            output = ((99, 99),) if self.wrong else ((7, 7),)
        else:
            output = 999 if self.wrong else 5
        return SimpleNamespace(
            output=output,
            device_status={"ok": True},
            executable_identity_sha256=f"identity-{self.task}",
        )

    def close(self) -> None:
        self.close_count += 1
        self.events.append(f"prepared.close:{self.task}")


class _Session:
    def __init__(
        self, events: list[str], *, native_path: Path, native_sha256: str,
        wrong_task: str | None,
    ) -> None:
        self.events = events
        self.native_library_path = native_path
        self.native_library_sha256 = native_sha256
        self.cache_entry_identity = f"123:{native_sha256}"
        self.owner_pid = 123
        self.closed = False
        self.wrong_task = wrong_task
        self.prepared: list[_Prepared] = []

    def prepare(self, loaded: object, _static: object) -> _Prepared:
        self.events.append(f"session.prepare:{loaded.task}")
        owner = _Prepared(
            loaded.task, self.events, wrong=loaded.task == self.wrong_task)
        self.prepared.append(owner)
        return owner

    def close(self) -> None:
        self.events.append("session.close")
        self.closed = True


class _Loaded:
    def __init__(
        self, task: str, events: list[str], *, native_path: Path,
        native_sha256: str, wrong_task: str | None,
    ) -> None:
        self.task = task
        self.events = events
        self.executable_identity_sha256 = f"identity-{task}"
        self.composed_ptx = f"// composed PTX for {task}"
        self.native_path = native_path
        self.native_sha256 = native_sha256
        self.wrong_task = wrong_task
        self.open_count = 0
        self.session: _Session | None = None

    def open_runtime_session(self, native_path: Path) -> _Session:
        self.events.append(f"open_session:{self.task}")
        self.open_count += 1
        self.session = _Session(
            self.events, native_path=native_path,
            native_sha256=self.native_sha256,
            wrong_task=self.wrong_task)
        return self.session


class _Runtime:
    __name__ = "rtdsl"

    def __init__(
        self, events: list[str], *, native_path: Path,
        native_sha256: str, wrong_task: str | None = None,
    ) -> None:
        self.events = events
        self.loaded: dict[str, _Loaded] = {}
        self.native_path = native_path
        self.native_sha256 = native_sha256
        self.wrong_task = wrong_task

    def install_rtdlexe_deployment(self, **kwargs: object) -> object:
        deployment_id = str(kwargs["deployment_id"])
        task = deployment_id.rsplit("/", 1)[-1]
        self.events.append(f"install:{task}")
        return SimpleNamespace(task=task)

    def load_rtdlexe(self, **kwargs: object) -> _Loaded:
        task = kwargs["deployment"].task
        self.events.append(f"load:{task}")
        loaded = _Loaded(
            task, self.events, native_path=self.native_path,
            native_sha256=self.native_sha256,
            wrong_task=self.wrong_task)
        self.loaded[task] = loaded
        return loaded

    @staticmethod
    def BoundedRelationBufferStaticInput(**kwargs: object) -> object:
        return ("relation-static", kwargs)

    @staticmethod
    def BoundedRelationBufferBatch(**kwargs: object) -> object:
        return ("relation-batch", kwargs)

    @staticmethod
    def TriangleReductionBufferStaticInput(**kwargs: object) -> object:
        return ("triangle-static", kwargs)

    @staticmethod
    def TriangleReductionBufferBatch(**kwargs: object) -> object:
        return ("triangle-batch", kwargs)


class _Workloads:
    __file__ = __file__

    @staticmethod
    def relation_workload() -> dict[str, object]:
        return {
            "indexed": [[0.0, 0.0, 1.0, 1.0, 7]],
            "sources": [[0.0, 0.0, 1.0, 1.0, 7]],
            "expected_rows": [[7, 7]],
        }

    @staticmethod
    def triangle_workload() -> dict[str, object]:
        return {
            "vertices": [
                [-1.0, -1.0, 1.0], [1.0, -1.0, 1.0],
                [0.0, 1.0, 1.0],
            ],
            "queries": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], 2.0]],
            "weights": [5],
            "expected_reduced_u64": 5,
        }


def _admitted(root: Path, native_sha256: str) -> dict[str, object]:
    native = root / "librtdl_optix.so"
    return {
        "target_path": root / "target.json",
        "target_file_sha256": "a" * 64,
        "candidate_path": root / "candidate.json",
        "candidate_file_sha256": "b" * 64,
        "target": {
            "target_manifest_sha256": "c" * 64,
            "files": {
                "native_library": {
                    "path": str(native), "sha256": native_sha256,
                },
                "matched_ptx": {"sha256": "9" * 64},
                "trust_root": {"path": str(root / "root.json")},
                "trust_head": {"path": str(root / "head.json")},
                "trust_package": {"path": str(root / "package.json")},
            },
        },
        "candidates": {
            task: {
                "artifact_path": root / f"{task}.rtdlexe",
                "artifact_sha256": ("d" if task == "relation" else "e") * 64,
                "authority_path": root / f"{task}.authority.json",
                "authority_sha256": ("f" if task == "relation" else "0") * 64,
                "deployment_id": f"deployment/{task}",
                "executable_identity_sha256": f"identity-{task}",
            }
            for task in pilot.TASK_KEYS
        },
    }


class RuntimeSessionTwoAppPilotTest(unittest.TestCase):
    def _run(
        self, root: Path, *, first_app: str = "relation",
        wrong_task: str | None = None,
    ) -> tuple[dict[str, object], _Runtime, list[str]]:
        events: list[str] = []
        native_sha256 = "1" * 64
        runtime = _Runtime(
            events, native_path=root / "librtdl_optix.so",
            native_sha256=native_sha256, wrong_task=wrong_task)
        implementation = SimpleNamespace(__name__="rtdsl.v4_rtdlexe")
        args = argparse.Namespace(
            target_manifest=root / "target.json",
            expected_target_manifest_sha256="a" * 64,
            execution_identity_manifest=root / "execution_identity.json",
            expected_execution_identity_manifest_sha256="b" * 64,
            first_app=first_app,
        )
        with mock.patch.object(
                pilot, "_admit_target",
                return_value=_admitted(root, native_sha256)), mock.patch.object(
                pilot, "_preload_runtime",
                return_value=(
                    _Workloads, runtime, implementation,
                    {"status": "PASS__SYNTHETIC_PRELOAD"}, bulk_input)), \
                mock.patch.object(
                    pilot, "admit_execution_identity",
                    return_value={
                        "manifest_file_sha256": "b" * 64,
                        "execution_identity_sha256": "c" * 64,
                        "file_count": 27,
                        "files_rehashed": True,
                        "runtime_environment_admission": {
                            "environment_identity_sha256": "7" * 64,
                        },
                    }), mock.patch.object(
                    pilot, "verify_loaded_rtdl",
                    return_value={
                        "rtdl_loaded_identity_verified": True,
                        "loaded_modules": {},
                    }), mock.patch.object(
                    pilot, "verify_loaded_modules",
                    return_value={
                        "loaded_module_identity_verified": True,
                        "loaded_modules": {},
                    }), mock.patch.object(
                    pilot, "verify_loaded_runtime_dependencies",
                    return_value={
                        "loaded_dependency_identity_sha256": "8" * 64,
                    }), mock.patch.dict(pilot.sys.modules, {
                        "rtdsl.physical_execution_provenance": SimpleNamespace(
                            __file__=str(root / "provenance.py")),
                        "experiments.goal5802_premeasurement.rtdlexe_arm": (
                            SimpleNamespace(__file__=str(root / "arm.py"))),
                    }):
            result = pilot._run(args, clock=_Clock())
        return result, runtime, events

    def test_one_session_executes_both_apps_once_and_closes_in_reverse(self) \
            -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result, runtime, events = self._run(
                Path(temporary), first_app="triangle")

        self.assertEqual(result["lifecycle"]["app_order"], [
            "triangle", "relation"])
        self.assertEqual(result["lifecycle"]["runtime_session_count"], 1)
        self.assertEqual(result["lifecycle"]["execute_call_count"], 2)
        self.assertEqual(result["lifecycle"]["warmup_execute_call_count"], 0)
        self.assertEqual(runtime.loaded["triangle"].open_count, 1)
        self.assertEqual(runtime.loaded["relation"].open_count, 0)
        self.assertEqual(events, [
            "install:relation", "load:relation",
            "install:triangle", "load:triangle",
            "open_session:triangle",
            "session.prepare:triangle", "execute:triangle:False",
            "session.prepare:relation", "execute:relation:False",
            "prepared.close:relation", "prepared.close:triangle",
            "session.close",
        ])
        self.assertTrue(result["applications"]["relation"][
            "exact_oracle_passed"])
        self.assertTrue(result["applications"]["triangle"][
            "exact_oracle_passed"])
        self.assertNotEqual(
            result["applications"]["relation"]["composed_ptx_sha256"],
            result["applications"]["triangle"]["composed_ptx_sha256"])
        self.assertTrue(result["lifecycle"][
            "post_custody_admission_file_bytes_already_rehashed"])
        self.assertFalse(result["lifecycle"][
            "artifact_file_cache_coldness_preserved"])
        self.assertEqual(
            result["phase_times_absolute"]["phase_order"],
            list(pilot.REQUIRED_PHASES))
        self.assertEqual(pilot.REQUIRED_PHASES[6:10], (
            "first_app_prepare",
            "first_app_first_exact_execute",
            "second_app_prepare",
            "second_app_first_exact_execute",
        ))
        for row in result["phase_times_absolute"]["phases"].values():
            self.assertEqual(row["duration_ns"], 100)
            self.assertEqual(row["duration_ms"], 0.0001)
            self.assertLess(
                row["start_perf_counter_ns"], row["end_perf_counter_ns"])
        self.assertTrue(result["session_identity"][
            "closed_after_close_phase"])
        self.assertEqual(result["registered_performance_timing_count"], 0)
        self.assertEqual(
            result["status"],
            "COMPLETE__DIAGNOSTIC_TWO_APPLICATION_RUNTIME_SESSION_PILOT")
        self.assertEqual(
            result["schema"],
            "rtdl.goal5809.runtime_session_two_app_pilot.v2")
        self.assertTrue(result["scope"]["nonformal_diagnostic"])
        self.assertFalse(result["scope"]["formal_evidence"])
        self.assertFalse(result["scope"]["paper_evidence"])
        self.assertFalse(result["scope"][
            "threshold_or_noninferiority_claim_authorized"])
        self.assertTrue(result["lifecycle"][
            "each_app_prepare_and_first_exact_execute_separately_observed"])
        self.assertTrue(result["lifecycle"][
            "prepare_and_first_exact_execute_phase_rows_adjacent"])
        self.assertFalse(result["lifecycle"]["zero_interphase_gap_claimed"])
        self.assertTrue(result["phase_times_absolute"][
            "interphase_gaps_all_nonnegative"])
        self.assertTrue(result["execution_identity"][
            "rtdl_loaded_identity_verified"])

    def test_oracle_failure_closes_failed_owner_and_the_only_session(self) \
            -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            events: list[str] = []
            native_sha256 = "1" * 64
            runtime = _Runtime(
                events, native_path=root / "librtdl_optix.so",
                native_sha256=native_sha256, wrong_task="relation")
            args = argparse.Namespace(
                target_manifest=root / "target.json",
                expected_target_manifest_sha256="a" * 64,
                execution_identity_manifest=root / "execution_identity.json",
                expected_execution_identity_manifest_sha256="b" * 64,
                first_app="relation",
            )
            with mock.patch.object(
                    pilot, "_admit_target",
                    return_value=_admitted(root, native_sha256)), \
                    mock.patch.object(
                    pilot, "_preload_runtime",
                    return_value=(
                        _Workloads, runtime,
                        SimpleNamespace(__name__="rtdsl.v4_rtdlexe"),
                        {"status": "PASS__SYNTHETIC_PRELOAD"}, bulk_input)), \
                    mock.patch.object(
                        pilot, "admit_execution_identity",
                        return_value={
                            "manifest_file_sha256": "b" * 64,
                            "execution_identity_sha256": "c" * 64,
                            "file_count": 27,
                            "files_rehashed": True,
                            "runtime_environment_admission": {
                                "environment_identity_sha256": "7" * 64,
                            },
                        }):
                with self.assertRaisesRegex(
                        RuntimeError, "relation exact oracle mismatch"):
                    pilot._run(args, clock=_Clock())

        session = runtime.loaded["relation"].session
        self.assertIsNotNone(session)
        self.assertTrue(session.closed)
        self.assertEqual(session.prepared[0].close_count, 1)
        self.assertNotIn("session.prepare:triangle", events)
        self.assertEqual(events.count("session.close"), 1)

    def test_target_admission_rehashes_nested_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            files: dict[str, Path] = {}
            for name in (
                    "trust_root", "trust_head", "trust_package",
                    "native_library", "matched_ptx",
                    "relation_compaction_cubin", "runtime_manifest",
                    "target_observation"):
                path = root / f"{name}.bin"
                path.write_bytes(name.encode("ascii"))
                files[name] = path
            candidates: dict[str, dict[str, object]] = {}
            for index, task in enumerate(pilot.TASK_KEYS):
                artifact = root / f"{task}.rtdlexe"
                authority = root / f"{task}.authority.json"
                artifact.write_bytes(f"artifact-{task}".encode("ascii"))
                authority.write_bytes(f"authority-{task}".encode("ascii"))
                candidates[task] = {
                    "artifact_path": str(artifact),
                    "artifact_sha256": hashlib.sha256(
                        artifact.read_bytes()).hexdigest(),
                    "authority_path": str(authority),
                    "authority_sha256": hashlib.sha256(
                        authority.read_bytes()).hexdigest(),
                    "deployment_id": f"test/{task}/{index}",
                    "executable_identity_sha256": str(index + 2) * 64,
                }
            candidate = {
                "schema": "rtdl.test.candidate.v1",
                "registered_timing_count": 0,
                "native_sha256": _file_sha(files["native_library"]),
                "candidates": candidates,
            }
            candidate_path = root / "candidate.json"
            candidate_path.write_text(
                json.dumps(candidate, sort_keys=True), encoding="utf-8")
            target_files = {
                **{name: file_record(path) for name, path in files.items()},
                "candidate_manifest": file_record(candidate_path),
            }
            target: dict[str, object] = {
                "schema": "rtdl.goal5805.target_products.v1",
                "status": "TARGET_PRODUCTS_FROZEN__FORMAL_WORKER_ZERO",
                "files": target_files,
                "registered_performance_timing_count": 0,
                "formal_worker_count": 0,
            }
            target["target_manifest_sha256"] = digest(target)
            target_path = root / "target.json"
            target_path.write_text(
                json.dumps(target, sort_keys=True), encoding="utf-8")
            target_file_sha256 = _file_sha(target_path)

            admitted = pilot._admit_target(
                target_path, expected_file_sha256=target_file_sha256)
            self.assertEqual(set(admitted["candidates"]), set(pilot.TASK_KEYS))

            Path(candidates["triangle"]["artifact_path"]).write_bytes(
                b"mutated")
            with self.assertRaisesRegex(
                    RuntimeError, "triangle artifact bytes differ"):
                pilot._admit_target(
                    target_path, expected_file_sha256=target_file_sha256)

    def test_source_opens_one_session_and_has_no_formal_execution_route(self) \
            -> None:
        text = Path(pilot.__file__).read_text(encoding="utf-8")
        self.assertEqual(text.count(".open_runtime_session("), 1)
        self.assertNotIn(".bind_provider(", text)
        self.assertNotIn("formal_worker.py", text)
        self.assertNotIn("first_app_prepare_execute", text)
        self.assertNotIn("second_app_prepare_execute", text)
        self.assertEqual(text.count("session.prepare("), 1)
        self.assertEqual(text.count("prepared.execute("), 1)
        self.assertIn('"ratio_computation_authorized": False', text)
        self.assertIn('"paper_evidence": False', text)
        self.assertIn('"registered_performance_timing_count": 0', text)


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()

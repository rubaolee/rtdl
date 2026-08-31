from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from experiments.goal5802_premeasurement import controller as premeasurement


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5802_run_pod_s0_untimed.py"
SPEC = importlib.util.spec_from_file_location("goal5802_pod_s0", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
s0 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(s0)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(s0._canonical(value) + b"\n")


class Goal5802PodS0OrchestratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.source = self.base / "source"
        self.run_root = self.base / "run"
        self.source.mkdir()
        self.git = Path(shutil.which("git") or "")
        if not self.git.is_file():
            self.skipTest("git executable unavailable")
        for target in sorted(set(s0.SCRIPT_TARGETS.values())):
            path = self.source / target
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        (self.source / "experiments").mkdir(exist_ok=True)
        (self.source / "experiments/__init__.py").write_text(
            "", encoding="utf-8")
        (self.source / "experiments/s0_import_probe.py").write_text(
            "VALUE = 'SOURCE_ROOT_IMPORT_OK'\n", encoding="utf-8")
        (self.source / "src/rtdsl").mkdir(parents=True)
        (self.source / "src/rtdsl/__init__.py").write_text(
            "VALUE = 'SOURCE_SRC_IMPORT_OK'\n", encoding="utf-8")
        source_probe = self.source / s0.SCRIPT_TARGETS["source_packet_verify"]
        source_probe.write_text(
            "from pathlib import Path\n"
            "import os,sys\n"
            "from experiments.s0_import_probe import VALUE\n"
            "Path(sys.argv[1]).write_text(VALUE + ':' + "
            "os.environ.get('PYTHONHASHSEED','NONE'), encoding='utf-8')\n",
            encoding="utf-8")
        candidate_probe = self.source / s0.SCRIPT_TARGETS["candidate_seed1"]
        candidate_probe.write_text(
            "from pathlib import Path\n"
            "import os,sys\n"
            "from rtdsl import VALUE\n"
            "Path(sys.argv[2]).write_text(VALUE + ':' + "
            "os.environ.get('PYTHONHASHSEED','NONE'), encoding='utf-8')\n",
            encoding="utf-8")
        subprocess.run(
            [str(self.git), "init", "-q", str(self.source)], check=True)
        subprocess.run(
            [str(self.git), "-C", str(self.source), "config", "user.name", "test"],
            check=True)
        subprocess.run(
            [str(self.git), "-C", str(self.source), "config", "user.email",
             "test@example.invalid"], check=True)
        subprocess.run(
            [str(self.git), "-C", str(self.source), "config", "core.autocrlf",
             "false"], check=True)
        subprocess.run(
            [str(self.git), "-C", str(self.source), "add", "."], check=True)
        subprocess.run(
            [str(self.git), "-C", str(self.source), "commit", "-q", "-m", "fixture"],
            check=True)
        self.commit = subprocess.check_output(
            [str(self.git), "-C", str(self.source), "rev-parse", "HEAD"],
            text=True).strip()
        self.tree = subprocess.check_output(
            [str(self.git), "-C", str(self.source), "rev-parse", "HEAD^{tree}"],
            text=True).strip()
        self.packet_manifest = self.base / "source_packet_manifest.json"
        self.public_root = self.base / "public_root.json"
        self.packet_manifest.write_bytes(b"{}\n")
        self.public_root.write_bytes(b"{}\n")
        self.config = self._config()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _steps(self, names: tuple[str, ...], phase: str) -> list[dict[str, object]]:
        rows = []
        for name in names:
            if name == "plan_only":
                runner = "python_module"
                target = s0.PLAN_ONLY_MODULE
                args = [
                    "--freeze", str(self.run_root / "final/freeze.json"),
                    "--root", str(self.source),
                    "--plan-output", str(self.run_root / "final/plan.json"),
                ]
            else:
                runner = "executable" if name == "pyoptix_clean_install" \
                    else "python_script"
                target = s0.SCRIPT_TARGETS[name]
                args = ["build"] if name.startswith("candidate_seed") \
                    else ["--synthetic"]
            environment = {}
            if name == "candidate_seed1":
                environment["PYTHONHASHSEED"] = "1"
            if name == "candidate_seed777":
                environment["PYTHONHASHSEED"] = "777"
            rows.append({
                "schema": s0.STEP_SCHEMA,
                "name": name,
                "runner": runner,
                "target": target,
                "interpreter": None if runner == "executable" else str(
                    Path(sys.executable).resolve()),
                "args": args,
                "environment": environment,
                "outputs": [{
                    "path": str(self.run_root / phase / f"{name}.json"),
                    "kind": "file",
                }],
            })
        return rows

    def _config(self) -> dict[str, object]:
        return {
            "schema": s0.CONFIG_SCHEMA,
            "source_root": str(self.source),
            "source_commit": self.commit,
            "source_tree": self.tree,
            "git": str(self.git.resolve()),
            "python": str(Path(sys.executable).resolve()),
            "run_root": str(self.run_root),
            "source_packet_manifest": str(self.packet_manifest),
            "public_trust_root": str(self.public_root),
            "trust_root_scope": s0.QUALIFICATION_ONLY_TRUST_SCOPE,
            "trust_root_file_sha256": hashlib.sha256(
                self.public_root.read_bytes()).hexdigest(),
            "private_key_sha256": "1" * 64,
            "deployment_generation": "v3",
            "candidate_seeds": [1, 777],
            "wheel_seeds": [1, 777],
            "relation_minimum_overlap_f32": 1.0,
            "prepare_steps": self._steps(s0.PREPARE_STEPS, "prepare"),
            "finish_steps": self._steps(s0.FINISH_STEPS, "finish"),
            "candidate_manifests": {
                "seed1": str(self.run_root / "candidates/seed1/candidate_manifest.json"),
                "seed777": str(
                    self.run_root / "candidates/seed777/candidate_manifest.json"),
            },
            "final_outputs": {
                "freeze": str(self.run_root / "final/freeze.json"),
                "runtime_manifest": str(self.run_root / "final/runtime.json"),
                "dual_validation": str(self.run_root / "final/dual.json"),
                "plan": str(self.run_root / "final/plan.json"),
            },
            "claim_boundary": {
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
                "execution_authority_consumed": False,
                "gpu_use": "UNTIMED_TARGET_OBSERVATION_AND_OPERATION_KATS_ONLY",
                "retry_resume_replacement_allowed": False,
                "target_selection_allowed": False,
            },
        }

    def _load(self, value: dict[str, object]) -> dict[str, object]:
        path = self.base / "config.json"
        _write_json(path, value)
        return s0._load_config(path, self.run_root)

    def test_exact_stage_order_zero_lock_and_source_identity_pass(self) -> None:
        loaded = self._load(self.config)
        self.assertEqual(
            [row["name"] for row in loaded["prepare_steps"]],
            list(s0.PREPARE_STEPS))
        self.assertEqual(
            [row["name"] for row in loaded["finish_steps"]],
            list(s0.FINISH_STEPS))
        s0._verify_source(loaded)

    def test_prepare_uses_one_config_payload_when_source_path_is_replaced(
            self) -> None:
        config_a = copy.deepcopy(self.config)
        config_b = copy.deepcopy(self.config)
        config_a["prepare_steps"][0]["environment"] = {"LANG": "A"}
        config_b["prepare_steps"][0]["environment"] = {"LANG": "B"}
        config_path = self.base / "replaceable_config.json"
        _write_json(config_path, config_a)
        payload_a = config_path.read_bytes()
        original_loader = s0._load_config_with_bytes

        def load_then_replace(path: Path, run_root: Path):
            loaded, payload = original_loader(path, run_root)
            _write_json(config_path, config_b)
            return loaded, payload

        pass_receipt = {
            "status": "PASS__CREATE_ONLY_UNTIMED_STEP",
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
        }
        comparison = {"seeds": [1, 777], "identical": True}
        with mock.patch.object(
                s0, "_load_config_with_bytes", side_effect=load_then_replace), \
                mock.patch.object(s0, "_verify_source"), \
                mock.patch.object(
                    s0, "_run_step", return_value=pass_receipt), \
                mock.patch.object(
                    s0, "_verify_double_seed", return_value=comparison), \
                mock.patch.object(
                    s0, "_trust_request", return_value={"request": "test"}):
            state = s0.prepare(config_path, self.run_root)
            validated_state, validated_config = s0._validate_prepared_state(
                self.run_root / "prepared_state.json")

        copied = (self.run_root / "s0_config.json").read_bytes()
        self.assertEqual(copied, payload_a)
        self.assertNotEqual(copied, config_path.read_bytes())
        self.assertEqual(
            state["config"]["sha256"], hashlib.sha256(payload_a).hexdigest())
        self.assertEqual(validated_state, state)
        self.assertEqual(
            validated_config["prepare_steps"][0]["environment"],
            {"LANG": "A"})

    def test_formal_authority_seed_and_order_mutations_reject(self) -> None:
        hostile = copy.deepcopy(self.config)
        hostile["finish_steps"][-1]["args"].append("--execution-authority")
        with self.assertRaises(s0.S0Error):
            self._load(hostile)

        hostile = copy.deepcopy(self.config)
        hostile["prepare_steps"][-1]["environment"]["PYTHONHASHSEED"] = "1"
        with self.assertRaises(s0.S0Error):
            self._load(hostile)

    def test_postuse_custody_baseline_distinguishes_formal_from_qualification(self) -> None:
        formal = s0._expected_postuse_custody_counters({
            "key_id": s0.FORMAL_MEASUREMENT_TRUST_KEY_ID,
        })
        qualification = s0._expected_postuse_custody_counters({
            "key_id": "TEST_ONLY_goal5802_final_home_qualification_unit",
        })
        self.assertEqual(
            formal["diagnostic_keypair_signing_invocation_known_minimum"], 0)
        self.assertFalse(formal[
            "diagnostic_keypair_signing_invocation_count_exactly_attested"])
        self.assertIsNone(formal[
            "diagnostic_keypair_signing_invocation_exact_count"])
        self.assertEqual(
            qualification["diagnostic_keypair_signing_invocation_known_minimum"], 2)
        self.assertTrue(qualification[
            "diagnostic_keypair_signing_invocation_count_exactly_attested"])
        self.assertEqual(qualification[
            "diagnostic_keypair_signing_invocation_exact_count"], 2)

        hostile = copy.deepcopy(self.config)
        hostile["prepare_steps"][0], hostile["prepare_steps"][1] = (
            hostile["prepare_steps"][1], hostile["prepare_steps"][0])
        with self.assertRaises(s0.S0Error):
            self._load(hostile)

    def _candidate(self, root: Path, artifact_payload: bytes) -> Path:
        root.mkdir(parents=True)
        candidates = {}
        for family in ("relation", "triangle"):
            artifact = root / f"{family}.rtdlexe"
            authority = root / f"{family}.authority.json"
            artifact.write_bytes(artifact_payload + family.encode())
            authority.write_bytes((family + "-authority\n").encode())
            candidates[family] = {
                "deployment_id": f"goal5801/lx1/{family}/v3",
                "artifact_path": str(artifact),
                "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "authority_path": str(authority),
                "authority_sha256": hashlib.sha256(authority.read_bytes()).hexdigest(),
                "executable_identity_sha256": (
                    "a" if family == "relation" else "b") * 64,
            }
        manifest = {
            "schema": "rtdl.goal5801.lx1_untimed_candidate_manifest.v2",
            "status": "UNTRUSTED_CANDIDATES__NOT_AUTHORIZED",
            "registered_timing_count": 0,
            "native_path": "/target/native.so",
            "native_sha256": "a" * 64,
            "proof_path": "/source/proof.json",
            "proof_sha256": "b" * 64,
            "relation_protocol": {"capacity": 4096},
            "candidates": candidates,
        }
        path = root / "candidate_manifest.json"
        path.write_bytes(json.dumps(
            manifest, indent=2, sort_keys=True).encode() + b"\n")
        return path

    def test_candidate_double_seed_requires_byte_identical_payloads(self) -> None:
        first = self._candidate(self.base / "seed1", b"same-")
        second = self._candidate(self.base / "seed777", b"same-")
        config = {"candidate_manifests": {
            "seed1": str(first), "seed777": str(second)}}
        value = s0._verify_double_seed(config)
        self.assertEqual(value["seeds"], [1, 777])
        (second.parent / "triangle.rtdlexe").write_bytes(b"mutated")
        with self.assertRaises(s0.S0Error):
            s0._verify_double_seed(config)

    def test_terminal_receipt_is_create_only_and_zero_locked(self) -> None:
        self.run_root.mkdir()
        s0._terminal(self.run_root, "prepare", [], s0.S0Error("synthetic"))
        value = json.loads(
            (self.run_root / "prepare_terminal_failure.json").read_text())
        self.assertEqual(value["formal_worker_count"], 0)
        self.assertEqual(value["registered_performance_timing_count"], 0)
        self.assertFalse(value["execution_authority_consumed"])
        before = (self.run_root / "prepare_terminal_failure.json").read_bytes()
        s0._terminal(self.run_root, "prepare", [], s0.S0Error("different"))
        self.assertEqual(
            before, (self.run_root / "prepare_terminal_failure.json").read_bytes())

    def _current_final_outputs(
            self) -> tuple[dict[str, object], dict[str, object]]:
        final_root = self.base / "current_final_outputs"
        final_root.mkdir()
        source_freeze = final_root / "source_freeze.json"
        _write_json(source_freeze, {
            "schema": premeasurement.SCHEMA,
            "freeze_sha256": "f" * 64,
            "worker_row_count": 432,
            "build_cold_absolute_worker_row_count": 72,
        })
        with mock.patch.object(premeasurement, "validate_freeze"):
            plan = premeasurement.local_plan(source_freeze, ROOT)
        paths = {
            "freeze": final_root / "freeze.json",
            "runtime_manifest": final_root / "runtime.json",
            "dual_validation": final_root / "dual.json",
            "plan": final_root / "plan.json",
        }
        _write_json(paths["freeze"], {
            "registered_performance_timing_count": 0,
        })
        _write_json(paths["runtime_manifest"], {
            "registered_performance_timing_count": 0,
        })
        _write_json(paths["dual_validation"], {
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "execution_authority_consumed": False,
        })
        _write_json(paths["plan"], plan)
        return {"final_outputs": {
            name: str(path) for name, path in paths.items()}}, plan

    def test_final_outputs_consume_real_current_plan_schema(self) -> None:
        config, plan = self._current_final_outputs()
        self.assertEqual(plan["worker_row_count"], 432)
        self.assertEqual(plan["build_cold_absolute_worker_row_count"], 72)
        self.assertNotIn("comparative_worker_count", plan)
        self.assertNotIn("build_cold_absolute_worker_count", plan)
        records = s0._validate_final_outputs(config)
        self.assertEqual(set(records), set(config["final_outputs"]))

    def test_final_plan_old_schema_wrong_values_and_bool_aliases_reject(self) -> None:
        config, baseline = self._current_final_outputs()
        plan_path = Path(str(config["final_outputs"]["plan"]))

        old_schema = copy.deepcopy(baseline)
        del old_schema["worker_row_count"]
        del old_schema["build_cold_absolute_worker_row_count"]
        old_schema["comparative_worker_count"] = 432
        old_schema["build_cold_absolute_worker_count"] = 72
        _write_json(plan_path, old_schema)
        with self.assertRaises(s0.S0Error):
            s0._validate_final_outputs(config)

        for field, value in (
                ("worker_row_count", 431),
                ("build_cold_absolute_worker_row_count", 71),
                ("worker_row_count", False),
                ("build_cold_absolute_worker_row_count", False),
                ("registered_performance_timing_count", False)):
            with self.subTest(field=field, value=value):
                hostile = copy.deepcopy(baseline)
                hostile[field] = value
                _write_json(plan_path, hostile)
                with self.assertRaises(s0.S0Error):
                    s0._validate_final_outputs(config)

        for field in ("formal_worker_zero", "legacy_goal5798_worker_allowed"):
            with self.subTest(field=field):
                hostile = copy.deepcopy(baseline)
                hostile[field] = True
                _write_json(plan_path, hostile)
                with self.assertRaises(s0.S0Error):
                    s0._validate_final_outputs(config)

    def test_source_root_import_bootstrap_and_step_interpreter_are_real(self) -> None:
        value = copy.deepcopy(self.config)
        output = self.run_root / "probe.txt"
        value["prepare_steps"][0]["args"] = [str(output)]
        value["prepare_steps"][0]["environment"] = {"PYTHONHASHSEED": "313"}
        value["prepare_steps"][0]["outputs"] = [
            {"path": str(output), "kind": "file"}]
        for row in value["prepare_steps"]:
            if row["name"] == "native_build":
                row["outputs"] = [{
                    "path": str(self.run_root / "native_build"),
                    "kind": "directory",
                }]
        loaded = self._load(value)
        self.run_root.mkdir()
        journal = self.run_root / "journal"
        journal.mkdir()
        receipt = s0._run_step(
            loaded["prepare_steps"][0], loaded, journal, 1)
        self.assertEqual(receipt["status"], "PASS__CREATE_ONLY_UNTIMED_STEP")
        self.assertEqual(output.read_text(encoding="utf-8"),
                         "SOURCE_ROOT_IMPORT_OK:313")

    def test_dynamic_context_is_derived_not_manually_supplied(self) -> None:
        value = copy.deepcopy(self.config)
        observation = self.run_root / "target.json"
        native_root = self.run_root / "native_build"
        for row in value["prepare_steps"]:
            if row["name"] == "target_observation":
                row["outputs"] = [{"path": str(observation), "kind": "file"}]
            if row["name"] == "native_build":
                row["outputs"] = [{"path": str(native_root), "kind": "directory"}]
        loaded = self._load(value)
        self.run_root.mkdir()
        _write_json(observation, {
            "schema": "rtdl.goal5802.target_observation.v2",
            "status": "PASS__UNTIMED_EXACT_TARGET_OBSERVATION",
            "compute_capability": "8.9",
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
        })
        links = {}
        for name in ("cuda", "nvrtc", "geos_c"):
            path = self.base / f"lib{name}.so"
            path.write_bytes(name.encode("ascii"))
            links[name] = path.resolve()
        receipts = native_root / "tool_receipts"
        receipts.mkdir(parents=True)
        (receipts / "native_ldd.txt").write_text(
            f"libcuda.so.1 => {links['cuda']} (0x1)\n"
            f"libnvrtc.so.12 => {links['nvrtc']} (0x2)\n"
            f"libgeos_c.so.1 => {links['geos_c']} (0x3)\n",
            encoding="utf-8")
        first = self._candidate(self.base / "dynamic_seed1", b"same-")
        loaded["candidate_manifests"]["seed1"] = str(first)
        context = s0._dynamic_context(loaded, None)
        self.assertEqual(context["${OBSERVED_CC}"], "8.9")
        self.assertEqual(context["${OBSERVED_SM}"], "sm_89")
        self.assertEqual(context["${LDD_CUDA}"], str(links["cuda"]))
        self.assertEqual(
            context["${RELATION_DEPLOYMENT_ID}"],
            "goal5801/lx1/relation/v3")
        self.assertEqual(
            s0._expand_dynamic(
                "cuda=${LDD_CUDA}", context, "test link input"),
            f"cuda={links['cuda']}")
        with self.assertRaises(s0.S0Error):
            s0._expand_dynamic(
                "wrong=${LDD_CUDA}", context, "test link input")
        with self.assertRaises(s0.S0Error):
            s0._expand_dynamic(
                "prefix-${LDD_CUDA}", context, "test link input")

    def test_candidate_bootstrap_adds_exact_source_src_and_preserves_seed(self) -> None:
        value = copy.deepcopy(self.config)
        output = self.run_root / "candidate_probe.txt"
        for row in value["prepare_steps"]:
            if row["name"] == "native_build":
                row["outputs"] = [{
                    "path": str(self.run_root / "native_build"),
                    "kind": "directory",
                }]
            if row["name"] == "candidate_seed1":
                row["args"] = ["build", str(output)]
                row["outputs"] = [{"path": str(output), "kind": "file"}]
        loaded = self._load(value)
        self.run_root.mkdir()
        journal = self.run_root / "journal"
        journal.mkdir()
        step = next(row for row in loaded["prepare_steps"]
                    if row["name"] == "candidate_seed1")
        receipt = s0._run_step(step, loaded, journal, 8)
        self.assertEqual(receipt["status"], "PASS__CREATE_ONLY_UNTIMED_STEP")
        self.assertEqual(output.read_text(encoding="utf-8"),
                         "SOURCE_SRC_IMPORT_OK:1")


if __name__ == "__main__":
    unittest.main()

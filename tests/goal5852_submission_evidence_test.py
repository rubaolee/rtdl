from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


VERIFY = _load_module(
    "goal5852_verify_test_module",
    ROOT / "paper" / "cgo2027" / "artifact_post_goal5851" / "verify.py",
)
EXPORTER = _load_module(
    "goal5852_exporter_test_module",
    ROOT / "scripts" / "goal5852_build_submission_evidence.py",
)


def _seal_row(body: dict[str, object]) -> dict[str, object]:
    return {**body, "row_sha256": VERIFY.digest(body)}


def _reseal_row(row: dict[str, object]) -> None:
    row.pop("row_sha256", None)
    row["row_sha256"] = VERIFY.digest(row)


def _reseal_projection(value: dict[str, object]) -> str:
    value.pop("projection_sha256", None)
    value["projection_sha256"] = VERIFY.digest(value)
    return value["projection_sha256"]


def _lifecycle(seed: int) -> dict[str, object]:
    post = 10_000 + seed
    partition = {name: 0 for name in VERIFY.PARTITION_KEYS}
    partition[VERIFY.PARTITION_KEYS[0]] = post
    return {
        "component_diagnostics_ns": {
            name: None for name in VERIFY.COMPONENT_KEYS
        },
        "endpoint_partition_ns": partition,
        "implementation_entry_to_first_correct_result_ns": 101 + post,
        "implementation_import_ns": 100,
        "implementation_import_to_endpoint_gap_ns": 1,
        "post_import_to_first_correct_result_ns": post,
    }


def _fixture_projection() -> dict[str, object]:
    formal = []
    for generation_index, generation in enumerate(VERIFY.GENERATIONS):
        for block in range(VERIFY.BLOCKS):
            for task_index, task in enumerate(VERIFY.TASKS):
                for arm_index, arm in enumerate(VERIFY.ARMS):
                    seed = 100_000 + generation_index * 10_000 + block * 100 + task_index * 10 + arm_index
                    samples = [seed + index for index in range(VERIFY.STEADY_REPETITIONS)]
                    formal.append(_seal_row({
                        "arm": arm,
                        "block": block,
                        "cell_id": f"{generation}-B{block:02d}-T{task_index}-A{arm_index}",
                        "generation": generation,
                        "lifecycle": None if arm == "D_DIRECT_CUDA_OPTIX" else _lifecycle(seed),
                        "oracle_exact": True,
                        "output_sha256": VERIFY.OUTPUT_SHA256[task],
                        "phase_instrumentation": None if arm == "D_DIRECT_CUDA_OPTIX" else True,
                        "source_label": VERIFY.SOURCE_LABEL_E if arm == VERIFY.ARMS[4] else VERIFY.SOURCE_LABEL_M,
                        "steady_median_ns": VERIFY.integer_median(samples),
                        "steady_samples_ns": samples,
                        "steady_samples_sha256": VERIFY.digest(samples),
                        "task": task,
                    }))
    instrumentation = []
    for generation_index, generation in enumerate(VERIFY.GENERATIONS):
        for task_index, task in enumerate(VERIFY.TASKS):
            for block in range(VERIFY.BLOCKS):
                for mode_index, mode in enumerate(("off", "on")):
                    for replicate in range(VERIFY.INSTRUMENTATION_REPLICATES):
                        instrumentation.append(_seal_row({
                            "block": block,
                            "endpoint_ns": 1_000_000 + generation_index * 10_000 + task_index * 1_000 + block * 100 + mode_index * 10 + replicate,
                            "generation": generation,
                            "mode": mode,
                            "replicate": replicate,
                            "source_label": VERIFY.SOURCE_LABEL_M,
                            "task": task,
                        }))
    aot = []
    competence = []
    for generation_index, generation in enumerate(VERIFY.GENERATIONS):
        for task_index, task in enumerate(VERIFY.TASKS):
            durations = [50_000_000 + generation_index * 1_000 + task_index * 100 + index for index in range(5)]
            aot.append(_seal_row({
                "cold_first_resolution_ns": 5_000_000_000,
                "durations_ns": durations,
                "generation": generation,
                "source_label": VERIFY.SOURCE_LABEL_M,
                "task": task,
            }))
            for arm_index, arm in enumerate(("B_IDIOMATIC_PINNED_PYOPTIX", "C_STRONG_DEVICE_CONTINUATION_PYOPTIX")):
                samples = [200_000 + generation_index * 1_000 + task_index * 100 + arm_index * 10 + index for index in range(VERIFY.STEADY_REPETITIONS)]
                competence.append(_seal_row({
                    "arm": arm,
                    "generation": generation,
                    "source_label": VERIFY.SOURCE_LABEL_M,
                    "steady_median_ns": VERIFY.integer_median(samples),
                    "steady_samples_ns": samples,
                    "steady_samples_sha256": VERIFY.digest(samples),
                    "task": task,
                }))
    body: dict[str, object] = {
        "schema": VERIFY.PROJECTION_SCHEMA,
        "contract": copy.deepcopy(VERIFY.EXPECTED_CONTRACT),
        "formal_workers": formal,
        "instrumentation_workers": instrumentation,
        "aot_qualification": aot,
        "nonformal_competence_workers": competence,
        "claim_boundary": {
            "cross_machine_raw_time_ratio_computed": False,
            "external_review_complete": False,
            "offline_recount_is_gpu_execution": False,
            "original_per_execution_receipt_requirement_fulfilled": False,
            "public_or_manuscript_claim_authorized": False,
        },
    }
    return {**body, "projection_sha256": VERIFY.digest(body)}


class Goal5852SubmissionEvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = _fixture_projection()

    def validate(self, value: dict[str, object]) -> None:
        VERIFY.validate_projection(
            value,
            expected_projection_sha256=value["projection_sha256"],
        )

    def test_complete_structural_fixture_accepts_legal_predecessor_exception(self) -> None:
        self.validate(self.projection)
        predecessor_rows = [
            row for row in self.projection["formal_workers"]
            if row["arm"] == VERIFY.ARMS[4]
        ]
        self.assertEqual(32, len(predecessor_rows))
        self.assertTrue(all(row["source_label"] == VERIFY.SOURCE_LABEL_E for row in predecessor_rows))

    def test_missing_worker_is_rejected_after_projection_reseal(self) -> None:
        self.projection["formal_workers"].pop()
        _reseal_projection(self.projection)
        with self.assertRaisesRegex(VERIFY.VerificationError, "worker count"):
            self.validate(self.projection)

    def test_duplicate_schedule_cell_is_rejected(self) -> None:
        self.projection["formal_workers"][-1] = copy.deepcopy(self.projection["formal_workers"][0])
        _reseal_projection(self.projection)
        with self.assertRaisesRegex(VERIFY.VerificationError, "duplicate schedule cell"):
            self.validate(self.projection)

    def test_missing_sample_is_rejected_even_when_all_hashes_are_resealed(self) -> None:
        row = self.projection["formal_workers"][0]
        row["steady_samples_ns"].pop()
        row["steady_samples_sha256"] = VERIFY.digest(row["steady_samples_ns"])
        row["steady_median_ns"] = VERIFY.integer_median(row["steady_samples_ns"])
        _reseal_row(row)
        _reseal_projection(self.projection)
        with self.assertRaisesRegex(VERIFY.VerificationError, "sample count"):
            self.validate(self.projection)

    def test_mutated_nanosecond_is_rejected_without_assert(self) -> None:
        row = self.projection["formal_workers"][0]
        row["steady_samples_ns"][0] += 1
        _reseal_row(row)
        _reseal_projection(self.projection)
        with self.assertRaisesRegex(VERIFY.VerificationError, "sample digest"):
            self.validate(self.projection)

    def test_wrong_successor_source_label_is_rejected(self) -> None:
        row = next(row for row in self.projection["formal_workers"] if row["arm"] == "A_RTDL_AOT_PUBLIC")
        row["source_label"] = VERIFY.SOURCE_LABEL_E
        _reseal_row(row)
        _reseal_projection(self.projection)
        with self.assertRaisesRegex(VERIFY.VerificationError, "source identity"):
            self.validate(self.projection)

    def test_wrong_predecessor_source_label_is_rejected(self) -> None:
        row = next(
            row
            for row in self.projection["formal_workers"]
            if row["arm"] == VERIFY.ARMS[4]
        )
        row["source_label"] = VERIFY.SOURCE_LABEL_M
        _reseal_row(row)
        _reseal_projection(self.projection)
        with self.assertRaisesRegex(VERIFY.VerificationError, "source identity"):
            self.validate(self.projection)

    def test_public_verifier_has_no_internal_goal_identifier(self) -> None:
        payload = (
            ROOT / "paper" / "cgo2027" / "artifact_post_goal5851" / "verify.py"
        ).read_text(encoding="utf-8")
        self.assertNotRegex(payload, r"(?i)goal\d+")

    def test_wrong_threshold_and_gate_type_are_rejected(self) -> None:
        for field, value in (("median_ppm", 1199999), ("gate_type", "post_hoc")):
            mutated = copy.deepcopy(self.projection)
            mutated["contract"]["registered_gates"]["a_over_d_prepared_steady"][field] = value
            _reseal_projection(mutated)
            with self.subTest(field=field), self.assertRaisesRegex(
                VERIFY.VerificationError, "contract or gate type"
            ):
                self.validate(mutated)

    def test_malformed_projection_hash_is_rejected(self) -> None:
        self.projection["projection_sha256"] = "not-a-sha256"
        with self.assertRaisesRegex(VERIFY.VerificationError, "invalid SHA-256"):
            self.validate(self.projection)

    def test_unexpected_public_member_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in VERIFY.REQUIRED_PUBLIC_FILES:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"placeholder\n")
            rows = []
            for name in sorted(VERIFY.REQUIRED_PUBLIC_FILES):
                payload = (root / name).read_bytes()
                rows.append({"path": name, "bytes": len(payload), "sha256": VERIFY.digest_bytes(payload)})
            body = {
                "schema": VERIFY.MANIFEST_SCHEMA,
                "file_count": len(rows),
                "payload_bytes": sum(row["bytes"] for row in rows),
                "files": rows,
            }
            (root / "manifest.json").write_text(
                json.dumps({**body, "manifest_sha256": VERIFY.digest(body)}, sort_keys=True),
                encoding="utf-8",
            )
            (root / "UNEXPECTED.txt").write_text("unexpected\n", encoding="utf-8")
            with self.assertRaisesRegex(VERIFY.VerificationError, "unexpected"):
                VERIFY.verify_artifact(root, expected_projection_sha256=self.projection["projection_sha256"])

    def test_existing_output_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(
            EXPORTER.ExportError, "overwrite refused"
        ):
            EXPORTER.require_new_external_output_root(Path(temporary))

    def test_rejections_survive_python_optimized_mode(self) -> None:
        if os.environ.get("RTDL_GOAL5852_OPTIMIZED_CHILD") == "1":
            row = self.projection["formal_workers"][0]
            row["steady_samples_ns"][0] += 1
            _reseal_row(row)
            _reseal_projection(self.projection)
            with self.assertRaisesRegex(VERIFY.VerificationError, "sample digest"):
                self.validate(self.projection)
            return
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(ROOT)
        environment["RTDL_GOAL5852_OPTIMIZED_CHILD"] = "1"
        result = subprocess.run(
            [
                sys.executable,
                "-O",
                "-m",
                "unittest",
                "tests.goal5852_submission_evidence_test.Goal5852SubmissionEvidenceTest.test_mutated_nanosecond_is_rejected_without_assert",
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

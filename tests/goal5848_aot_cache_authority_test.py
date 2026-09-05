from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from experiments.goal5848_strong_baseline import aot_cache_authority, contracts


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


class Goal5848AOTCacheAuthorityTest(unittest.TestCase):
    def _fixture(self, root: Path, *, hit_ns: int = 50) -> tuple[Path, Path]:
        source = "a" * 40
        candidate_root = root / "candidate"
        evidence_root = root / "evidence"
        candidate_root.mkdir()
        evidence_root.mkdir()
        manifest = {
            "schema": "rtdl.goal5848.aot_candidates.v1",
            "status": "PASS__EXACT_AOT_CACHE_AND_CANDIDATES_VERIFIED",
            "source_commit": source,
            "rows": {
                label: {
                    "first_resolution_cache_hit": False,
                    "producer_invocation_count": 1,
                    "first_resolution_ns": 1_000,
                    "aot_request_identity_sha256": character * 64,
                }
                for label, character in (("relation", "b"), ("triangle", "c"))
            },
        }
        manifest["manifest_sha256"] = contracts.digest(manifest)
        manifest_path = candidate_root / "manifest.json"
        _write(manifest_path, manifest)
        processes = []
        worker_seals = []
        tasks = {}
        pids = []
        for task_index, task in enumerate(contracts.TASKS):
            label = "relation" if task_index == 0 else "triangle"
            request = manifest["rows"][label]["aot_request_identity_sha256"]
            durations = []
            for repetition in range(contracts.AOT_HIT_REPETITIONS):
                worker_id = f"G5848_AOT_{label}_{repetition:02d}"
                worker = {
                    "schema": "rtdl.goal5848.aot_fresh_process_hit.v1",
                    "status": (
                        "PASS__EXACT_VERIFIED_HIT__NO_PRODUCER_NO_COMPILER"
                    ),
                    "worker_id": worker_id,
                    "task": task,
                    "pid": 100 + task_index * 10 + repetition,
                    "python": "3.12.0",
                    "source_commit": source,
                    "request_identity_sha256": request,
                    "entry_path": f"/tmp/{label}",
                    "duration_ns": hit_ns,
                    "cache_hit": True,
                    "producer_invoked": False,
                    "producer_call_count": 0,
                    "compiler_modules_before": [],
                    "compiler_modules_after": [],
                    "nvrtc_mappings_before": [],
                    "nvrtc_mappings_after": [],
                    "verification": {
                        "artifact_sha256": "d" * 64,
                        "authority_sha256": "e" * 64,
                        "family": label,
                        "deployment_id": f"goal5848-{label}",
                        "executable_identity_sha256": "f" * 64,
                        "family_executable_identity_sha256": "1" * 64,
                        "target_sha256": "2" * 64,
                        "native_library_sha256": "3" * 64,
                    },
                    "public_or_manuscript_claim_authorized": False,
                }
                worker["receipt_sha256"] = contracts.digest(worker)
                worker_path = evidence_root / f"{worker_id}.json"
                _write(worker_path, worker)
                stdout = json.dumps(worker, sort_keys=True) + "\n"
                processes.append(
                    {
                        "worker_id": worker_id,
                        "command": ["python", "worker", worker_id],
                        "exit_code": 0,
                        "stdout_sha256": hashlib.sha256(
                            stdout.encode("utf-8")
                        ).hexdigest(),
                        "stderr_sha256": hashlib.sha256(b"").hexdigest(),
                    }
                )
                worker_seals.append(worker["receipt_sha256"])
                pids.append(worker["pid"])
                durations.append(hit_ns)
            median = contracts.integer_median(durations)
            relative = contracts.ratio_ppm(median, 1_000)
            tasks[task] = {
                "cold_first_resolution_ns": 1_000,
                "fresh_process_hit_durations_ns": durations,
                "fresh_process_hit_median_ns": median,
                "fresh_process_hit_over_cold_ppm": relative,
                "absolute_limit_ns": contracts.AOT_HIT_ABSOLUTE_LIMIT_NS,
                "relative_limit_ppm": contracts.AOT_HIT_COLD_RATIO_LIMIT_PPM,
                "pass": relative <= contracts.AOT_HIT_COLD_RATIO_LIMIT_PPM,
            }
        value = {
            "schema": "rtdl.goal5848.aot_cache_authority.v1",
            "status": "PASS__AC8_EXACT_FRESH_PROCESS_AOT_REUSE",
            "source_commit": source,
            "candidate_manifest_path": str(manifest_path.resolve()),
            "candidate_manifest_sha256": hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest(),
            "worker_count": len(worker_seals),
            "process_count": len(processes),
            "distinct_pid_count": len(set(pids)),
            "producer_invocation_count_across_hits": 0,
            "compiler_module_count_across_hits": 0,
            "nvrtc_mapping_count_across_hits": 0,
            "qualification_timing_count": len(worker_seals),
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "included_in_formal_estimators": False,
            "prior_in_process_hit_timings_included": False,
            "tasks": tasks,
            "processes": processes,
            "worker_receipt_sha256": worker_seals,
            "retry_count": 0,
            "discard_count": 0,
            "external_review_complete": False,
            "public_or_manuscript_claim_authorized": False,
        }
        value["authority_sha256"] = contracts.digest(value)
        authority_path = evidence_root / "authority.json"
        _write(authority_path, value)
        return authority_path, manifest_path

    def test_exact_authority_passes_and_worker_mutation_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            authority_path, manifest_path = self._fixture(root)
            value = aot_cache_authority.load_aot_cache_authority(
                authority_path,
                candidate_manifest=manifest_path,
                expected_source_commit="a" * 40,
            )
            self.assertEqual(value["worker_count"], 10)
            worker_path = authority_path.parent / "G5848_AOT_relation_00.json"
            worker = json.loads(worker_path.read_text())
            worker["compiler_modules_after"] = ["numba"]
            worker["receipt_sha256"] = contracts.digest(
                {
                    key: item
                    for key, item in worker.items()
                    if key != "receipt_sha256"
                }
            )
            _write(worker_path, worker)
            with self.assertRaisesRegex(RuntimeError, "worker differs"):
                aot_cache_authority.load_aot_cache_authority(
                    authority_path,
                    candidate_manifest=manifest_path,
                    expected_source_commit="a" * 40,
                )

    def test_coherent_slow_hits_still_fail_hard_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            authority_path, manifest_path = self._fixture(root, hit_ns=200)
            with self.assertRaisesRegex(RuntimeError, "task gate differs"):
                aot_cache_authority.load_aot_cache_authority(
                    authority_path,
                    candidate_manifest=manifest_path,
                    expected_source_commit="a" * 40,
                )


if __name__ == "__main__":
    unittest.main()

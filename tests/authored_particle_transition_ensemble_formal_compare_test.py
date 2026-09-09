from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from scripts import authored_particle_transition_ensemble_formal_compare as formal
from scripts import authored_particle_transition_ensemble_independent_recount as recount


class AuthoredParticleTransitionEnsembleFormalCompareTest(unittest.TestCase):
    @staticmethod
    def _prereg() -> dict[str, object]:
        return {
            "source_root": "/source",
            "source_commit": "a" * 40,
            "source_tree": "b" * 40,
            "base_particle_dir": "/data/particle",
            "ensemble_dir": "/data/ensemble",
            "native_library": {"path": "/native.so", "sha256": "c" * 64},
            "pyoptix_ptx": {"path": "/baseline.ptx", "sha256": "d" * 64},
            "python": "/python",
            "optix_include": "/optix/include",
            "cuda_include": "/cuda/include",
            "cuda_home": "/cuda",
            "ld_library_path": "/cuda/lib",
            "optix_sdk": "8.0.0",
            "gpu": {
                "uuid": "GPU-test",
                "name": "Test GPU",
                "driver": "1.0",
                "compute_capability": "8.9",
            },
            "hostname": "host",
            "python_version": "3.12.3",
            "numba_cuda_use_nvidia_binding": "1",
            "ensemble_manifest": {"sha256": "e" * 64},
            "base_manifest": {"sha256": "3" * 64},
            "input_sha256": "f" * 64,
            "independent_oracle_sha256": "1" * 64,
            "output_sha256": "2" * 64,
        }

    @classmethod
    def _worker(cls, arm: str, *, formal_worker: bool) -> dict[str, object]:
        prereg = cls._prereg()
        count = formal.QUERY_COUNT
        value = {
            "schema": "rtdl.v4.authored_particle.transition_ensemble_worker.v2",
            "status": "PASS",
            "arm": arm,
            "source": {
                "commit": prereg["source_commit"],
                "tree": prereg["source_tree"],
            },
            "machine": {
                "hostname": prereg["hostname"],
                "python": prereg["python_version"],
                "gpu_name": prereg["gpu"]["name"],
                "gpu_uuid": prereg["gpu"]["uuid"],
                "driver": prereg["gpu"]["driver"],
                "compute_capability": prereg["gpu"]["compute_capability"],
                "cuda_visible_devices": prereg["gpu"]["uuid"],
                "numba_cuda_use_nvidia_binding": "1",
            },
            "query_count": count,
            "output_shape": [count, 3],
            "ensemble_manifest_sha256": prereg["ensemble_manifest"]["sha256"],
            "base_manifest_sha256": prereg["base_manifest"]["sha256"],
            "input_sha256": prereg["input_sha256"],
            "independent_oracle_sha256": prereg["independent_oracle_sha256"],
            "output_sha256": prereg["output_sha256"],
            "warmup_count": formal.WARMUPS,
            "sample_count": formal.SAMPLES,
            "samples_ns": [1, 2, 3],
            "median_ns": 2,
            "prepare_ns": 4,
            "close_ns": 5,
            "claim_boundary": {
                "diagnostic_only": True,
                "formal_worker_zero_reached": formal_worker,
                "natural_single_transition_ensemble": True,
                "temporal_particle_simulation": False,
            },
        }
        if arm == "rtdl":
            value.update({
                "metadata": {
                    "path_class": "public_rtdl_provider_native_closest_prepared",
                    "native_library_sha256": prereg["native_library"]["sha256"],
                    "prepared_query_batch_device_resident": True,
                    "oracle_validation": "canonical_u32x3_sha256",
                },
                "last_execution_evidence": {
                    "output_sha256": prereg["output_sha256"],
                    "physical_executor_classification": "optix_traversal_observed",
                    "role_counters": [0, count, 0, 0, count, 0, count],
                },
            })
        else:
            value.update({
                "metadata": {
                    "path_class": "public_pyoptix_native_closest_prepared",
                    "pyoptix_ptx_sha256": prereg["pyoptix_ptx"]["sha256"],
                    "prepared_query_batch_device_resident": True,
                    "output_layout": "aos_u32x3_c_contiguous",
                    "output_strides": [12, 4],
                    "prepared_query_batch_operation_counts": {
                        "query_h2d_copy_call_count": 7,
                        "query_h2d_bytes": count * 7 * 4,
                        "pinned_host_allocation_call_count": 0,
                    },
                },
                "last_execution_evidence": {
                    "control": [count, 0xFFFFFFFF, 0, 0],
                    "operation_counts": {
                        "query_h2d_copy_call_count": 0,
                        "query_h2d_bytes": 0,
                        "optix_launch_call_count": 1,
                        "output_d2h_bytes": count * 3 * 4,
                    },
                },
            })
        return value

    def test_schedule_is_balanced_and_natural_scale_is_fixed(self):
        self.assertEqual(
            formal.SCHEMA,
            "rtdl.v4.authored_particle.transition_ensemble_formal.v3")
        self.assertEqual(recount.TRANSACTION_SCHEMA, formal.SCHEMA)
        self.assertIn(
            "src/rtdsl/v4_callback_cuda_inline_codegen.py",
            formal.SOURCE_PATHS,
        )
        self.assertEqual(recount.SOURCE_PATHS, formal.SOURCE_PATHS)
        self.assertEqual(formal.QUERY_COUNT, 160_000_000)
        self.assertEqual(len(formal.ORDERS), 8)
        self.assertEqual(sum(row[0] == "rtdl" for row in formal.ORDERS), 4)
        self.assertEqual(sum(row[0] == "pyoptix" for row in formal.ORDERS), 4)
        self.assertEqual((formal.WARMUPS, formal.SAMPLES), (1, 3))

    def test_formal_worker_flag_is_explicit(self):
        prereg = self._prereg()
        command = formal.worker_command(
            prereg, "rtdl", samples=3, formal_worker=True)
        self.assertIn("--formal-worker", command)
        calibration = formal.worker_command(
            prereg, "pyoptix", samples=1, formal_worker=False)
        self.assertNotIn("--formal-worker", calibration)

    def test_worker_environment_pins_numba_cuda_binding(self):
        environment = formal.worker_environment(self._prereg())
        self.assertEqual(environment["NUMBA_CUDA_USE_NVIDIA_BINDING"], "1")

    def test_public_pyoptix_output_is_direct_contiguous_aos(self):
        authored = (formal.ROOT / "experiments/v4_authored_particle" /
                    "pyoptix_device.cu").read_text(encoding="utf-8")
        paper = (formal.ROOT / "experiments/v4_paper_apps_pyoptix" /
                 "particle_device.cu").read_text(encoding="utf-8")
        owner = (formal.ROOT / "experiments/goal5814_particle" /
                 "public_pyoptix_owner.py").read_text(encoding="utf-8")
        for source in (authored, paper):
            self.assertIn("const unsigned int row = 3u * query;", source)
            self.assertGreaterEqual(source.count("[row] ="), 3)
        self.assertIn("(shape.query_count, 3), np.uint32", owner)
        self.assertIn("output_base + np.dtype(np.uint32).itemsize", owner)
        self.assertNotIn(
            "output_base + output_stride", owner)

    def test_both_worker_contracts_and_identity_drift(self):
        prereg = self._prereg()
        for arm in ("rtdl", "pyoptix"):
            with self.subTest(arm=arm):
                value = self._worker(arm, formal_worker=True)
                formal.validate_worker(
                    prereg, value, arm, samples=formal.SAMPLES,
                    formal_worker=True)
                changed = deepcopy(value)
                changed["output_sha256"] = "0" * 64
                with self.assertRaisesRegex(ValueError, "worker contract"):
                    formal.validate_worker(
                        prereg, changed, arm, samples=formal.SAMPLES,
                        formal_worker=True)

    def test_controller_retains_failures_and_process_groups(self):
        source = Path(formal.__file__).read_text(encoding="utf-8")
        for token in (
            "start_new_session=True", "os.killpg(",
            "APPEND_ONLY_LEDGER.jsonl", "TERMINAL_FAILURE_RETAINED_NO_RETRY",
            '"worker_directory": str(directory.resolve())',
            '"retained_artifacts": retained_artifacts',
            '"retry_count": 0', '"discard_count": 0',
        ):
            self.assertIn(token, source)

    def test_freeze_runs_rtdl_target_probe_before_formal_worker_zero(self):
        source = Path(formal.__file__).read_text(encoding="utf-8")
        self.assertIn('"rtdl_target_compatibility_probe"', source)
        self.assertLess(
            source.index('directory=calibration_root / "rtdl_target_compatibility_probe"'),
            source.index('"status": "FROZEN_BEFORE_FORMAL_WORKER_ZERO"'),
        )

    def test_source_identity_rejects_untracked_files(self):
        formal_source = Path(formal.__file__).read_text(encoding="utf-8")
        worker_source = (formal.ROOT / "scripts" /
                         "authored_particle_transition_ensemble_worker.py").read_text(
                             encoding="utf-8")
        ptx_builder_source = (formal.ROOT / "scripts" /
                              "build_authored_particle_pyoptix_ptx.py").read_text(
                                  encoding="utf-8")
        for source in (formal_source, worker_source, ptx_builder_source):
            self.assertNotIn('"--untracked-files=no"', source)

    def test_bootstrap_is_deterministic(self):
        values = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
        self.assertEqual(
            formal.bootstrap_interval(values),
            formal.bootstrap_interval(values))


if __name__ == "__main__":
    unittest.main()

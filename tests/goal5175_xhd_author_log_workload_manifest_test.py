import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "extract_xhd_author_log_manifest.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("extract_xhd_author_log_manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5175AuthorLogWorkloadManifestTest(unittest.TestCase):
    def _write_fixture_repo(self, root: Path) -> None:
        (root / "expr" / "logs" / "end2end" / "rt_gpu" / "graphics").mkdir(
            parents=True
        )
        (root / "expr" / "common.sh").write_text(
            'export DATASET_ROOT="/local/storage/shared/HDDatasets"\n'
        )
        (root / "expr" / "run_fig5.sh").write_text("echo run_fig5\n")
        payload = {
            "DateTime": "2026-01-01T00:00:00",
            "GPU": "fixture gpu",
            "HDResult": 0.125,
            "Input": {
                "NumDims": 3,
                "Type": "ply",
                "Normalize": True,
                "Translate": False,
                "Limit": None,
                "SerializationPrefix": "/local/storage/shared/HDDatasets/ser",
                "Files": [
                    {
                        "Path": "/local/storage/shared/HDDatasets/graphics/a.ply",
                        "NumPoints": 10,
                        "GiniIndex": 0.25,
                        "Density": 1.5,
                        "StatsGridNumPointsPerCell": 15,
                        "MBR": [[0, 0, 0], [1, 1, 1]],
                    },
                    {
                        "Path": "/local/storage/shared/HDDatasets/graphics/b.ply",
                        "NumPoints": 12,
                        "GiniIndex": 0.5,
                    },
                ],
            },
            "Running": {
                "AvgTime": 3.2,
                "Seed": 123,
                "NumPointsPerCell": 15,
                "LB": 256,
                "EB": True,
                "Prune": True,
                "Repeats": [
                    {
                        "ReportedTime": 3.0,
                        "BVHBuildTime": 0.5,
                        "Iterations": [
                            {
                                "RTTime": 0.1,
                                "CUDATime": 0.2,
                                "OffloadingSize": 7,
                            }
                        ],
                    },
                    {
                        "ReportedTime": 5.0,
                        "BVHBuildTime": 0.7,
                        "Iterations": [
                            {
                                "RTTime": 0.3,
                                "CUDATime": 0.4,
                                "OffloadingSize": 11,
                            }
                        ],
                    },
                ],
            },
        }
        log = (
            root
            / "expr"
            / "logs"
            / "end2end"
            / "rt_gpu"
            / "graphics"
            / "a.ply_b.ply.json"
        )
        log.write_text(json.dumps(payload))

    def test_author_log_manifest_extracts_workload_and_keeps_claims_bounded(self):
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._write_fixture_repo(repo)

            manifest = module.build_manifest(repo)

        self.assertEqual(
            manifest["schema"],
            "rtdl.paper_reproduction.xhd.author_log_workload_manifest.v1",
        )
        self.assertEqual(
            manifest["status"],
            "author_log_workload_manifest_extracted__input_files_not_present",
        )
        self.assertEqual(manifest["summary"]["total_json_logs"], 1)
        self.assertEqual(manifest["summary"]["unique_input_path_count"], 2)
        self.assertEqual(
            manifest["summary"]["input_files_available_on_current_machine"], 0
        )
        self.assertEqual(
            manifest["log_roots_scanned"],
            [{"path": "expr/logs", "json_count": 1}],
        )

        workload = manifest["workloads"][0]
        self.assertEqual(workload["log_root"], "expr/logs")
        self.assertEqual(workload["log_family"], "end2end")
        self.assertEqual(workload["variant_execution"], "rt_gpu")
        self.assertEqual(workload["category"], "graphics")
        self.assertEqual(workload["hd_result"], 0.125)
        self.assertEqual(workload["input"]["num_dims"], 3)
        self.assertEqual(workload["input"]["files"][0]["basename"], "a.ply")
        self.assertEqual(
            workload["input"]["files"][0]["exact_status"],
            "author_log_path_known__input_file_not_available",
        )
        self.assertEqual(workload["running"]["reported_time_median"], 4.0)
        self.assertEqual(workload["running"]["bvh_build_time_median"], 0.6)
        self.assertEqual(workload["running"]["iteration_count"], 2)
        self.assertAlmostEqual(workload["running"]["iteration_rt_time_sum"], 0.4)
        self.assertAlmostEqual(workload["running"]["iteration_cuda_time_sum"], 0.6)
        self.assertEqual(workload["running"]["iteration_offloading_size_sum"], 18)

        self.assertIn("expr/common.sh", manifest["author_repo"]["source_hashes"])
        self.assertIn("expr/run_fig5.sh", manifest["author_repo"]["source_hashes"])
        self.assertEqual(
            manifest["additional_branch_log_inventories"][0]["status"],
            "inventory_only__json_blobs_not_parsed_into_workloads",
        )
        self.assertFalse(manifest["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(
            manifest["claim_boundary"]["exact_paper_dataset_reproduction_claimed"]
        )
        self.assertFalse(manifest["claim_boundary"]["figure_reproduction_claimed"])
        self.assertFalse(manifest["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()

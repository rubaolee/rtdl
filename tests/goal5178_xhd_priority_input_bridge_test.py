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
    / "build_xhd_priority_input_bridge.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("build_xhd_priority_input_bridge", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_ply(path: Path, vertex_count: int, face_count: int = 0):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        "ply",
        "format ascii 1.0",
        f"element vertex {vertex_count}",
        "property float x",
        "property float y",
        "property float z",
        f"element face {face_count}",
        "property list uchar int vertex_indices",
        "end_header",
    ]
    rows.extend("0 0 0" for _ in range(vertex_count))
    path.write_text("\n".join(rows) + "\n")


def _write_binary_header_ply(path: Path, vertex_count: int, face_count: int = 0):
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "\n".join(
        [
            "ply",
            "format binary_big_endian 1.0",
            f"element vertex {vertex_count}",
            "property float x",
            "property float y",
            "property float z",
            f"element face {face_count}",
            "property list uchar int vertex_indices",
            "end_header",
        ]
    ).encode("ascii") + b"\n"
    path.write_bytes(header + b"\xff\x00\x01\x02")


class Goal5178PriorityInputBridgeTest(unittest.TestCase):
    def test_bridge_matches_public_candidate_counts_but_refuses_exact_identity(self):
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            app_root = Path(tmp)
            _write_ply(app_root / "data/external/stanford/dragon_recon/dragon_vrip.ply", 3)
            _write_ply(app_root / "data/external/stanford/happy_recon/happy_vrip.ply", 4)
            _write_ply(app_root / "data/fixtures/stanford_dragon_res4_full.ply", 2)
            _write_ply(app_root / "data/fixtures/stanford_happy_res4_full.ply", 2)
            (app_root / "data/external/stanford/dragon_recon.tar.gz").parent.mkdir(
                parents=True, exist_ok=True
            )
            (app_root / "data/external/stanford/dragon_recon.tar.gz").write_bytes(b"dragon")
            (app_root / "data/external/stanford/happy_recon.tar.gz").write_bytes(b"happy")
            (app_root / "results").mkdir(parents=True)
            (app_root / "results/stanford_dragon_res4_full_summary.json").write_text(
                json.dumps({"sample_point_count": 2})
            )
            (app_root / "results/stanford_happy_res4_full_summary.json").write_text(
                json.dumps({"sample_point_count": 2})
            )

            mapping = {
                "priority_subsets": [
                    {
                        "name": "graphics_dragon_happy_buddha",
                        "status": "paper_log_workload_identified__input_files_missing",
                        "record_summary": {"record_count": 1},
                        "blocker": "need exact bytes",
                    }
                ]
            }
            log_index = {
                "run_all_records": [
                    {
                        "section": "rt_gpu",
                        "config": "dragon.ply_happy_buddha.ply.json",
                        "hd_result": 0.125,
                        "input": {
                            "files": [
                                {
                                    "basename": "dragon.ply",
                                    "path": "/author/dragon.ply",
                                    "num_points": 3,
                                    "exact_status": "author_log_path_known__input_file_not_available",
                                },
                                {
                                    "basename": "happy_buddha.ply",
                                    "path": "/author/happy_buddha.ply",
                                    "num_points": 4,
                                    "exact_status": "author_log_path_known__input_file_not_available",
                                },
                            ]
                        },
                        "running": {"avg_time": 5.0, "reported_time_median": 4.0},
                    }
                ]
            }

            bridge = module.build_bridge(
                app_root=app_root,
                mapping=mapping,
                log_index=log_index,
                target="graphics_dragon_happy_buddha",
            )

        self.assertEqual(
            bridge["schema"],
            "rtdl.paper_reproduction.xhd.priority_input_bridge.v1",
        )
        self.assertEqual(bridge["author_basename_order"], ["dragon.ply", "happy_buddha.ply"])
        self.assertEqual(bridge["source_basename"], "dragon.ply")
        self.assertEqual(bridge["target_basename"], "happy_buddha.ply")
        self.assertEqual(bridge["author_log_records"]["record_count"], 1)
        self.assertTrue(
            bridge["bridge_assessment"]["full_public_candidate_point_counts_match_author_logs"]
        )
        self.assertTrue(bridge["bridge_assessment"]["strong_same_source_candidate"])
        self.assertFalse(bridge["bridge_assessment"]["exact_paper_dataset_identity_proved"])
        self.assertFalse(bridge["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(bridge["claim_boundary"]["figure_reproduction_claimed"])
        self.assertTrue(bridge["claim_boundary"]["level_b_same_source_candidate_claimed"])
        self.assertEqual(
            bridge["public_same_source_candidates"]["dragon.ply"]["ply_header"]["vertex_count"],
            3,
        )
        self.assertIn("author logs provide paths", bridge["bridge_assessment"]["reason_exact_not_proved"][0])

    def test_bridge_supports_dragon_asian_dragon_binary_ply_candidate(self):
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            app_root = Path(tmp)
            _write_ply(app_root / "data/external/stanford/dragon_recon/dragon_vrip.ply", 3)
            _write_binary_header_ply(app_root / "data/external/stanford/asian_dragon.ply", 5)
            (app_root / "data/external/stanford/dragon_recon.tar.gz").parent.mkdir(
                parents=True, exist_ok=True
            )
            (app_root / "data/external/stanford/dragon_recon.tar.gz").write_bytes(b"dragon")
            (app_root / "data/external/stanford/xyzrgb_dragon.ply.gz").write_bytes(b"asian")

            mapping = {
                "priority_subsets": [
                    {
                        "name": "graphics_dragon_asian_dragon",
                        "status": "paper_log_workload_identified__input_files_missing",
                        "record_summary": {"record_count": 1},
                        "blocker": "need exact bytes",
                    }
                ]
            }
            log_index = {
                "run_all_records": [
                    {
                        "section": "rt_gpu",
                        "config": "dragon.ply_asian_dragon.ply.json",
                        "hd_result": 0.065,
                        "input": {
                            "files": [
                                {
                                    "basename": "dragon.ply",
                                    "path": "/author/dragon.ply",
                                    "num_points": 3,
                                    "exact_status": "author_log_path_known__input_file_not_available",
                                },
                                {
                                    "basename": "asian_dragon.ply",
                                    "path": "/author/asian_dragon.ply",
                                    "num_points": 5,
                                    "exact_status": "author_log_path_known__input_file_not_available",
                                },
                            ]
                        },
                        "running": {"avg_time": 50.0, "reported_time_median": 49.0},
                    }
                ]
            }

            bridge = module.build_bridge(
                app_root=app_root,
                mapping=mapping,
                log_index=log_index,
                target="graphics_dragon_asian_dragon",
            )

        self.assertEqual(bridge["target"], "graphics_dragon_asian_dragon")
        self.assertEqual(bridge["author_basename_order"], ["dragon.ply", "asian_dragon.ply"])
        self.assertEqual(bridge["source_basename"], "dragon.ply")
        self.assertEqual(bridge["target_basename"], "asian_dragon.ply")
        self.assertTrue(bridge["bridge_assessment"]["strong_same_source_candidate"])
        self.assertFalse(bridge["bridge_assessment"]["exact_paper_dataset_identity_proved"])
        self.assertEqual(
            bridge["public_same_source_candidates"]["asian_dragon.ply"]["ply_header"]["format"],
            "binary_big_endian 1.0",
        )
        self.assertEqual(
            bridge["public_same_source_candidates"]["asian_dragon.ply"]["ply_header"]["vertex_count"],
            5,
        )
        self.assertFalse(bridge["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])


if __name__ == "__main__":
    unittest.main()

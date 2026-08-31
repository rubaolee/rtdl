import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "extract_xhd_paper_branch_log_index.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("extract_xhd_paper_branch_log_index", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> None:
    subprocess.check_call(["git", "-C", str(repo), *args])


class Goal5176PaperBranchLogIndexTest(unittest.TestCase):
    def _init_repo(self, root: Path) -> None:
        subprocess.check_call(["git", "init", str(root)])
        _git(root, "config", "user.email", "test@example.com")
        _git(root, "config", "user.name", "test")
        run_all = (
            root
            / "expr"
            / "for_the_paper"
            / "logs"
            / "run_all"
            / "rt_gpu"
            / "graphics"
        )
        train = (
            root
            / "expr"
            / "for_the_paper"
            / "logs"
            / "train"
            / "geo"
            / "n_points_cell"
        )
        run_all.mkdir(parents=True)
        train.mkdir(parents=True)
        self._write_log(run_all / "a.ply_b.ply.json", 0.5, "ply", 3, 3.0)
        self._write_log(train / "roads.wkt_parks.wkt_translate_0.1.json", 2.5, "wkt", 2, 7.0)
        _git(root, "add", "expr/for_the_paper/logs")
        _git(root, "commit", "-m", "fixture logs")

    def _write_log(self, path: Path, hd_result: float, input_type: str, dims: int, avg: float) -> None:
        payload = {
            "DateTime": "2026-01-01",
            "GPU": {"name": "fixture"},
            "HDResult": hd_result,
            "Input": {
                "NumDims": dims,
                "Type": input_type,
                "Normalize": True,
                "Translate": False,
                "Files": [
                    {
                        "Path": f"/local/storage/shared/HDDatasets/{path.stem}_a.dat",
                        "NumPoints": 10,
                        "GiniIndex": 0.1,
                    },
                    {
                        "Path": f"/local/storage/shared/HDDatasets/{path.stem}_b.dat",
                        "NumPoints": 12,
                        "GiniIndex": 0.2,
                    },
                ],
            },
            "Running": {
                "AvgTime": avg,
                "Repeats": [{"ReportedTime": avg - 1}, {"ReportedTime": avg + 1}],
            },
        }
        path.write_text(json.dumps(payload))

    def test_build_index_uses_git_tree_and_keeps_claims_bounded(self):
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._init_repo(repo)

            index = module.build_index(
                repo,
                "HEAD",
                "expr/for_the_paper/logs",
                max_sample_records=10,
            )

        self.assertEqual(
            index["schema"],
            "rtdl.paper_reproduction.xhd.paper_branch_log_index.v1",
        )
        self.assertEqual(index["summary"]["json_blob_count"], 2)
        self.assertEqual(index["summary"]["parsed_json_count"], 2)
        self.assertEqual(index["summary"]["parse_error_count"], 0)
        self.assertEqual(index["summary"]["run_all_record_count"], 1)
        self.assertEqual(index["summary"]["sample_record_count"], 1)
        self.assertEqual(index["summary"]["unique_input_path_count"], 4)
        self.assertEqual(index["summary"]["by_log_group"], {"run_all": 1, "train": 1})
        self.assertEqual(index["summary"]["by_input_type"], {"ply": 1, "wkt": 1})
        self.assertEqual(index["summary"]["by_num_dims"], {"2": 1, "3": 1})
        self.assertEqual(index["summary"]["hd_result_stats"]["count"], 2)
        self.assertEqual(index["summary"]["running_avg_time_stats"]["median"], 5.0)

        run_record = index["run_all_records"][0]
        self.assertEqual(run_record["log_group"], "run_all")
        self.assertEqual(run_record["section"], "rt_gpu")
        self.assertEqual(run_record["category"], "graphics")
        self.assertEqual(run_record["running"]["reported_time_median"], 3.0)
        self.assertEqual(
            run_record["input"]["files"][0]["exact_status"],
            "author_log_path_known__input_file_not_available",
        )
        self.assertTrue(index["output_bounding"]["all_run_all_records_included"])
        self.assertTrue(index["output_bounding"]["non_run_all_records_are_sampled"])
        self.assertFalse(index["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(index["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(index["claim_boundary"]["figure_reproduction_claimed"])
        self.assertFalse(index["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2204_rayjoin_same_query_artifact_import.py"
REPORT = ROOT / "docs" / "reports" / "goal2204_rayjoin_same_query_artifact_importer_2026-05-17.md"


def _rayjoin_log(*, query_ms: float, optix_launches: int = 0) -> str:
    launches = "\n".join("I20260517 rt_engine.cu:554] optixLaunch, [w,h,d] = 10,1,1" for _ in range(optix_launches))
    return f"""{launches}
I20260517 run_query.cu:306] Intersections: 3 Queue Load Factor: 0.1
Timing results:
 - Build Index: 0.5 ms

 - Query: {query_ms} ms
"""


def _rtdl_artifact(workload: str) -> dict[str, object]:
    return {
        "schema": "rtdl.rayjoin.same_query_result.v1",
        "query_stream": f"/tmp/rayjoin_{workload}_gen10_stream.json",
        "query_stream_schema": "rtdl.rayjoin.same_query_stream.v1",
        "query_stream_producer": "rayjoin_query_exec_export_patch",
        "workload": workload,
        "query_count": 10,
        "base_cdb": "/tmp/base.cdb",
        "warmups": 1,
        "repeats": 3,
        "reference_row_count": 5,
        "backends": {
            "cpu": {
                "elapsed_sec_values": [0.3, 0.31, 0.32],
                "elapsed_sec_median": 0.31,
                "row_counts": [5, 5, 5],
                "all_parity_vs_cpu_python_reference": True,
                "rt_core_accelerated": False,
            },
            "embree": {
                "elapsed_sec_values": [0.2, 0.21, 0.22],
                "elapsed_sec_median": 0.21,
                "row_counts": [5, 5, 5],
                "all_parity_vs_cpu_python_reference": True,
                "rt_core_accelerated": False,
            },
            "optix": {
                "elapsed_sec_values": [0.1, 0.11, 0.12],
                "elapsed_sec_median": 0.11,
                "row_counts": [5, 5, 5],
                "all_parity_vs_cpu_python_reference": True,
                "rt_core_accelerated": True,
            },
        },
        "claim_boundary": {
            "same_contract_with_rayjoin_query_exec": True,
            "paper_scale_perf_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "v2_0_release_authorized": False,
        },
    }


def _write_fake_goal2198_artifacts(path: pathlib.Path) -> None:
    (path / "environment.txt").write_text("gpu=NVIDIA RTX test\n", encoding="utf-8")
    (path / "progress.log").write_text("[goal2198] complete\n", encoding="utf-8")
    (path / "summary.json").write_text(json.dumps({"goal": "2198", "status": "pass"}), encoding="utf-8")
    for workload in ("lsi", "pip"):
        for mode in ("grid", "lbvh", "rt"):
            (path / f"rayjoin_{workload}_{mode}.log").write_text(
                _rayjoin_log(query_ms=1.0 if mode == "rt" else 4.0, optix_launches=4 if mode == "rt" else 0),
                encoding="utf-8",
            )
        (path / f"rtdl_{workload}_same_rayjoin_stream.json").write_text(
            json.dumps(_rtdl_artifact(workload), indent=2),
            encoding="utf-8",
        )
        (path / f"rayjoin_{workload}_gen10_stream.json").write_text(
            json.dumps({"schema": "rtdl.rayjoin.same_query_stream.v1", "workload": workload, "queries": []}),
            encoding="utf-8",
        )


class Goal2204RayJoinSameQueryArtifactImporterTest(unittest.TestCase):
    def test_importer_copies_compact_artifacts_and_hashes_streams(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            artifact_dir = root / "pod_artifacts"
            output_dir = root / "repo_artifacts"
            artifact_dir.mkdir()
            _write_fake_goal2198_artifacts(artifact_dir)

            output_json = root / "goal2204.json"
            output_md = root / "goal2204.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--artifact-dir",
                    str(artifact_dir),
                    "--output-dir",
                    str(output_dir),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
            )

            data = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "imported")
            self.assertFalse(data["include_streams"])
            self.assertTrue((output_dir / "rayjoin_lsi_rt.log").exists())
            self.assertTrue((output_dir / "rtdl_pip_same_rayjoin_stream.json").exists())
            self.assertTrue((output_dir / "evidence_summary.regenerated.json").exists())
            self.assertFalse((output_dir / "rayjoin_lsi_gen10_stream.json").exists())
            self.assertEqual({item["workload"] for item in data["stream_provenance"]}, {"lsi", "pip"})
            self.assertTrue(all(item["sha256"] for item in data["stream_provenance"]))
            self.assertFalse(data["claim_boundary"]["v2_0_release_authorized"])
            self.assertIn("Stream Provenance", output_md.read_text(encoding="utf-8"))

    def test_importer_can_copy_streams_when_explicitly_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            artifact_dir = root / "pod_artifacts"
            output_dir = root / "repo_artifacts"
            artifact_dir.mkdir()
            _write_fake_goal2198_artifacts(artifact_dir)

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--artifact-dir",
                    str(artifact_dir),
                    "--output-dir",
                    str(output_dir),
                    "--output-json",
                    str(root / "goal2204.json"),
                    "--output-md",
                    str(root / "goal2204.md"),
                    "--include-streams",
                ],
                cwd=ROOT,
                check=True,
            )

            self.assertTrue((output_dir / "rayjoin_lsi_gen10_stream.json").exists())
            self.assertTrue((output_dir / "rayjoin_pip_gen10_stream.json").exists())

    def test_report_documents_boundary_and_default_stream_policy(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("does not copy the full query streams", text)
        self.assertIn("--include-streams", text)
        self.assertIn("RTDL beating RayJoin", text)
        self.assertIn("v2.0 release readiness", text)


if __name__ == "__main__":
    unittest.main()

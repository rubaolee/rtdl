from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1193_public_wording_evidence_batch_intake as goal1193


ROOT = Path(__file__).resolve().parents[1]


def _write(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def _write_fixture(directory: Path, *, optix_phase: float = 0.25) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    _write(
        directory / "database_compact_summary_embree.json",
        {
            "results": [
                {
                    "status": "ok",
                    "prepared_session_warm_query_sec": {"median_sec": 0.42},
                    "reported_run_phase_totals_sec": {"compact_summary_operation_count": 3},
                }
            ]
        },
    )
    _write(
        directory / "database_compact_summary_optix.json",
        {
            "results": [
                {
                    "status": "ok",
                    "prepared_session_warm_query_sec": {"median_sec": optix_phase},
                    "reported_native_db_phase_totals_sec": {"counter_status": "exported"},
                }
            ]
        },
    )
    _write(
        directory / "graph_visibility_edges_embree.json",
        {
            "graph_phase_totals_sec": {"query_visibility_pair_rows_sec": 0.5},
            "sections": {"visibility_edges": {"summary": {"blocked_edge_count": 3}}},
        },
    )
    _write(
        directory / "graph_visibility_edges_optix.json",
        {
            "status": "pass",
            "strict_pass": True,
            "records": [
                {
                    "label": "optix_visibility_anyhit",
                    "status": "ok",
                    "sec": optix_phase,
                    "digest": {"summary": {"blocked_edge_count": 3}},
                }
            ],
        },
    )
    _write(
        directory / "road_hazard_native_summary_embree.json",
        {"run_phases": {"query_and_materialize_sec": 0.55}, "priority_segment_count": 2},
    )
    _write(
        directory / "road_hazard_native_summary_optix.json",
        {
            "status": "pass",
            "strict_pass": True,
            "timings_sec": {"optix_query_sec": {"median_sec": optix_phase}},
            "result": {"matches_oracle": True},
        },
    )
    _write(
        directory / "polygon_pair_candidate_discovery_embree.json",
        {
            "run_phases": {"rt_candidate_discovery_sec": 0.6, "native_exact_continuation_sec": 0.1},
            "candidate_row_count": 6,
        },
    )
    _write(
        directory / "polygon_pair_candidate_discovery_optix.json",
        {
            "status": "pass",
            "parity_vs_cpu": True,
            "phases": {"optix_candidate_discovery_sec": optix_phase},
            "optix_metadata": {"rt_core_candidate_discovery_active": True},
        },
    )
    _write(
        directory / "polygon_jaccard_safe_chunk_embree.json",
        {
            "run_phases": {"rt_candidate_discovery_sec": 0.61, "native_exact_continuation_sec": 0.1},
            "candidate_row_count": 6,
        },
    )
    _write(
        directory / "polygon_jaccard_safe_chunk_optix.json",
        {
            "status": "pass",
            "parity_vs_cpu": True,
            "phases": {"optix_candidate_discovery_sec": optix_phase},
            "optix_metadata": {"rt_core_candidate_discovery_active": True},
        },
    )
    _write(
        directory / "hausdorff_threshold_prepared_embree.json",
        {"run_phases": {"native_directed_summary_sec": 0.7}, "matches_oracle": True},
    )
    _write(
        directory / "hausdorff_threshold_prepared_optix.json",
        {
            "scenario": {
                "mode": "optix",
                "timings_sec": {"optix_query_sec": {"median_sec": optix_phase}},
                "result": {"matches_oracle": True},
            }
        },
    )


class Goal1193PublicWordingEvidenceBatchIntakeTest(unittest.TestCase):
    def test_artifact_contract_covers_goal1192_outputs(self) -> None:
        self.assertEqual(set(goal1193.ARTIFACTS), set(goal1193.PAIRS["database_analytics"] + goal1193.PAIRS["graph_analytics"] + goal1193.PAIRS["road_hazard_screening"] + goal1193.PAIRS["polygon_pair_overlap_area_rows"] + goal1193.PAIRS["polygon_set_jaccard"] + goal1193.PAIRS["hausdorff_distance"]))
        self.assertEqual(len(goal1193.ARTIFACTS), 12)
        self.assertEqual(len(goal1193.PAIRS), 6)

    def test_build_intake_accepts_complete_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "batch"
            _write_fixture(input_dir)
            payload = goal1193.build_intake(input_dir)
            self.assertTrue(payload["valid"], payload)
            self.assertEqual(payload["valid_schema_artifact_count"], 12)
            self.assertEqual(payload["public_wording_review_ready_pair_count"], 6)
            self.assertEqual(payload["not_ready_apps"], [])

    def test_timing_floor_can_block_public_wording_without_schema_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "batch"
            _write_fixture(input_dir, optix_phase=0.01)
            payload = goal1193.build_intake(input_dir)
            self.assertTrue(payload["valid"], payload)
            self.assertEqual(payload["public_wording_review_ready_pair_count"], 0)
            self.assertEqual(set(payload["not_ready_apps"]), set(goal1193.PAIRS))

    def test_cli_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_dir = tmp_path / "batch"
            output_json = tmp_path / "intake.json"
            output_md = tmp_path / "intake.md"
            _write_fixture(input_dir)
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1193_public_wording_evidence_batch_intake.py",
                    "--input-dir",
                    str(input_dir),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("does not authorize public RTX speedup wording", markdown)


if __name__ == "__main__":
    unittest.main()

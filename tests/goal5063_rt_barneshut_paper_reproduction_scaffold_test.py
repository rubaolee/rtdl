from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "rt-barneshut-paper"


class Goal5063RtBarnesHutPaperReproductionScaffoldTest(unittest.TestCase):
    def test_project_files_exist_and_boundary_is_explicit(self) -> None:
        required = [
            APP_DIR / "README.md",
            APP_DIR / ".gitignore",
            APP_DIR / "data" / "manifest.json",
            APP_DIR / "author_patches" / "README.md",
            APP_DIR / "scripts" / "setup_author_official.sh",
            APP_DIR / "scripts" / "check_pod_environment.sh",
            APP_DIR / "scripts" / "apply_author_official_patch.py",
            APP_DIR / "scripts" / "run_author_smoke.sh",
            APP_DIR / "scripts" / "run_author_same_input.sh",
            APP_DIR / "scripts" / "compare_force_outputs.py",
            APP_DIR / "scripts" / "run_author_source_contract_gate.py",
            APP_DIR / "scripts" / "run_author_source_contract_gate.sh",
            APP_DIR / "scripts" / "compare_author_contract_to_rtdl_reference.py",
            APP_DIR / "scripts" / "run_author_comparator_gate.sh",
            APP_DIR / "scripts" / "run_rtdl_diagnostic.sh",
            APP_DIR / "scripts" / "run_author_contract_rtdl_cuda_gate.sh",
            APP_DIR / "scripts" / "run_generic_aggregate_force_same_input_gate.sh",
            APP_DIR / "scripts" / "run_generic_aggregate_force_same_input_gate.py",
            APP_DIR / "scripts" / "run_same_input_rtdl_comparison_gate.sh",
            APP_DIR / "scripts" / "run_same_input_performance_gate.py",
            APP_DIR / "scripts" / "run_same_input_performance_gate.sh",
            APP_DIR / "scripts" / "run_phase_boundary_review_gate.py",
            APP_DIR / "scripts" / "run_phase_boundary_review_gate.sh",
            APP_DIR / "scripts" / "run_full_pod_reproduction_gate.py",
            APP_DIR / "scripts" / "run_full_pod_reproduction_gate.sh",
            APP_DIR / "scripts" / "run_remote_full_pod_gate.py",
            APP_DIR / "scripts" / "run_completion_audit.py",
            APP_DIR / "scripts" / "run_completion_audit.sh",
            APP_DIR / "scripts" / "run_local_contract_gate.py",
            APP_DIR / "scripts" / "run_local_contract_gate.sh",
            APP_DIR / "rt_barneshut_reproduction.py",
            APP_DIR / "author_contract_reference.py",
        ]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), path)

        readme = (APP_DIR / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "completed the bounded same-input RT-BarnesHut prepared-state",
            readme,
        )
        self.assertIn("force-output reproduction", readme)
        self.assertIn("not completed independent tree construction", readme)
        self.assertIn("same-input", readme)
        self.assertIn("AuthorOfficial", readme)
        self.assertNotIn("RTDL is faster than", readme)
        gitignore = (APP_DIR / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("_work/", gitignore)
        self.assertIn("_data/", gitignore)
        self.assertIn("_runs/", gitignore)

    def test_manifest_pins_author_artifact_and_marks_gap(self) -> None:
        payload = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))
        author = payload["author_artifact"]
        self.assertEqual(author["repository"], "https://github.com/vani-nag/OWLRayTracing")
        self.assertEqual(author["branch"], "BarnesHutRT")
        self.assertEqual(author["commit"], "2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7")
        self.assertFalse(payload["current_rtdl_status"]["paper_reproduction_complete"])
        self.assertTrue(payload["current_rtdl_status"]["bounded_same_input_reproduction_complete"])
        self.assertIn("none", payload["current_rtdl_status"]["known_gap"])
        self.assertEqual(payload["current_rtdl_status"]["same_input_author_rtdl_match"]["mismatch_count"], 0)
        self.assertIn("RTBH_FORCE_OUT", payload["known_compatibility_requirements"]["force_output"])

    def test_status_entrypoint_runs_without_cuda_or_author_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "status.json"
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "rt_barneshut_reproduction.py"),
                    "--mode",
                    "status",
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(payload["project"], "rt-barneshut-paper")
        self.assertFalse(payload["paper_reproduction_complete"])
        self.assertTrue(payload["bounded_same_input_reproduction_complete"])
        self.assertTrue(payload["same_input_comparator_closed"])
        self.assertIn("bounded same-input", payload["claim_boundary"])

    @unittest.skipUnless(
        importlib.util.find_spec("numba") is not None,
        "Numba is required for aggregate-numba-parity CLI smoke",
    )
    def test_aggregate_numba_parity_mode_runs_on_synthetic_prepared_arrays(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "rtbh_author_contract_reference_for_cli_parity",
            APP_DIR / "author_contract_reference.py",
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as tmp:
            prepared = Path(tmp) / "prepared.json"
            out = Path(tmp) / "aggregate_numba_parity.json"
            module.write_prepared_arrays(prepared, module.make_synthetic_bodies(32))
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "rt_barneshut_reproduction.py"),
                    "--mode",
                    "aggregate-numba-parity",
                    "--prepared-arrays-json",
                    str(prepared),
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual("aggregate_numba_parity", payload["mode"])
        self.assertTrue(payload["generic_public_rtdl_api_used"])
        self.assertFalse(payload["paper_reproduction_complete"])
        self.assertFalse(payload["same_input_author_comparator"])
        self.assertEqual("numba", payload["parity"]["candidate_backend"])
        self.assertTrue(payload["parity"]["comparison"]["match"])
        self.assertEqual(0, payload["parity"]["comparison"]["mismatch_count"])

    @unittest.skipUnless(
        importlib.util.find_spec("numba") is not None,
        "Numba is required for aggregate-numba-force-output CLI smoke",
    )
    def test_aggregate_numba_force_output_mode_writes_scalar_force_file(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "rtbh_author_contract_reference_for_cli_force_bridge",
            APP_DIR / "author_contract_reference.py",
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as tmp:
            prepared = Path(tmp) / "prepared.json"
            out = Path(tmp) / "aggregate_numba_force_bridge.json"
            force_out = Path(tmp) / "aggregate_numba_forces.txt"
            module.write_prepared_arrays(prepared, module.make_synthetic_bodies(32))
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "rt_barneshut_reproduction.py"),
                    "--mode",
                    "aggregate-numba-force-output",
                    "--prepared-arrays-json",
                    str(prepared),
                    "--force-output",
                    str(force_out),
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
            force_lines = force_out.read_text(encoding="utf-8").splitlines()

        self.assertEqual("aggregate_numba_force_output", payload["mode"])
        self.assertTrue(payload["generic_public_rtdl_api_used"])
        self.assertFalse(payload["paper_reproduction_complete"])
        self.assertFalse(payload["same_input_author_comparator"])
        self.assertTrue(payload["force_output_exists"])
        self.assertEqual(32, len(force_lines))
        self.assertEqual("numba", payload["bridge"]["candidate_backend"])
        self.assertTrue(payload["bridge"]["comparison_to_reference_executor_force_rows"]["match"])
        self.assertEqual(0, payload["bridge"]["comparison_to_reference_executor_force_rows"]["mismatch_count"])

    @unittest.skipUnless(
        importlib.util.find_spec("numba") is not None,
        "Numba is required for aggregate-numba-force-compare CLI smoke",
    )
    def test_aggregate_numba_force_compare_mode_matches_author_contract_force_file(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "rtbh_author_contract_reference_for_cli_force_compare",
            APP_DIR / "author_contract_reference.py",
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as tmp:
            bodies = module.make_synthetic_bodies(32)
            prepared = Path(tmp) / "prepared.json"
            expected_force = Path(tmp) / "expected_forces.txt"
            candidate_force = Path(tmp) / "candidate_forces.txt"
            out = Path(tmp) / "aggregate_numba_force_compare.json"
            module.write_prepared_arrays(prepared, bodies)
            module.write_force_rows(expected_force, module.compute_author_contract_forces(bodies)["force_rows"])
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "rt_barneshut_reproduction.py"),
                    "--mode",
                    "aggregate-numba-force-compare",
                    "--prepared-arrays-json",
                    str(prepared),
                    "--expected-force-output",
                    str(expected_force),
                    "--force-output",
                    str(candidate_force),
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual("aggregate_numba_force_compare", payload["mode"])
        self.assertTrue(payload["generic_public_rtdl_api_used"])
        self.assertFalse(payload["paper_reproduction_complete"])
        self.assertTrue(payload["same_input_author_comparator"])
        self.assertTrue(payload["force_comparison"]["matched"])
        self.assertEqual(0, payload["force_comparison"]["mismatch_count"])
        self.assertIn("app_owned_same_input_scalar_force_comparator_gate", payload["claim_boundary"])

    @unittest.skipUnless(
        importlib.util.find_spec("numba") is not None,
        "Numba is required for generic aggregate force same-input gate smoke",
    )
    def test_generic_aggregate_force_same_input_gate_python_runner(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "rtbh_author_contract_reference_for_python_gate",
            APP_DIR / "author_contract_reference.py",
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as tmp:
            bodies = module.make_synthetic_bodies(32)
            prepared = Path(tmp) / "prepared.json"
            expected_force = Path(tmp) / "expected_forces.txt"
            run_dir = Path(tmp) / "gate"
            module.write_prepared_arrays(prepared, bodies)
            module.write_force_rows(expected_force, module.compute_author_contract_forces(bodies)["force_rows"])
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "run_generic_aggregate_force_same_input_gate.py"),
                    "--prepared-arrays",
                    str(prepared),
                    "--expected-force",
                    str(expected_force),
                    "--run-dir",
                    str(run_dir),
                    "--python",
                    sys.executable,
                ],
                cwd=ROOT,
                check=True,
            )
            payload = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))

        self.assertEqual("aggregate_numba_force_compare", payload["mode"])
        self.assertTrue(payload["same_input_author_comparator"])
        self.assertTrue(payload["force_comparison"]["matched"])
        self.assertEqual(0, payload["force_comparison"]["mismatch_count"])
        self.assertEqual("generic_aggregate_force_same_input_gate", payload["gate_runner"]["mode"])

    def test_generic_aggregate_force_same_input_gate_fails_closed_without_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "gate"
            result = subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "run_generic_aggregate_force_same_input_gate.py"),
                    "--prepared-arrays",
                    str(Path(tmp) / "missing_prepared.json"),
                    "--expected-force",
                    str(Path(tmp) / "missing_forces.txt"),
                    "--run-dir",
                    str(run_dir),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertEqual(2, result.returncode)
        self.assertIn("prepared arrays not found", result.stderr)

    def test_rtdl_diagnostic_force_output_is_wired_for_same_input_comparison(self) -> None:
        entry = (APP_DIR / "rt_barneshut_reproduction.py").read_text(encoding="utf-8")
        diagnostic = (ROOT / "scripts" / "goal2547_barnes_hut_3d_scalar_subtree_kernel.py").read_text(
            encoding="utf-8"
        )
        gate = (APP_DIR / "scripts" / "run_same_input_rtdl_comparison_gate.sh").read_text(encoding="utf-8")
        contract_gate = (APP_DIR / "scripts" / "run_author_contract_rtdl_cuda_gate.sh").read_text(
            encoding="utf-8"
        )
        source_contract_gate = (APP_DIR / "scripts" / "run_author_source_contract_gate.py").read_text(
            encoding="utf-8"
        )
        preflight = (APP_DIR / "scripts" / "check_pod_environment.sh").read_text(encoding="utf-8")
        full_gate = (APP_DIR / "scripts" / "run_full_pod_reproduction_gate.py").read_text(
            encoding="utf-8"
        )
        performance_gate = (APP_DIR / "scripts" / "run_same_input_performance_gate.py").read_text(
            encoding="utf-8"
        )
        phase_review_gate = (APP_DIR / "scripts" / "run_phase_boundary_review_gate.py").read_text(
            encoding="utf-8"
        )
        completion_audit = (APP_DIR / "scripts" / "run_completion_audit.py").read_text(
            encoding="utf-8"
        )
        setup_author = (APP_DIR / "scripts" / "setup_author_official.sh").read_text(encoding="utf-8")
        run_author_same_input = (APP_DIR / "scripts" / "run_author_same_input.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("--force-output", entry)
        self.assertIn("--force-out", entry)
        self.assertIn("--expected-force-output", entry)
        self.assertIn("aggregate-numba-force-compare", entry)
        self.assertIn("--prepared-arrays-json", entry)
        self.assertIn("--traversal-policy", entry)
        self.assertIn("parser.add_argument(\"--force-out\"", diagnostic)
        self.assertIn("parser.add_argument(\"--prepared-arrays-json\"", diagnostic)
        self.assertIn("TRAVERSAL_AUTHOR_OPENING", diagnostic)
        self.assertIn("TRAVERSAL_AUTHOR_OPTIX_PAYLOAD", diagnostic)
        self.assertIn("author_vs_rtdl_force_compare.json", gate)
        self.assertIn("run_author_comparator_gate.sh first", gate)
        self.assertIn("AUTHOR_BINARY_PREPARED_ARRAYS", gate)
        self.assertIn("author_treelogy_prepared_arrays.json", gate)
        self.assertIn("author_binary_prepared_arrays_selected", gate)
        self.assertIn("no Python tree reconstruction", gate)
        self.assertIn("author-optix-payload", gate)
        self.assertIn("selected_traversal_policy", gate)
        self.assertIn("author_sorted_input_for_rtdl.txt", gate)
        self.assertIn("author_prepared_arrays_for_rtdl.json", gate)
        self.assertIn("COMPARE_STATUS=$?", gate)
        self.assertIn("TRAVERSAL_POLICY=\"${SELECTED_TRAVERSAL_POLICY}\"", gate)
        self.assertIn("--prepared-arrays-json", contract_gate)
        self.assertIn("--traversal-policy author-opening", contract_gate)
        self.assertIn("author_contract_vs_rtdl_cuda_compare.json", contract_gate)
        self.assertIn("patched author binary remains the paper comparator", contract_gate)
        self.assertIn("git_head_matches_manifest", source_contract_gate)
        self.assertIn("new_mode_writes_five_headers", source_contract_gate)
        self.assertIn("post_sort_ids_are_reassigned", source_contract_gate)
        self.assertIn("cpu_opening_rule_matches_reference", source_contract_gate)
        self.assertIn("raw_source_has_no_force_dump_patch", source_contract_gate)
        self.assertIn("ready_for_author_build", preflight)
        self.assertIn("ready_for_rtdl_cuda_gate", preflight)
        self.assertIn("optix_header_exists", preflight)
        self.assertIn("torch.cuda.is_available", preflight)
        self.assertIn("local_contract_gate", full_gate)
        self.assertIn("author_source_contract_gate", full_gate)
        self.assertIn("pod_environment_preflight", full_gate)
        self.assertIn("author_contract_rtdl_cuda_gate", full_gate)
        self.assertIn("author_comparator_gate", full_gate)
        self.assertIn("same_input_author_vs_rtdl_gate", full_gate)
        self.assertIn("same_input_performance_gate", full_gate)
        self.assertIn("performance_timing_gate_ready", full_gate)
        self.assertIn("performance_review_complete", full_gate)
        self.assertIn("paper_reproduction_complete", full_gate)
        self.assertIn("rt_core_force_ms", performance_gate)
        self.assertIn("resident_kernel_min", performance_gate)
        self.assertIn("narrow_force_kernel_ratio_rtdl_over_author", performance_gate)
        self.assertIn("human review of matched phase boundaries", performance_gate)
        self.assertIn("accepted_author_phase", phase_review_gate)
        self.assertIn("reviewed_ratio_matches_summary", phase_review_gate)
        self.assertIn("blocked_review_incomplete_or_mismatched", phase_review_gate)
        self.assertIn("performance_phase_boundary_reviewed", completion_audit)
        self.assertIn("local_contract_gate_closed", completion_audit)
        self.assertIn("author_source_contract_gate_closed", completion_audit)
        self.assertIn("phase_boundary_review_gate", completion_audit)
        self.assertIn("paper_reproduction_complete", completion_audit)
        self.assertIn("Completion audit only", completion_audit)
        self.assertIn("checkout --force", setup_author)
        self.assertIn("git reset --hard", setup_author)
        self.assertIn("RTBH_PREPARED_ARRAYS_OUT", run_author_same_input)
        self.assertIn("prepared_arrays_output", run_author_same_input)

    def test_remote_full_pod_gate_runner_is_minimal_and_evidence_pulling(self) -> None:
        runner = (APP_DIR / "scripts" / "run_remote_full_pod_gate.py").read_text(encoding="utf-8")
        readme = (APP_DIR / "README.md").read_text(encoding="utf-8")
        self.assertIn("run_full_pod_reproduction_gate.sh", runner)
        self.assertIn("goal2547_barnes_hut_3d_scalar_subtree_kernel.py", runner)
        self.assertIn("Paper-reproduction-apps/rt-barneshut-paper", runner)
        self.assertIn("EXCLUDED_PARTS", runner)
        self.assertIn("CRITICAL_ARCHIVE_ENTRIES", runner)
        self.assertIn("--package-only", runner)
        self.assertIn("safe_to_upload", runner)
        self.assertIn("package_ready", runner)
        self.assertIn("critical_entries_present", runner)
        self.assertIn("run_author_contract_rtdl_cuda_gate.sh", runner)
        self.assertIn("run_generic_aggregate_force_same_input_gate.py", runner)
        self.assertIn("run_generic_aggregate_force_same_input_gate.sh", runner)
        self.assertIn("run_same_input_performance_gate.py", runner)
        for excluded in ("_work", "_runs", "_data", "__pycache__"):
            self.assertIn(excluded, runner)
        self.assertIn("pull_remote_runs", runner)
        self.assertIn("remote_full_gate_summary", runner)
        self.assertIn("run_remote_full_pod_gate.py", readme)
        self.assertIn("excludes", readme)
        self.assertIn("--package-only", readme)

    def test_author_contract_reference_matches_pairwise_for_single_bucket(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "rtbh_author_contract_reference",
            APP_DIR / "author_contract_reference.py",
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        bodies = [
            module.Body(id=0, mass=10.0, x=-1.0, y=0.0, z=0.0),
            module.Body(id=1, mass=20.0, x=1.0, y=0.0, z=0.0),
            module.Body(id=2, mass=30.0, x=0.0, y=2.0, z=0.0),
            module.Body(id=3, mass=40.0, x=0.0, y=0.0, z=-3.0),
        ]
        payload = module.compute_author_contract_forces(bodies)
        rows = payload["force_rows"]
        self.assertEqual(len(rows), 4)
        sorted_bodies, _, summary = module.build_author_bucket_tree(bodies)
        self.assertEqual(summary["bucket_leaf_count"], 1)

        expected = {}
        for source in sorted_bodies:
            total = 0.0
            for target in sorted_bodies:
                if target.id == source.id:
                    continue
                dx = source.x - target.x
                dy = source.y - target.y
                dz = source.z - target.z
                total += 0.1 * source.mass * target.mass / (dx * dx + dy * dy + dz * dz)
            expected[source.id] = total
        observed = {int(row["source_id"]): float(row["scalar_force"]) for row in rows}
        for body_id, value in expected.items():
            self.assertTrue(math.isclose(observed[body_id], value, rel_tol=1e-12, abs_tol=1e-12))

    def test_author_contract_reference_cli_writes_force_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_force = Path(tmp) / "forces.txt"
            out_summary = Path(tmp) / "summary.json"
            out_input = Path(tmp) / "input.txt"
            prepared_arrays = Path(tmp) / "prepared_arrays.json"
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "author_contract_reference.py"),
                    "--synthetic-count",
                    "8",
                    "--write-synthetic-input",
                    str(out_input),
                    "--write-rtdl-prepared-arrays",
                    str(prepared_arrays),
                    "--force-output",
                    str(out_force),
                    "--summary",
                    str(out_summary),
                ],
                cwd=ROOT,
                check=True,
            )
            payload = json.loads(out_summary.read_text(encoding="utf-8"))
            prepared = json.loads(prepared_arrays.read_text(encoding="utf-8"))
            force_lines = out_force.read_text(encoding="utf-8").splitlines()
            input_exists = out_input.exists()
        self.assertEqual(payload["summary"]["input_body_count"], 8)
        self.assertEqual(len(force_lines), 8)
        self.assertTrue(input_exists)
        self.assertEqual(
            prepared["schema"],
            "generic_aggregate_frontier_inverse_square_scalar_sum_3d_prepared_arrays_v1",
        )
        self.assertEqual(prepared["contract_source"], "rt_barneshut_author_bucket_tree_v1")
        self.assertEqual(len(prepared["points"]), 8)
        self.assertGreaterEqual(len(prepared["nodes"]), 1)

    def test_author_contract_vs_rtdl_reference_matches_single_bucket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gap.json"
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "compare_author_contract_to_rtdl_reference.py"),
                    "--synthetic-count",
                    "8",
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["body_count"], 8)
        self.assertIn("author-sorted", payload["alignment"])

    def test_author_contract_vs_rtdl_reference_reports_multibucket_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gap.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "compare_author_contract_to_rtdl_reference.py"),
                    "--synthetic-count",
                    "64",
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=False,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertIn(result.returncode, (0, 1))
        self.assertEqual(payload["body_count"], 64)
        self.assertIn("rtdl_summary", payload)
        self.assertIn("author_summary", payload)
        self.assertIn("Local contract diagnostic", payload["claim_boundary"])
        self.assertFalse(payload["matched"])
        self.assertEqual(payload["rtdl_contract_mode"], "current-rtdl-diagnostic-tree")

    def test_author_prepared_arrays_close_multibucket_local_contract_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gap.json"
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "compare_author_contract_to_rtdl_reference.py"),
                    "--synthetic-count",
                    "64",
                    "--rtdl-contract",
                    "author-prepared-arrays",
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["mismatch_count"], 0)
        self.assertEqual(payload["rtdl_contract_mode"], "author-prepared-arrays")
        self.assertEqual(payload["rtdl_contract"], "author_bucket_tree_over_generic_flat_aggregate_arrays")

    def test_local_contract_gate_runs_all_expected_probes(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "rtbh_local_contract_gate_for_test",
            APP_DIR / "scripts" / "run_local_contract_gate.py",
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as tmp:
            module.RUN_DIR = Path(tmp) / "local_contract_gate"
            payload, exit_code = module.build_gate()

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "passed")
        self.assertFalse(payload["paper_reproduction_complete"])
        probes = {probe["name"]: probe for probe in payload["probes"]}
        self.assertEqual(
            set(probes),
            {
                "single_bucket_current_tree_matches",
                "multi_bucket_current_tree_exposes_gap",
                "multi_bucket_author_prepared_arrays_matches",
            },
        )
        self.assertTrue(probes["single_bucket_current_tree_matches"]["observed_matched"])
        self.assertFalse(probes["multi_bucket_current_tree_exposes_gap"]["observed_matched"])
        self.assertTrue(probes["multi_bucket_author_prepared_arrays_matches"]["observed_matched"])
        self.assertIn("patched author binary POD comparator remains required", payload["claim_boundary"])

    def test_goal2547_reader_consumes_author_prepared_arrays_contract(self) -> None:
        author_spec = importlib.util.spec_from_file_location(
            "rtbh_author_contract_reference_for_prepared_reader",
            APP_DIR / "author_contract_reference.py",
        )
        self.assertIsNotNone(author_spec)
        self.assertIsNotNone(author_spec.loader)
        author_module = importlib.util.module_from_spec(author_spec)
        sys.modules[author_spec.name] = author_module
        author_spec.loader.exec_module(author_module)

        diag_path = ROOT / "scripts" / "goal2547_barnes_hut_3d_scalar_subtree_kernel.py"
        diag_spec = importlib.util.spec_from_file_location("goal2547_bh_diag_for_prepared_reader", diag_path)
        self.assertIsNotNone(diag_spec)
        self.assertIsNotNone(diag_spec.loader)
        diag_module = importlib.util.module_from_spec(diag_spec)
        sys.modules[diag_spec.name] = diag_module
        diag_spec.loader.exec_module(diag_module)

        bodies = author_module.make_synthetic_bodies(64)
        author_payload = author_module.compute_author_contract_forces(bodies)
        with tempfile.TemporaryDirectory() as tmp:
            prepared_path = Path(tmp) / "prepared.json"
            author_module.write_prepared_arrays(prepared_path, bodies)
            prepared = diag_module.read_prepared_arrays_3d(prepared_path)
        reference = diag_module.reference_scalar_sum_3d(
            prepared["points"],
            tuple(prepared["nodes"]),
            theta=0.5,
            softening=0.0,
            traversal_policy=diag_module.TRAVERSAL_AUTHOR_OPENING,
        )
        author_forces = [float(row["scalar_force"]) for row in author_payload["force_rows"]]
        rtdl_forces = [float(row["scalar_force"]) * 0.1 for row in reference["scalar_sum_rows"]]
        max_abs_error = max(abs(left - right) for left, right in zip(author_forces, rtdl_forces))
        self.assertEqual(prepared["contract_source"], "rt_barneshut_author_bucket_tree_v1")
        self.assertLess(max_abs_error, 1e-9)

    def test_goal2547_reader_fills_author_binary_prepared_resume_indices(self) -> None:
        diag_path = ROOT / "scripts" / "goal2547_barnes_hut_3d_scalar_subtree_kernel.py"
        diag_spec = importlib.util.spec_from_file_location(
            "goal2547_bh_diag_for_author_binary_dump_reader",
            diag_path,
        )
        self.assertIsNotNone(diag_spec)
        self.assertIsNotNone(diag_spec.loader)
        diag_module = importlib.util.module_from_spec(diag_spec)
        sys.modules[diag_spec.name] = diag_module
        diag_spec.loader.exec_module(diag_module)

        payload = {
            "schema": "generic_aggregate_frontier_inverse_square_scalar_sum_3d_prepared_arrays_v1",
            "contract_source": "rt_barneshut_author_binary_prepared_state_v1",
            "points": [
                {"id": 0, "mass": 10.0, "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": 1, "mass": 20.0, "x": 1.0, "y": 0.0, "z": 0.0},
            ],
            "nodes": [
                {
                    "id": 1,
                    "cx": 0.5,
                    "cy": 0.0,
                    "cz": 0.0,
                    "half_size": 4.0,
                    "mass": 30.0,
                    "member_ids": [],
                    "child_ids": [2],
                    "dfs_index": 0,
                    "resume_index": None,
                    "is_leaf": False,
                },
                {
                    "id": 2,
                    "cx": 0.5,
                    "cy": 0.0,
                    "cz": 0.0,
                    "half_size": 2.0,
                    "mass": 30.0,
                    "member_ids": [0, 1],
                    "child_ids": [],
                    "dfs_index": 1,
                    "resume_index": None,
                    "is_leaf": True,
                },
            ],
            "ordered_primary_launch_rays": [
                {"launch_index": 0, "point_id": 0, "prim_id": 0},
                {"launch_index": 1, "point_id": 1, "prim_id": 0},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            prepared_path = Path(tmp) / "author_binary_prepared.json"
            prepared_path.write_text(json.dumps(payload), encoding="utf-8")
            prepared = diag_module.read_prepared_arrays_3d(prepared_path)
        self.assertEqual(prepared["contract_source"], "rt_barneshut_author_binary_prepared_state_v1")
        self.assertEqual(prepared["node_resume_index"], [-1, -1])
        self.assertEqual(prepared["node_subtree_end_index"], [2, 2])
        self.assertEqual(prepared["node_next_prim_index"], [-1, -1])
        self.assertEqual(prepared["node_auto_rope_index"], [-1, -1])
        self.assertEqual(prepared["member_indices"], [0, 1])

    def test_top_level_paper_reproduction_index_lists_bounded_app(self) -> None:
        text = (ROOT / "Paper-reproduction-apps" / "README.md").read_text(encoding="utf-8")
        self.assertIn("RT-BarnesHut paper", text)
        self.assertIn("Bounded same-input prepared-state", text)
        self.assertIn("Not full paper reproduction", text)

    def test_author_official_patch_script_updates_minimal_source_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "OWLRayTracing"
            sample = source / "samples" / "cmdline" / "s01-rtbarneshut"
            sample.mkdir(parents=True)
            (sample / "GeomTypes.h").write_text(
                "//constexpr int NUM_POINTS = 51794907;\n"
                "constexpr int NUM_POINTS = 100000000;\n",
                encoding="utf-8",
            )
            (sample / "hostCode.cu").write_text(
                textwrap.dedent(
                    """
                    #include <limits>

                    int gpuDeviceID = 1;
                    OWLContext context = owlContextCreate(&gpuDeviceID, 1);

                    int main(int ac, char **av) {
                      installAutoRopes(root);
                      auto auto_ropes_end = chrono::steady_clock::now();
                      profileStats->installAutoRopesTime += chrono::duration_cast<chrono::microseconds>(auto_ropes_end - auto_ropes_start);
                      const float *rtComputedForces = (const float *)owlBufferGetPointer(ComputedForcesBuffer,0);
                      auto end1 = std::chrono::steady_clock::now();
                      profileStats->forceCalculationTime = std::chrono::duration_cast<std::chrono::microseconds>(end1 - start1);
                    }
                    """
                ).lstrip(),
                encoding="utf-8",
            )
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "apply_author_official_patch.py"),
                    "--source-root",
                    str(source),
                    "--body-count",
                    "32768",
                ],
                cwd=ROOT,
                check=True,
            )
            host_code = (sample / "hostCode.cu").read_text(encoding="utf-8")
            geom_types = (sample / "GeomTypes.h").read_text(encoding="utf-8")

        self.assertIn("RTBH_CUDA_DEVICE", host_code)
        self.assertIn("RTBH_PREPARED_ARRAYS_OUT", host_code)
        self.assertIn("dumpPreparedArraysForRtdl", host_code)
        self.assertIn("rt_barneshut_author_binary_prepared_state_v1", host_code)
        self.assertIn("author_device", host_code)
        self.assertIn("RTBH_FORCE_OUT", host_code)
        self.assertIn("std::setprecision(9)", host_code)
        self.assertIn("//constexpr int NUM_POINTS = 51794907;", geom_types)
        self.assertIn("constexpr int NUM_POINTS = 32768;", geom_types)
        self.assertNotIn("constexpr int NUM_POINTS = 100000000;", geom_types)

    def test_author_source_contract_gate_checks_source_anchors_on_fixture(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "rtbh_author_source_contract_gate_for_test",
            APP_DIR / "scripts" / "run_author_source_contract_gate.py",
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "OWLRayTracing"
            sample = source / "samples" / "cmdline" / "s01-rtbarneshut"
            sample.mkdir(parents=True)
            (sample / "GeomTypes.h").write_text(
                "constexpr int NUM_POINTS = 100000000;\nconstexpr int NUM_STEPS = 1;\n",
                encoding="utf-8",
            )
            (sample / "barnesHutTree.h").write_text(
                "#define GRID_SIZE 10.0f\n#define THRESHOLD 0.5f\n"
                "#define GRAVITATIONAL_CONSTANT .1f\n#define BUCKET_SIZE 32\n",
                encoding="utf-8",
            )
            (sample / "barnesHutTree.cpp").write_text(
                "if(bhNode->particles[i] != point.idX) {}\n"
                "result += (((mass_one * mass_two) / r_2) * GRAVITATIONAL_CONSTANT);\n"
                "result = (((mass_one * mass_two) / r_2) * GRAVITATIONAL_CONSTANT);\n"
                "if(node->s < distanceBetweenObjects(point, node) * THRESHOLD) {}\n",
                encoding="utf-8",
            )
            (sample / "deviceCode.cu").write_text(
                "float force = ((point.mass * optixLaunchParams.devicePoints[pointID].mass) / r_2) * GRAVITATIONAL_CONSTANT;\n"
                "float rayLength = sqrtf(r_2) * THRESHOLD;\n",
                encoding="utf-8",
            )
            (sample / "less.hpp").write_text("auto FloatXorMsb() {}\nstruct Less {};\n", encoding="utf-8")
            (sample / "hostCode.cu").write_text(
                textwrap.dedent(
                    r'''
                    #include "less.hpp"
                    void f() {
                      if(std::string(av[1]) == "new") {}
                      else if(std::string(av[1]) == "treelogy") {}
                      fprintf(outFile, "%d\n", NUM_POINTS);
                      fprintf(outFile, "%d\n", NUM_STEPS);
                      fprintf(outFile, "%f\n", (0.025));
                      fprintf(outFile, "%f\n", (0.05));
                      fprintf(outFile, "%f\n", THRESHOLD);
                      fprintf(outFile, "%f %f %f %f %f %f %f\n", p.mass, p.pos.x, p.pos.y, p.pos.z, nullptr, nullptr, nullptr);
                      for(int i = 0; i < 5; i++) { fscanf(inFile, "%f\n", &randomStuff); }
                      while (fscanf(inFile, "%f %f %f %f %f %f %f", &mass, &x, &y, &z, &(velRead.x), &(velRead.y), &(velRead.z)) == 7) {}
                      std::sort(pts.begin(), pts.end(), zorder_knn::Less<sortPoint, 3>());
                      p.idX = i;
                      numLeaves = std::ceil(leaves.size() / double(BUCKET_SIZE));
                      for(int j = 0; j < BUCKET_SIZE; j++) { new_node->particles.push_back(leaves[(i * BUCKET_SIZE) + j]->pointID); }
                      tree->insertNode(root, new_node, gridSize * 0.5);
                      tree->computeCOM(root);
                      owlLaunch2D(rayGen, points.size(), 1, lp);
                      profileStats->forceCalculationTime = std::chrono::duration_cast<std::chrono::microseconds>(end1 - start1);
                    }
                    '''
                ).lstrip(),
                encoding="utf-8",
            )
            manifest = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))
            payload = module.audit_author_source(source, manifest, require_git=False)

        self.assertEqual(payload["status"], "passed")
        checks = {row["name"]: row["status"] for row in payload["checks"]}
        self.assertEqual(checks["git_checks_disabled_for_fixture"], "passed")
        self.assertEqual(checks["raw_source_has_no_force_dump_patch"], "passed")

    def test_force_comparator_passes_and_fails_with_explicit_tolerances(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp) / "left.txt"
            right = Path(tmp) / "right.txt"
            out = Path(tmp) / "compare.json"
            left.write_text("0 1.0\n1 2.0\n", encoding="utf-8")
            right.write_text("0 1.0\n1 2.000001\n", encoding="utf-8")
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "compare_force_outputs.py"),
                    "--left",
                    str(left),
                    "--right",
                    str(right),
                    "--rtol",
                    "1e-4",
                    "--atol",
                    "1e-6",
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
            )
            passed = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(passed["matched"])

            right.write_text("0 1.0\n1 2.1\n", encoding="utf-8")
            failed = subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "compare_force_outputs.py"),
                    "--left",
                    str(left),
                    "--right",
                    str(right),
                    "--rtol",
                    "1e-4",
                    "--atol",
                    "1e-6",
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=False,
            )
            self.assertEqual(failed.returncode, 1)
            payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertFalse(payload["matched"])
        self.assertEqual(payload["mismatch_count"], 1)

    def test_same_input_performance_gate_reports_ready_with_fixture_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / "rt-barneshut-paper"
            (app / "_runs" / "author_same_input").mkdir(parents=True)
            (app / "_runs" / "rtdl_diagnostic").mkdir(parents=True)
            (app / "_runs" / "author_comparator_gate").mkdir(parents=True)
            (app / "_runs" / "same_input_rtdl_comparison_gate").mkdir(parents=True)
            (app / "_runs" / "author_same_input" / "summary.json").write_text(
                json.dumps(
                    {
                        "preprocessing_ms": 12.0,
                        "rt_core_force_ms": 2.0,
                        "execution_ms": 20.0,
                    }
                ),
                encoding="utf-8",
            )
            (app / "_runs" / "rtdl_diagnostic" / "summary.json").write_text(
                json.dumps(
                    {
                        "rtdl_payload": {
                            "timing_ms": {
                                "tree_prepare_cpu": 30.0,
                                "extension_compile": 40.0,
                                "tensor_prepare_host_to_device": 5.0,
                                "resident_kernel_min": 3.0,
                                "resident_kernel_mean": 3.5,
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            (app / "_runs" / "author_comparator_gate" / "summary.json").write_text(
                json.dumps({"same_input_author_comparator_closed": True}),
                encoding="utf-8",
            )
            (app / "_runs" / "same_input_rtdl_comparison_gate" / "summary.json").write_text(
                json.dumps(
                    {
                        "same_input_author_rtdl_comparator_closed": True,
                        "matched": True,
                        "force_count": 64,
                        "max_abs_error": 1e-9,
                        "max_rel_error": 1e-10,
                        "mismatch_count": 0,
                    }
                ),
                encoding="utf-8",
            )
            out = Path(tmp) / "perf_summary.json"
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "run_same_input_performance_gate.py"),
                    "--app-dir",
                    str(app),
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ready_for_phase_boundary_review")
        self.assertTrue(payload["correctness_ready"])
        self.assertFalse(payload["paper_reproduction_complete"])
        self.assertFalse(payload["performance_review_complete"])
        self.assertEqual(payload["same_input_compare"]["force_count"], 64)
        self.assertEqual(payload["author_treelogy_timing_ms"]["rt_core_force"], 2.0)
        self.assertEqual(payload["rtdl_diagnostic_timing_ms"]["resident_kernel_min"], 3.0)
        self.assertEqual(payload["narrow_force_kernel_ratio_rtdl_over_author"], 1.5)

    def test_same_input_performance_gate_fails_closed_when_summaries_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / "rt-barneshut-paper"
            app.mkdir()
            out = Path(tmp) / "perf_summary.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "run_same_input_performance_gate.py"),
                    "--app-dir",
                    str(app),
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=False,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(payload["status"], "blocked_missing_required_summaries")
        self.assertEqual(len(payload["missing"]), 4)
        self.assertFalse(payload["paper_reproduction_complete"])

    def _write_ready_performance_summary(self, app: Path, ratio_value: float = 1.5) -> Path:
        perf_dir = app / "_runs" / "same_input_performance_gate"
        perf_dir.mkdir(parents=True, exist_ok=True)
        summary = perf_dir / "summary.json"
        summary.write_text(
            json.dumps(
                {
                    "mode": "same_input_performance_gate",
                    "status": "ready_for_phase_boundary_review",
                    "narrow_force_kernel_ratio_rtdl_over_author": ratio_value,
                }
            ),
            encoding="utf-8",
        )
        return summary

    def test_phase_boundary_review_gate_accepts_bound_matching_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / "rt-barneshut-paper"
            summary = self._write_ready_performance_summary(app, ratio_value=1.5)
            review = app / "_runs" / "same_input_performance_gate" / "phase_boundary_review.json"
            review.write_text(
                json.dumps(
                    {
                        "performance_review_complete": True,
                        "phase_boundary_accepted": True,
                        "reviewed_summary_path": str(summary),
                        "accepted_author_phase": "author_treelogy_timing_ms.rt_core_force",
                        "accepted_rtdl_phase": "rtdl_diagnostic_timing_ms.resident_kernel_min",
                        "reviewed_ratio_rtdl_over_author": 1.5,
                    }
                ),
                encoding="utf-8",
            )
            out = Path(tmp) / "phase_review_gate.json"
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "run_phase_boundary_review_gate.py"),
                    "--app-dir",
                    str(app),
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "accepted")
        self.assertTrue(all(payload["checks"].values()))
        self.assertFalse(payload["paper_reproduction_complete"])

    def test_phase_boundary_review_gate_rejects_unbound_or_mismatched_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / "rt-barneshut-paper"
            summary = self._write_ready_performance_summary(app, ratio_value=1.5)
            review = app / "_runs" / "same_input_performance_gate" / "phase_boundary_review.json"
            review.write_text(
                json.dumps(
                    {
                        "performance_review_complete": True,
                        "phase_boundary_accepted": True,
                        "reviewed_summary_path": str(summary),
                        "accepted_author_phase": "author_treelogy_timing_ms.execution",
                        "accepted_rtdl_phase": "rtdl_diagnostic_timing_ms.resident_kernel_min",
                        "reviewed_ratio_rtdl_over_author": 99.0,
                    }
                ),
                encoding="utf-8",
            )
            out = Path(tmp) / "phase_review_gate.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "run_phase_boundary_review_gate.py"),
                    "--app-dir",
                    str(app),
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=False,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(payload["status"], "blocked_review_incomplete_or_mismatched")
        self.assertFalse(payload["checks"]["accepted_author_phase_matches"])
        self.assertFalse(payload["checks"]["reviewed_ratio_matches_summary"])

    def _load_full_gate_module(self):
        spec = importlib.util.spec_from_file_location(
            "rtbh_full_pod_gate_for_test",
            APP_DIR / "scripts" / "run_full_pod_reproduction_gate.py",
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def test_full_pod_gate_runner_reports_ready_with_stubbed_successful_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            app = root / "Paper-reproduction-apps" / "rt-barneshut-paper"
            run_dir = app / "_runs" / "full_pod_reproduction_gate"
            module = self._load_full_gate_module()
            calls: list[str] = []
            summaries = {
                "local_contract_gate": {"status": "passed"},
                "author_source_contract_gate": {"status": "passed"},
                "pod_environment_preflight": {
                    "ready_for_author_build": True,
                    "ready_for_rtdl_cuda_gate": True,
                },
                "author_contract_rtdl_cuda_gate": {"matched": True},
                "author_comparator_gate": {"same_input_author_comparator_closed": True},
                "generic_aggregate_force_same_input_gate": {
                    "same_input_author_comparator": True,
                    "force_comparison": {"matched": True},
                },
                "same_input_author_vs_rtdl_gate": {
                    "matched": True,
                    "same_input_author_rtdl_comparator_closed": True,
                },
                "same_input_performance_gate": {"status": "ready_for_phase_boundary_review"},
            }

            def fake_run_gate(name, command, summary_path, *, root_dir, run_dir):
                calls.append(name)
                return {
                    "name": name,
                    "status": "passed",
                    "returncode": 0,
                    "command": command,
                    "summary_path": str(summary_path),
                    "summary": summaries[name],
                }

            original_run_gate = module.run_gate
            module.run_gate = fake_run_gate
            try:
                payload, exit_code = module.build_full_gate_summary(root_dir=root, app_dir=app, run_dir=run_dir)
            finally:
                module.run_gate = original_run_gate
        self.assertEqual(
            payload["overall_status"],
            "passed_correctness_and_timing_gates__phase_boundary_review_required",
        )
        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["correctness_gates_complete"])
        self.assertTrue(payload["performance_timing_gate_ready"])
        self.assertFalse(payload["paper_reproduction_complete"])
        self.assertEqual(
            calls,
            [
                "local_contract_gate",
                "author_source_contract_gate",
                "pod_environment_preflight",
                "author_contract_rtdl_cuda_gate",
                "author_comparator_gate",
                "generic_aggregate_force_same_input_gate",
                "same_input_author_vs_rtdl_gate",
                "same_input_performance_gate",
            ],
        )
        self.assertTrue(payload["generic_aggregate_force_same_input_gate_complete"])
        self.assertEqual([gate["status"] for gate in payload["gates"]], ["passed"] * 8)

    def test_full_pod_gate_runner_skips_dependents_when_preflight_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            app = root / "Paper-reproduction-apps" / "rt-barneshut-paper"
            run_dir = app / "_runs" / "full_pod_reproduction_gate"
            module = self._load_full_gate_module()
            calls: list[str] = []

            def fake_run_gate(name, command, summary_path, *, root_dir, run_dir):
                calls.append(name)
                if name == "local_contract_gate":
                    return {
                        "name": name,
                        "status": "passed",
                        "returncode": 0,
                        "command": command,
                        "summary_path": str(summary_path),
                        "summary": {"status": "passed"},
                    }
                if name == "author_source_contract_gate":
                    return {
                        "name": name,
                        "status": "passed",
                        "returncode": 0,
                        "command": command,
                        "summary_path": str(summary_path),
                        "summary": {"status": "passed"},
                    }
                return {
                    "name": name,
                    "status": "failed",
                    "returncode": 2,
                    "command": command,
                    "summary_path": str(summary_path),
                    "summary": {
                        "ready_for_author_build": False,
                        "ready_for_rtdl_cuda_gate": False,
                    },
                }

            original_run_gate = module.run_gate
            module.run_gate = fake_run_gate
            try:
                payload, exit_code = module.build_full_gate_summary(root_dir=root, app_dir=app, run_dir=run_dir)
            finally:
                module.run_gate = original_run_gate
        self.assertEqual(exit_code, 2)
        self.assertEqual(calls, ["local_contract_gate", "author_source_contract_gate", "pod_environment_preflight"])
        self.assertEqual(payload["overall_status"], "blocked_by_pod_environment_preflight")
        self.assertEqual([gate["status"] for gate in payload["gates"][:3]], ["passed", "passed", "failed"])
        self.assertEqual([gate["status"] for gate in payload["gates"][3:]], ["skipped"] * 5)
        self.assertFalse(payload["correctness_gates_complete"])
        self.assertFalse(payload["performance_timing_gate_ready"])

    def _write_completion_fixture(
        self,
        app: Path,
        *,
        correctness: bool,
        timing_ready: bool,
        review_ready: bool,
    ) -> None:
        (app / "data").mkdir(parents=True, exist_ok=True)
        (app / "_runs" / "local_contract_gate").mkdir(parents=True, exist_ok=True)
        (app / "_runs" / "author_source_contract_gate").mkdir(parents=True, exist_ok=True)
        (app / "_runs" / "full_pod_reproduction_gate").mkdir(parents=True, exist_ok=True)
        (app / "_runs" / "same_input_performance_gate").mkdir(parents=True, exist_ok=True)
        (app / "_runs" / "phase_boundary_review_gate").mkdir(parents=True, exist_ok=True)
        (app / "data" / "manifest.json").write_text(
            json.dumps(
                {
                    "author_artifact": {
                        "repository": "repo",
                        "branch": "branch",
                        "commit": "commit",
                        "sample_path": "sample",
                        "binary_target": "rtbarneshut",
                    }
                }
            ),
            encoding="utf-8",
        )
        (app / "_runs" / "local_contract_gate" / "summary.json").write_text(
            json.dumps({"status": "passed", "paper_reproduction_complete": False}),
            encoding="utf-8",
        )
        (app / "_runs" / "author_source_contract_gate" / "summary.json").write_text(
            json.dumps({"status": "passed", "source_root": "fixture", "git": {"clean": True}}),
            encoding="utf-8",
        )
        (app / "_runs" / "full_pod_reproduction_gate" / "summary.json").write_text(
            json.dumps(
                {
                    "local_contract_gate_complete": True,
                    "author_source_contract_gate_complete": True,
                    "correctness_gates_complete": correctness,
                    "performance_timing_gate_ready": timing_ready,
                    "overall_status": "fixture",
                    "gates": [
                        {"name": "local_contract_gate", "status": "passed"},
                        {"name": "author_source_contract_gate", "status": "passed"},
                        {"name": "pod_environment_preflight", "status": "passed"},
                        {"name": "author_contract_rtdl_cuda_gate", "status": "passed"},
                        {"name": "author_comparator_gate", "status": "passed"},
                        {"name": "generic_aggregate_force_same_input_gate", "status": "passed"},
                        {"name": "same_input_author_vs_rtdl_gate", "status": "passed"},
                        {"name": "same_input_performance_gate", "status": "passed"},
                    ],
                }
            ),
            encoding="utf-8",
        )
        if review_ready:
            (app / "_runs" / "phase_boundary_review_gate" / "summary.json").write_text(
                json.dumps({"status": "accepted", "checks": {"fixture": True}}),
                encoding="utf-8",
            )

    def test_completion_audit_fails_until_all_evidence_is_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / "rt-barneshut-paper"
            self._write_completion_fixture(app, correctness=True, timing_ready=True, review_ready=False)
            out = Path(tmp) / "audit.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "run_completion_audit.py"),
                    "--app-dir",
                    str(app),
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=False,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(payload["overall_status"], "incomplete")
        self.assertFalse(payload["paper_reproduction_complete"])
        statuses = {row["id"]: row["status"] for row in payload["requirements"]}
        self.assertEqual(statuses["performance_phase_boundary_reviewed"], "missing")
        self.assertEqual(statuses["same_input_correctness_closed"], "complete")

    def test_completion_audit_can_only_complete_with_all_fixture_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / "rt-barneshut-paper"
            self._write_completion_fixture(app, correctness=True, timing_ready=True, review_ready=True)
            out = Path(tmp) / "audit.json"
            subprocess.run(
                [
                    sys.executable,
                    str(APP_DIR / "scripts" / "run_completion_audit.py"),
                    "--app-dir",
                    str(app),
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(payload["overall_status"], "complete")
        self.assertTrue(payload["paper_reproduction_complete"])
        self.assertTrue(all(row["status"] == "complete" for row in payload["requirements"]))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import ast
from argparse import Namespace
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import subprocess
import struct
import tempfile
import sys
from types import SimpleNamespace
import unittest
from unittest import mock

from scripts import goal5790_a1_home_controller as controller
from scripts import goal5790_a1_home_worker as worker
from scripts import goal5790_a1_build_portable_source as portable_builder
from scripts.goal5790_a1_rejected_encoding_cases import (
    CASE_IDS,
    build_suite,
    canonical_sha256,
)


ROOT = Path(__file__).resolve().parents[1]
HOME_AUTHORITY_PATH = (
    ROOT / "history/internal_docs/"
    "goal5790_frozen_home_machine_authority_20260816.json")


def exact_home_machine():
    authority = json.loads(HOME_AUTHORITY_PATH.read_text(encoding="utf-8"))
    value = {
        "hostname": controller.HOME_HOSTNAME,
        "gpu": controller.HOME_GPU,
        "driver": controller.HOME_DRIVER,
        "uuid": controller.HOME_UUID,
        "compute_capability": controller.HOME_CC,
        "classification": "exact_home_lx1__not_pod",
        "frozen_home_authority_file_sha256": (
            controller.HOME_AUTHORITY_FILE_SHA256),
        "frozen_home_authority_receipt_sha256": (
            controller.HOME_AUTHORITY_RECEIPT_SHA256),
        "home_toolchain_identity_sha256": canonical_sha256({
            field: authority[field]
            for field in controller.HOME_TOOLCHAIN_FIELDS}),
    }
    value["home_machine_authority_sha256"] = canonical_sha256(value)
    return value


def minimal_execution_spec(suite):
    rows = []
    for case in suite["cases"]:
        row = {
            "case_id": case["case_id"],
            "upstream_case_sha256": case["case_sha256"],
        }
        row["case_execution_spec_sha256"] = canonical_sha256(row)
        rows.append(row)
    result = {
        "schema": "rtdl.goal5790_a1.home_execution_spec.v2",
        "upstream_suite_sha256": suite["suite_sha256"],
        "pre_run_source_members": [{
            "logical_path": "scripts/goal5790_a1_home_worker.py",
            "evidence_path": "PRE_RUN_SOURCE/scripts/goal5790_a1_home_worker.py",
            "sha256": hashlib.sha256((
                ROOT / "scripts/goal5790_a1_home_worker.py").read_bytes()).hexdigest(),
            "roles": ["trusted_test_classifier", "home_worker"],
        }],
        "cases": rows,
    }
    result["execution_spec_sha256"] = canonical_sha256(result)
    return result


class Goal5790A1HomeWorkerTest(unittest.TestCase):
    def test_receipt_completion_matches_real_goal5783_integer_schema(self):
        fixture_path = (
            ROOT / "history/internal_docs/goal5783_home_functional_result_20260814/"
            "GOAL5783_FUNCTIONAL_RECEIPT.json")
        self.assertEqual(
            hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
            "1f490e072476c43c3807ace165859e217133afcfc8caee601ba8d8f8d960235b")
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        receipt = fixture["cold_cases"][0]["traversal_receipt"]
        snapshot = receipt["native_snapshot"]
        self.assertIs(type(snapshot["pending_context_at_finish"]), int)
        self.assertIs(type(snapshot["session_error"]), int)
        self.assertTrue(worker._receipt_is_complete(receipt))

        zero_fields = (
            "failed_launch_count",
            "incomplete_context_launch_count",
            "pending_context_at_finish",
            "session_error",
        )
        for field in zero_fields:
            for label, replacement in (("bool", False), ("nonzero", 1)):
                with self.subTest(field=field, mutation=label):
                    tampered = json.loads(json.dumps(receipt))
                    tampered["native_snapshot"][field] = replacement
                    self.assertFalse(worker._receipt_is_complete(tampered))
            with self.subTest(field=field, mutation="missing"):
                tampered = json.loads(json.dumps(receipt))
                del tampered["native_snapshot"][field]
                self.assertFalse(worker._receipt_is_complete(tampered))

        for field in (
            "successful_launch_count",
            "complete_context_launch_count",
            "raygen_invocation_count",
        ):
            for label, replacement in (("bool", True), ("zero", 0)):
                with self.subTest(field=field, mutation=label):
                    tampered = json.loads(json.dumps(receipt))
                    tampered["native_snapshot"][field] = replacement
                    self.assertFalse(worker._receipt_is_complete(tampered))
            with self.subTest(field=field, mutation="missing"):
                tampered = json.loads(json.dumps(receipt))
                del tampered["native_snapshot"][field]
                self.assertFalse(worker._receipt_is_complete(tampered))

        tampered = json.loads(json.dumps(receipt))
        tampered["native_snapshot"]["complete_context_launch_count"] = 2
        self.assertFalse(worker._receipt_is_complete(tampered))
        for field, replacement in (
            ("physical_executor_classification", "optix_template_selected"),
            ("expected_program_observed_at_receipt_edge", 1),
        ):
            with self.subTest(field=field, mutation="wrong_type_or_value"):
                tampered = json.loads(json.dumps(receipt))
                tampered[field] = replacement
                self.assertFalse(worker._receipt_is_complete(tampered))
            with self.subTest(field=field, mutation="missing"):
                tampered = json.loads(json.dumps(receipt))
                del tampered[field]
                self.assertFalse(worker._receipt_is_complete(tampered))

    def test_portable_deep_blob_gate_rejects_suffix_magic_and_native(self):
        for label, payloads in (
            ("archive_suffix", {"hidden/evidence.tar.gz": b"not gzip"}),
            ("hidden_gzip_magic", {"hidden/evidence.dat": b"\x1f\x8bpayload"}),
            ("hidden_elf_magic", {"hidden/provider.dat": b"\x7fELFpayload"}),
            ("hidden_fatbin_magic", {"hidden/device.dat": b"P\xedU\xbapayload"}),
        ):
            with self.subTest(label=label), self.assertRaises(RuntimeError):
                portable_builder._deep_successor_blob_audit(payloads)
        clean = portable_builder._deep_successor_blob_audit({
            "src/example.py": b"print('source')\n",
            "history/result.json": b"{}\n",
        })
        self.assertTrue(clean["all_successor_payload_bytes_scanned"])
        self.assertEqual(clean["scanned_payload_count"], 2)
        self.assertEqual(clean["maximum_nested_container_depth"], 0)

    def test_host_compiler_authority_preserves_lexical_symlink_spelling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "x86_64-linux-gnu-g++-12"
            target.write_bytes(b"test executable placeholder\n")
            lexical = root / "g++-12"
            try:
                lexical.symlink_to(target)
            except OSError:
                # Windows CI commonly denies symlink creation.  The mocked
                # resolve below still reproduces the Home lexical/target split
                # and, critically, proves that admission never calls resolve.
                pass
            self.assertNotEqual(str(lexical), str(target))
            expected_version = "g++-12 (Ubuntu 12.4.0) 12.4.0"
            completed = subprocess.CompletedProcess(
                [str(lexical), "--version"], 0, expected_version + "\n", "")
            authority = {
                "cuda_host_compiler_path": str(lexical),
                "cuda_host_compiler_version": expected_version,
            }
            with mock.patch.object(Path, "is_file", return_value=True), \
                    mock.patch.object(
                        Path, "resolve", return_value=target) as resolver, \
                    mock.patch.object(
                    controller.subprocess, "run",
                    return_value=completed) as run:
                admitted = controller._verify_cuda_host_compiler(authority)
            self.assertEqual(admitted, lexical)
            resolver.assert_not_called()
            run.assert_called_once_with(
                [str(lexical), "--version"], check=True, text=True,
                capture_output=True)

    def test_worker_has_no_eager_gpu_or_product_compiler_import(self):
        path = ROOT / "scripts/goal5790_a1_home_worker.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        self.assertFalse(any(name == "numba" or name.startswith("numba.")
                             or name == "cupy" or name.startswith("cupy.")
                             or name.startswith("rtdsl.")
                             for name in imported))

    def test_product_rejection_is_named_and_has_zero_execution(self):
        expected_product_rules = {
            CASE_IDS[0]: "SP024_EXACTNESS_POLICY_MISMATCH",
            CASE_IDS[1]: "SP025_TIE_POLICY_MISMATCH",
            CASE_IDS[2]: "SP027_OVERFLOW_POLICY_MISMATCH",
            CASE_IDS[3]: "SP026_MULTIPLICITY_POLICY_MISMATCH",
            CASE_IDS[4]: "triangle_orientation_mapping",
            CASE_IDS[5]: "SP024_EXACTNESS_POLICY_MISMATCH",
        }
        for index, case in enumerate(build_suite()["cases"]):
            code = (
                "import json; from pathlib import Path; "
                "from types import SimpleNamespace; "
                "from scripts.goal5790_a1_rejected_encoding_cases import build_suite; "
                "from scripts.goal5790_a1_home_worker import _product_reject; "
                f"case=build_suite()['cases'][{index}]; "
                "args=SimpleNamespace(cc='61',optix_sdk='9.0.0',"
                "native=Path('scripts/goal5790_a1_home_worker.py')); "
                "print(json.dumps(_product_reject(case,args),sort_keys=True))")
            completed = subprocess.run(
                [sys.executable, "-c", code], cwd=ROOT, check=True,
                text=True, capture_output=True)
            result = json.loads(completed.stdout)
            self.assertEqual(result["verdict"], "INCOMPATIBLE")
            self.assertEqual(
                result["product_rule_ids"],
                [expected_product_rules[case["case_id"]]])
            self.assertNotIn("SP000_MALFORMED_INPUT", result["product_rule_ids"])
            self.assertEqual(result["named_case_rule_id"], case["expected_rule_id"])
            self.assertEqual(result["compiler_call_count"], 0)
            self.assertEqual(result["native_prepare_call_count"], 0)
            self.assertEqual(result["native_execute_call_count"], 0)
            self.assertEqual(result["traversal_launch_count"], 0)
            self.assertFalse(result["execution_authorized"])
            self.assertFalse(result["executable_issued"])
            self.assertFalse(result["forbidden_gpu_or_compiler_imports"])

    def test_strict_box_variant_changes_only_the_four_comparators(self):
        from rtdsl.v4_box_relation_callback import BOX_RELATION_SOURCE

        strict = worker._strict_box_source()
        self.assertNotEqual(strict, BOX_RELATION_SOURCE)
        self.assertIn("primitive.lower.x < source_max_x", strict)
        self.assertIn("primitive.upper.x > source_min_x", strict)
        self.assertIn("primitive.lower.y < source_max_y", strict)
        self.assertIn("primitive.upper.y > source_min_y", strict)
        self.assertNotIn("primitive.lower.x <= source_max_x", strict)
        before = BOX_RELATION_SOURCE.splitlines()
        after = strict.splitlines()
        changed = [(left, right) for left, right in zip(before, after) if left != right]
        self.assertEqual(len(changed), 1)

    def test_accepted_compile_helpers_require_product_admission_wrapper(self):
        source = (ROOT / "scripts/goal5790_a1_home_worker.py").read_text(
            encoding="utf-8")
        self.assertIn("v4_semantically_admitted_compiler", source)
        self.assertIn("compile_semantically_admitted_builtin_triangle_executable", source)
        self.assertIn("compile_semantically_admitted_bounded_relation_executable", source)
        self.assertIn("compile_semantically_admitted_triangle_reduction_executable", source)
        self.assertIn("admit_builtin_triangle_compilation", source)
        self.assertIn("admit_bounded_relation_compilation", source)
        self.assertIn("admit_triangle_reduction_compilation", source)
        self.assertIn("run_semantically_admitted_builtin_triangle_callback", source)
        self.assertIn("run_semantically_admitted_bounded_relation_callback", source)
        self.assertIn("run_semantically_admitted_triangle_reduction_callback", source)
        self.assertNotIn("def _require_accepted_program", source)
        self.assertNotIn("def _bridge_fixture", source)
        self.assertIn("FAIL_CLOSED_OVERFLOW", source)
        self.assertIn("output_produced\": False", source)
        self.assertNotIn("validate_weighted_reduction_summary", source)
        self.assertIn("weighted = overflow or not diagnostic", source)

    def test_pre_run_authorities_bind_real_stage_sources_without_unused_manifest(self):
        from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile

        target = ReferenceTargetProfile(
            provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
            native_sha256="1" * 64, supports_custom_aabb=True,
            supports_builtin_triangle=True)
        snapshot = worker.build_pre_run_suite_authorities(
            build_suite(), target)
        self.assertEqual(len(snapshot["cases"]), 6)
        self.assertEqual(snapshot["low_level_compiler_call_count"], 0)
        self.assertEqual(snapshot["traversal_launch_count"], 0)
        self.assertEqual(
            snapshot["particle_gate_authority_sha256"],
            "84872fdb24f5d398644ec421b55a8a53c7f6cc19af4860ac4ad10f440d958625")
        for row in snapshot["cases"]:
            for entry in row["physical_registry"]["entries"]:
                guarantee = entry["guarantee"]
                mapped = {edge["source_id"] for edge in guarantee["maps"]}
                self.assertEqual(set(guarantee["source_manifest"]), mapped)
                for edge in guarantee["maps"]:
                    self.assertEqual(
                        edge["source_sha256"],
                        guarantee["source_manifest"][edge["source_id"]])
            self.assertEqual(
                row["diagnostic_transform_authority"][
                    "implementation_path"],
                "scripts/goal5790_a1_home_worker.py")
        particle = snapshot["cases"][4]
        self.assertEqual(
            particle["diagnostic_early_reject"]["code"],
            "triangle_orientation_mapping")
        self.assertIsNotNone(particle["diagnostic_family_attempt"])

    def test_stage_source_catalog_is_the_actual_a1_call_graph(self):
        catalog = worker._TRUSTED_STAGE_SOURCES_BY_CASE
        self.assertEqual(
            catalog[CASE_IDS[0]][0]["encode"],
            "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py")
        self.assertEqual(
            catalog[CASE_IDS[0]][0]["decode"],
            "scripts/goal5790_a1_home_worker.py")
        for case_id in CASE_IDS[2:4]:
            canonical = catalog[case_id][0]
            self.assertEqual(
                canonical["trace"],
                "src/rtdsl/v4_triangle_reduction_optix_runtime.py")
            self.assertEqual(
                canonical["continuation"],
                "src/rtdsl/v4_triangle_reduction.py")
            self.assertEqual(
                canonical["encode"],
                "scripts/goal5790_a1_home_worker.py")
            self.assertEqual(
                canonical["decode"],
                "scripts/goal5790_a1_home_worker.py")
        self.assertEqual(
            catalog[CASE_IDS[4]][1]["continuation"],
            "src/rtdsl/v4_builtin_triangle_standard_library.py")
        relation = catalog[CASE_IDS[5]][0]
        self.assertEqual(
            relation["encode"], "scripts/goal5790_a1_home_worker.py")
        self.assertEqual(
            relation["decode"], "scripts/goal5790_a1_home_worker.py")

    def test_u64_accepted_control_uses_weighted_route_and_emits_no_receipt(self):
        case = build_suite()["cases"][2]
        calls = []

        class ExpectedOverflow(ValueError):
            def __init__(self):
                self.code = "unsigned_overflow"
                self.path = "reducer"

        def checked_runtime(*_args, **kwargs):
            calls.append(kwargs)
            raise ExpectedOverflow()

        fake_program = SimpleNamespace(
            authority=object(), contract=object(), abi=object(),
            executable=object(), proof=object(), admission=object())
        fake_target = SimpleNamespace(target_sha256="1" * 64)
        fake_args = SimpleNamespace(native=Path("native.so"))
        modules = {
            "rtdsl.v4_semantically_admitted_compiler": SimpleNamespace(
                run_semantically_admitted_triangle_reduction_callback=(
                    checked_runtime)),
            "rtdsl.v4_triangle_reduction": SimpleNamespace(
                TriangleReductionError=ExpectedOverflow),
        }
        with mock.patch.dict("sys.modules", modules), \
                mock.patch.object(
                    worker, "_compile_triangle_accepted",
                    return_value=fake_program) as compile_accepted, \
                mock.patch.object(
                    worker, "_program_identity", return_value={"family": "test"}):
            result = worker._run_triangle(
                case, "accepted_control", fake_target, fake_args)
        self.assertEqual(
            compile_accepted.call_args.kwargs, {"weighted": True})
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["metadata"], {
            "query.weight": tuple(case["minimal_witness"]["weights"])})
        self.assertEqual(result["accepted_disposition"]["status"],
                         "FAIL_CLOSED_OVERFLOW")
        self.assertIsNone(result["output"])
        self.assertEqual(result["traversal_receipts"], [])
        self.assertFalse(result["behaviorally_true_optix"])
        self.assertIn("executed_input", result)
        self.assertEqual(
            result["executed_input_sha256"],
            canonical_sha256(result["executed_input"]))

    def test_unchecked_u64_diagnostic_is_a_bound_device_operation(self):
        class FakeOutput:
            def __init__(self):
                self.value = 99

            def get(self):
                return [self.value]

        class FakeKernel:
            def __init__(self, source, entry, options):
                self.source = source
                self.entry = entry
                self.options = options

            def __call__(self, grid, block, arguments):
                self.grid = grid
                self.block = block
                arguments[-1].value = 0

        fake_runtime = SimpleNamespace(
            runtimeGetVersion=lambda: 12020,
            getDevice=lambda: 0,
            deviceSynchronize=mock.Mock())
        fake_cupy = SimpleNamespace(
            __version__="14.0.1",
            uint64=lambda value: int(value),
            asarray=lambda value, dtype: list(value),
            zeros=lambda count, dtype: FakeOutput(),
            RawKernel=FakeKernel,
            cuda=SimpleNamespace(runtime=fake_runtime),
        )
        with mock.patch.dict("sys.modules", {"cupy": fake_cupy}):
            output, receipt = worker._run_unchecked_u64_device_continuation(
                (1, 1), (1 << 63, 1 << 63), target_sha256="2" * 64,
                home_toolchain_identity_sha256="4" * 64)
        self.assertEqual(output, 0)
        self.assertEqual(receipt["output_value"], 0)
        self.assertEqual(receipt["device_kernel_launch_count"], 1)
        self.assertEqual(receipt["host_synchronization_count"], 1)
        self.assertEqual(receipt["target_sha256"], "2" * 64)
        self.assertEqual(receipt["home_toolchain_identity_sha256"], "4" * 64)
        self.assertTrue(receipt["test_only_nonregistrable"])
        self.assertFalse(receipt["production_authority_minted"])
        self.assertFalse(receipt["host_fallback_used"])
        self.assertEqual(
            receipt["operation_recipe_sha256"],
            canonical_sha256(receipt["operation_recipe"]))
        self.assertEqual(
            receipt["frozen_home_authority_file_sha256"],
            controller.HOME_AUTHORITY_FILE_SHA256)
        fake_runtime.deviceSynchronize.assert_called_once_with()

    def test_exact_executed_input_uses_little_endian_binary_columns(self):
        payload = worker._triangle_exact_input(
            family="test", vertices=((1.0, -0.0, 0.5),),
            triangles=((0, 0, 0),),
            queries=(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),),
            front_values=(7,), back_values=(9,), weights=(1 << 63,),
            event_capacity=4)
        self.assertEqual(
            payload["columns"]["vertices_xyz"]["bytes_hex"],
            struct.pack("<fff", 1.0, -0.0, 0.5).hex())
        for column in payload["columns"].values():
            raw = bytes.fromhex(column["bytes_hex"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),
                             column["bytes_sha256"])
        sealed = worker._executed_input(payload)
        self.assertEqual(
            sealed["executed_input_sha256"],
            canonical_sha256(sealed["executed_input"]))

    def test_overflow_diagnostic_preserves_weighted_input_and_uses_no_host_sum(self):
        source = (ROOT / "scripts/goal5790_a1_home_worker.py").read_text(
            encoding="utf-8")
        self.assertIn("weighted = overflow or not diagnostic", source)
        self.assertIn("_run_weighted_per_ray_diagnostic", source)
        self.assertNotIn("sum(per_ray", source)
        self.assertNotIn("& ((1 << 64) - 1)", source)
        self.assertIn('"host_fallback_used": False', source)

    def test_controller_command_is_one_case_one_arm_and_no_timing_flag(self):
        command = controller.build_worker_command(
            python="python3", suite=Path("suite.json"), output=Path("raw.json"),
            case_id=CASE_IDS[0], arm="accepted_control",
            native=Path("native.so"), optix_include=Path("optix"),
            cuda_include=Path("cuda"), compute_capability="61",
            optix_sdk="9.0.0", expected_python="3.12.0",
            expected_numba="0.61.2", expected_numpy="2.2.6",
            home_authority_sha256=(
                exact_home_machine()["home_machine_authority_sha256"]),
            home_authority_file=HOME_AUTHORITY_PATH,
            home_authority_file_sha256=(
                controller.HOME_AUTHORITY_FILE_SHA256),
            execution_spec=Path("execution-spec.json"),
            execution_spec_sha256="3" * 64)
        self.assertEqual(command[:3], ["python3", "-m", "scripts.goal5790_a1_home_worker"])
        self.assertEqual(command.count("--case-id"), 1)
        self.assertEqual(command.count("--arm"), 1)
        self.assertNotIn("--timing", command)
        self.assertNotIn("--performance", command)

    def test_controller_enforces_three_fresh_pids_and_zero_timing(self):
        suite = build_suite()
        by_id = {row["case_id"]: row for row in suite["cases"]}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            suite_path = root / "suite.json"
            suite_path.write_text(
                json.dumps(suite, sort_keys=True, allow_nan=False) + "\n",
                encoding="utf-8")
            spec = minimal_execution_spec(suite)
            spec_path = root / "execution-spec.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            native = root / "librtdl_optix.so"
            native.write_bytes(b"test-native")
            optix = root / "optix"
            cuda = root / "cuda"
            optix.mkdir()
            cuda.mkdir()
            next_pid = iter(range(70_000, 70_100))
            worker_environments = []

            def fake_run(command, **kwargs):
                worker_environments.append(dict(kwargs["env"]))
                output = Path(command[command.index("--output") + 1])
                case_id = command[command.index("--case-id") + 1]
                arm = command[command.index("--arm") + 1]
                value = {
                    "schema": "rtdl.goal5790_a1.home_worker.v1",
                    "status": "PASS", "case_id": case_id,
                    "case_sha256": by_id[case_id]["case_sha256"],
                    "execution_spec_sha256": spec["execution_spec_sha256"],
                    "input_sha256": "0" * 64, "arm": arm,
                    "parent_pid": next(next_pid),
                    "arm_result": ({
                        "production_facade_called": (
                            case_id != CASE_IDS[4]),
                        "product_rejection_gate": (
                            "verify_typed_physical_schema"
                            if case_id == CASE_IDS[4]
                            else "v4_semantically_admitted_compiler.admit_*"),
                    } if arm == "product_admission_reject" else {}),
                    "home_machine": exact_home_machine(),
                    "home_machine_authority_sha256": (
                        exact_home_machine()["home_machine_authority_sha256"]),
                    "cache_policy": {
                        "formal_leaf_cache_environment_cleared": True,
                        "cupy_cache_dir": "test/cupy",
                        "numba_cache_dir": "test/numba",
                        "initially_empty": True,
                        "per_arm_isolated": True,
                        "cache_is_execution_authority": False,
                        "cache_contents_used_as_evidence": False,
                    },
                    "elapsed_values_recorded": False,
                    "registered_performance_timing_created": False,
                    "performance_claimed": False, "pod_used": False,
                    "formal_worker": False,
                }
                value["worker_result_sha256"] = canonical_sha256(value)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(value), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, "", "")

            with mock.patch.object(controller.subprocess, "run", side_effect=fake_run):
                result = controller.run_controller(
                    suite_path=suite_path, output_root=root / "out",
                    native=native, optix_include=optix, cuda_include=cuda,
                    compute_capability="61", optix_sdk="9.0.0",
                    case_ids=CASE_IDS[:2], python="python3",
                    expected_python="3.12.0", expected_numba="0.61.2",
                    expected_numpy="2.2.6",
                    home_machine=exact_home_machine(),
                    frozen_home_authority=json.loads(
                        HOME_AUTHORITY_PATH.read_text(encoding="utf-8")),
                    execution_spec_path=spec_path,
                    execution_spec_sha256=spec["execution_spec_sha256"])
            self.assertEqual(result["case_count"], 2)
            self.assertEqual(result["arm_count"], 6)
            self.assertEqual(result["fresh_parent_pid_count"], 6)
            self.assertEqual(result["product_admission_launch_count"], 0)
            self.assertEqual(result["registered_performance_timing_count"], 0)
            self.assertFalse(result["performance_claimed"])
            self.assertFalse(result["pod_used"])
            self.assertEqual(len(worker_environments), 6)
            self.assertEqual(len({environment["CUPY_CACHE_DIR"]
                                  for environment in worker_environments}), 6)
            self.assertEqual(len({environment["NUMBA_CACHE_DIR"]
                                  for environment in worker_environments}), 6)
            self.assertTrue(all(
                not any(key.startswith("RTDL_V4_FORMAL_LEAF_CACHE")
                        for key in environment)
                for environment in worker_environments))

    def test_worker_source_records_no_elapsed_value(self):
        worker_source = (ROOT / "scripts/goal5790_a1_home_worker.py").read_text(
            encoding="utf-8")
        controller_source = (
            ROOT / "scripts/goal5790_a1_home_controller.py").read_text(
                encoding="utf-8")
        for source in (worker_source, controller_source):
            self.assertNotIn("perf_counter", source)
            self.assertNotIn("time.time(", source)
        self.assertIn('"elapsed_values_recorded": False', worker_source)
        self.assertIn('"registered_performance_timing_count": 0', controller_source)

    def test_worker_exact_home_gate_is_first_and_rejects_identity_drift(self):
        authority_file_sha = controller.HOME_AUTHORITY_FILE_SHA256
        expected_machine_sha = exact_home_machine()[
            "home_machine_authority_sha256"]
        good_line = ", ".join((
            controller.HOME_GPU, controller.HOME_DRIVER,
            controller.HOME_UUID, controller.HOME_CC)) + "\n"
        completed = subprocess.CompletedProcess(
            ["nvidia-smi"], 0, good_line, "")
        with mock.patch.object(worker.platform, "node", return_value="lx1"), \
                mock.patch.object(worker.subprocess, "run", return_value=completed):
            observed = worker._query_exact_home_machine(
                expected_machine_sha, HOME_AUTHORITY_PATH, authority_file_sha)
        self.assertEqual(observed, exact_home_machine())

        for label, node, line, expected_sha in (
            ("host", "not-lx1", good_line, expected_machine_sha),
            ("gpu", "lx1", good_line.replace(
                controller.HOME_GPU, "NVIDIA RTX 4000 Ada"), expected_machine_sha),
            ("driver", "lx1", good_line.replace(
                controller.HOME_DRIVER, "999.0"), expected_machine_sha),
            ("uuid", "lx1", good_line.replace(
                controller.HOME_UUID, "GPU-attacker"), expected_machine_sha),
            ("cc", "lx1", good_line.replace(
                controller.HOME_CC, "8.9"), expected_machine_sha),
            ("authority", "lx1", good_line, "0" * 64),
        ):
            with self.subTest(label=label), \
                    mock.patch.object(worker.platform, "node", return_value=node), \
                    mock.patch.object(
                        worker.subprocess, "run",
                        return_value=subprocess.CompletedProcess(
                            ["nvidia-smi"], 0, line, "")):
                with self.assertRaises(RuntimeError):
                    worker._query_exact_home_machine(
                        expected_sha, HOME_AUTHORITY_PATH, authority_file_sha)

    def test_direct_worker_home_failure_happens_before_case_or_arm(self):
        args = Namespace(
            home_authority_sha256="0" * 64,
            home_authority_file=HOME_AUTHORITY_PATH,
            home_authority_file_sha256=controller.HOME_AUTHORITY_FILE_SHA256,
            cc="61", suite=Path("must-not-open"), case_id=CASE_IDS[0],
            arm="accepted_control")
        with mock.patch.object(
                worker, "_query_exact_home_machine",
                side_effect=RuntimeError("wrong Home authority")) as gate, \
                mock.patch.object(worker, "_case_from_suite") as case_loader:
            with self.assertRaisesRegex(RuntimeError, "wrong Home authority"):
                worker.run_worker(args)
        gate.assert_called_once()
        case_loader.assert_not_called()


if __name__ == "__main__":
    unittest.main()

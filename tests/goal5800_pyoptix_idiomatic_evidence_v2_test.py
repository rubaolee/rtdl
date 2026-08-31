from __future__ import annotations

import copy
import base64
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

from scripts import goal5800_freeze_pyoptix_idiomatic_evidence_v2 as freezer
from scripts import goal5800_build_pyoptix_execution_authority as authority_builder
from scripts import goal5800_build_execution_launch_pin as launch_pin_builder
from scripts import goal5800_verify_pyoptix_idiomatic_evidence_v2 as verifier


def identity(path: str, value: bytes) -> dict[str, object]:
    return {"path": path, "bytes": len(value), "sha256": verifier.sha256(value)}


def stage_origin_sources(target: Path) -> tuple[str, str]:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True).strip()
    tree = subprocess.check_output(
        ["git", "rev-parse", f"{commit}^{{tree}}"], text=True).strip()
    for relative in authority_builder.REQUIRED_PATHS:
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(subprocess.check_output(
            ["git", "show", f"{commit}:{relative}"]))
    return commit, tree


def current_authority_fixture() -> tuple[dict[str, object], dict[str, bytes]]:
    with tempfile.TemporaryDirectory() as temporary:
        source = Path(temporary)
        commit, tree = stage_origin_sources(source)
        document = authority_builder.build(
            source, origin_repository=Path("."),
            origin_commit=commit, origin_tree=tree)
    files = {
        f"executed_source/{row['path']}": subprocess.check_output(
            ["git", "show", f"{commit}:{row['path']}"])
        for row in document["files"]
    }
    return document, files


def operation_result() -> tuple[dict[str, object], dict[str, bytes]]:
    guard = {
        "scope": "PYTHON_VISIBLE_TASK_OWNER_EXECUTE__NOT_CUPTI_OR_DRIVER_WIDE",
        "unapproved_device_allocation_call_count": 0,
        "unapproved_pinned_host_allocation_call_count": 0,
        "unapproved_blocking_asnumpy_call_count": 0,
        "unauthorized_direct_stream_sync_count": 0,
        "complete_driver_operation_observation_claimed": False,
    }
    relation_prepare = verifier.exact_counts(
        prepare_device_allocation_call_count=11,
        prepare_pinned_host_allocation_call_count=4,
        prepare_h2d_call_count=4,
        prepare_stream_creation_count=1,
    )
    triangle_prepare = verifier.exact_counts(
        prepare_device_allocation_call_count=9,
        prepare_pinned_host_allocation_call_count=4,
        prepare_h2d_call_count=3,
        prepare_stream_creation_count=1,
    )
    relation_execute = verifier.exact_counts(
        execute_async_h2d_call_count=2,
        execute_async_d2h_call_count=2,
        execute_device_zero_fill_call_count=2,
        execute_explicit_stream_sync_call_count=2,
        execute_launch_call_count=2,
    )
    triangle_execute = verifier.exact_counts(
        execute_async_h2d_call_count=1,
        execute_async_d2h_call_count=3,
        execute_device_zero_fill_call_count=3,
        execute_explicit_stream_sync_call_count=2,
        execute_launch_call_count=1,
    )
    relation = {
        "output": [[index, index] for index in range(4096)],
        "raw_event_count": 8192,
        "device_status": 0,
        "device_overflow": 0,
        "launch_count": 2,
        "required_sync_count": 2,
        "control_d2h_bytes": 12,
        "output_d2h_bytes": 65536,
        "rows_reset_bytes": 65552,
        "control_reset_bytes": 12,
        "total_host_blocking_count": 2,
        "operation_order": [
            "rows_reset", "control_reset", "params0_h2d", "launch0",
            "params1_h2d", "launch1", "control_d2h", "status_ready_sync",
            "rows_d2h", "output_ready_sync",
        ],
        "prepare_operation_counts": relation_prepare,
        "operation_ledger_scope": verifier.OPERATION_LEDGER_SCOPE,
        "execute_operation_counts": relation_execute,
        "independent_execute_guard": guard,
    }
    triangle = {
        "per_ray": [0] * 16384,
        "weighted_sum": 65530,
        "device_status": 0,
        "launch_count": 1,
        "required_sync_count": 2,
        "status_d2h_bytes": 4,
        "per_ray_d2h_bytes": 131072,
        "weighted_d2h_bytes": 8,
        "per_ray_reset_bytes": 131072,
        "weighted_reset_bytes": 8,
        "status_reset_bytes": 4,
        "total_host_blocking_count": 2,
        "operation_order": [
            "per_ray_reset", "weighted_reset", "status_reset", "params_h2d",
            "launch", "control_d2h", "status_ready_sync", "per_ray_d2h",
            "weighted_d2h", "output_ready_sync",
        ],
        "prepare_operation_counts": triangle_prepare,
        "operation_ledger_scope": verifier.OPERATION_LEDGER_SCOPE,
        "execute_operation_counts": triangle_execute,
        "independent_execute_guard": guard,
    }
    result = {
        "relation": {
            "initial_execution": relation, "repeat_execution": copy.deepcopy(relation),
        },
        "triangle": {
            "initial_execution": triangle, "repeat_execution": copy.deepcopy(triangle),
        },
    }
    failure_witness = {
        "raw_event_count": 2, "device_overflow": 1, "device_status": 0,
        "raw_capacity": 1, "application_output_exposed": False,
        "application_output_d2h_call_count": 0,
        "operation_order": [
            "rows_reset", "control_reset", "params0_h2d", "launch0",
            "params1_h2d", "launch1", "control_d2h", "status_ready_sync",
        ],
        "execute_operation_counts": verifier.exact_counts(
            execute_async_h2d_call_count=2, execute_async_d2h_call_count=1,
            execute_device_zero_fill_call_count=2,
            execute_explicit_stream_sync_call_count=1, execute_launch_call_count=2,
        ),
        "independent_execute_guard": guard,
    }
    result["device_failure_status_before_output_witness"] = failure_witness
    arm = Path(
        "experiments/goal5800_pyoptix_owl/pyoptix_idiomatic_arm.py").read_bytes()
    baseline = Path(
        "experiments/goal5796_matched/pyoptix_baseline.py").read_bytes()
    files = {
        "executed_source/experiments/goal5800_pyoptix_owl/pyoptix_idiomatic_arm.py": arm,
        "executed_source/experiments/goal5796_matched/pyoptix_baseline.py": baseline,
    }
    source_boundary = verifier.derive_execute_source_boundary(arm)
    result["execute_source_boundary"] = source_boundary
    result["operation_ledger"] = {
        "schema": "rtdl.goal5800.pyoptix_operation_ledger.v3",
        "scope": verifier.OPERATION_LEDGER_SCOPE,
        "source_observable_wrapper_counter_keys": list(verifier.OPERATION_COUNT_KEYS),
        "execute_source_boundary": source_boundary,
        "complete_driver_operation_observation_claimed": False,
        "relation": {
            "prepare_operation_counts": relation_prepare,
            "initial": verifier.execution_projection(
                relation, ("rows_reset_bytes", "control_reset_bytes",
                           "control_d2h_bytes", "output_d2h_bytes")),
            "repeat": verifier.execution_projection(
                relation, ("rows_reset_bytes", "control_reset_bytes",
                           "control_d2h_bytes", "output_d2h_bytes")),
            "initial_repeat_exact": True,
        },
        "triangle": {
            "prepare_operation_counts": triangle_prepare,
            "initial": verifier.execution_projection(
                triangle, ("per_ray_reset_bytes", "weighted_reset_bytes",
                           "status_reset_bytes", "status_d2h_bytes",
                           "per_ray_d2h_bytes", "weighted_d2h_bytes")),
            "repeat": verifier.execution_projection(
                triangle, ("per_ray_reset_bytes", "weighted_reset_bytes",
                           "status_reset_bytes", "status_d2h_bytes",
                           "per_ray_d2h_bytes", "weighted_d2h_bytes")),
            "initial_repeat_exact": True,
        },
        "context_module_pipeline_sbt_prepare_counted": False,
        "owner_close_operation_counts_claimed": False,
        "device_failure_status_before_output_witness": failure_witness,
    }
    return result, files


def receipt_fixture() -> tuple[dict[str, object], dict[str, bytes]]:
    extension = b"native-optix-extension"
    extension_member = "optix/_optix.cpython-312-x86_64-linux-gnu.so"
    wheel_buffer = io.BytesIO()
    with zipfile.ZipFile(wheel_buffer, "w") as archive:
        archive.writestr(extension_member, extension)
    wheel = wheel_buffer.getvalue()
    source = b"pinned source\n"
    reports = {
        "install_report.json": b"{}\n",
        "virtualenv_bootstrap_install_report.json": b"{}\n",
        "pip_freeze.txt": b"pyoptix==9.1.0\n",
    }
    build = {
        "schema": "rtdl.goal5800.pyoptix_clean_wheel_build_receipt.v1",
        "status": "PASS__CLEAN_SOURCE_TO_WHEEL_BUILD__UNTIMED",
        "transaction_kind": "build_provenance_not_performance",
        "registered_performance_timing_count": 0,
        "pyoptix_source": {
            "commit": verifier.PYOPTIX_COMMIT, "tree": verifier.PYOPTIX_TREE,
            "archive_projection_file_count": 1,
            "archive_projection_files": [identity("a.py", source)],
        },
        "optix_headers": {
            "commit": "fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd",
            "tree": "c30f1b41cb64f6cba6290d7ad82686cc84922267",
            "api_macro": 90000, "root": "/headers",
        },
        "build": {
            "python": "/python", "python_version": "3.12.3",
            "cmake_args": "-D", "pip": "25", "scikit_build_core": "0.11",
            "pybind11": "3", "ninja": "1", "cmake": {}, "cxx": {}, "nvcc": {},
            "command_file": "logs/build_command.shell",
            "stdout_file": "logs/build_stdout.txt",
            "stderr_file": "logs/build_stderr.txt", "exit_code": 0,
        },
        "wheel": {
            "path": "wheelhouse/pyoptix-9.1.0.whl", "bytes": len(wheel),
            "sha256": verifier.sha256(wheel), "extension_member": extension_member,
            "extension_bytes": len(extension), "extension_sha256": verifier.sha256(extension),
        },
    }
    distributions = {
        name: {"canonical_name": name, "version": version}
        for name, version in {
            "pyoptix": "9.1.0", "numpy": "2.4.4", "cupy-cuda12x": "14.0.1",
            "cuda-python": "12.9.7", "cuda-bindings": "12.9.7",
            "cuda-pathfinder": "1.6.1",
        }.items()
    }
    install = {
        "schema": "rtdl.goal5800.pyoptix_clean_install_receipt.v1",
        "status": "PASS__FRESH_VENV__CLEAN_BUILT_EXTENSION_LOADED__UNTIMED",
        "transaction_kind": "installation_and_import_not_performance",
        "registered_performance_timing_count": 0,
        "python": {"executable": "/clean/bin/python", "version": "3.12.3"},
        "wheel": {"path": "/build/pyoptix.whl", "bytes": len(wheel),
                  "sha256": verifier.sha256(wheel)},
        "loaded_optix_package_initializer": {
            "path": "/clean/optix/__init__.py", "bytes": 1,
            "sha256": verifier.sha256(b"i"),
        },
        "loaded_optix_extension": {
            "module": "optix._optix", "path": f"/clean/site/{extension_member}",
            "bytes": len(extension), "sha256": verifier.sha256(extension),
        },
        "optix_api_version": "9.0.0", "cupy_device_name": "GPU",
        "numpy_version": "2.4.4", "distributions": distributions,
    }
    for name, value in reports.items():
        key = ({"install_report.json": "install_report",
                "virtualenv_bootstrap_install_report.json":
                    "virtualenv_bootstrap_install_report",
                "pip_freeze.txt": "pip_freeze"})[name]
        install[key] = identity(name, value)
    build_bytes = json.dumps(build, sort_keys=True).encode()
    install_bytes = json.dumps(install, sort_keys=True).encode()
    wheel_identity = identity("/build/pyoptix.whl", wheel)
    extension_identity = identity(f"/clean/site/{extension_member}", extension)
    result = {
        "pyoptix_source_authority_identity": {
            "path": "/source", "commit": verifier.PYOPTIX_COMMIT,
            "tree": verifier.PYOPTIX_TREE, "status_porcelain": "", "clean": True,
        },
        "loaded_optix_extension": {
            "module": "optix._optix", "source_path": extension_member,
            "distribution_path": f"/clean/site/{extension_member}",
            "bytes": len(extension), "sha256": verifier.sha256(extension),
        },
        "pyoptix_install_provenance": {
            "wheel_build_receipt": {
                "file": identity("/build/build_receipt.json", build_bytes),
                "document": build, "wheel_identity": wheel_identity,
                "wheel_sha256": verifier.sha256(wheel),
                "extension_sha256": verifier.sha256(extension),
                "optix_headers_root": "/headers",
            },
            "clean_install_receipt": {
                "file": identity("/install/clean_install_receipt.json", install_bytes),
                "document": install, "wheel_identity": wheel_identity,
                "wheel_sha256": verifier.sha256(wheel),
                "extension_identity": extension_identity,
                "extension_sha256": verifier.sha256(extension),
            },
            "built_wheel_equals_installed_wheel": True,
            "receipt_extensions_equal_loaded_extension": True,
        },
    }
    files = {
        "provenance/clean_build/source/a.py": source,
        "provenance/clean_build/logs/build_command.shell": b"build\n",
        "provenance/clean_build/logs/build_stdout.txt": b"ok\n",
        "provenance/clean_build/logs/build_stderr.txt": b"",
        "provenance/clean_build/wheelhouse/pyoptix-9.1.0.whl": wheel,
        "provenance/clean_build/build_receipt.json": build_bytes,
        "provenance/clean_install/clean_install_receipt.json": install_bytes,
    }
    files.update({f"provenance/clean_install/{name}": value
                  for name, value in reports.items()})
    return result, files


class Goal5800V2VerifierTest(unittest.TestCase):
    def test_git_membership_rejects_coherently_resealed_nonorigin_blob(self) -> None:
        document, files = current_authority_fixture()
        verifier.verify_git_membership_proof(document, files, document["files"])
        forged = copy.deepcopy(document)
        row = forged["files"][0]
        payload_name = f"executed_source/{row['path']}"
        files[payload_name] += b"\ncoherent-forgery\n"
        row["bytes"] = len(files[payload_name])
        row["sha256"] = verifier.sha256(files[payload_name])
        row["git_blob_sha1"] = verifier._git_object_id("blob", files[payload_name])
        forged["files_sha256"] = verifier.sha256(verifier.canonical(forged["files"]))
        with self.assertRaisesRegex(RuntimeError, "origin-tree membership"):
            verifier.verify_git_membership_proof(forged, files, forged["files"])

    def test_git_membership_rejects_unused_tree_node(self) -> None:
        document, files = current_authority_fixture()
        forged = copy.deepcopy(document)
        forged["git_membership_proof"]["tree_nodes"].append(copy.deepcopy(
            forged["git_membership_proof"]["tree_nodes"][-1]))
        with self.assertRaisesRegex(RuntimeError, "unused nodes"):
            verifier.verify_git_membership_proof(forged, files, forged["files"])

    def test_git_membership_rejects_commit_object_byte_mutation(self) -> None:
        document, files = current_authority_fixture()
        forged = copy.deepcopy(document)
        commit = forged["git_membership_proof"]["commit_object"]
        raw = base64.b64decode(commit["base64"])
        commit["base64"] = base64.b64encode(raw + b"x").decode("ascii")
        commit["bytes"] += 1
        with self.assertRaisesRegex(RuntimeError, "identity mismatch"):
            verifier.verify_git_membership_proof(forged, files, forged["files"])

    def test_empty_optix_metadata_mapping_requires_exact_record_ownership(self) -> None:
        extension_path = "optix/_optix.cpython-312-x86_64-linux-gnu.so"
        paths = [
            "optix/__init__.py",
            extension_path,
            "pyoptix-9.1.0.dist-info/METADATA",
            "pyoptix-9.1.0.dist-info/RECORD",
        ]
        paths.sort()
        record = "".join(f"{path},,\n" for path in paths).encode()
        values = {
            "optix/__init__.py": b"from ._optix import *\n",
            extension_path: b"native-extension",
            "pyoptix-9.1.0.dist-info/METADATA": (
                b"Metadata-Version: 2.1\nName: pyoptix\nVersion: 9.1.0\n"),
            "pyoptix-9.1.0.dist-info/RECORD": record,
        }
        installed_rows = [identity(path, values[path]) for path in paths]
        files = {
            f"installed_distribution/{path}": value
            for path, value in values.items()
        }
        proof = verifier.verify_pyoptix_record_ownership(files, installed_rows)
        self.assertEqual(proof["distribution"], "pyoptix")
        self.assertEqual(proof["native_extension_path"], extension_path)
        tampered = copy.deepcopy(installed_rows)
        tampered.pop(0)
        with self.assertRaisesRegex(RuntimeError, "does not own"):
            verifier.verify_pyoptix_record_ownership(files, tampered)

    def test_preexecution_authority_binds_four_exact_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            commit, tree = stage_origin_sources(source)
            document = authority_builder.build(
                source, origin_repository=Path("."),
                origin_commit=commit, origin_tree=tree)
        self.assertEqual(
            [row["path"] for row in document["files"]],
            list(verifier.REQUIRED_EXECUTED_SOURCE_PATHS))
        self.assertEqual(document["file_count"], 4)
        self.assertEqual(
            document["files_sha256"],
            verifier.sha256(verifier.canonical(document["files"])))

    def test_preexecution_authority_rejects_archived_source_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            commit, tree = stage_origin_sources(source)
            document = authority_builder.build(
                source, origin_repository=Path("."),
                origin_commit=commit, origin_tree=tree)
        authority_bytes = (
            json.dumps(document, indent=2, sort_keys=True).encode("utf-8") + b"\n")
        with tempfile.TemporaryDirectory() as pin_temporary:
            authority_path = Path(pin_temporary) / "authority.json"
            authority_path.write_bytes(authority_bytes)
            pin_document = launch_pin_builder.build(authority_path)
        pin_bytes = (
            json.dumps(pin_document, indent=2, sort_keys=True).encode("utf-8") + b"\n")
        files = {
            f"executed_source/{row['path']}": subprocess.check_output(
                ["git", "show", f"{commit}:{row['path']}"])
            for row in document["files"]
        }
        files["provenance/execution_authority.json"] = authority_bytes
        files["provenance/execution_launch_pin.json"] = pin_bytes
        result = {"executed_source_authority": {
            "file": identity("execution_authority.json", authority_bytes),
            "document": document,
            "launch_pin": {
                "file": identity("execution_launch_pin.json", pin_bytes),
                "document": pin_document,
            },
        }}
        environment = {"executed_sources": [
            {"path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"]}
            for row in document["files"]
        ]}
        verifier.verify_execution_authority(result, files, environment)
        first_source = f"executed_source/{document['files'][0]['path']}"
        files[first_source] += b"\n// unauthorized post-freeze mutation\n"
        with self.assertRaisesRegex(RuntimeError, "authority differs"):
            verifier.verify_execution_authority(result, files, environment)

    def test_exact_operation_projection_passes(self) -> None:
        result, files = operation_result()
        self.assertEqual(verifier.verify_operation_ledger(result, files), 4)

    def test_static_source_boundary_accepts_exact_crlf_encoding(self) -> None:
        _, files = operation_result()
        crlf_files = {
            name: value.replace(b"\n", b"\r\n")
            if name.endswith(".py") else value
            for name, value in files.items()
        }
        verifier.verify_static_operation_sources(crlf_files)

    def test_execute_allocation_counter_is_rejected(self) -> None:
        result, files = operation_result()
        result["relation"]["initial_execution"][
            "execute_operation_counts"]["execute_device_allocation_call_count"] = 1
        with self.assertRaisesRegex(RuntimeError, "exact operation counts"):
            verifier.verify_operation_ledger(result, files)

    def test_sync_undercount_is_rejected(self) -> None:
        result, files = operation_result()
        result["triangle"]["initial_execution"][
            "execute_operation_counts"]["execute_explicit_stream_sync_call_count"] = 1
        with self.assertRaisesRegex(RuntimeError, "exact operation counts"):
            verifier.verify_operation_ledger(result, files)

    def test_missing_output_d2h_is_rejected(self) -> None:
        result, files = operation_result()
        result["relation"]["initial_execution"][
            "execute_operation_counts"]["execute_async_d2h_call_count"] = 1
        with self.assertRaisesRegex(RuntimeError, "exact operation counts"):
            verifier.verify_operation_ledger(result, files)

    def test_failure_witness_output_exposure_is_rejected(self) -> None:
        result, files = operation_result()
        result["device_failure_status_before_output_witness"][
            "application_output_exposed"] = True
        with self.assertRaisesRegex(RuntimeError, "exposed"):
            verifier.verify_operation_ledger(result, files)

    def test_blocking_asnumpy_source_is_rejected(self) -> None:
        result, files = operation_result()
        arm_path = next(path for path in files if path.endswith("pyoptix_idiomatic_arm.py"))
        files[arm_path] += b"\ncp.asnumpy(x)\n"
        with self.assertRaisesRegex(RuntimeError, "cp.asnumpy"):
            verifier.verify_operation_ledger(result, files)

    def test_coherently_resealed_execute_helper_escape_is_rejected(self) -> None:
        arm = Path(
            "experiments/goal5800_pyoptix_owl/pyoptix_idiomatic_arm.py").read_bytes()
        signature = b"    def _execute_observed(self) -> dict[str, Any]:\n"
        self.assertIn(signature, arm)
        mutated = arm.replace(
            signature, signature + b"        self.cheat()\n", 1)
        with self.assertRaisesRegex(RuntimeError, "executed source boundary mismatch"):
            verifier.derive_execute_source_boundary(mutated)

    def test_loaded_extension_fields_are_not_swappable(self) -> None:
        extension_bytes = b"native-extension"
        relative = "optix/_optix.cpython-312-x86_64-linux-gnu.so"
        absolute = f"/clean/venv/site-packages/{relative}"
        result = {"loaded_optix_extension": {
            "module": "optix._optix", "source_path": relative,
            "distribution_path": absolute, "bytes": len(extension_bytes),
            "sha256": verifier.sha256(extension_bytes),
        }}
        files = {f"installed_distribution/{relative}": extension_bytes}
        rows = [verifier.digest_row(relative, extension_bytes)]
        environment = {"dynamic_dependencies": {
            "subject_sha256": verifier.sha256(extension_bytes),
            "rows": [{
                "observation": "PROCESS_MAP", "resolved_path": absolute,
                "sha256": verifier.sha256(extension_bytes),
            }],
        }}
        verifier.verify_loaded_extension(result, files, rows, environment)
        swapped = copy.deepcopy(result)
        swapped["loaded_optix_extension"]["source_path"] = absolute
        swapped["loaded_optix_extension"]["distribution_path"] = relative
        with self.assertRaises(RuntimeError):
            verifier.verify_loaded_extension(swapped, files, rows, environment)

    def test_nested_clean_build_install_receipt_chain_passes(self) -> None:
        result, files = receipt_fixture()
        verifier.verify_receipt_chain(result, files)

    def test_build_projections_derive_generated_rows_without_hardcoded_count(self) -> None:
        prebuild_rows = [
            identity(f"src/prebuild_{index:02d}.py", f"p{index}\n".encode())
            for index in range(42)
        ]
        generated_rows = [
            identity(f"build/generated_{index}.cpp", f"g{index}\n".encode())
            for index in range(2)
        ]
        source_rows = sorted(prebuild_rows + generated_rows,
                             key=lambda row: str(row["path"]))
        wheel_buffer = io.BytesIO()
        with zipfile.ZipFile(wheel_buffer, "w") as archive:
            for index in range(7):
                archive.writestr(f"wheel/member_{index}", f"w{index}\n".encode())
        wheel_bytes = wheel_buffer.getvalue()
        wheel_rows = []
        with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as archive:
            for name in sorted(archive.namelist()):
                wheel_rows.append(identity(name, archive.read(name)))
        installed_rows = [
            identity(f"optix/installed_{index}", f"i{index}\n".encode())
            for index in range(11)
        ]
        result = {"pyoptix_install_provenance": {"wheel_build_receipt": {
            "document": {
                "pyoptix_source": {"archive_projection_files": source_rows},
                "wheel": {
                    "path": "wheelhouse/test.whl", "bytes": len(wheel_bytes),
                    "sha256": verifier.sha256(wheel_bytes),
                },
            },
        }}}
        projection = {
            "upstream_prebuild_source": {
                "projection_kind": "COMPLETE_PINNED_GIT_TREE",
                "file_count": len(prebuild_rows),
                "files_sha256": verifier.sha256(verifier.canonical(prebuild_rows)),
                "files": prebuild_rows, "payload_bytes_embedded": True,
            },
            "postbuild_generated_source_tree_files": {
                "projection_kind": (
                    "SET_DIFFERENCE_POSTBUILD_RECEIPT_MINUS_PINNED_GIT_TREE"),
                "file_count": len(generated_rows),
                "files_sha256": verifier.sha256(verifier.canonical(generated_rows)),
                "files": generated_rows, "payload_bytes_embedded": True,
            },
            "postbuild_complete_source_tree": {
                "projection_kind": (
                    "COMPLETE_BUILD_RECEIPT_SOURCE_TREE_AFTER_WHEEL_BUILD"),
                "file_count": len(source_rows),
                "files_sha256": verifier.sha256(verifier.canonical(source_rows)),
                "payload_bytes_embedded": True,
            },
            "wheel_postbuild": {
                "projection_kind": "COMPLETE_CLEAN_BUILT_WHEEL_REGULAR_MEMBERS",
                "file_count": len(wheel_rows),
                "files_sha256": verifier.sha256(verifier.canonical(wheel_rows)),
                "wheel_bytes_embedded": True,
            },
            "clean_installed_distribution": {
                "projection_kind": "COMPLETE_IMPORTLIB_METADATA_DISTRIBUTION_FILES",
                "file_count": len(installed_rows),
                "files_sha256": verifier.sha256(verifier.canonical(installed_rows)),
                "payload_bytes_embedded": True,
            },
            "projections_are_not_interchangeable": True,
        }
        environment = {"pyoptix_build_projections": projection}
        files = {"provenance/clean_build/wheelhouse/test.whl": wheel_bytes}
        verifier.verify_build_projections(result, environment, files, installed_rows)
        projection["postbuild_generated_source_tree_files"]["file_count"] = 30
        with self.assertRaisesRegex(RuntimeError, "absent, conflated, or overstated"):
            verifier.verify_build_projections(result, environment, files, installed_rows)

    def test_receipt_extension_drift_is_rejected(self) -> None:
        result, files = receipt_fixture()
        result["pyoptix_install_provenance"]["clean_install_receipt"][
            "extension_sha256"] = "0" * 64
        with self.assertRaisesRegex(RuntimeError, "receipt projection"):
            verifier.verify_receipt_chain(result, files)

    def test_v1_archive_is_intentionally_rejected_by_v2(self) -> None:
        archive = Path(
            "history/internal_docs/goal5800_pyoptix_idiomatic_untimed_evidence_20260824/"
            "goal5800_pyoptix_idiomatic_untimed_evidence.tar.gz")
        if not archive.is_file():
            self.skipTest("frozen v1 archive is absent")
        with self.assertRaisesRegex(RuntimeError, "legacy or unknown evidence manifest"):
            verifier.verify(archive)

    def test_freezer_path_and_role_classification(self) -> None:
        with self.assertRaises(RuntimeError):
            freezer.safe_relative("../escape")
        extension = Path("/x/optix/_optix.cpython-312-x86_64-linux-gnu.so")
        self.assertEqual(freezer.classify_loaded_role(extension, extension),
                         "optix_extension")
        self.assertEqual(
            freezer.classify_loaded_role(Path("/usr/lib/libnvrtc.so.12"), extension),
            "nvrtc")
        self.assertIsNone(
            freezer.classify_loaded_role(
                Path("/x/cupy/_core/_kernel.cpython-312-x86_64-linux-gnu.so"),
                extension))


if __name__ == "__main__":
    unittest.main()

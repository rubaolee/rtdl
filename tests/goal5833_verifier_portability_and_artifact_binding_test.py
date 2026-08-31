"""Focused regressions for Goal5833 evidence portability and byte bridges."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "goal5833_portable_verifier",
    ROOT / "scripts" / "goal5833_verify_home_builtin_sphere.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Goal5833 verifier cannot be loaded")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _execution_records(path: str):
    traversal = {"provider_library_path": path}
    physical = {
        "authorized_native_library_path": path,
        "loaded_native_library_path": path,
    }
    return traversal, physical


class Goal5833VerifierPortabilityAndArtifactBindingTest(unittest.TestCase):
    def test_original_execution_paths_agree_without_preserved_path_equality(self):
        original = "/original/home/build/librtdl_optix.so"
        traversal, physical = _execution_records(original)
        # The preserved artifact may live anywhere; it is deliberately absent
        # from this original-run consistency check and is SHA-bound by verify().
        VERIFIER._verify_execution_native_binding(
            original, traversal, physical, label="primary")

        for owner, key in (
            (traversal, "provider_library_path"),
            (physical, "authorized_native_library_path"),
            (physical, "loaded_native_library_path"),
        ):
            with self.subTest(key=key):
                hostile_traversal, hostile_physical = _execution_records(original)
                target = hostile_traversal if owner is traversal else hostile_physical
                target[key] = "/different/provider.so"
                with self.assertRaisesRegex(RuntimeError, "paths differ"):
                    VERIFIER._verify_execution_native_binding(
                        original, hostile_traversal, hostile_physical,
                        label="primary")

    def test_artifact_manifest_rehashes_every_member_and_returns_identities(self):
        names = {
            "callback_source.py", "wrapper.cu", "wrapper.ptx", "composed.ptx",
            "nvrtc.log",
            "compiler_options.json",
            "leaf_0_make_ray.py", "leaf_1_closest_hit.py",
            "leaf_2_miss.py", "leaf_3_finalize.py",
            "leaf_0_make_ray.ptx", "leaf_1_closest_hit.ptx",
            "leaf_2_miss.ptx", "leaf_3_finalize.ptx",
        }
        with tempfile.TemporaryDirectory() as temporary:
            artifact_root = Path(temporary)
            root = artifact_root / "accepted"
            root.mkdir()
            members = []
            for name in sorted(names):
                body = ("bytes-for:" + name).encode("utf-8")
                (root / name).write_bytes(body)
                members.append({
                    "path": name,
                    "size": len(body),
                    "sha256": hashlib.sha256(body).hexdigest(),
                })
            manifest = {
                "schema": "rtdl.goal5833.generated_executable_artifacts.v1",
                "executable_sha256": "e" * 64,
                "member_count": len(members),
                "members": members,
            }
            manifest_bytes = (
                json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8")
            (root / "manifest.json").write_bytes(manifest_bytes)
            record = {
                "subdirectory": "accepted",
                "executable_sha256": "e" * 64,
                "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                "member_count": len(members),
                "members": members,
            }
            observed = VERIFIER._verify_artifact_set(artifact_root, record)
            self.assertEqual(set(observed), names)
            self.assertEqual(
                observed["wrapper.cu"],
                hashlib.sha256(b"bytes-for:wrapper.cu").hexdigest())

    def test_wrapper_and_composed_ptx_are_directly_bound_to_result_fields(self):
        wrapper = hashlib.sha256(b"wrapper").hexdigest()
        accepted_ptx = hashlib.sha256(b"accepted-ptx").hexdigest()
        hostile_ptx = hashlib.sha256(b"hostile-ptx").hexdigest()
        result = {
            "source_sha256": hashlib.sha256(b"accepted-source").hexdigest(),
            "wrapper_source_sha256": wrapper,
            "composed_ptx_sha256": accepted_ptx,
        }
        hostile = {
            "source_sha256": hashlib.sha256(b"hostile-source").hexdigest(),
            "wrapper_source_sha256": wrapper,
            "composed_ptx_sha256": hostile_ptx,
        }
        accepted_members = {
            "callback_source.py": result["source_sha256"],
            "wrapper.cu": wrapper, "composed.ptx": accepted_ptx}
        hostile_members = {
            "callback_source.py": hostile["source_sha256"],
            "wrapper.cu": wrapper, "composed.ptx": hostile_ptx}
        VERIFIER._verify_artifact_bridges(
            result, hostile, accepted_members, hostile_members)

        for side, key in (
            ("accepted", "wrapper.cu"),
            ("accepted", "composed.ptx"),
            ("hostile", "wrapper.cu"),
            ("hostile", "composed.ptx"),
        ):
            with self.subTest(member=key, side=side):
                accepted = dict(accepted_members)
                hostile_set = dict(hostile_members)
                (accepted if side == "accepted" else hostile_set)[key] = "0" * 64
                with self.assertRaises(RuntimeError):
                    VERIFIER._verify_artifact_bridges(
                        result, hostile, accepted, hostile_set)

    def test_full_compiler_identity_rederives_from_projections_and_member_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            artifact_root = Path(temporary)
            root = artifact_root / "accepted"
            root.mkdir()
            roles = ("make_ray", "closest_hit", "miss", "finalize")
            payloads = {
                "callback_source.py": b"public callback source",
                "wrapper.cu": b"wrapper-source",
                "wrapper.ptx": b"wrapper-ptx",
                "composed.ptx": b"composed-ptx",
                "nvrtc.log": b"",
                "compiler_options.json": b'["--std=c++14"]\n',
            }
            for index, role in enumerate(roles):
                payloads[f"leaf_{index}_{role}.py"] = (
                    "source:" + role).encode("ascii")
                payloads[f"leaf_{index}_{role}.ptx"] = (
                    "ptx:" + role).encode("ascii")
            member_sha = {}
            for name, body in payloads.items():
                (root / name).write_bytes(body)
                member_sha[name] = hashlib.sha256(body).hexdigest()

            program = {
                "schema_id": "test",
                "schema_version": "v1",
                "manifest": {},
                "records": [],
                "functions": [{
                    "name": "finalize",
                    "body": [{
                        "kind": "return_effect",
                        "effect": {"kind": "output", "fields": {}},
                    }],
                }],
                "normalized_source": "return output\n",
                "source_sha256": hashlib.sha256(
                    b"return output\n").hexdigest(),
            }
            ir_projection = dict(program)
            ir_projection.pop("normalized_source")
            ir_projection.pop("source_sha256")
            ir_sha = _canonical_digest(ir_projection)
            effect_sha = _canonical_digest([["finalize", ["output"]]])
            schema = {"schema_id": "sphere-test", "field": "closed"}
            target = {"provider": "optix-test", "native_sha256": "a" * 64}
            schema_sha = _canonical_digest(schema)
            target_sha = _canonical_digest(target)
            nonce = _canonical_digest({
                "kind": "builtin_sphere_physical_authority_v1",
                "callback": ir_sha,
                "effect": effect_sha,
                "schema": schema_sha,
                "target": target_sha,
            })
            plan = {
                "template_id": "test",
                "schema_sha256": schema_sha,
                "callback_ir_sha256": ir_sha,
                "effect_digest": effect_sha,
                "target_sha256": target_sha,
                "authority_nonce": nonce,
                "executable": False,
            }
            plan_sha = _canonical_digest(plan)
            abi = {"schema_id": "abi-test", "roles": []}
            abi_sha = _canonical_digest(abi)
            abi["abi_sha256"] = abi_sha
            authority = {
                "callback_ir_sha256": ir_sha,
                "callback_effect_digest": effect_sha,
                "schema_sha256": schema_sha,
                "target_sha256": target_sha,
                "authority_nonce": nonce,
            }
            authority_sha = _canonical_digest(authority)
            executable = {
                "schema": "rtdl.v4.verified_sphere_executable.v1",
                "authority_sha256": authority_sha,
                "plan_sha256": plan_sha,
                "abi_sha256": abi_sha,
                "wrapper_source_sha256": member_sha["wrapper.cu"],
                "wrapper_ptx_sha256": member_sha["wrapper.ptx"],
                "generated_leaf_sha256": [
                    member_sha[f"leaf_{index}_{role}.py"]
                    for index, role in enumerate(roles)],
                "compiled_leaf_sha256": [
                    member_sha[f"leaf_{index}_{role}.ptx"]
                    for index, role in enumerate(roles)],
                "composed_ptx_sha256": member_sha["composed.ptx"],
                "compiler_options": ["--std=c++14"],
                "nvrtc_log_sha256": member_sha["nvrtc.log"],
            }
            executable_sha = _canonical_digest(executable)
            identity = {
                "schema": "rtdl.goal5833.sphere_compiler_identity_projection.v1",
                "callback_program": program,
                "public_source_sha256": member_sha["callback_source.py"],
                "verified_callback": {
                    "ir_sha256": ir_sha, "effect_digest": effect_sha},
                "physical_schema": schema,
                "target": target,
                "canonical_plan": plan,
                "callback_abi": abi,
                "authority": authority,
                "authority_sha256": authority_sha,
                "executable_record": executable,
            }
            record = {
                "subdirectory": "accepted",
                "compiler_identity": identity,
                "executable_sha256": executable_sha,
            }
            scientific = {
                "source_sha256": member_sha["callback_source.py"],
                "callback_ir_sha256": ir_sha,
                "callback_effect_digest": effect_sha,
                "physical_schema_sha256": schema_sha,
                "target_sha256": target_sha,
                "canonical_plan_sha256": plan_sha,
                "callback_abi_sha256": abi_sha,
                "authority_sha256": authority_sha,
                "executable_sha256": executable_sha,
            }
            VERIFIER._verify_compiler_identity(
                artifact_root, record, scientific, member_sha)

            mutated = dict(scientific)
            mutated["callback_ir_sha256"] = "0" * 64
            with self.assertRaisesRegex(RuntimeError, "Callback IR"):
                VERIFIER._verify_compiler_identity(
                    artifact_root, record, mutated, member_sha)
            mutated_members = dict(member_sha)
            mutated_members["composed.ptx"] = "0" * 64
            with self.assertRaisesRegex(RuntimeError, "executable record"):
                VERIFIER._verify_compiler_identity(
                    artifact_root, record, scientific, mutated_members)


if __name__ == "__main__":
    unittest.main()

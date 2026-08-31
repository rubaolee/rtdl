from __future__ import annotations

import dataclasses
import json
import pathlib
import tempfile
import unittest

from rtdsl.v4_callback_artifact_cache import (
    CallbackArtifactCacheError,
    V4CallbackProviderKey,
    load_callback_artifact,
    materialize_callback_artifact,
)


ROLES = (
    "bounds", "make_ray", "intersection", "any_hit",
    "closest_hit", "miss", "finalize",
)


def key() -> V4CallbackProviderKey:
    return V4CallbackProviderKey(
        callback_ir_sha256="1" * 64,
        callback_abi_sha256="2" * 64,
        generated_source_sha256_by_role=tuple(
            (role, f"{index + 3:x}" * 64) for index, role in enumerate(ROLES)),
        leaf_ptx_sha256_by_role=tuple(
            (role, f"{index + 10:x}"[0] * 64) for index, role in enumerate(ROLES)),
        wrapper_source_sha256="a" * 64,
        wrapper_template="trusted_optix_wrapper_v1",
        physical_template="tested_analytic_sphere_nearest_search_v1",
        payload_layout_sha256="b" * 64,
        attribute_layout_sha256="c" * 64,
        sbt_layout_sha256="d" * 64,
        native_provider_sha256="e" * 64,
        target_compute_capability=(6, 1),
        python_version="3.12.3",
        numba_version="0.65.1",
        numpy_version="2.4.4",
        llvmlite_version="0.48.0",
        cuda_toolkit_version="13.0",
        optix_sdk_version="9.0.0",
        ptx_isa="8.0",
        wrapper_numeric_policy="strict",
        leaf_numeric_policy="strict",
        composer_schema="rtdl.v4.composed_callback_ptx.v1",
        compile_options=("--std=c++14", "--gpu-architecture=compute_61"),
        link_options=("max_trace_depth=1", "payload_values=10"),
    )


class Goal5751CallbackArtifactCacheTest(unittest.TestCase):
    def test_materialize_then_exact_hit_is_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            first = materialize_callback_artifact(
                directory, key(), composed_ptx=".version 8.0\n",
                construction_receipt={"leaf_count": 7, "externals": []},
            )
            second = materialize_callback_artifact(
                directory, key(), composed_ptx=".version 8.0\n",
                construction_receipt={"leaf_count": 7, "externals": []},
            )
            self.assertFalse(first.cache_hit)
            self.assertTrue(second.cache_hit)
            self.assertEqual(first.provider_identity, second.provider_identity)
            self.assertEqual(first.artifact_manifest_sha256, second.artifact_manifest_sha256)
            self.assertTrue(first.provider_identity.startswith("rtdl.v4.generated_provider."))

    def test_every_load_bearing_key_class_changes_provider_identity(self):
        baseline = key()
        variants = (
            dataclasses.replace(baseline, callback_ir_sha256="f" * 64),
            dataclasses.replace(baseline, wrapper_source_sha256="f" * 64),
            dataclasses.replace(baseline, target_compute_capability=(8, 9)),
            dataclasses.replace(baseline, numba_version="0.66.0"),
            dataclasses.replace(baseline, optix_sdk_version="8.1.0"),
            dataclasses.replace(baseline, compile_options=("--std=c++14",)),
            dataclasses.replace(baseline, native_provider_sha256="f" * 64),
        )
        self.assertEqual(len({baseline.key_sha256, *(item.key_sha256 for item in variants)}), 8)

    def test_ptx_receipt_and_extra_member_mutations_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            current = key()
            materialize_callback_artifact(
                directory, current, composed_ptx=".version 8.0\n",
                construction_receipt={"leaf_count": 7},
            )
            root = pathlib.Path(directory) / current.key_sha256
            (root / "composed.ptx").write_text("tampered")
            with self.assertRaises(CallbackArtifactCacheError) as caught:
                load_callback_artifact(directory, current)
            self.assertEqual(caught.exception.code, "cache_ptx_hash")

            (root / "composed.ptx").write_text(".version 8.0\n")
            (root / "unexpected").write_text("x")
            with self.assertRaises(CallbackArtifactCacheError) as caught:
                load_callback_artifact(directory, current)
            self.assertEqual(caught.exception.code, "cache_membership")

    def test_key_replay_and_collision_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            current = key()
            materialize_callback_artifact(
                directory, current, composed_ptx=".version 8.0\n",
                construction_receipt={"leaf_count": 7},
            )
            with self.assertRaises(CallbackArtifactCacheError) as caught:
                materialize_callback_artifact(
                    directory, current, composed_ptx=".version 8.1\n",
                    construction_receipt={"leaf_count": 7},
                )
            self.assertEqual(caught.exception.code, "cache_collision")

            root = pathlib.Path(directory) / current.key_sha256
            manifest_path = root / "artifact.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["provider_key_sha256"] = "0" * 64
            manifest_path.write_text(json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n")
            with self.assertRaises(CallbackArtifactCacheError) as caught:
                load_callback_artifact(directory, current)
            self.assertEqual(caught.exception.code, "cache_key_replay")

    def test_role_omission_and_application_identity_have_no_admission_path(self):
        with self.assertRaises(CallbackArtifactCacheError):
            dataclasses.replace(
                key(), generated_source_sha256_by_role=key().generated_source_sha256_by_role[:-1])
        fields = {field.name for field in dataclasses.fields(V4CallbackProviderKey)}
        self.assertNotIn("application", fields)
        self.assertNotIn("publication", fields)
        self.assertNotIn("candidate_name", fields)


if __name__ == "__main__":
    unittest.main()

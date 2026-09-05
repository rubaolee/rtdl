import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.goal5842_causal_admission.contracts import RELATION_TASK
from experiments.goal5842_causal_admission.tasks import build_task
from rtdsl.v4_generic_family_lifecycle import (
    FAMILY_DEPLOYMENT_FORMAT_RTDLEXE_V2,
)
from rtdsl.v4_rtdlexe import (
    RTDLExecutableBuildRoots,
    RTDLExecutableError,
    build_family_rtdlexe,
    install_rtdlexe_deployment,
    load_rtdlexe,
)
import rtdsl.v4_rtdlexe as runtime_module
from scripts.goal5801_rtdlexe_trust import create_root, freeze
from tests.goal5801_rtdlexe_runtime_test import (
    _MappingObject,
    _candidate,
    _digest,
    _native_descriptor,
)


ROOT = Path(__file__).resolve().parents[1]


class Goal5847FamilyRTDLExecutablePublicRouteTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.artifacts = self.root / "artifacts"
        self.artifacts.mkdir()
        self.old_materialized, self.declaration, self.projection = _candidate(
            "goal5847-family", "goal5847-family-slot"
        )
        for name, value in self.old_materialized.identity.to_dict().items():
            setattr(self.old_materialized.identity, name, value)
        task = build_task(RELATION_TASK)
        self.route = task.route_factory()
        self.route.provider._materializer = (  # type: ignore[attr-defined]
            lambda _target, _toolchain: self.old_materialized
        )
        self.materialized = self.route.compile().materialize(
            target=self.old_materialized._target,
            toolchain=self.old_materialized._toolchain,
        )
        self.roots = RTDLExecutableBuildRoots(
            llvmlite_version="0.44.0",
            cuda_toolkit_version="12.8",
            link_options=("max_trace_depth=1", "debug=none"),
        )

    def tearDown(self):
        self.temporary.cleanup()

    def _build(self):
        authority = self.root / "family.authority.json"
        with patch(
            "rtdsl.v4_callback_lifecycle._declared_protocol_contract",
            return_value=_MappingObject(self.declaration),
        ), patch(
            "rtdsl.v4_callback_lifecycle._compiled_protocol_projection",
            return_value=_MappingObject(self.projection),
        ), patch(
            "rtdsl.v4_rtdlexe._build_native_producer_descriptor",
            return_value=_native_descriptor(),
        ):
            built = build_family_rtdlexe(
                self.materialized,
                artifact_directory=self.artifacts,
                authority_path=authority,
                build_roots=self.roots,
                deployment_id="goal5847-family-slot",
            )
        return built

    def test_public_family_build_sign_install_and_load_binds_family_identity(self):
        built = self._build()
        artifact = json.loads(built.artifact_path.read_text(encoding="utf-8"))
        authority = json.loads(built.authority_path.read_text(encoding="utf-8"))
        binding = artifact["product_projection"]["generic_family_binding"]
        self.assertEqual(artifact["schema"], "rtdl.v4.rtdlexe.v2")
        self.assertEqual(artifact["format_version"], 2)
        self.assertEqual(
            binding["format_id"], FAMILY_DEPLOYMENT_FORMAT_RTDLEXE_V2
        )
        self.assertEqual(
            binding["family_executable_identity"]["identity_sha256"],
            self.materialized.identity.identity_sha256,
        )
        self.assertEqual(
            authority["family_executable_identity_sha256"],
            self.materialized.identity.identity_sha256,
        )
        self.assertEqual(
            built.family_executable_identity_sha256,
            self.materialized.identity.identity_sha256,
        )

        private = self.root / "private.json"
        public = self.root / "public.json"
        package = self.root / "package.json"
        head = self.root / "head.json"
        create_root(
            private_path=private,
            public_path=public,
            key_id="TEST_ONLY_goal5847_family",
            bits=2048,
        )
        freeze(
            private_path=private,
            root_path=public,
            authority_path=built.authority_path,
            output_path=package,
            head_output_path=head,
            previous_path=None,
        )
        deployment = install_rtdlexe_deployment(
            trust_root_path=public,
            trust_head_path=head,
            trust_package_path=package,
            deployment_id="goal5847-family-slot",
        )
        loaded = load_rtdlexe(
            built.artifact_path,
            authority_path=built.authority_path,
            deployment=deployment,
        )
        self.assertEqual(
            loaded.family_executable_identity_sha256,
            self.materialized.identity.identity_sha256,
        )

    def test_old_materialized_cannot_impersonate_public_family_route(self):
        with self.assertRaisesRegex(
            RTDLExecutableError, "MaterializedGenericFamilyProgram required"
        ):
            build_family_rtdlexe(
                self.old_materialized,
                artifact_directory=self.artifacts,
                authority_path=self.root / "rejected.authority.json",
                build_roots=self.roots,
                deployment_id="goal5847-family-slot",
            )

    def test_build_rejects_cross_product_family_binding_drift(self):
        exported = self.materialized.export_deployment(
            FAMILY_DEPLOYMENT_FORMAT_RTDLEXE_V2
        )
        binding = json.loads(json.dumps(dict(exported.family_binding)))
        identity = dict(binding["family_executable_identity"])
        identity["target_sha256"] = "f" * 64
        identity_body = dict(identity)
        identity_body.pop("identity_sha256")
        identity["identity_sha256"] = _digest(identity_body)
        binding["family_executable_identity"] = identity
        binding_body = dict(binding)
        binding_body.pop("binding_sha256")
        binding["binding_sha256"] = _digest(binding_body)
        with patch(
            "rtdsl.v4_callback_lifecycle._declared_protocol_contract",
            return_value=_MappingObject(self.declaration),
        ), patch(
            "rtdsl.v4_callback_lifecycle._compiled_protocol_projection",
            return_value=_MappingObject(self.projection),
        ), patch(
            "rtdsl.v4_rtdlexe._build_native_producer_descriptor",
            return_value=_native_descriptor(),
        ), self.assertRaisesRegex(
            RTDLExecutableError, "family/provider/product chain differs"
        ):
            runtime_module._build_rtdlexe_impl(
                exported.provider_payload,
                artifact_directory=self.artifacts,
                authority_path=self.root / "drift.authority.json",
                build_roots=self.roots,
                deployment_id="goal5847-family-slot",
                generic_family_binding=binding,
            )

    def test_public_builder_does_not_unwrap_private_family_handles(self):
        source = Path(
            build_family_rtdlexe.__code__.co_filename
        ).read_text(encoding="utf-8")
        body = source.split("def build_family_rtdlexe(", 1)[1].split(
            "\ndef _verify_contract_pair(", 1
        )[0]
        self.assertNotIn("._handle", body)
        self.assertNotIn("._materialized", body)
        self.assertIn("materialized.export_deployment", body)

    def test_public_exports_are_available_without_private_adapter_access(self):
        import rtdsl
        from rtdsl import v4_family

        self.assertIs(rtdsl.build_family_rtdlexe, build_family_rtdlexe)
        self.assertEqual(
            v4_family.FAMILY_DEPLOYMENT_FORMAT_RTDLEXE_V2,
            FAMILY_DEPLOYMENT_FORMAT_RTDLEXE_V2,
        )
        exported = self.materialized.export_deployment(
            FAMILY_DEPLOYMENT_FORMAT_RTDLEXE_V2
        )
        self.assertEqual(
            exported.family_binding["family_executable_identity"]
                ["identity_sha256"],
            self.materialized.identity.identity_sha256,
        )

    def test_minimal_aot_builder_exports_exact_runtime_surface(self):
        from scripts import build_v4_optix_native_snapshot as builder

        export_map = builder.RTDLEXE_EXPORT_MAP.read_text(encoding="utf-8")
        exported = tuple(
            line.strip().removesuffix(";")
            for line in export_map.splitlines()
            if line.strip().startswith("rtdl_optix_")
        )
        self.assertEqual(exported, builder.RTDLEXE_AOT_REQUIRED_SYMBOLS)
        translation_unit = (
            ROOT / "src/native/rtdl_optix_rtdlexe.cpp"
        ).read_text(encoding="utf-8")
        self.assertIn('rtdl_optix_v4_callback_poc.cpp', translation_unit)
        self.assertIn('rtdl_optix_rtdlexe_api.inc', translation_unit)
        self.assertNotIn('rtdl_optix_workloads.cpp', translation_unit)
        self.assertIn('rtdl_optix_api.cpp', translation_unit)
        api = (
            ROOT / "src/native/optix/rtdl_optix_api.cpp"
        ).read_text(encoding="utf-8-sig")
        self.assertGreaterEqual(
            api.count("#if !defined(RTDL_OPTIX_RTDLEXE_AOT_RUNTIME)"),
            5,
        )
        self.assertEqual(
            api.count("#if !defined(RTDL_OPTIX_RTDLEXE_AOT_RUNTIME)"),
            api.count("#endif  // !RTDL_OPTIX_RTDLEXE_AOT_RUNTIME"),
        )
        helper = (
            ROOT / "src/native/optix/rtdl_optix_cuda_helpers.cu"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "#if defined(RTDL_OPTIX_RTDLEXE_AOT_RUNTIME)", helper
        )


if __name__ == "__main__":
    unittest.main()

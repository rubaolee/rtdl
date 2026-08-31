from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"


class Goal5751FormalNativeRuntimeStaticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = NATIVE.read_text(encoding="utf-8")
        cls.api = API.read_text(encoding="utf-8")
        cls.prelude = PRELUDE.read_text(encoding="utf-8")

    def test_public_boundary_accepts_only_composed_ptx_and_typed_buffers(self):
        self.assertIn("rtdl_optix_v4_run_formal_callback_v1", self.api)
        formal = self.api.split("rtdl_optix_v4_run_formal_callback_v1", 1)[1]
        formal = formal.split("extern \"C\" int", 1)[0]
        self.assertIn("const char* composed_ptx", formal)
        self.assertIn("const V4CallbackSphere* spheres", formal)
        for forbidden in ("PyObject", "python_source", "user_callable", "callback_name"):
            self.assertNotIn(forbidden, formal)

    def test_one_module_owns_all_optix_program_groups_and_stack_synthesis(self):
        formal = self.native.split("v4_build_formal_callback_pipeline", 1)[1]
        formal = formal.split("static void run_v4_formal_callback", 1)[0]
        for entry in (
            "__raygen__rtdl_v4_formal",
            "__intersection__rtdl_v4_formal",
            "__anyhit__rtdl_v4_formal",
            "__closesthit__rtdl_v4_formal",
            "__miss__rtdl_v4_formal",
        ):
            self.assertIn(entry, formal)
        self.assertEqual(formal.count("holder->modules[0]"), 5)
        self.assertIn("rtdlOptixAccumulateStackSizesCompat", formal)
        compat = self.prelude.split(
            "inline OptixResult rtdlOptixAccumulateStackSizesCompat", 1)[1]
        compat = compat.split("}\n", 1)[0]
        self.assertIn("optixUtilAccumulateStackSizes", compat)
        self.assertIn("OPTIX_VERSION >= 70700", compat)
        self.assertIn("optixUtilComputeStackSizes", formal)
        self.assertIn("optixPipelineSetStackSize", formal)
        self.assertIn("pco.numPayloadValues = 10", formal)

    def test_formal_launch_is_behaviorally_bound_and_all_roles_are_required(self):
        formal = self.native.split("static void run_v4_formal_callback", 1)[1]
        self.assertIn('"v4_formal_callback_ir_seven_role_composed"', formal)
        self.assertIn("rtdl_optix_bind_traversal_audit_context", formal)
        self.assertIn("optixLaunch(", formal)
        self.assertIn("cuStreamSynchronize(0)", formal)
        self.assertIn("output_status[index].first_error_claimed", formal)
        self.assertIn("output_counters[index] == 0", formal)

    def test_legacy_poc_payload_contract_was_not_silently_changed(self):
        legacy = self.native.split("static std::unique_ptr<V4CallbackPipelineHolder> v4_build_callback_pipeline", 1)[1]
        legacy = legacy.split("static std::unique_ptr<V4CallbackPipelineHolder> v4_build_formal_callback_pipeline", 1)[0]
        self.assertIn("pco.numPayloadValues = 2", legacy)
        self.assertNotIn("pco.numPayloadValues = 10", legacy)

    def test_new_formal_runtime_has_no_application_identity_dispatch(self):
        formal = self.native.split("v4_build_formal_callback_pipeline", 1)[1]
        # Stop before the generic built-in-triangle section, including its
        # forward declaration.  Triangle is a physical geometry family, not an
        # application identity and does not belong to the formal-sphere slice.
        formal = formal.split(
            "static TriangleAccelHolder build_v4_triangle_anyhit_accel", 1)[0]
        for forbidden in ("arkade", "rayjoin", "x_hd", "triangle", "paper_app"):
            self.assertNotIn(forbidden, formal.lower())


if __name__ == "__main__":
    unittest.main()

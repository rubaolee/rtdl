import hashlib
import json
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "src/native/optix/rtdl_optix_v4_particle_template.h"
CALLBACK = ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
STATUS = ROOT / "src/native/optix/rtdl_optix_v4_product_status.h"
PRODUCT = ROOT / "src/native/rtdl_optix_v4_product.cpp"


def _template_source(header: str) -> str:
    match = re.search(
        r'kRtdlV4ParticleStrictInteriorSource = R"RTDLCUDA\((.*?)\)RTDLCUDA";',
        header,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("Particle source raw string is absent")
    return match.group(1)


def _literal(header: str, name: str) -> str:
    match = re.search(
        rf'{re.escape(name)}\s*=\s*\n?\s*"([^"]+)";', header
    )
    if match is None:
        raise AssertionError(f"Particle literal is absent: {name}")
    return match.group(1)


class Goal5814ParticleProductNativePrerequisitesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template_header = TEMPLATE.read_text(encoding="utf-8")
        cls.source = _template_source(cls.template_header)
        cls.callback = CALLBACK.read_text(encoding="utf-8")
        cls.api = API.read_text(encoding="utf-8")
        cls.prelude = PRELUDE.read_text(encoding="utf-8")
        cls.status = STATUS.read_text(encoding="utf-8")
        cls.product = PRODUCT.read_text(encoding="utf-8")

    def test_shared_source_and_semantic_digests_are_exact(self):
        source_sha = hashlib.sha256(self.source.encode()).hexdigest()
        self.assertEqual(
            source_sha,
            _literal(
                self.template_header,
                "kRtdlV4ParticleStrictInteriorSourceSha256",
            ),
        )
        semantic = {
            "schema": "rtdl.v4.particle_strict_interior_semantics.v1",
            "source_sha256": source_sha,
            "entry_points": {
                "raygen": "__raygen__rtdl_particle_strict_interior",
                "closest_hit": "__closesthit__rtdl_particle_strict_interior",
                "miss": "__miss__rtdl_particle_strict_interior",
                "intersection": None,
                "any_hit": None,
            },
            "layout": {
                "parameters_bytes": 120,
                "query": "seven_soa_f32",
                "static": "front_u32_back_u32_by_primitive",
                "output": "selected_neighbor_face_three_soa_u32",
                "control": "u32x4",
            },
            "pipeline": {
                "payload_values": 2,
                "attribute_values": 2,
                "max_trace_depth": 1,
                "primitive": "triangle",
                "single_gas": True,
            },
            "domain": {
                "query_count": 5000,
                "strict_interior": True,
                "edge_vertex_ties": "outside_domain_fail_closed",
            },
            "transfers": {
                "query_h2d_bytes": 140000,
                "launches": 1,
                "control_d2h_bytes": 16,
                "output_d2h_bytes": 60000,
                "failure_output_d2h_bytes": 0,
            },
            "boundary_owner_table_bytes": 0,
        }
        digest = hashlib.sha256(
            json.dumps(
                semantic, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        self.assertEqual(
            digest,
            _literal(
                self.template_header,
                "kRtdlV4ParticleStrictInteriorSemanticSha256",
            ),
        )

    def test_device_template_is_closest_hit_only_and_rejects_boundary(self):
        for symbol in (
            "__raygen__rtdl_particle_strict_interior",
            "__closesthit__rtdl_particle_strict_interior",
            "__miss__rtdl_particle_strict_interior",
        ):
            self.assertEqual(self.source.count(symbol), 1)
        self.assertNotIn("__anyhit__", self.source)
        self.assertNotIn("__intersection__", self.source)
        self.assertIn("OPTIX_RAY_FLAG_DISABLE_ANYHIT", self.source)
        self.assertIn("barycentrics.x <= 0.0f", self.source)
        self.assertIn("barycentrics.y <= 0.0f", self.source)
        self.assertIn("barycentric_a <= 0.0f", self.source)
        self.assertNotIn("boundary_owner", self.source)

    def test_host_parameter_layout_has_no_boundary_owner(self):
        match = re.search(
            r"struct V4ParticleParams \{(.*?)\n\};", self.callback, re.DOTALL
        )
        self.assertIsNotNone(match)
        body = match.group(1)
        self.assertNotIn("boundary_owner", body)
        self.assertEqual(body.count("const float* query_"), 7)
        self.assertIn("const uint32_t* front_values", body)
        self.assertIn("const uint32_t* back_values", body)
        self.assertIn("uint32_t* output_selected", body)
        self.assertIn("uint32_t* output_neighbor", body)
        self.assertIn("uint32_t* output_face", body)
        self.assertIn("sizeof(V4ParticleParams) == 120u", self.callback)

    def test_frozen_scale_transfer_and_launch_contract_is_structural(self):
        self.assertIn("kV4ParticleStrictInteriorQueryCount = 5000u", self.callback)
        self.assertIn("query_h2d_copy_call_count = 7u", self.callback)
        self.assertIn("control_d2h_bytes = sizeof(RtdlV4ParticleControl)", self.callback)
        self.assertIn("boundary_owner_table_bytes = 0u", self.callback)
        execute = self.callback.index(
            "static void execute_v4_prepared_particle_strict_interior("
        )
        destroy = self.callback.index(
            "static void destroy_v4_prepared_particle_strict_interior(", execute
        )
        body = self.callback[execute:destroy]
        # Three enqueue sites: the query site executes exactly seven times,
        # followed by one control-reset and one parameter upload.
        self.assertEqual(body.count("upload_async("), 3)
        self.assertIn("const std::array<const float*, 7> inputs", body)
        query_upload_loop = body.index(
            "for (size_t column = 0; column < inputs.size(); ++column)\n"
            "        upload_async("
        )
        control_upload = body.index(
            "prepared->control->ptr, prepared->control_host->data", query_upload_loop
        )
        self.assertLess(query_upload_loop, control_upload)
        self.assertEqual(body.count("OPTIX_CHECK(optixLaunch("), 1)
        receipt_zero = body.index(
            "*output_receipt = RtdlV4ParticleFastReceipt{};"
        )
        control_copy = body.index(
            "CU_CHECK(cuMemcpyDtoHAsync(\n"
            "        prepared->control_host->data, prepared->control->ptr"
        )
        control_sync = body.index("cuStreamSynchronize(prepared->stream)", control_copy)
        status_evidence = body.index(
            "output_receipt->status_before_output = 1u;", control_sync
        )
        status_gate = body.index(
            "if (output_control->validated_row_count", status_evidence
        )
        failure_return = body.index("output_d2h_after_status_failure = 0u", control_sync)
        output_copy = body.index("prepared->output_host->data", failure_return)
        output_sync = body.index("cuStreamSynchronize(prepared->stream)", output_copy)
        self.assertEqual(
            body.count("output_receipt->status_before_output = 1u;"), 1
        )
        self.assertLess(receipt_zero, control_copy)
        self.assertLess(control_copy, control_sync)
        self.assertLess(control_sync, status_evidence)
        self.assertLess(status_evidence, status_gate)
        self.assertLess(status_gate, failure_return)
        self.assertLess(control_sync, failure_return)
        self.assertLess(failure_return, output_copy)
        self.assertLess(output_copy, output_sync)
        self.assertIn("kV4ParticleStrictInteriorOutputBytes", body)
        self.assertIn("*output_columns_soa = nullptr", body)
        self.assertIn("*output_row_count = 0u", body)
        self.assertIn("*output_columns_soa = prepared->output_host->data", body)
        self.assertIn(
            "*output_row_count = kV4ParticleStrictInteriorQueryCount", body)
        self.assertNotIn("std::memcpy(output_selected", body)
        self.assertIn(
            '",\\"query_h2d_copy_call_count\\":7"', self.callback
        )

    def test_prevalidated_v3_skips_only_redundant_value_scan(self):
        execute = self.callback.index(
            "static void execute_v4_prepared_particle_strict_interior("
        )
        destroy = self.callback.index(
            "static void destroy_v4_prepared_particle_strict_interior(", execute
        )
        body = self.callback[execute:destroy]
        self.assertIn("bool values_prevalidated", body)
        pack = body.index("std::memcpy(")
        value_gate = body.index("if (!values_prevalidated) {")
        value_loop = body.index(
            "for (size_t index = 0; index < query_count; ++index)", value_gate
        )
        query_upload = body.index(
            "for (size_t column = 0; column < inputs.size(); ++column)\n"
            "        upload_async("
        )
        self.assertLess(pack, value_gate)
        self.assertLess(value_gate, value_loop)
        self.assertLess(value_loop, query_upload)
        self.assertEqual(body.count("std::isfinite("), 7)
        # The successor changes neither transfer nor execution topology.
        self.assertEqual(body.count("OPTIX_CHECK(optixLaunch("), 1)
        self.assertIn("query_h2d_copy_call_count = 7u", body)
        self.assertIn("control_d2h_copy_call_count = 1u", body)
        self.assertIn("status_before_output = 1u", body)
        self.assertIn("output_d2h_copy_call_count = 1u", body)

        v1 = self.api[
            self.api.index(
                'extern "C" int '
                "rtdl_optix_v4_execute_prepared_particle_strict_interior_v1("):
            self.api.index(
                'extern "C" int '
                "rtdl_optix_v4_execute_prepared_particle_strict_interior_v2(")
        ]
        v2 = self.api[
            self.api.index(
                'extern "C" int '
                "rtdl_optix_v4_execute_prepared_particle_strict_interior_v2("):
            self.api.index(
                'extern "C" int\n'
                "rtdl_optix_v4_execute_prepared_particle_strict_interior_"
                "prevalidated_v3(")
        ]
        v3 = self.api[
            self.api.index(
                'extern "C" int\n'
                "rtdl_optix_v4_execute_prepared_particle_strict_interior_"
                "prevalidated_v3("):
            self.api.index(
                'extern "C" int '
                "rtdl_optix_v4_destroy_prepared_particle_strict_interior_v1(")
        ]
        self.assertIn("output_control, output_receipt, false);", v1)
        self.assertIn("output_control, output_receipt, false);", v2)
        self.assertIn("output_control, output_receipt, true);", v3)
        self.assertNotIn("false);", v3)

    def test_control_and_receipt_layouts_are_frozen(self):
        self.assertIn("struct RtdlV4ParticleControl", self.status)
        self.assertIn("uint32_t validated_row_count;", self.status)
        self.assertIn("uint32_t first_error;", self.status)
        self.assertIn("uint32_t error_code;", self.status)
        self.assertIn("uint32_t status;", self.status)
        self.assertIn("sizeof(RtdlV4ParticleControl) == 16", self.status)
        self.assertIn("sizeof(RtdlV4ParticleFastReceipt) == 96", self.status)
        self.assertIn("uint32_t status_before_output;", self.status)

    def test_source_descriptor_and_lifecycle_are_product_exports(self):
        names = (
            "rtdl_optix_v4_particle_strict_interior_source_v1",
            "rtdl_optix_v4_particle_strict_interior_descriptor_v1",
            "rtdl_optix_v4_prepare_particle_strict_interior_v1",
            "rtdl_optix_v4_execute_prepared_particle_strict_interior_v1",
            "rtdl_optix_v4_execute_prepared_particle_strict_interior_v2",
            "rtdl_optix_v4_execute_prepared_particle_strict_interior_prevalidated_v3",
            "rtdl_optix_v4_destroy_prepared_particle_strict_interior_v1",
        )
        guard_end = self.api.index("#endif  // RTDL_V4_PRODUCT_ONLY")
        for name in names:
            self.assertIn(name, self.api[guard_end:])
            self.assertIn(name, self.prelude)
        self.assertIn('#define RTDL_V4_PRODUCT_ONLY 1', self.product)
        self.assertIn('#include "optix/rtdl_optix_v4_callback_poc.cpp"', self.product)
        self.assertIn('#include "optix/rtdl_optix_api.cpp"', self.product)

    def test_descriptor_discloses_exact_domain_and_avoided_table(self):
        for text in (
            "strictly_positive_barycentric_coordinates_required",
            "OUTSIDE_DOMAIN_FAIL_CLOSED",
            "query_h2d_bytes\\\":140000",
            "control_d2h_bytes\\\":16",
            "success_output_d2h_bytes\\\":60000",
            "failure_output_d2h_bytes\\\":0",
            "execute_abi_version\\\":3",
            "legacy_defensive_execute_abi_version\\\":2",
            "product_public_registry_authenticated_token_over_immutable_bytes",
            "native_skips_only",
            "borrowed_native_owned_pinned_packed_soa_u32",
            "until_next_execute_or_destroy",
            "null_pointer_zero_rows",
            "avoided_generic_table_bytes_at_frozen_scale\\\":94990840",
        ):
            self.assertIn(text, self.callback)

    def test_compiled_product_dso_returns_exact_source_and_descriptor(self):
        native_path = os.environ.get("RTDL_GOAL5814_NATIVE")
        if not native_path:
            self.skipTest("RTDL_GOAL5814_NATIVE is not set")
        library = ctypes.CDLL(native_path)

        def query(name):
            function = getattr(library, name)
            function.argtypes = [
                ctypes.c_void_p,
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_size_t),
                ctypes.c_char_p,
                ctypes.c_size_t,
            ]
            function.restype = ctypes.c_int
            error = ctypes.create_string_buffer(2048)
            byte_count = ctypes.c_size_t()
            self.assertEqual(
                function(None, 0, ctypes.byref(byte_count), error, len(error)),
                0,
                error.value.decode(errors="replace"),
            )
            output = ctypes.create_string_buffer(byte_count.value + 1)
            self.assertEqual(
                function(
                    output,
                    len(output),
                    ctypes.byref(byte_count),
                    error,
                    len(error),
                ),
                0,
                error.value.decode(errors="replace"),
            )
            return output.raw[: byte_count.value]

        source = query("rtdl_optix_v4_particle_strict_interior_source_v1")
        self.assertEqual(source, self.source.encode())
        descriptor = json.loads(query(
            "rtdl_optix_v4_particle_strict_interior_descriptor_v1"
        ))
        self.assertEqual(descriptor["source_bytes"], len(source))
        self.assertEqual(
            descriptor["source_sha256"], hashlib.sha256(source).hexdigest()
        )
        self.assertEqual(descriptor["domain"]["query_count"], 5000)
        self.assertEqual(
            descriptor["domain"]["edge_or_vertex_hit"],
            "OUTSIDE_DOMAIN_FAIL_CLOSED",
        )
        self.assertEqual(descriptor["transfer_contract"]["query_h2d_bytes"], 140000)
        self.assertEqual(
            descriptor["transfer_contract"]["query_h2d_copy_call_count"], 7
        )
        self.assertEqual(
            descriptor["transfer_contract"]["execute_abi_version"], 3
        )
        self.assertEqual(
            descriptor["transfer_contract"][
                "legacy_defensive_execute_abi_version"], 2)
        self.assertEqual(
            descriptor["native_abi"],
            "rtdl.v4.prepared_particle_strict_interior.v3")
        validation = descriptor["host_value_validation_contract"]
        self.assertEqual(
            validation["preferred_execute_symbol"],
            "rtdl_optix_v4_execute_prepared_particle_strict_interior_"
            "prevalidated_v3")
        self.assertEqual(
            validation["native_skips_only"], [
                "finite_value_rescan", "positive_tmax_rescan",
                "nonzero_direction_rescan",
            ])
        self.assertTrue(validation["legacy_native_value_scan"])
        self.assertEqual(
            descriptor["transfer_contract"]["borrowed_output_lifetime"],
            "until_next_execute_or_destroy",
        )
        self.assertEqual(descriptor["transfer_contract"]["control_d2h_bytes"], 16)
        self.assertEqual(
            descriptor["transfer_contract"]["success_output_d2h_bytes"], 60000
        )
        self.assertEqual(descriptor["boundary_owner_table"]["bytes"], 0)

    def test_shared_source_compiles_to_exact_three_entry_ptx(self):
        nvcc = os.environ.get("RTDL_GOAL5814_NVCC")
        optix_include = os.environ.get("RTDL_GOAL5814_OPTIX_INCLUDE")
        if not nvcc or not optix_include:
            self.skipTest("Goal5814 nvcc/OptiX include environment is not set")
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "particle_strict_interior.cu"
            ptx_path = Path(directory) / "particle_strict_interior.ptx"
            source_path.write_text(self.source, encoding="utf-8", newline="")
            completed = subprocess.run(
                [
                    nvcc,
                    "-ptx",
                    "-std=c++14",
                    "-arch=compute_61",
                    f"-I{optix_include}",
                    str(source_path),
                    "-o",
                    str(ptx_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            ptx = ptx_path.read_text(encoding="utf-8")
        for symbol in (
            "__raygen__rtdl_particle_strict_interior",
            "__closesthit__rtdl_particle_strict_interior",
            "__miss__rtdl_particle_strict_interior",
        ):
            self.assertEqual(ptx.count(f".entry {symbol}"), 1)
        self.assertNotIn("__anyhit__", ptx)
        self.assertNotIn("__intersection__", ptx)


if __name__ == "__main__":
    unittest.main()

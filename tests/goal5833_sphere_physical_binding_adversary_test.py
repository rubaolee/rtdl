"""Adversarial native-fact and device-query binding tests for Goal5833."""

from __future__ import annotations

import ctypes
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl import v4_sphere_prepared_runtime as runtime


def _descriptor(*, executed: bool = False) -> dict[str, object]:
    fingerprint = "a" * 64
    descriptor: dict[str, object] = {
        "schema": "rtdl.v4.native_builtin_sphere_descriptor.v2",
        **runtime._EXPECTED_OPTIX9_SPHERE_FACTS,
        "builtin_is_module": True,
        "user_intersection_program": False,
        "uses_motion_blur": False,
        "center_stride_bytes": 12,
        "radius_stride_bytes": 4,
        "single_radius": False,
        "primitive_index_offset": 0,
        "sbt_record_count": 1,
        "gas_count": 1,
        "primitive_count": 1,
        "motion_key_count": 0,
        "max_payload_values": 8,
        "max_attribute_values": 0,
        "max_trace_depth": 1,
        "program_group_count": 3,
        "compiled_optix_version": 90000,
        "compiled_optix_major": 9,
        "compiled_optix_minor": 0,
        "compiled_optix_patch": 0,
        "cuda_device_ordinal": 0,
        "cuda_compute_capability_major": 8,
        "cuda_compute_capability_minor": 9,
        "cuda_driver_version": 12090,
        "static_input_fingerprint": fingerprint,
        "device_static_input_fingerprint": fingerprint,
        "center_device_pointer": 1,
        "radius_device_pointer": 2,
        "application_id_device_pointer": 3,
        "traversable_identity": 4,
        "last_execution_present": executed,
        "last_status_failed": False,
        "last_query_count": 1 if executed else 0,
        "last_status_d2h_call_count": 1 if executed else 0,
        "last_application_output_d2h_call_count": 6 if executed else 0,
        "last_output_after_status_failure_count": 0,
        "last_query_device_pointer_nonzero_count": 6 if executed else 0,
        "last_output_device_pointer_nonzero_count": 8 if executed else 0,
        "last_query_fingerprint": fingerprint if executed else "",
        "last_device_query_fingerprint": fingerprint if executed else "",
        "last_output_fingerprint": "b" * 64 if executed else "",
        "last_status_fingerprint": "c" * 64 if executed else "",
        "last_counter_fingerprint": "d" * 64 if executed else "",
        "last_query_device_pointer_fingerprint": "e" * 64 if executed else "",
        "last_output_device_pointer_fingerprint": "f" * 64 if executed else "",
    }
    return descriptor


def _read_descriptor(value: dict[str, object]) -> dict[str, object]:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()

    def describe(_token, output, _capacity, size_out, _error, _error_size):
        size_out._obj.value = len(encoded)
        if output is not None:
            ctypes.memmove(output, encoded, len(encoded))
        return 0

    return runtime._read_native_descriptor(describe, 7)


class Goal5833SpherePhysicalBindingAdversaryTest(unittest.TestCase):
    def test_exact_pinned_optix9_sphere_enum_and_flag_values_are_required(self):
        baseline = _descriptor()
        self.assertEqual(_read_descriptor(baseline), baseline)
        for key, expected in runtime._EXPECTED_OPTIX9_SPHERE_FACTS.items():
            with self.subTest(key=key):
                hostile = dict(baseline)
                hostile[key] = expected ^ 1
                with self.assertRaisesRegex(RuntimeError, "contract differs"):
                    _read_descriptor(hostile)

    def test_descriptor_schema_device_query_and_pointer_fingerprints_fail_closed(self):
        baseline = _descriptor(executed=True)
        self.assertEqual(_read_descriptor(baseline), baseline)
        mutations = {
            "wrong_schema": {"schema": "rtdl.v4.native_builtin_sphere_descriptor.v1"},
            "device_query_differs": {"last_device_query_fingerprint": "9" * 64},
            "zero_query_pointer_fingerprint": {
                "last_query_device_pointer_fingerprint": "0" * 64},
            "zero_output_pointer_fingerprint": {
                "last_output_device_pointer_fingerprint": "0" * 64},
        }
        for name, delta in mutations.items():
            with self.subTest(name=name):
                hostile = {**baseline, **delta}
                with self.assertRaises(RuntimeError):
                    _read_descriptor(hostile)

    def test_host_consumer_requires_device_query_and_pointer_binding(self):
        normalized = ((0.0, 0.0, 0.0, 4.0, 0.0, 0.0),)
        outputs = ((1, 1056964608, 7),)
        primitive = (0,)
        kind = (0,)
        hit_t = (0.5,)
        statuses = ({
            name: 0 for name, _ctype in runtime._Status._fields_
        },)
        counters = (0,) * 7
        query_fingerprint = runtime._native_query_fingerprint(normalized)
        descriptor = {
            "last_execution_present": True,
            "last_status_failed": False,
            "last_query_count": 1,
            "last_query_fingerprint": query_fingerprint,
            "last_device_query_fingerprint": query_fingerprint,
            "last_output_fingerprint": runtime._native_output_fingerprint(
                outputs, primitive, kind, hit_t),
            "last_status_fingerprint": runtime._native_status_fingerprint(statuses),
            "last_counter_fingerprint": runtime._native_counter_fingerprint(counters),
            "last_query_device_pointer_fingerprint": "1" * 64,
            "last_output_device_pointer_fingerprint": "2" * 64,
        }
        runtime._require_native_execution_fingerprints(
            descriptor, normalized=normalized, outputs=outputs,
            observed_primitive=primitive, observed_kind=kind,
            observed_t=hit_t, statuses=statuses, counters=counters)
        for key, value in (
            ("last_device_query_fingerprint", "3" * 64),
            ("last_query_device_pointer_fingerprint", "0" * 64),
            ("last_output_device_pointer_fingerprint", "0" * 64),
        ):
            with self.subTest(key=key):
                hostile = {**descriptor, key: value}
                with self.assertRaisesRegex(RuntimeError, "content fingerprint"):
                    runtime._require_native_execution_fingerprints(
                        hostile, normalized=normalized, outputs=outputs,
                        observed_primitive=primitive, observed_kind=kind,
                        observed_t=hit_t, statuses=statuses, counters=counters)

    def test_native_rehashes_all_six_query_columns_from_device_before_launch(self):
        source = (ROOT / "src" / "native" / "optix" /
                  "rtdl_optix_v4_callback_poc.cpp").read_text(encoding="utf-8")
        launch = source.index("OPTIX_CHECK(optixLaunch(", source.index(
            "execute_v4_prepared_builtin_sphere_callback"))
        for column in ("qsx", "qsy", "qsz", "qex", "qey", "qez"):
            transfer = source.index(
                f"download(observed_{column}.data(), {column}_d.ptr, query_count)")
            self.assertLess(transfer, launch)
        comparison = source.index(
            "if (device_query_fingerprint != host_query_fingerprint)")
        self.assertLess(comparison, launch)
        self.assertIn(
            "prepared->last_device_query_fingerprint = device_query_fingerprint",
            source,
        )


if __name__ == "__main__":
    unittest.main()

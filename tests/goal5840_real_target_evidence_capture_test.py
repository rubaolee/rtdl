from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from types import MappingProxyType, SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from rtdsl.v4_target_evidence_capture import (
    TargetEvidenceCaptureError,
    capture_real_target_evidence_bundle,
)


ROUTE_ID = "stable::bounded_relation::canonical_bounded_pair_collection"


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class _Profile:
    provider: str
    optix_sdk: str
    compute_capability: str
    native_sha256: str

    @property
    def target_sha256(self) -> str:
        return _sha("target")


@dataclass(frozen=True)
class _Toolchain:
    compute_capability: tuple[int, int]
    optix_include: Path
    cuda_include: Path
    expected_python_version: str
    expected_numba_version: str
    expected_numpy_version: str


class _Record:
    def __init__(self, value: dict[str, object]) -> None:
        self._value = value

    def to_dict(self) -> dict[str, object]:
        return dict(self._value)


def _fixture(native: Path):
    native_sha = hashlib.sha256(native.read_bytes()).hexdigest()
    plan = _Record({
        "family_shape": {
            "graph_nodes": [{"primitive_kind": "custom_primitive"}],
            "buffers": [
                {"ordinal": 0, "semantic": "primitive.bounds", "value_type": "aabb3f_bits"},
                {"ordinal": 1, "semantic": "result.canonical_pair", "value_type": "u32x2"},
            ],
            "physical": {"sbt": {
                "record_stride": 1,
                "record_count_relation": "primitive_count",
            }},
        }
    })
    plan.plan_sha256 = _sha("plan")
    artifacts = object()
    descriptor = _Record({"descriptor_sha256": _sha("descriptor")})
    provider = SimpleNamespace(descriptor=descriptor)
    route = SimpleNamespace(plan=plan, artifacts=artifacts, provider=provider)
    projection = _Record({"projection_sha256": _sha("projection")})
    projection.projection_sha256 = _sha("projection")
    program = SimpleNamespace(
        plan=plan, artifacts=artifacts, provider_projection=projection
    )
    identity = _Record({
        "schema": "rtdl.family_executable_identity.v1",
        "provider_descriptor_sha256": _sha("descriptor"),
        "provider_projection_sha256": _sha("projection"),
        "plan_sha256": _sha("plan"),
        "target_sha256": _sha("target"),
        "executable_sha256": _sha("executable"),
        "provider_artifact_sha256": native_sha,
        "generated_artifact_sha256": _sha("generated"),
        "identity_sha256": _sha("identity"),
    })
    identity.executable_sha256 = _sha("executable")
    executable = SimpleNamespace(executable_sha256=_sha("executable"))
    raw = SimpleNamespace(_backend={"executable": executable})
    bridge_type = type("_MaterializedBridge", (), {})
    bridge = bridge_type()
    bridge._materialized = raw
    materialized = SimpleNamespace(
        _program=program, _handle=bridge, identity=identity
    )
    target = SimpleNamespace(
        profile=_Profile("optix", "9.0.0", "8.9", native_sha),
        native_library_path=native,
    )
    toolchain = _Toolchain(
        (8, 9), native.parent, native.parent, "3.12.0", "test", "test"
    )
    result = SimpleNamespace(
        executable_identity_sha256=_sha("identity"),
        provider_projection_sha256=_sha("projection"),
        output_sha256=_sha("output"),
        traversal_receipt={
            "physical_executor_classification": "optix_traversal_observed",
            "provider_library_sha256": native_sha,
            "output_digest": _sha("output"),
        },
    )
    return route, program, materialized, result, target, toolchain


class Goal5840RealTargetEvidenceCaptureTest(unittest.TestCase):
    def test_capture_binds_live_program_target_and_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            native = Path(name) / "librtdl_optix.so"
            native.write_bytes(b"goal5840-test-native")
            route, program, materialized, result, target, toolchain = _fixture(native)
            with patch(
                "rtdsl.v4_target_evidence_capture.build_family_target_declaration",
                return_value={"declaration": "captured"},
            ), patch(
                "rtdsl.v4_target_evidence_capture.capture_family_program_artifacts",
                return_value=[{"artifact": "captured"}],
            ), patch(
                "rtdsl.v4_target_evidence_capture.capture_generated_target_artifacts",
                return_value={"generated": "captured"},
            ), patch(
                "rtdsl.v4_target_evidence_capture.build_target_evidence_bundle",
                side_effect=lambda **kwargs: kwargs,
            ):
                captured = capture_real_target_evidence_bundle(
                    route_id=ROUTE_ID,
                    mode="capacity_fail_closed_collection",
                    route=route,
                    program=program,
                    materialized=materialized,
                    result=result,
                    target=target,
                    toolchain=toolchain,
                    declaration_authority_sha256=_sha("authority"),
                )
        receipt = captured["execution_receipt"]
        self.assertEqual(receipt["status"], "OK")
        self.assertEqual(receipt["output_sha256"], _sha("output"))
        self.assertEqual(
            receipt["control_flow_manifest_sha256"],
            captured["target_control_flow_evidence"]["manifest_sha256"],
        )
        self.assertEqual(
            captured["native_producer_descriptor"]["build_input_type_name"],
            "OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES",
        )
        self.assertEqual(
            captured["target_binding"]["native_library_sha256"],
            captured["executable_identity"]["provider_artifact_sha256"],
        )

    def test_nested_read_only_traversal_receipt_is_canonicalized(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            native = Path(name) / "librtdl_optix.so"
            native.write_bytes(b"goal5840-test-native")
            route, program, materialized, result, target, toolchain = _fixture(native)
            result.traversal_receipt = MappingProxyType({
                "physical_executor_classification": "optix_traversal_observed",
                "provider_library_sha256": target.profile.native_sha256,
                "output_digest": _sha("output"),
                "backend_receipt": MappingProxyType({
                    "launch_dimensions": (1, 1, 1),
                    "program_groups": (
                        MappingProxyType({"kind": "any_hit"}),
                    ),
                }),
            })
            with patch(
                "rtdsl.v4_target_evidence_capture.build_family_target_declaration",
                return_value={"declaration": "captured"},
            ), patch(
                "rtdsl.v4_target_evidence_capture.capture_family_program_artifacts",
                return_value=[{"artifact": "captured"}],
            ), patch(
                "rtdsl.v4_target_evidence_capture.capture_generated_target_artifacts",
                return_value={"generated": "captured"},
            ), patch(
                "rtdsl.v4_target_evidence_capture.build_target_evidence_bundle",
                side_effect=lambda **kwargs: kwargs,
            ):
                captured = capture_real_target_evidence_bundle(
                    route_id=ROUTE_ID,
                    mode="capacity_fail_closed_collection",
                    route=route,
                    program=program,
                    materialized=materialized,
                    result=result,
                    target=target,
                    toolchain=toolchain,
                    declaration_authority_sha256=_sha("authority"),
                )
        receipt = captured["execution_receipt"]["traversal_receipt"]
        self.assertIs(type(receipt), dict)
        self.assertIs(type(receipt["backend_receipt"]), dict)
        self.assertEqual(
            receipt["backend_receipt"]["launch_dimensions"], [1, 1, 1]
        )
        self.assertIs(
            type(receipt["backend_receipt"]["program_groups"][0]), dict
        )
        json.dumps(receipt, sort_keys=True, allow_nan=False)

    def test_non_optix_receipt_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            native = Path(name) / "librtdl_optix.so"
            native.write_bytes(b"goal5840-test-native")
            route, program, materialized, result, target, toolchain = _fixture(native)
            result.traversal_receipt["physical_executor_classification"] = (
                "host_fallback"
            )
            with self.assertRaisesRegex(
                TargetEvidenceCaptureError, "true OptiX traversal required"
            ):
                capture_real_target_evidence_bundle(
                    route_id=ROUTE_ID,
                    mode="capacity_fail_closed_collection",
                    route=route,
                    program=program,
                    materialized=materialized,
                    result=result,
                    target=target,
                    toolchain=toolchain,
                    declaration_authority_sha256=_sha("authority"),
                )


if __name__ == "__main__":
    unittest.main()

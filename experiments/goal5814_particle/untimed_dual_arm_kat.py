#!/usr/bin/env python3
"""Single untimed Goal5814 Particle dual-arm KAT transaction.

The transaction loads durable scientific arrays and the three executable
assets, constructs seven contiguous SoA query columns once as common input,
prepares B and D once, and runs exactly four complete executions in this order:
B success, D success, B deterministic device miss, D deterministic device
miss.  It contains no clock, retry, resume, replacement, or timing output.

The final public D owner was not yet frozen when this runner was authored.
Formal D preparation is one deliberately delayed public boundary: after both
request-external manifests and every bound asset have been checked, the runner
imports ``rtdsl.v4_particle_rtdlexe`` and directly performs public
install/load/prepare.  It never routes through the intermediate native-product
adapter, a private loader, or a caller-selected factory.
"""

from __future__ import annotations

import argparse
import ast
import base64
from dataclasses import asdict, dataclass
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
from typing import Any, Callable, Protocol

import numpy as np

from experiments.goal5814_particle.public_pyoptix_owner import (
    FORMAL_PARTICLE_SHAPE,
    ParticleDeviceStatusError as PyOptixDeviceStatusError,
    ParticleProblemShape,
    PrevalidatedParticleExecutionInput,
    prevalidate_formal_particle_execution_input,
    prepare_formal_particle_owner,
    read_prebuilt_ptx,
)


ARM_B = "B_PUBLIC_PYOPTIX"
ARM_D = "D_PUBLIC_VERIFIED_RTDSLEXE"
MISS_ERROR_CODE = 1
UINT32_MAX = 0xFFFFFFFF
SCIENTIFIC_MANIFEST_NAME = "SCIENTIFIC_INPUT_MANIFEST.json"
SCIENTIFIC_MANIFEST_SCHEMA = (
    "rtdl.goal5814.particle_tracking_durable_scientific_input.v1")
EXECUTABLE_MANIFEST_SCHEMA = (
    "rtdl.goal5814.particle_strict_interior_executable_manifest.v1")
DEPLOYMENT_CAPABILITY_SCHEMA = (
    "rtdl.goal5814.particle_dual_arm_deployment_capability.v1")
KAT_RESULT_SCHEMA = "rtdl.goal5814.particle_dual_arm_untimed_kat_result.v1"
PARTICLE_RTDEXE_SCHEMA = "rtdl.v4.particle_strict_interior.rtdlexe.v1"
FORMAL_SCIENTIFIC_MANIFEST_BYTES = 3_650
FORMAL_SCIENTIFIC_MANIFEST_SHA256 = (
    "911f02302fd48356935ab370911fc31303dc7fe56ffb7232cc060958d42e861b")
FORMAL_EXECUTABLE_MANIFEST_BYTES = 5_924
FORMAL_EXECUTABLE_MANIFEST_SHA256 = (
    "373d4eefeda2be29fc39b4564b797f5dc03f5e72a206a4939b7ac25e30f6f7f9")
FORMAL_CONTROLLING_POLICY_SHA256 = (
    "79f0d56f8765894666eaaec363f7e149c92de68e85d35ce43d3aa765132e625e")
FORMAL_LOADER_ORACLE_BINDING_SHA256 = (
    "7351cc39534961f5c0626cbf6f6e6039305ca200307bca63decc06ce4f810c99")
FORMAL_PROTOCOL_VERIFIER_SOURCE_SHA256 = (
    "7afc8971436987d29d6ce4d5078693528300f8e109e487c4658882b42d823767")
FORMAL_SOURCE_SEMANTICS_SHA256 = (
    "e67c909d6bea027dc882189aacce4b6f82fde8e6a28c41315b46037692d3b8b7")


class KatContractError(RuntimeError):
    """An arm or durable input violated the frozen KAT contract."""


@dataclass(frozen=True)
class ExpectedAssetAuthority:
    bytes: int
    sha256: str

    def __post_init__(self) -> None:
        if type(self.bytes) is not int or self.bytes <= 0:
            raise KatContractError("requested identity bytes must be positive")
        if not isinstance(self.sha256, str) \
                or re.fullmatch(r"[0-9a-f]{64}", self.sha256) is None:
            raise KatContractError("requested identity SHA-256 is invalid")


FORMAL_SCIENTIFIC_MANIFEST_IDENTITY = ExpectedAssetAuthority(
    bytes=FORMAL_SCIENTIFIC_MANIFEST_BYTES,
    sha256=FORMAL_SCIENTIFIC_MANIFEST_SHA256,
)


@dataclass(frozen=True)
class KatAssetPaths:
    scientific_input_directory: Path
    prebuilt_ptx: Path
    native_dso: Path
    rtdlexe: Path
    executable_manifest: Path
    executable_manifest_identity: ExpectedAssetAuthority
    scientific_manifest_identity: ExpectedAssetAuthority = \
        FORMAL_SCIENTIFIC_MANIFEST_IDENTITY


@dataclass(frozen=True)
class FrozenFileIdentity:
    path: str
    bytes: int
    sha256: str


@dataclass(frozen=True)
class FrozenDigestIdentity:
    location: str
    sha256: str


@dataclass(frozen=True)
class DeploymentCapability:
    schema: str
    manifest: ExpectedAssetAuthority
    artifact: FrozenFileIdentity
    native: FrozenFileIdentity
    ptx: FrozenFileIdentity
    source: FrozenFileIdentity
    descriptor: FrozenFileIdentity
    protocol_decision: FrozenDigestIdentity
    template_semantic: FrozenDigestIdentity


def _require_array(
        label: str,
        value: Any,
        dtype: Any,
        shape: tuple[int, ...],
        ) -> np.ndarray:
    if not isinstance(value, np.ndarray):
        raise KatContractError(f"{label} is not a NumPy ndarray")
    if value.dtype != np.dtype(dtype):
        raise KatContractError(
            f"{label} dtype must be exactly {np.dtype(dtype)}")
    if value.shape != shape:
        raise KatContractError(f"{label} shape must be exactly {shape}")
    if not value.flags.c_contiguous:
        raise KatContractError(f"{label} must be C contiguous")
    return value


def _require_borrowed_output(
        label: str,
        value: Any,
        *,
        query_count: int,
        ) -> np.ndarray:
    """Require the exact zero-copy view over packed native SoA columns.

    The single 60-KB output transfer contains three contiguous U32 columns.
    Exposing those bytes as ``[query, field]`` therefore has exact strides
    ``(4, query_count * 4)``.  A C-contiguous Nx3 requirement would force an
    additional host packing copy and contradict the frozen transfer contract.
    """

    if not isinstance(value, np.ndarray):
        raise KatContractError(f"{label} is not a NumPy ndarray")
    if value.dtype != np.dtype(np.uint32):
        raise KatContractError(f"{label} dtype must be exactly uint32")
    if value.shape != (query_count, 3):
        raise KatContractError(
            f"{label} shape must be exactly {(query_count, 3)}")
    item_bytes = np.dtype(np.uint32).itemsize
    expected_strides = (item_bytes, query_count * item_bytes)
    if value.strides != expected_strides or not value.flags.f_contiguous:
        raise KatContractError(
            f"{label} is not the frozen borrowed packed-SoA view: "
            f"expected_strides={expected_strides}, actual={value.strides}")
    return value


@dataclass(frozen=True)
class KatStaticInput:
    vertices: np.ndarray
    triangles: np.ndarray
    front_values: np.ndarray
    back_values: np.ndarray
    shape: ParticleProblemShape

    def __post_init__(self) -> None:
        _require_array(
            "vertices", self.vertices, np.float32,
            (self.shape.vertex_count, 3))
        _require_array(
            "triangles", self.triangles, np.uint32,
            (self.shape.triangle_count, 3))
        _require_array(
            "front_values", self.front_values, np.uint32,
            (self.shape.triangle_count,))
        _require_array(
            "back_values", self.back_values, np.uint32,
            (self.shape.triangle_count,))


@dataclass(frozen=True)
class KatSoAColumns:
    ox: np.ndarray
    oy: np.ndarray
    oz: np.ndarray
    dx: np.ndarray
    dy: np.ndarray
    dz: np.ndarray
    tmax: np.ndarray
    query_count: int

    def __post_init__(self) -> None:
        for label, column in zip(
                ("ox", "oy", "oz", "dx", "dy", "dz", "tmax"),
                self.native_order()):
            _require_array(
                label, column, np.float32, (self.query_count,))

    def native_order(self) -> tuple[np.ndarray, ...]:
        return (
            self.ox, self.oy, self.oz,
            self.dx, self.dy, self.dz, self.tmax,
        )


@dataclass(frozen=True)
class LoadedParticleKat:
    paths: KatAssetPaths
    shape: ParticleProblemShape
    scientific_manifest: ExpectedAssetAuthority
    executable_manifest: ExpectedAssetAuthority
    deployment_capability: DeploymentCapability
    prebuilt_ptx: bytes
    rtdlexe_bytes: bytes
    static_input: KatStaticInput
    expected_output: np.ndarray
    success_queries: KatSoAColumns
    miss_queries: KatSoAColumns


@dataclass(frozen=True)
class KatExecutionLedger:
    h2d_copy_call_count: int
    h2d_bytes: int
    query_h2d_copy_call_count: int
    query_h2d_bytes: int
    control_reset_h2d_copy_call_count: int
    control_reset_h2d_bytes: int
    parameter_h2d_copy_call_count: int
    parameter_h2d_bytes: int
    optix_launch_call_count: int
    raygen_invocation_count: int
    control_d2h_copy_call_count: int
    control_d2h_bytes: int
    output_d2h_copy_call_count: int
    output_d2h_bytes: int
    status_before_output: bool
    output_d2h_after_status_failure: int
    blocking_boundary_count: int


@dataclass(frozen=True)
class KatArmSuccess:
    arm: str
    output: np.ndarray
    control: tuple[int, int, int, int]
    ledger: KatExecutionLedger


class KatDeviceStatusFailure(RuntimeError):
    """Normalized failure raised by either KAT arm after its status gate."""

    def __init__(
            self,
            arm: str,
            control: tuple[int, int, int, int],
            ledger: KatExecutionLedger,
            ) -> None:
        super().__init__(f"{arm} device-status failure: {control}")
        self.arm = arm
        self.control = control
        self.ledger = ledger


class KatArm(Protocol):
    label: str
    deployment_capability: DeploymentCapability

    def execute_complete(
            self,
            query_columns: KatSoAColumns,
            expected_output: np.ndarray,
            ) -> KatArmSuccess:
        ...

    def close(self) -> None:
        ...


class ExactCoreKatArm(KatArm, Protocol):
    def admit_exact_core_input(
            self, query_columns: KatSoAColumns,
            expected_output: np.ndarray) -> Any:
        ...

    def execute_exact_core(self, admitted: Any) -> Any:
        ...

    def materialize_exact_core(self, completion: Any) -> KatArmSuccess:
        ...


ArmFactory = Callable[[LoadedParticleKat], KatArm]


@dataclass(frozen=True)
class KatSuccessSummary:
    arm: str
    exact: bool
    output_read_only: bool
    control: tuple[int, int, int, int]
    ledger: KatExecutionLedger


@dataclass(frozen=True)
class KatFailureSummary:
    arm: str
    device_status_failure: bool
    control: tuple[int, int, int, int]
    ledger: KatExecutionLedger


@dataclass(frozen=True)
class DualArmKatResult:
    b_success: KatSuccessSummary
    d_success: KatSuccessSummary
    b_miss: KatFailureSummary
    d_miss: KatFailureSummary
    execution_order: tuple[str, str, str, str]
    timed: bool = False
    retry_count: int = 0
    replacement_count: int = 0


def _load_exact_npy(
        path: Path,
        *,
        dtype: Any,
        shape: tuple[int, ...],
        ) -> np.ndarray:
    try:
        value = np.load(path, allow_pickle=False)
    except BaseException as error:
        raise KatContractError(f"unable to load durable array {path}") from error
    value = _require_array(path.name, value, dtype, shape)
    return value


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _require_exact_keys(
        value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        raise KatContractError(
            f"{label} exact keys differ: expected={sorted(expected)}, "
            f"actual={actual}")
    return value


def _canonical_manifest_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True)
        + "\n").encode("utf-8")


def _canonical_result_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True)
        + "\n").encode("utf-8")


def _reject_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise KatContractError(f"manifest contains duplicate key {key}")
        result[key] = value
    return result


def _read_requested_manifest(
        path: Path,
        requested: ExpectedAssetAuthority,
        label: str,
        ) -> dict[str, Any]:
    raw = path.read_bytes()
    observed = ExpectedAssetAuthority(len(raw), hashlib.sha256(raw).hexdigest())
    if observed != requested:
        raise KatContractError(
            f"{label} request-external identity differs: "
            f"expected={requested}, actual={observed}")
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_object,
            parse_constant=lambda token: (_ for _ in ()).throw(
                KatContractError(f"manifest contains {token}")),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise KatContractError(f"{label} is not strict UTF-8 JSON") from error
    if raw != _canonical_manifest_bytes(value):
        raise KatContractError(f"{label} is not canonical sorted JSON")
    if not isinstance(value, dict):
        raise KatContractError(f"{label} root is not an object")
    return value


def _require_identity_fields(value: Any, label: str) -> dict[str, Any]:
    identity = _require_exact_keys(
        value, {"path", "bytes", "sha256"}, label)
    if not isinstance(identity["path"], str) or not identity["path"]:
        raise KatContractError(f"{label} path is invalid")
    relative = Path(identity["path"])
    if relative.is_absolute() or ".." in relative.parts \
            or "\\" in identity["path"]:
        raise KatContractError(f"{label} path is not a legal relative path")
    ExpectedAssetAuthority(identity["bytes"], identity["sha256"])
    return identity


def _verify_manifest_member(
        manifest_path: Path,
        value: Any,
        label: str,
        *,
        exact_path: Path | None = None,
        ) -> FrozenFileIdentity:
    identity = _require_identity_fields(value, label)
    member = (manifest_path.parent / identity["path"]).resolve(strict=True)
    if exact_path is not None and member != exact_path.resolve(strict=True):
        raise KatContractError(f"{label} path does not bind the requested asset")
    if not member.is_file():
        raise KatContractError(f"{label} is not a regular file")
    observed_bytes = member.stat().st_size
    observed_sha256 = _sha256_path(member)
    if observed_bytes != identity["bytes"] \
            or observed_sha256 != identity["sha256"]:
        raise KatContractError(
            f"{label} member identity differs: "
            f"expected=({identity['bytes']},{identity['sha256']}), "
            f"actual=({observed_bytes},{observed_sha256})")
    return FrozenFileIdentity(
        path=identity["path"], bytes=observed_bytes,
        sha256=observed_sha256)


def _verify_scientific_manifest(
        directory: Path,
        requested: ExpectedAssetAuthority,
        shape: ParticleProblemShape,
        ) -> ExpectedAssetAuthority:
    manifest_path = directory / SCIENTIFIC_MANIFEST_NAME
    manifest = _read_requested_manifest(
        manifest_path, requested, "scientific input manifest")
    _require_exact_keys(manifest, {
        "claim_boundary", "controlling_policy", "date", "payload_bytes",
        "payload_count", "payloads", "schema", "source_authority",
        "status", "superseded_goal5776_v1_accepted",
        "temporary_source_root_required_after_materialization",
        "upstream_goal5776_v2_manifest",
    }, "scientific input manifest")
    if manifest["schema"] != SCIENTIFIC_MANIFEST_SCHEMA \
            or manifest["status"] != \
            "DURABLE_BYTE_IDENTICAL_SUCCESSOR__NO_TMP_RUNTIME_DEPENDENCY":
        raise KatContractError("scientific manifest schema/status differs")
    if manifest["date"] != "2026-08-28" \
            or manifest["superseded_goal5776_v1_accepted"] is not False \
            or manifest["temporary_source_root_required_after_materialization"] \
            is not False:
        raise KatContractError("scientific manifest frozen flags differ")
    if _require_exact_keys(manifest["claim_boundary"], {
            "executable_bytes_frozen", "oracle_rederivation_completed",
            "performance_worker_authorized", "scientific_input_custody_only",
            }, "scientific claim boundary") != {
                "executable_bytes_frozen": False,
                "oracle_rederivation_completed": False,
                "performance_worker_authorized": False,
                "scientific_input_custody_only": True,
            }:
        raise KatContractError("scientific claim boundary differs")
    controlling = _require_exact_keys(
        manifest["controlling_policy"], {"bytes", "path", "sha256"},
        "scientific controlling policy")
    ExpectedAssetAuthority(controlling["bytes"], controlling["sha256"])
    if not isinstance(controlling["path"], str) or not controlling["path"]:
        raise KatContractError("scientific controlling policy path is invalid")

    expected_numpy = {
        "back_values_u32.npy": ("uint32", [shape.triangle_count]),
        "expected_u32.npy": ("uint32", [shape.query_count, 3]),
        "front_values_u32.npy": ("uint32", [shape.triangle_count]),
        "queries_f32.npy": ("float32", [shape.query_count, 7]),
        "query_cells_u32.npy": ("uint32", [shape.query_count]),
        "triangles_u32.npy": ("uint32", [shape.triangle_count, 3]),
        "vertices_f32.npy": ("float32", [shape.vertex_count, 3]),
    }
    expected_names = {
        "GOAL5776_MANIFEST.json", "solution_4.vtu", *expected_numpy}
    payloads = manifest["payloads"]
    if not isinstance(payloads, list) or manifest["payload_count"] != 9 \
            or len(payloads) != 9:
        raise KatContractError("scientific payload count differs")
    identities: dict[str, FrozenFileIdentity] = {}
    declared_total = 0
    for index, payload in enumerate(payloads):
        if not isinstance(payload, dict) or "name" not in payload:
            raise KatContractError(f"scientific payload {index} is invalid")
        name = payload["name"]
        if name in identities or name not in expected_names:
            raise KatContractError(f"scientific payload name differs: {name}")
        expected_keys = {"bytes", "name", "role", "sha256"}
        if name in expected_numpy:
            expected_keys |= {"dtype", "shape"}
        _require_exact_keys(payload, expected_keys, f"scientific payload {name}")
        if Path(name).name != name:
            raise KatContractError("scientific payload name is not a basename")
        identity = _verify_manifest_member(
            manifest_path,
            {"path": name, "bytes": payload["bytes"],
             "sha256": payload["sha256"]},
            f"scientific payload {name}")
        identities[name] = identity
        declared_total += payload["bytes"]
        if name in expected_numpy:
            dtype, member_shape = expected_numpy[name]
            if payload["role"] != "FROZEN_GOAL5776_V2_NUMPY_PAYLOAD" \
                    or payload["dtype"] != dtype \
                    or payload["shape"] != member_shape:
                raise KatContractError(
                    f"scientific NumPy metadata differs for {name}")
        elif name == "GOAL5776_MANIFEST.json" and payload["role"] != \
                "BYTE_IDENTICAL_CONTROLLING_GOAL5776_V2_MANIFEST":
            raise KatContractError("Goal5776 manifest role differs")
        elif name == "solution_4.vtu" and payload["role"] != \
                "PINNED_PUBLIC_RTXADVECT_SOURCE_MESH":
            raise KatContractError("source mesh role differs")
    if set(identities) != expected_names \
            or manifest["payload_bytes"] != declared_total:
        raise KatContractError("scientific payload set/byte total differs")

    source = _require_exact_keys(manifest["source_authority"], {
        "bytes", "commit", "project", "repository_path", "sha256",
    }, "scientific source authority")
    solution = identities["solution_4.vtu"]
    if source != {
            "bytes": solution.bytes,
            "commit": "5cfe63fed227c238905a8f24082b59b5d3160966",
            "project": "RTxAdvect",
            "repository_path": "dataset/microfludics/solution_4.vtu",
            "sha256": solution.sha256,
            }:
        raise KatContractError("scientific source authority differs")
    upstream = _require_exact_keys(
        manifest["upstream_goal5776_v2_manifest"],
        {"bytes", "copied_name", "sha256"}, "Goal5776 authority")
    goal5776 = identities["GOAL5776_MANIFEST.json"]
    if upstream != {
            "bytes": goal5776.bytes,
            "copied_name": "GOAL5776_MANIFEST.json",
            "sha256": goal5776.sha256,
            }:
        raise KatContractError("Goal5776 authority differs")
    return requested


def _compact_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise KatContractError("value is not canonicalizable JSON") from error


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) \
            or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise KatContractError(f"{label} SHA-256 is invalid")
    return value


def _verify_declared_local_file(
        manifest_path: Path,
        declared_path: Any,
        *,
        expected_sha256: Any,
        label: str,
        expected_bytes: Any | None = None,
        exact_path: Path | None = None,
        ) -> FrozenFileIdentity:
    if not isinstance(declared_path, str) or not declared_path:
        raise KatContractError(f"{label} declared path is invalid")
    basename = Path(declared_path).name
    if not basename or basename in {".", ".."}:
        raise KatContractError(f"{label} declared basename is invalid")
    member = (manifest_path.parent / basename).resolve(strict=True)
    if exact_path is not None and member != exact_path.resolve(strict=True):
        raise KatContractError(f"{label} path does not bind the requested asset")
    if not member.is_file():
        raise KatContractError(f"{label} is not a regular file")
    expected_sha = _require_sha256(expected_sha256, label)
    if expected_bytes is not None \
            and (type(expected_bytes) is not int or expected_bytes <= 0):
        raise KatContractError(f"{label} byte count is invalid")
    observed_bytes = member.stat().st_size
    observed_sha = _sha256_path(member)
    if observed_sha != expected_sha \
            or (expected_bytes is not None
                and observed_bytes != expected_bytes):
        raise KatContractError(
            f"{label} member identity differs: "
            f"expected=({expected_bytes},{expected_sha}), "
            f"actual=({observed_bytes},{observed_sha})")
    return FrozenFileIdentity(
        path=basename, bytes=observed_bytes, sha256=observed_sha)


def _decode_artifact_member(
        artifact: dict[str, Any], data_key: str, sha_key: str) -> bytes:
    encoded = artifact[data_key]
    expected = _require_sha256(artifact[sha_key], f"artifact {sha_key}")
    if not isinstance(encoded, str):
        raise KatContractError(f"artifact {data_key} is not base64 text")
    try:
        raw = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (UnicodeEncodeError, ValueError) as error:
        raise KatContractError(f"artifact {data_key} is invalid base64") \
            from error
    if hashlib.sha256(raw).hexdigest() != expected:
        raise KatContractError(f"artifact {data_key} SHA-256 differs")
    return raw


def _parse_particle_artifact(artifact_bytes: bytes) -> dict[str, Any]:
    try:
        artifact = json.loads(
            artifact_bytes.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_object,
            parse_constant=lambda token: (_ for _ in ()).throw(
                KatContractError(f"artifact contains {token}")),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise KatContractError("public .rtdlexe is not strict UTF-8 JSON") \
            from error
    if artifact_bytes != _compact_json_bytes(artifact) + b"\n":
        raise KatContractError("public Particle .rtdlexe is not canonical JSON")
    _require_exact_keys(artifact, {
        "build_identity", "descriptor_base64", "descriptor_sha256",
        "format_version", "native_library_sha256", "ptx_base64",
        "ptx_sha256", "schema", "source_base64", "source_sha256",
        "specialization_binding", "standard_protocol",
        "template_semantic_sha256",
    }, "public Particle .rtdlexe")
    if artifact["schema"] != PARTICLE_RTDEXE_SCHEMA \
            or artifact["format_version"] != 1:
        raise KatContractError("public Particle .rtdlexe schema/version differs")
    return artifact


def _verify_artifact_embedded_ptx(
        artifact_bytes: bytes,
        standalone_ptx: bytes,
        ) -> dict[str, Any]:
    if b"\x00" in standalone_ptx:
        raise KatContractError("standalone PTX contains unconsumed NUL bytes")
    artifact = _parse_particle_artifact(artifact_bytes)
    embedded = _decode_artifact_member(
        artifact, "ptx_base64", "ptx_sha256")
    if b"\x00" in embedded:
        raise KatContractError("embedded PTX contains unconsumed NUL bytes")
    if embedded != standalone_ptx:
        raise KatContractError(
            "standalone PTX is not byte-identical to artifact embedded PTX")
    return artifact


def _verify_executable_manifest(
        paths: KatAssetPaths,
        manifest_path: Path,
        ptx_path: Path,
        dso_path: Path,
        rtdlexe_path: Path,
        ) -> tuple[ExpectedAssetAuthority, DeploymentCapability]:
    requested = paths.executable_manifest_identity
    manifest = _read_requested_manifest(
        manifest_path, requested, "executable manifest")
    _require_exact_keys(manifest, {
        "build_argv", "build_host", "build_only_no_registered_timing",
        "controlling_policy", "identities", "manifest_body_sha256",
        "runtime_boundary", "schema", "specialization_scope",
        "standard_protocol", "status", "tool_identity",
    }, "executable manifest")
    if manifest["schema"] != EXECUTABLE_MANIFEST_SCHEMA \
            or manifest["status"] != \
            "PASS__EXACT_PUBLIC_ARTIFACT_BUILT_AND_LOAD_VERIFIED__NO_EXECUTE" \
            or manifest["build_only_no_registered_timing"] is not True:
        raise KatContractError("executable manifest schema/status differs")
    body = dict(manifest)
    body_seal = _require_sha256(
        body.pop("manifest_body_sha256"), "executable manifest body")
    if hashlib.sha256(_compact_json_bytes(body)).hexdigest() != body_seal:
        raise KatContractError("executable manifest body seal differs")

    identities = _require_exact_keys(manifest["identities"], {
        "artifact_absolute_path", "artifact_bytes", "artifact_sha256",
        "builder_source_absolute_path", "builder_source_sha256",
        "descriptor_absolute_path", "descriptor_sha256",
        "native_absolute_path", "native_sha256", "ptx_bytes",
        "ptx_pass1_absolute_path", "ptx_pass2_absolute_path",
        "ptx_passes_byte_identical", "ptx_sha256",
        "specialization_binding_sha256", "template_semantic_sha256",
        "template_source_absolute_path", "template_source_sha256",
    }, "executable identities")
    if identities["ptx_passes_byte_identical"] is not True:
        raise KatContractError("executable manifest PTX passes differ")
    artifact = _verify_declared_local_file(
        manifest_path, identities["artifact_absolute_path"],
        expected_sha256=identities["artifact_sha256"],
        expected_bytes=identities["artifact_bytes"],
        exact_path=rtdlexe_path, label="rtdlexe artifact")
    if artifact.path != f"{artifact.sha256}.rtdlexe":
        raise KatContractError("rtdlexe artifact is not content-addressed")
    native = _verify_declared_local_file(
        manifest_path, identities["native_absolute_path"],
        expected_sha256=identities["native_sha256"], exact_path=dso_path,
        label="native DSO")
    ptx = _verify_declared_local_file(
        manifest_path, identities["ptx_pass1_absolute_path"],
        expected_sha256=identities["ptx_sha256"],
        expected_bytes=identities["ptx_bytes"], exact_path=ptx_path,
        label="prebuilt PTX pass 1")
    ptx_pass2 = _verify_declared_local_file(
        manifest_path, identities["ptx_pass2_absolute_path"],
        expected_sha256=identities["ptx_sha256"],
        expected_bytes=identities["ptx_bytes"], label="prebuilt PTX pass 2")
    source = _verify_declared_local_file(
        manifest_path, identities["template_source_absolute_path"],
        expected_sha256=identities["template_source_sha256"],
        label="device source")
    descriptor = _verify_declared_local_file(
        manifest_path, identities["descriptor_absolute_path"],
        expected_sha256=identities["descriptor_sha256"],
        label="device descriptor")
    if ptx.sha256 != ptx_pass2.sha256 \
            or ptx_path.read_bytes() != \
            (manifest_path.parent / ptx_pass2.path).read_bytes():
        raise KatContractError("two frozen PTX passes are not byte-identical")

    protocol = _require_exact_keys(manifest["standard_protocol"], {
        "decision_sha256", "findings", "independent_oracle_binding_sha256",
        "independent_oracle_verifier_source_sha256", "producer",
        "source_semantics_sha256", "verdict",
    }, "executable standard protocol")
    if protocol["producer"] != "compile_standard_builtin_triangle_program" \
            or protocol["verdict"] != "ACCEPT" \
            or protocol["findings"] != [] \
            or protocol["independent_oracle_binding_sha256"] != \
            FORMAL_LOADER_ORACLE_BINDING_SHA256 \
            or protocol["independent_oracle_verifier_source_sha256"] != \
            FORMAL_PROTOCOL_VERIFIER_SOURCE_SHA256 \
            or protocol["source_semantics_sha256"] != \
            FORMAL_SOURCE_SEMANTICS_SHA256:
        raise KatContractError("executable standard protocol differs")
    for name in (
            "decision_sha256", "independent_oracle_binding_sha256",
            "independent_oracle_verifier_source_sha256",
            "source_semantics_sha256"):
        _require_sha256(protocol[name], f"standard protocol {name}")
    scope = _require_exact_keys(manifest["specialization_scope"], {
        "arbitrary_user_dsl_generalization_claimed",
        "complete_particle_advection_claimed", "name",
    }, "executable specialization scope")
    if scope != {
            "arbitrary_user_dsl_generalization_claimed": False,
            "complete_particle_advection_claimed": False,
            "name": "STRICT_INTERIOR_STANDARD_LIBRARY_SPECIALIZATION_ONLY",
            }:
        raise KatContractError("executable specialization scope differs")
    boundary = _require_exact_keys(manifest["runtime_boundary"], {
        "build_self_consistency_public_load_roundtrip_passed",
        "compiler_numba_or_nvrtc_imported_on_cache_hit",
        "external_manifest_authority_kat_passed",
        "formal_worker_zero_authorized",
        "installer_authenticates_provenance_by_itself", "performance_claimed",
        "real_prepare_or_execute_attempted", "runtime_product_abi_symbol_count",
        "runtime_product_abi_symbols",
    }, "executable runtime boundary")
    legacy_v2_symbols = [
        "rtdl_optix_v4_particle_strict_interior_source_v1",
        "rtdl_optix_v4_particle_strict_interior_descriptor_v1",
        "rtdl_optix_v4_prepare_particle_strict_interior_v1",
        "rtdl_optix_v4_execute_prepared_particle_strict_interior_v2",
        "rtdl_optix_v4_destroy_prepared_particle_strict_interior_v1",
    ]
    prevalidated_v3_symbols = [
        *legacy_v2_symbols[:-1],
        "rtdl_optix_v4_execute_prepared_particle_strict_interior_"
        "prevalidated_v3",
        legacy_v2_symbols[-1],
    ]
    symbol_variant = (
        boundary["runtime_product_abi_symbol_count"],
        boundary["runtime_product_abi_symbols"],
    )
    if boundary["build_self_consistency_public_load_roundtrip_passed"] \
            is not True \
            or boundary["compiler_numba_or_nvrtc_imported_on_cache_hit"] \
            is not False \
            or boundary["installer_authenticates_provenance_by_itself"] \
            is not False \
            or boundary["external_manifest_authority_kat_passed"] is not False \
            or boundary["formal_worker_zero_authorized"] is not False \
            or boundary["performance_claimed"] is not False \
            or boundary["real_prepare_or_execute_attempted"] is not False \
            or not isinstance(boundary["runtime_product_abi_symbols"], list) \
            or symbol_variant not in (
                (5, legacy_v2_symbols), (6, prevalidated_v3_symbols)):
        raise KatContractError("executable runtime boundary differs")
    policy = _require_exact_keys(manifest["controlling_policy"], {
        "absolute_path", "loader_oracle_binding_sha256", "sha256",
    }, "executable controlling policy")
    if policy["sha256"] != FORMAL_CONTROLLING_POLICY_SHA256 \
            or policy["loader_oracle_binding_sha256"] != \
            FORMAL_LOADER_ORACLE_BINDING_SHA256:
        raise KatContractError("executable controlling policy differs")
    _require_exact_keys(manifest["tool_identity"], {
        "compute_arch", "numba_version", "numpy_version",
        "nvcc_absolute_path", "nvcc_executable_sha256",
        "optix_device_header_sha256", "optix_include_absolute_path",
        "python_executable", "python_version",
    }, "executable tool identity")
    if not isinstance(manifest["build_argv"], list) \
            or not all(isinstance(value, str) for value in manifest["build_argv"]):
        raise KatContractError("executable build argv differs")

    artifact_bytes = rtdlexe_path.read_bytes()
    standalone_ptx = ptx_path.read_bytes()
    artifact_value = _verify_artifact_embedded_ptx(
        artifact_bytes, standalone_ptx)
    embedded_source = _decode_artifact_member(
        artifact_value, "source_base64", "source_sha256")
    embedded_descriptor = _decode_artifact_member(
        artifact_value, "descriptor_base64", "descriptor_sha256")
    if embedded_source != (manifest_path.parent / source.path).read_bytes() \
            or embedded_descriptor != \
            (manifest_path.parent / descriptor.path).read_bytes():
        raise KatContractError(
            "artifact embedded source/descriptor differs from standalone asset")
    try:
        descriptor_value = json.loads(
            embedded_descriptor.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_object,
            parse_constant=lambda token: (_ for _ in ()).throw(
                KatContractError(f"descriptor contains {token}")),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise KatContractError("device descriptor is not strict UTF-8 JSON") \
            from error
    if not isinstance(descriptor_value, dict) \
            or descriptor_value.get("source_sha256") != source.sha256 \
            or descriptor_value.get("source_bytes") != source.bytes \
            or descriptor_value.get("semantic_sha256") != \
            identities["template_semantic_sha256"]:
        raise KatContractError("device descriptor authority differs")
    if artifact_value["native_library_sha256"] != native.sha256 \
            or artifact_value["ptx_sha256"] != ptx.sha256 \
            or artifact_value["source_sha256"] != source.sha256 \
            or artifact_value["descriptor_sha256"] != descriptor.sha256 \
            or artifact_value["template_semantic_sha256"] != \
            identities["template_semantic_sha256"]:
        raise KatContractError("artifact member identity differs from manifest")
    specialization = artifact_value["specialization_binding"]
    if not isinstance(specialization, dict) \
            or specialization.get("binding_sha256") != \
            identities["specialization_binding_sha256"]:
        raise KatContractError("artifact specialization identity differs")
    artifact_protocol = artifact_value["standard_protocol"]
    if not isinstance(artifact_protocol, dict):
        raise KatContractError("artifact standard protocol is invalid")
    decision = _require_exact_keys(artifact_protocol.get("decision"), {
        "contract_sha256", "decision_sha256", "executable_capability_issued",
        "findings", "projection_sha256", "schema", "verdict",
    }, "artifact protocol decision")
    decision_body = dict(decision)
    decision_sha = _require_sha256(
        decision_body.pop("decision_sha256"), "artifact protocol decision")
    if hashlib.sha256(_compact_json_bytes(decision_body)).hexdigest() \
            != decision_sha \
            or decision_sha != protocol["decision_sha256"] \
            or decision["verdict"] != "ACCEPT" or decision["findings"] != []:
        raise KatContractError("artifact protocol decision seal differs")
    semantic_sha = _require_sha256(
        identities["template_semantic_sha256"], "template semantic")

    return requested, DeploymentCapability(
        schema=DEPLOYMENT_CAPABILITY_SCHEMA,
        manifest=requested,
        artifact=artifact, native=native, ptx=ptx, source=source,
        descriptor=descriptor,
        protocol_decision=FrozenDigestIdentity(
            location="artifact.standard_protocol.decision",
            sha256=decision_sha),
        template_semantic=FrozenDigestIdentity(
            location="artifact.template_semantic_sha256",
            sha256=semantic_sha),
    )


def _make_common_soa(
        queries: np.ndarray,
        *,
        query_count: int,
        ) -> KatSoAColumns:
    """Common-input stage: materialize seven exact contiguous columns once."""

    _require_array("queries_f32.npy", queries, np.float32, (query_count, 7))
    columns = tuple(
        np.array(
            queries[:, column_index], dtype=np.float32,
            order="C", copy=True)
        for column_index in range(7))
    for column in columns:
        column.setflags(write=False)
    return KatSoAColumns(*columns, query_count=query_count)


def _make_deterministic_miss(
        success: KatSoAColumns,
        vertices: np.ndarray,
        ) -> KatSoAColumns:
    """Change only row zero to a ray provably outside and leaving the bbox."""

    minimum = vertices.min(axis=0).astype(np.float64, copy=False)
    maximum = vertices.max(axis=0).astype(np.float64, copy=False)
    extent = float(np.max(maximum - minimum))
    if not np.isfinite(extent):
        raise KatContractError("mesh bounding box is nonfinite")
    margin = max(extent, 1.0) * 2.0
    outside = np.asarray(maximum + margin, dtype=np.float32)
    direction_value = np.float32(1.0 / np.sqrt(3.0))
    if not bool(np.isfinite(outside).all()) \
            or not bool((outside > maximum).all()):
        raise KatContractError("unable to construct an exterior miss origin")

    columns = tuple(column.copy(order="C") for column in success.native_order())
    columns[0][0], columns[1][0], columns[2][0] = outside
    columns[3][0] = direction_value
    columns[4][0] = direction_value
    columns[5][0] = direction_value
    columns[6][0] = np.float32(1.0)
    for column in columns:
        column.setflags(write=False)
    return KatSoAColumns(*columns, query_count=success.query_count)


def load_durable_particle_kat(
        paths: KatAssetPaths,
        *,
        shape: ParticleProblemShape = FORMAL_PARTICLE_SHAPE,
        ) -> LoadedParticleKat:
    """Load all durable assets and finish common input creation."""

    directory = Path(paths.scientific_input_directory).resolve(strict=True)
    ptx_path = Path(paths.prebuilt_ptx).resolve(strict=True)
    dso_path = Path(paths.native_dso).resolve(strict=True)
    rtdlexe_path = Path(paths.rtdlexe).resolve(strict=True)
    executable_manifest_path = Path(
        paths.executable_manifest).resolve(strict=True)
    resolved_paths = KatAssetPaths(
        directory, ptx_path, dso_path, rtdlexe_path,
        executable_manifest_path, paths.executable_manifest_identity,
        paths.scientific_manifest_identity)
    if not directory.is_dir():
        raise KatContractError("scientific input path is not a directory")
    scientific_manifest = _verify_scientific_manifest(
        directory, paths.scientific_manifest_identity, shape)
    executable_manifest, deployment_capability = \
        _verify_executable_manifest(
            resolved_paths, executable_manifest_path, ptx_path, dso_path,
            rtdlexe_path)
    if not dso_path.is_file() or dso_path.stat().st_size == 0:
        raise KatContractError("native DSO is absent or empty")
    with dso_path.open("rb") as stream:
        if stream.read(4) != b"\x7fELF":
            raise KatContractError("native DSO is not an ELF artifact")
    if rtdlexe_path.suffix != ".rtdlexe" or not rtdlexe_path.is_file():
        raise KatContractError("public artifact is not a .rtdlexe file")
    rtdlexe_bytes = rtdlexe_path.read_bytes()
    if not rtdlexe_bytes:
        raise KatContractError("public .rtdlexe artifact is empty")
    prebuilt_ptx = read_prebuilt_ptx(ptx_path)
    _verify_artifact_embedded_ptx(rtdlexe_bytes, prebuilt_ptx)

    vertices = _load_exact_npy(
        directory / "vertices_f32.npy", dtype=np.float32,
        shape=(shape.vertex_count, 3))
    triangles = _load_exact_npy(
        directory / "triangles_u32.npy", dtype=np.uint32,
        shape=(shape.triangle_count, 3))
    front_values = _load_exact_npy(
        directory / "front_values_u32.npy", dtype=np.uint32,
        shape=(shape.triangle_count,))
    back_values = _load_exact_npy(
        directory / "back_values_u32.npy", dtype=np.uint32,
        shape=(shape.triangle_count,))
    queries = _load_exact_npy(
        directory / "queries_f32.npy", dtype=np.float32,
        shape=(shape.query_count, 7))
    expected = _load_exact_npy(
        directory / "expected_u32.npy", dtype=np.uint32,
        shape=(shape.query_count, 3))
    if not bool(np.isfinite(vertices).all()) \
            or not bool(np.isfinite(queries).all()):
        raise KatContractError("durable floating-point input is nonfinite")

    static_input = KatStaticInput(
        vertices, triangles, front_values, back_values, shape)
    success_queries = _make_common_soa(
        queries, query_count=shape.query_count)
    miss_queries = _make_deterministic_miss(success_queries, vertices)
    for value in (
            vertices, triangles, front_values, back_values, expected):
        value.setflags(write=False)
    return LoadedParticleKat(
        paths=resolved_paths,
        shape=shape,
        scientific_manifest=scientific_manifest,
        executable_manifest=executable_manifest,
        deployment_capability=deployment_capability,
        prebuilt_ptx=prebuilt_ptx,
        rtdlexe_bytes=rtdlexe_bytes,
        static_input=static_input,
        expected_output=expected,
        success_queries=success_queries,
        miss_queries=miss_queries,
    )


class _PublicPyOptixKatArm:
    label = ARM_B

    def __init__(
            self, owner: Any,
            deployment_capability: DeploymentCapability) -> None:
        self._owner = owner
        self.deployment_capability = deployment_capability

    @staticmethod
    def _ledger(counts: Any) -> KatExecutionLedger:
        return KatExecutionLedger(
            h2d_copy_call_count=int(counts.h2d_copy_call_count),
            h2d_bytes=int(counts.h2d_copy_bytes),
            query_h2d_copy_call_count=int(
                counts.query_h2d_copy_call_count),
            query_h2d_bytes=int(counts.query_h2d_bytes),
            control_reset_h2d_copy_call_count=int(
                counts.control_reset_h2d_copy_call_count),
            control_reset_h2d_bytes=int(counts.control_reset_h2d_bytes),
            parameter_h2d_copy_call_count=int(
                counts.parameter_h2d_copy_call_count),
            parameter_h2d_bytes=int(counts.parameter_h2d_bytes),
            optix_launch_call_count=int(counts.optix_launch_call_count),
            raygen_invocation_count=int(counts.raygen_invocation_count),
            control_d2h_copy_call_count=int(
                counts.control_d2h_copy_call_count),
            control_d2h_bytes=int(counts.control_d2h_bytes),
            output_d2h_copy_call_count=int(
                counts.output_d2h_copy_call_count),
            output_d2h_bytes=int(counts.output_d2h_bytes),
            status_before_output=bool(counts.status_before_output),
            output_d2h_after_status_failure=int(
                counts.output_d2h_after_status_failure),
            blocking_boundary_count=int(
                counts.explicit_stream_sync_call_count),
        )

    def execute_complete(
            self,
            query_columns: KatSoAColumns,
            expected_output: np.ndarray,
            ) -> KatArmSuccess:
        try:
            result = self._owner.execute_complete(
                *query_columns.native_order(), expected_output)
        except PyOptixDeviceStatusError as error:
            raise KatDeviceStatusFailure(
                self.label, tuple(error.control),
                self._ledger(error.operation_counts)) from error
        return KatArmSuccess(
            arm=self.label,
            output=result.output,
            control=tuple(result.control),
            ledger=self._ledger(result.operation_counts),
        )

    def admit_exact_core_input(
            self, query_columns: KatSoAColumns,
            expected_output: np.ndarray) -> PrevalidatedParticleExecutionInput:
        return prevalidate_formal_particle_execution_input(
            *query_columns.native_order(), expected_output)

    def execute_exact_core(self, admitted: Any) -> Any:
        return self._owner.execute_exact_core_prevalidated(admitted)

    def materialize_exact_core(self, completion: Any) -> KatArmSuccess:
        result = self._owner.materialize_exact_core_completion(completion)
        return KatArmSuccess(
            arm=self.label,
            output=result.output,
            control=tuple(result.control),
            ledger=self._ledger(result.operation_counts),
        )

    def close(self) -> None:
        self._owner.close()


def prepare_public_pyoptix_kat_arm(bundle: LoadedParticleKat) -> KatArm:
    """Prepare B from the common durable assets."""

    if bundle.shape != FORMAL_PARTICLE_SHAPE:
        raise KatContractError("real B factory requires the frozen formal shape")
    static = bundle.static_input
    owner = prepare_formal_particle_owner(
        prebuilt_ptx=bundle.prebuilt_ptx,
        vertices=static.vertices,
        triangles=static.triangles,
        front_values=static.front_values,
        back_values=static.back_values,
    )
    return _PublicPyOptixKatArm(owner, bundle.deployment_capability)


_PUBLIC_D_RECEIPT_KEYS = {
    "boundary_owner_table_bytes", "control_d2h_bytes",
    "control_d2h_copy_call_count", "control_reset_h2d_bytes",
    "control_reset_h2d_copy_call_count", "host_blocking_boundary_count",
    "optix_launch_count", "output_d2h_after_status_failure",
    "output_d2h_bytes", "output_d2h_copy_call_count",
    "parameter_h2d_bytes", "parameter_h2d_copy_call_count", "query_count",
    "query_h2d_bytes", "query_h2d_copy_call_count", "schema_version",
    "status_before_output",
}


def _public_d_ledger(receipt_value: Any) -> KatExecutionLedger:
    if not isinstance(receipt_value, dict):
        try:
            receipt_value = dict(receipt_value)
        except (TypeError, ValueError) as error:
            raise KatContractError(
                "public D did not expose a native-validated receipt") from error
    receipt = _require_exact_keys(
        receipt_value, _PUBLIC_D_RECEIPT_KEYS, "public D native receipt")
    if any(type(receipt[name]) is not int for name in receipt):
        raise KatContractError("public D native receipt contains a non-integer")
    if receipt["schema_version"] != 1 \
            or receipt["boundary_owner_table_bytes"] != 0 \
            or receipt["status_before_output"] not in (0, 1):
        raise KatContractError("public D native receipt identity differs")
    query_calls = receipt["query_h2d_copy_call_count"]
    reset_calls = receipt["control_reset_h2d_copy_call_count"]
    parameter_calls = receipt["parameter_h2d_copy_call_count"]
    query_bytes = receipt["query_h2d_bytes"]
    reset_bytes = receipt["control_reset_h2d_bytes"]
    parameter_bytes = receipt["parameter_h2d_bytes"]
    return KatExecutionLedger(
        h2d_copy_call_count=query_calls + reset_calls + parameter_calls,
        h2d_bytes=query_bytes + reset_bytes + parameter_bytes,
        query_h2d_copy_call_count=query_calls,
        query_h2d_bytes=query_bytes,
        control_reset_h2d_copy_call_count=reset_calls,
        control_reset_h2d_bytes=reset_bytes,
        parameter_h2d_copy_call_count=parameter_calls,
        parameter_h2d_bytes=parameter_bytes,
        optix_launch_call_count=receipt["optix_launch_count"],
        raygen_invocation_count=receipt["query_count"],
        control_d2h_copy_call_count=receipt["control_d2h_copy_call_count"],
        control_d2h_bytes=receipt["control_d2h_bytes"],
        output_d2h_copy_call_count=receipt["output_d2h_copy_call_count"],
        output_d2h_bytes=receipt["output_d2h_bytes"],
        status_before_output=bool(receipt["status_before_output"]),
        output_d2h_after_status_failure=receipt[
            "output_d2h_after_status_failure"],
        blocking_boundary_count=receipt["host_blocking_boundary_count"],
    )


def _public_d_failure_control(value: Any) -> tuple[int, int, int, int]:
    try:
        control_value = dict(value)
    except (TypeError, ValueError) as error:
        raise KatContractError(
            "public D failure control is not a mapping") from error
    control = _require_exact_keys(control_value, {
        "error_code", "first_error", "status", "validated_row_count",
    }, "public D failure control")
    if any(type(control[name]) is not int for name in control):
        raise KatContractError("public D failure control contains a non-integer")
    return (
        control["validated_row_count"], control["first_error"],
        control["error_code"], control["status"],
    )


class _PublicVerifiedRTDLExecutableKatArm:
    label = ARM_D

    def __init__(
            self, *, loaded: Any, prepared: Any,
            device_status_error_type: type[BaseException],
            deployment_capability: DeploymentCapability) -> None:
        self._loaded = loaded
        self._prepared = prepared
        self._device_status_error_type = device_status_error_type
        self.deployment_capability = deployment_capability
        self._closed = False

    def execute_complete(
            self, query_columns: KatSoAColumns,
            expected_output: np.ndarray) -> KatArmSuccess:
        try:
            result = self._prepared.execute_complete(
                *query_columns.native_order(), expected_u32x3=expected_output)
        except self._device_status_error_type as error:
            control = _public_d_failure_control(getattr(error, "control", None))
            ledger = _public_d_ledger(getattr(error, "receipt", None))
            raise KatDeviceStatusFailure(
                self.label, control, ledger) from error
        if result.artifact_sha256 != \
                self.deployment_capability.artifact.sha256 \
                or result.ptx_sha256 != self.deployment_capability.ptx.sha256:
            raise KatContractError("public D result executable identity differs")
        return KatArmSuccess(
            arm=self.label,
            output=result.output_u32x3,
            control=tuple(result.control),
            ledger=_public_d_ledger(result.receipt),
        )

    def admit_exact_core_input(
            self, query_columns: KatSoAColumns,
            expected_output: np.ndarray) -> Any:
        return self._prepared.prevalidate_exact_core_input(
            *query_columns.native_order(), expected_u32x3=expected_output)

    def execute_exact_core(self, admitted: Any) -> Any:
        return self._prepared.execute_exact_core_prevalidated(admitted)

    def materialize_exact_core(self, completion: Any) -> KatArmSuccess:
        result = self._prepared.materialize_exact_core_completion(completion)
        if result.artifact_sha256 != \
                self.deployment_capability.artifact.sha256 \
                or result.ptx_sha256 != self.deployment_capability.ptx.sha256:
            raise KatContractError("public D result executable identity differs")
        return KatArmSuccess(
            arm=self.label,
            output=result.output_u32x3,
            control=tuple(result.control),
            ledger=_public_d_ledger(result.receipt),
        )

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._prepared.close()
        finally:
            self._loaded.close()


def prepare_public_verified_rtdlexe_kat_arm(
        bundle: LoadedParticleKat) -> KatArm:
    """Prepare D through only the public Particle RTDL executable lifecycle."""

    if bundle.shape != FORMAL_PARTICLE_SHAPE:
        raise KatContractError("real D factory requires the frozen formal shape")
    public = importlib.import_module("rtdsl.v4_particle_rtdlexe")
    capability = bundle.deployment_capability
    deployment = public.install_particle_rtdlexe_deployment(
        deployment_id=(
            "goal5814/formal-dual-arm-kat/"
            f"{capability.manifest.sha256}"),
        expected_artifact_sha256=capability.artifact.sha256,
        expected_native_sha256=capability.native.sha256,
        expected_protocol_decision_sha256=
            capability.protocol_decision.sha256,
        expected_template_semantic_sha256=
            capability.template_semantic.sha256,
    )
    loaded = public.load_particle_rtdlexe(
        bundle.paths.rtdlexe,
        deployment=deployment,
        native_library_path=bundle.paths.native_dso,
    )
    prepared = None
    try:
        if loaded.artifact_sha256 != capability.artifact.sha256 \
                or loaded.ptx_sha256 != capability.ptx.sha256 \
                or loaded.ptx_bytes != bundle.prebuilt_ptx:
            raise KatContractError("public D loaded identity differs")
        static = bundle.static_input
        public_static = public.ParticleStaticInput(
            vertices_f32=static.vertices,
            triangles_u32=static.triangles,
            front_values_u32=static.front_values,
            back_values_u32=static.back_values,
        )
        prepared = loaded.prepare(public_static)
        return _PublicVerifiedRTDLExecutableKatArm(
            loaded=loaded, prepared=prepared,
            device_status_error_type=public.ParticleDeviceStatusError,
            deployment_capability=capability,
        )
    except BaseException:
        if prepared is not None:
            prepared.close()
        loaded.close()
        raise


def _validate_ledger(
        ledger: KatExecutionLedger,
        *,
        shape: ParticleProblemShape,
        success: bool,
        ) -> None:
    expected = KatExecutionLedger(
        h2d_copy_call_count=9,
        h2d_bytes=shape.query_count * 7 * 4 + 16 + 120,
        query_h2d_copy_call_count=7,
        query_h2d_bytes=shape.query_count * 7 * 4,
        control_reset_h2d_copy_call_count=1,
        control_reset_h2d_bytes=16,
        parameter_h2d_copy_call_count=1,
        parameter_h2d_bytes=120,
        optix_launch_call_count=1,
        raygen_invocation_count=shape.query_count,
        control_d2h_copy_call_count=1,
        control_d2h_bytes=16,
        output_d2h_copy_call_count=1 if success else 0,
        output_d2h_bytes=shape.query_count * 3 * 4 if success else 0,
        status_before_output=True,
        output_d2h_after_status_failure=0,
        blocking_boundary_count=2 if success else 1,
    )
    if ledger != expected:
        raise KatContractError(
            f"KAT operation ledger differs: expected={expected}, actual={ledger}")


def _validate_success_result(
        arm: KatArm, bundle: LoadedParticleKat,
        result: KatArmSuccess) -> KatSuccessSummary:
    if not isinstance(result, KatArmSuccess) or result.arm != arm.label:
        raise KatContractError(f"{arm.label} success evidence type/label differs")
    _require_borrowed_output(
        f"{arm.label} output", result.output,
        query_count=bundle.shape.query_count)
    if result.output.flags.writeable:
        raise KatContractError(f"{arm.label} returned writable borrowed output")
    if result.control != (bundle.shape.query_count, UINT32_MAX, 0, 0):
        raise KatContractError(f"{arm.label} success control differs")
    _validate_ledger(result.ledger, shape=bundle.shape, success=True)
    if not np.array_equal(result.output, bundle.expected_output):
        raise KatContractError(f"{arm.label} success output is not exact")
    return KatSuccessSummary(
        arm=arm.label, exact=True, output_read_only=True,
        control=result.control, ledger=result.ledger)


def _run_success(
        arm: KatArm,
        bundle: LoadedParticleKat,
        ) -> KatSuccessSummary:
    result = arm.execute_complete(
        bundle.success_queries, bundle.expected_output)
    return _validate_success_result(arm, bundle, result)


def _exact_core_caller_boundary(arm: str, completion: Any) -> None:
    """Explicit untimed caller boundary between core return and materialize."""

    if arm not in (ARM_B, ARM_D) or completion is None:
        raise KatContractError("exact-core caller boundary differs")


def _run_exact_core_success(
        arm: ExactCoreKatArm,
        bundle: LoadedParticleKat,
        admitted: Any,
        caller_boundary: Callable[[str, Any], None],
        ) -> KatSuccessSummary:
    completion = arm.execute_exact_core(admitted)
    caller_boundary(arm.label, completion)
    result = arm.materialize_exact_core(completion)
    return _validate_success_result(arm, bundle, result)


def _run_expected_miss(
        arm: KatArm,
        bundle: LoadedParticleKat,
        ) -> KatFailureSummary:
    try:
        arm.execute_complete(bundle.miss_queries, bundle.expected_output)
    except KatDeviceStatusFailure as failure:
        if failure.arm != arm.label:
            raise KatContractError("device failure arm label differs") from failure
        expected_control = (
            bundle.shape.query_count - 1, 0, MISS_ERROR_CODE, 1)
        if failure.control != expected_control:
            raise KatContractError(
                f"{arm.label} miss control differs: {failure.control}") from failure
        _validate_ledger(failure.ledger, shape=bundle.shape, success=False)
        if failure.ledger.output_d2h_copy_call_count != 0 \
                or failure.ledger.output_d2h_bytes != 0:
            raise KatContractError(
                f"{arm.label} exposed output after status failure") from failure
        return KatFailureSummary(
            arm=arm.label, device_status_failure=True,
            control=failure.control, ledger=failure.ledger)
    raise KatContractError(
        f"{arm.label} deterministic miss did not fail at device status")


def run_untimed_dual_arm_kat(
        bundle: LoadedParticleKat,
        *,
        b_factory: ArmFactory = prepare_public_pyoptix_kat_arm,
        d_factory: ArmFactory,
        ) -> DualArmKatResult:
    """Run the sole fixed four-execution KAT transaction exactly once."""

    b_arm = b_factory(bundle)
    try:
        if b_arm.label != ARM_B:
            raise KatContractError("B factory returned the wrong arm label")
        if getattr(b_arm, "deployment_capability", None) \
                is not bundle.deployment_capability:
            raise KatContractError(
                "B did not install the request-external deployment capability")
        d_arm = d_factory(bundle)
        try:
            if d_arm.label != ARM_D:
                raise KatContractError("D factory returned the wrong arm label")
            if getattr(d_arm, "deployment_capability", None) \
                    is not bundle.deployment_capability:
                raise KatContractError(
                    "D did not install the request-external deployment capability")
            b_success = _run_success(b_arm, bundle)
            d_success = _run_success(d_arm, bundle)
            b_miss = _run_expected_miss(b_arm, bundle)
            d_miss = _run_expected_miss(d_arm, bundle)
            return DualArmKatResult(
                b_success=b_success,
                d_success=d_success,
                b_miss=b_miss,
                d_miss=d_miss,
                execution_order=(
                    "B_SUCCESS", "D_SUCCESS", "B_MISS", "D_MISS"),
            )
        finally:
            d_arm.close()
    finally:
        b_arm.close()


def run_untimed_dual_arm_exact_core_boundary_kat(
        bundle: LoadedParticleKat,
        *,
        b_factory: ArmFactory = prepare_public_pyoptix_kat_arm,
        d_factory: ArmFactory = prepare_public_verified_rtdlexe_kat_arm,
        caller_boundary: Callable[[str, Any], None] =
            _exact_core_caller_boundary,
        ) -> DualArmKatResult:
    """Run success through exact-core/caller/materialize for both public arms.

    The deterministic device-miss steps retain the complete compatibility API:
    a failed exact core has no successful completion to materialize.  This path
    is untimed and fixed by the target entry point; no CLI selects it.
    """

    b_arm = b_factory(bundle)
    try:
        if b_arm.label != ARM_B:
            raise KatContractError("B factory returned the wrong arm label")
        if getattr(b_arm, "deployment_capability", None) \
                is not bundle.deployment_capability:
            raise KatContractError(
                "B did not install the request-external deployment capability")
        d_arm = d_factory(bundle)
        try:
            if d_arm.label != ARM_D:
                raise KatContractError("D factory returned the wrong arm label")
            if getattr(d_arm, "deployment_capability", None) \
                    is not bundle.deployment_capability:
                raise KatContractError(
                    "D did not install the request-external deployment capability")
            b_admitted = b_arm.admit_exact_core_input(
                bundle.success_queries, bundle.expected_output)
            d_admitted = d_arm.admit_exact_core_input(
                bundle.success_queries, bundle.expected_output)
            b_success = _run_exact_core_success(
                b_arm, bundle, b_admitted, caller_boundary)
            d_success = _run_exact_core_success(
                d_arm, bundle, d_admitted, caller_boundary)
            b_miss = _run_expected_miss(b_arm, bundle)
            d_miss = _run_expected_miss(d_arm, bundle)
            return DualArmKatResult(
                b_success=b_success,
                d_success=d_success,
                b_miss=b_miss,
                d_miss=d_miss,
                execution_order=(
                    "B_SUCCESS", "D_SUCCESS", "B_MISS", "D_MISS"),
            )
        finally:
            d_arm.close()
    finally:
        b_arm.close()


def _identity_json(
        identity: ExpectedAssetAuthority | FrozenFileIdentity |
        FrozenDigestIdentity) -> dict[str, Any]:
    if isinstance(identity, ExpectedAssetAuthority):
        return {"bytes": identity.bytes, "sha256": identity.sha256}
    if isinstance(identity, FrozenDigestIdentity):
        return {"location": identity.location, "sha256": identity.sha256}
    return {
        "path": identity.path,
        "bytes": identity.bytes,
        "sha256": identity.sha256,
    }


def _control_json(control: tuple[int, int, int, int]) -> dict[str, int]:
    return {
        "validated_row_count": control[0],
        "first_error": control[1],
        "error_code": control[2],
        "status": control[3],
    }


def _success_step_json(value: KatSuccessSummary) -> dict[str, Any]:
    return {
        "arm": value.arm,
        "control": _control_json(value.control),
        "exact": value.exact,
        "kind": "SUCCESS",
        "ledger": asdict(value.ledger),
        "output_read_only": value.output_read_only,
    }


def _failure_step_json(value: KatFailureSummary) -> dict[str, Any]:
    return {
        "arm": value.arm,
        "control": _control_json(value.control),
        "device_status_failure": value.device_status_failure,
        "kind": "EXPECTED_DEVICE_MISS",
        "ledger": asdict(value.ledger),
    }


def canonical_kat_result(
        bundle: LoadedParticleKat,
        result: DualArmKatResult,
        ) -> dict[str, Any]:
    """Build post-close canonical evidence; this function performs no execute."""

    capability = bundle.deployment_capability
    return {
        "execution_order": list(result.execution_order),
        "identities": {
            "deployment_capability": {
                "schema": capability.schema,
                "artifact": _identity_json(capability.artifact),
                "native": _identity_json(capability.native),
                "ptx": _identity_json(capability.ptx),
                "source": _identity_json(capability.source),
                "descriptor": _identity_json(capability.descriptor),
                "protocol_decision": _identity_json(
                    capability.protocol_decision),
                "template_semantic": _identity_json(
                    capability.template_semantic),
            },
            "executable_manifest": _identity_json(
                bundle.executable_manifest),
            "scientific_input_manifest": _identity_json(
                bundle.scientific_manifest),
        },
        "replacement_count": result.replacement_count,
        "retry_count": result.retry_count,
        "schema": KAT_RESULT_SCHEMA,
        "status": "PASS__UNTIMED_DUAL_ARM_KAT",
        "steps": {
            "B_MISS": _failure_step_json(result.b_miss),
            "B_SUCCESS": _success_step_json(result.b_success),
            "D_MISS": _failure_step_json(result.d_miss),
            "D_SUCCESS": _success_step_json(result.d_success),
        },
        "timed": result.timed,
    }


def write_canonical_kat_result(
        output_path: Path,
        bundle: LoadedParticleKat,
        result: DualArmKatResult,
        ) -> ExpectedAssetAuthority:
    """Create the post-close result, or accept an already exact byte twin."""

    if result.timed or result.retry_count or result.replacement_count:
        raise KatContractError("refusing to serialize a non-frozen KAT result")
    output = Path(output_path)
    if not output.parent.is_dir():
        raise KatContractError("KAT output parent directory does not exist")
    encoded = _canonical_result_bytes(canonical_kat_result(bundle, result))
    try:
        with output.open("xb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        if output.read_bytes() != encoded:
            raise KatContractError(
                "KAT output exists with non-exact bytes") from None
    return ExpectedAssetAuthority(
        bytes=len(encoded), sha256=hashlib.sha256(encoded).hexdigest())


def run_untimed_dual_arm_kat_to_output(
        bundle: LoadedParticleKat,
        output_path: Path,
        *,
        b_factory: ArmFactory = prepare_public_pyoptix_kat_arm,
        d_factory: ArmFactory = prepare_public_verified_rtdlexe_kat_arm,
        ) -> tuple[DualArmKatResult, ExpectedAssetAuthority]:
    """Atomically reserve one fresh result, execute/close, then commit PASS."""

    return _run_untimed_kat_to_output(
        bundle, output_path,
        transaction=lambda: run_untimed_dual_arm_kat(
            bundle, b_factory=b_factory, d_factory=d_factory))


def run_untimed_dual_arm_exact_core_boundary_kat_to_output(
        bundle: LoadedParticleKat,
        output_path: Path,
        *,
        b_factory: ArmFactory = prepare_public_pyoptix_kat_arm,
        d_factory: ArmFactory = prepare_public_verified_rtdlexe_kat_arm,
        caller_boundary: Callable[[str, Any], None] =
            _exact_core_caller_boundary,
        ) -> tuple[DualArmKatResult, ExpectedAssetAuthority]:
    """Create-only exact-core boundary KAT; formal target entry fixes this."""

    return _run_untimed_kat_to_output(
        bundle, output_path,
        transaction=lambda: run_untimed_dual_arm_exact_core_boundary_kat(
            bundle, b_factory=b_factory, d_factory=d_factory,
            caller_boundary=caller_boundary))


def _run_untimed_kat_to_output(
        bundle: LoadedParticleKat,
        output_path: Path,
        *,
        transaction: Callable[[], DualArmKatResult],
        ) -> tuple[DualArmKatResult, ExpectedAssetAuthority]:
    """Reserve output before any factory, then run one fixed transaction."""

    output = Path(output_path)
    if not output.parent.is_dir():
        raise KatContractError("KAT output parent directory does not exist")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(output, flags, 0o644)
    except FileExistsError:
        raise KatContractError(
            "formal KAT output already exists; refusing repeated execution") \
            from None
    committed = False
    try:
        result = transaction()
        if result.timed or result.retry_count or result.replacement_count:
            raise KatContractError("refusing to serialize a non-frozen KAT result")
        encoded = _canonical_result_bytes(canonical_kat_result(bundle, result))
        offset = 0
        while offset != len(encoded):
            written = os.write(descriptor, encoded[offset:])
            if written <= 0:
                raise KatContractError("short write of formal KAT result")
            offset += written
        os.fsync(descriptor)
        committed = True
        identity = ExpectedAssetAuthority(
            bytes=len(encoded), sha256=hashlib.sha256(encoded).hexdigest())
        return result, identity
    finally:
        os.close(descriptor)
        if not committed:
            try:
                output.unlink()
            except FileNotFoundError:
                pass


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the single untimed Goal5814 dual-arm KAT")
    parser.add_argument("--scientific-input-directory", required=True)
    parser.add_argument("--prebuilt-ptx", required=True)
    parser.add_argument("--native-dso", required=True)
    parser.add_argument("--rtdlexe", required=True)
    parser.add_argument(
        "--executable-manifest", required=True)
    parser.add_argument("--output", required=True)
    return parser


def _main(argv: list[str] | None, *, exact_core_boundary: bool) -> int:
    arguments = _argument_parser().parse_args(argv)
    if FORMAL_EXECUTABLE_MANIFEST_BYTES is None \
            or FORMAL_EXECUTABLE_MANIFEST_SHA256 is None:
        raise KatContractError(
            "formal executable manifest authority is not frozen")
    executable_authority = ExpectedAssetAuthority(
        bytes=FORMAL_EXECUTABLE_MANIFEST_BYTES,
        sha256=FORMAL_EXECUTABLE_MANIFEST_SHA256)
    paths = KatAssetPaths(
        scientific_input_directory=Path(
            arguments.scientific_input_directory),
        prebuilt_ptx=Path(arguments.prebuilt_ptx),
        native_dso=Path(arguments.native_dso),
        rtdlexe=Path(arguments.rtdlexe),
        executable_manifest=Path(arguments.executable_manifest),
        executable_manifest_identity=executable_authority,
        scientific_manifest_identity=FORMAL_SCIENTIFIC_MANIFEST_IDENTITY,
    )
    bundle = load_durable_particle_kat(paths)
    if exact_core_boundary:
        result, output_identity = \
            run_untimed_dual_arm_exact_core_boundary_kat_to_output(
                bundle, Path(arguments.output),
                d_factory=prepare_public_verified_rtdlexe_kat_arm)
    else:
        result, output_identity = run_untimed_dual_arm_kat_to_output(
            bundle, Path(arguments.output),
            d_factory=prepare_public_verified_rtdlexe_kat_arm)
    if result.timed or result.retry_count or result.replacement_count:
        raise KatContractError("untimed single-transaction result drifted")
    print(
        "PASS Goal5814 untimed dual-arm KAT: "
        "B/D exact success and deterministic device miss; output D2H zero; "
        f"exact_core_boundary={str(exact_core_boundary).lower()}; "
        f"result_sha256={output_identity.sha256}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Compatibility complete-execute KAT entry point."""

    return _main(argv, exact_core_boundary=False)


def main_exact_core_boundary(argv: list[str] | None = None) -> int:
    """Formal untimed exact-core/caller/materialize KAT entry point."""

    return _main(argv, exact_core_boundary=True)


if __name__ == "__main__":
    raise SystemExit(main())

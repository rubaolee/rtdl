"""Standard-library derivation of exact Goal5848 AOT cache requests."""

from __future__ import annotations

from collections.abc import Mapping

from rtdsl.v4_aot_cache import ExactAOTBuildRequest

from .contracts import RELATION_TASK, TRIANGLE_TASK, digest

TASK_REQUESTS = {
    RELATION_TASK: {
        "family": "custom_aabb_bounded_relation_v1",
        "route_identity": "v4_callback_ir:custom_aabb_bounded_relation_v1",
        "task_semantics_sha256": (
            "644d26ebb0bca31b6d7a9c1e8ec1adb9d056a809f25fa630722bfae6e0e176ec"
        ),
        "label": "relation",
    },
    TRIANGLE_TASK: {
        "family": "builtin_triangle_reduction_v1",
        "route_identity": (
            "v4_builtin_triangle_callback_ir:checked_reduction_v1"
        ),
        "task_semantics_sha256": (
            "05821cab689ab737f98814cb11ab0ff1f4ef12ee97fc5d81f01ea6d7084f61c2"
        ),
        "label": "triangle",
    },
}


def target_sha256(
    *,
    native_library_sha256: str,
    optix_sdk: str,
    compute_capability: str,
) -> str:
    return digest({
        "provider": "optix",
        "optix_sdk": optix_sdk,
        "compute_capability": compute_capability,
        "native_sha256": native_library_sha256,
        "supports_custom_aabb": True,
        "supports_builtin_triangle": True,
        "max_graph_depth": 1,
        "triangle_front_hit_kind": 0xFE,
        "triangle_back_hit_kind": 0xFF,
    })


def request_for_task(
    task: str,
    *,
    source_commit: str,
    source_tree: str,
    native_library_sha256: str,
    native_build_manifest_sha256: str,
    optix_sdk: str,
    compute_capability: str,
    python_version: str,
    numba_version: str,
    numpy_version: str,
    llvmlite_version: str,
    cuda_toolkit_version: str,
    build_roots: Mapping[str, object],
    trust_root_file_sha256: str,
) -> ExactAOTBuildRequest:
    try:
        task_row = TASK_REQUESTS[task]
    except KeyError as error:
        raise ValueError(f"unsupported Goal5848 AOT task: {task}") from error
    label = str(task_row["label"])
    deployment_id = f"goal5848-{label}-slot"
    target = target_sha256(
        native_library_sha256=native_library_sha256,
        optix_sdk=optix_sdk,
        compute_capability=compute_capability,
    )
    toolchain = {
        "schema": "rtdl.goal5848.aot_toolchain_request.v1",
        "compute_capability": compute_capability,
        "optix_sdk": optix_sdk,
        "cuda_toolkit_version": cuda_toolkit_version,
        "python_version": python_version,
        "numba_version": numba_version,
        "numpy_version": numpy_version,
        "llvmlite_version": llvmlite_version,
        "native_build_manifest_sha256": native_build_manifest_sha256,
    }
    compiler_sources = {
        "schema": "rtdl.goal5848.compiler_source_request.v1",
        "source_tree": source_tree,
        "native_build_manifest_sha256": native_build_manifest_sha256,
        "task": task,
        "route_identity": task_row["route_identity"],
    }
    signing_policy = {
        "schema": "rtdl.goal5848.test_signing_policy.v1",
        "algorithm": "rsa-pkcs1-v1_5-sha256",
        "key_bits": 2048,
        "key_id": f"TEST_ONLY_goal5848_{label}",
        "private_key_path_unlinked_after_freeze": True,
        "production_key_custody_attested": False,
        "trust_root_file_sha256": trust_root_file_sha256,
    }
    return ExactAOTBuildRequest(
        source_commit=source_commit,
        source_tree=source_tree,
        family=str(task_row["family"]),
        route_identity=str(task_row["route_identity"]),
        deployment_id=deployment_id,
        task_semantics_sha256=str(task_row["task_semantics_sha256"]),
        native_library_sha256=native_library_sha256,
        target_sha256=target,
        toolchain_sha256=digest(toolchain),
        build_roots_sha256=digest(dict(build_roots)),
        compiler_source_manifest_sha256=digest(compiler_sources),
        signing_policy_sha256=digest(signing_policy),
        trust_root_file_sha256=trust_root_file_sha256,
    )


__all__ = ["TASK_REQUESTS", "request_for_task", "target_sha256"]

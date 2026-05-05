from __future__ import annotations

from typing import Any


def generic_prepared_anyhit_count_backend_status() -> tuple[dict[str, Any], ...]:
    """Return v1.5 prepared ANY_HIT/COUNT_HITS backend status."""
    return (
        {
            "backend": "optix",
            "status": "implemented",
            "role": "nvidia_rt_target",
            "prepared_semantics": "build_scene_once_prepare_rays_once_repeat_count_queries",
            "api": "run_generic_prepared_ray_triangle_any_hit_count",
            "public_wording_authorized": False,
        },
        {
            "backend": "embree",
            "status": "blocked_pending_scene_probe_split",
            "role": "cpu_rt_baseline_and_fallback",
            "prepared_semantics": "needs_build_scene_once_probe_many_contract",
            "api": "not_yet_implemented_for_prepared_generic_count",
            "public_wording_authorized": False,
        },
        {
            "backend": "vulkan",
            "status": "frozen_before_v2_1",
            "role": "compatibility_or_inactive",
            "prepared_semantics": "not_active_v1_5_target",
            "api": "not_applicable",
            "public_wording_authorized": False,
        },
        {
            "backend": "hiprt",
            "status": "frozen_before_v2_1",
            "role": "compatibility_or_inactive",
            "prepared_semantics": "not_active_v1_5_target",
            "api": "not_applicable",
            "public_wording_authorized": False,
        },
        {
            "backend": "apple_rt",
            "status": "frozen_before_v2_1",
            "role": "compatibility_or_inactive",
            "prepared_semantics": "not_active_v1_5_target",
            "api": "not_applicable",
            "public_wording_authorized": False,
        },
    )


def generic_prepared_anyhit_count_blockers() -> tuple[str, ...]:
    return (
        "Embree needs an app-name-free prepared scene/probe split or an explicitly accepted fallback contract.",
        "Same-contract parity must compare OptiX prepared count against Embree under a documented prepared semantics.",
        "NVIDIA performance evidence still requires a pod run; local status is not public wording evidence.",
        "Vulkan, HIPRT, and Apple RT remain frozen before v2.1.",
    )

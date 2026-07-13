#!/usr/bin/env python3
"""Patch an X-HD author source tree to emit lb status-machine trace fields.

This is an app-owned paper-reproduction helper. It does not modify RTDL core.
The patch is deliberately textual and fail-closed: if the expected author
source snippets are absent, it raises instead of guessing.
"""

from __future__ import annotations

import argparse
from pathlib import Path


LAUNCH_REL = Path("src/rt/launch_parameters.h")
SHADER_REL = Path("src/rt/shaders/shaders_nn_uniform_grid.cu")
RT_REL = Path("src/hd_impl/hausdorff_distance_rt.h")

MARKER = "RTDL_GOAL5374_LB_STATUS_TRACE"


def _replace_once(text: str, old: str, new: str, *, path: Path) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one match in {path}, found {count}: {old[:80]!r}")
    return text.replace(old, new)


def patch_launch_parameters(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    old = """  dev::Queue<uint32_t> offloading_point_ids;
  uint32_t* offloading_cell_ids;
"""
    new = """  dev::Queue<uint32_t> offloading_point_ids;
  uint32_t* offloading_cell_ids;
  // RTDL_GOAL5374_LB_STATUS_TRACE: optional app-owned instrumentation counters.
  uint64_t* status_offloading_count;
  uint64_t* status_cmax2_abort_count;
  uint64_t* status_point_loop_abort_count;
"""
    path.write_text(_replace_once(text, old, new, path=path), encoding="utf-8")
    return True


def patch_shader(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False

    text = _replace_once(
        text,
        """  if (params.prune && max_dist2 <= *params.cmax2) {
    update_cmin2(max_dist2);
    update_status(ShaderStatus::kAborted);
    optixReportIntersection(0, 0);
  }
""",
        """  if (params.prune && max_dist2 <= *params.cmax2) {
    if (params.status_cmax2_abort_count != nullptr) {
      atomicAdd(reinterpret_cast<unsigned long long*>(params.status_cmax2_abort_count), 1ULL);
    }
    update_cmin2(max_dist2);
    update_status(ShaderStatus::kAborted);
    optixReportIntersection(0, 0);
  }
""",
        path=path,
    )
    text = _replace_once(
        text,
        """  if (np_in_cell > params.processing_threshold) {
    auto tail = params.offloading_point_ids.Append(in_q_idx);
    params.offloading_cell_ids[tail] = mbr_id;
    update_status(ShaderStatus::kOffloading);
    return;
  }
""",
        """  if (np_in_cell > params.processing_threshold) {
    if (params.status_offloading_count != nullptr) {
      atomicAdd(reinterpret_cast<unsigned long long*>(params.status_offloading_count), 1ULL);
    }
    auto tail = params.offloading_point_ids.Append(in_q_idx);
    params.offloading_cell_ids[tail] = mbr_id;
    update_status(ShaderStatus::kOffloading);
    return;
  }
""",
        path=path,
    )
    text = _replace_once(
        text,
        """    if (params.eb && dist2 <= *params.cmax2) {
      optixSetPayload_2(optixGetPayload_2() + (offset - begin + 1));
      update_status(ShaderStatus::kAborted);
      optixReportIntersection(0, 0);  // return implicitly
    }
""",
        """    if (params.eb && dist2 <= *params.cmax2) {
      if (params.status_point_loop_abort_count != nullptr) {
        atomicAdd(reinterpret_cast<unsigned long long*>(params.status_point_loop_abort_count), 1ULL);
      }
      optixSetPayload_2(optixGetPayload_2() + (offset - begin + 1));
      update_status(ShaderStatus::kAborted);
      optixReportIntersection(0, 0);  // return implicitly
    }
""",
        path=path,
    )
    text = "// RTDL_GOAL5374_LB_STATUS_TRACE\n" + text
    path.write_text(text, encoding="utf-8")
    return True


def patch_rt_impl(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False

    text = _replace_once(
        text,
        """      rmm::device_uvector<coord_t> cmin2(batch_size, stream);
      stream.synchronize();
""",
        """      rmm::device_uvector<coord_t> cmin2(batch_size, stream);
      rmm::device_uvector<uint64_t> rtdl_goal5374_status_trace_counts(3, stream);
      stream.synchronize();
""",
        path=path,
    )
    text = _replace_once(
        text,
        """      size_t total_offloading_size = 0;
      // Batch process to reduce peak memory usage
""",
        """      size_t total_offloading_size = 0;
      uint64_t rtdl_goal5374_total_status_offloading_count = 0;
      uint64_t rtdl_goal5374_total_cmax2_abort_count = 0;
      uint64_t rtdl_goal5374_total_point_loop_abort_count = 0;
      uint64_t rtdl_goal5374_total_raw_offload_author_width_bytes = 0;
      nlohmann::json rtdl_goal5374_batch_trace = nlohmann::json::array();
      // Batch process to reduce peak memory usage
""",
        path=path,
    )
    text = _replace_once(
        text,
        """        thrust::fill(rmm::exec_policy_nosync(stream), cmin2.begin(), cmin2.end(),
                     std::numeric_limits<coord_t>::max());
""",
        """        thrust::fill(rmm::exec_policy_nosync(stream), cmin2.begin(), cmin2.end(),
                     std::numeric_limits<coord_t>::max());
        thrust::fill(rmm::exec_policy_nosync(stream),
                     rtdl_goal5374_status_trace_counts.begin(),
                     rtdl_goal5374_status_trace_counts.end(), uint64_t{0});
""",
        path=path,
    )
    text = _replace_once(
        text,
        """        params.offloading_point_ids = offloading_point_ids_.DeviceObject();
        params.offloading_cell_ids = offloading_cell_ids_.data();
        params.prune = config_.prune;
""",
        """        params.offloading_point_ids = offloading_point_ids_.DeviceObject();
        params.offloading_cell_ids = offloading_cell_ids_.data();
        params.status_offloading_count = rtdl_goal5374_status_trace_counts.data();
        params.status_cmax2_abort_count = rtdl_goal5374_status_trace_counts.data() + 1;
        params.status_point_loop_abort_count = rtdl_goal5374_status_trace_counts.data() + 2;
        params.prune = config_.prune;
""",
        path=path,
    )
    text = _replace_once(
        text,
        """        auto offloading_size = offloading_point_ids_.size(stream);
        wl_heavy_peak_bytes = std::max(
            wl_heavy_peak_bytes,
            (uint32_t)(offloading_size * 2 *
                       sizeof(uint32_t)));  // offloading_point_ids_+offloading_cell_ids_
        total_offloading_size += offloading_size;
        loadBalanceProcessing(
""",
        """        auto offloading_size = offloading_point_ids_.size(stream);
        uint64_t rtdl_goal5374_status_counts_host[3] = {0, 0, 0};
        CUDA_CHECK(cudaMemcpyAsync(
            rtdl_goal5374_status_counts_host, rtdl_goal5374_status_trace_counts.data(),
            sizeof(rtdl_goal5374_status_counts_host), cudaMemcpyDeviceToHost, stream.value()));
        stream.synchronize();
        const uint64_t rtdl_goal5374_raw_author_width_bytes =
            static_cast<uint64_t>(offloading_size) * 2ull * sizeof(uint32_t);
        wl_heavy_peak_bytes = std::max(
            wl_heavy_peak_bytes,
            (uint32_t)(offloading_size * 2 *
                       sizeof(uint32_t)));  // offloading_point_ids_+offloading_cell_ids_
        total_offloading_size += offloading_size;
        rtdl_goal5374_total_status_offloading_count += rtdl_goal5374_status_counts_host[0];
        rtdl_goal5374_total_cmax2_abort_count += rtdl_goal5374_status_counts_host[1];
        rtdl_goal5374_total_point_loop_abort_count += rtdl_goal5374_status_counts_host[2];
        rtdl_goal5374_total_raw_offload_author_width_bytes += rtdl_goal5374_raw_author_width_bytes;
        rtdl_goal5374_batch_trace.push_back({
            {"Batch", batch},
            {"ActiveInQueueSize", valid_batch_size},
            {"RawOffloadRowsBeforeSortReduce", offloading_size},
            {"RawOffloadRowsAuthorWidthBytes", rtdl_goal5374_raw_author_width_bytes},
            {"StatusInitCount", valid_batch_size},
            {"StatusOffloadingAppendCount", rtdl_goal5374_status_counts_host[0]},
            {"StatusCmax2MbrAbortCount", rtdl_goal5374_status_counts_host[1]},
            {"StatusPointLoopEarlyBreakCount", rtdl_goal5374_status_counts_host[2]}
        });
        loadBalanceProcessing(
""",
        path=path,
    )
    text = _replace_once(
        text,
        """      json_iter["OffloadingSize"] = total_offloading_size;
      json_iter["CUDATime"] = cuda_time;
      json_iter["Radius"] = radius;
""",
        """      json_iter["OffloadingSize"] = total_offloading_size;
      json_iter["LBTrace"] = {
          {"Schema", "rtdl.goal5374.author.lb_status_trace.v1"},
          {"ActiveInQueueSize", in_size},
          {"RawOffloadRowsBeforeSortReduce", total_offloading_size},
          {"RawOffloadRowsAuthorWidthBytes", rtdl_goal5374_total_raw_offload_author_width_bytes},
          {"StatusInitCount", in_size},
          {"StatusOffloadingAppendCount", rtdl_goal5374_total_status_offloading_count},
          {"StatusCmax2MbrAbortCount", rtdl_goal5374_total_cmax2_abort_count},
          {"StatusPointLoopEarlyBreakCount", rtdl_goal5374_total_point_loop_abort_count},
          {"Batches", rtdl_goal5374_batch_trace}
      };
      json_iter["CUDATime"] = cuda_time;
      json_iter["Radius"] = radius;
""",
        path=path,
    )
    text = "// RTDL_GOAL5374_LB_STATUS_TRACE\n" + text
    path.write_text(text, encoding="utf-8")
    return True


def patch_author_root(author_root: Path) -> dict[str, bool]:
    if not author_root.exists():
        raise FileNotFoundError(author_root)
    paths = {
        "launch_parameters": author_root / LAUNCH_REL,
        "shader": author_root / SHADER_REL,
        "rt_impl": author_root / RT_REL,
    }
    for label, path in paths.items():
        if not path.exists():
            raise FileNotFoundError(f"missing {label}: {path}")
    return {
        "launch_parameters": patch_launch_parameters(paths["launch_parameters"]),
        "shader": patch_shader(paths["shader"]),
        "rt_impl": patch_rt_impl(paths["rt_impl"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--author-root", required=True, type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()

    changed = patch_author_root(args.author_root)
    payload = {
        "schema": "rtdl.paper_reproduction.xhd.goal5374.author_lb_status_trace_instrumentation_patch.v1",
        "author_root": str(args.author_root),
        "changed": changed,
        "marker": MARKER,
        "patched": True,
    }
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(__import__("json").dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(__import__("json").dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

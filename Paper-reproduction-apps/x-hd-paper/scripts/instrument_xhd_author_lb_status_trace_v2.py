#!/usr/bin/env python3
"""Patch an X-HD author source tree to emit lb status trace v2 fields.

This is an app-owned paper-reproduction helper. It modifies only the external
author source tree and is deliberately textual/fail-closed. If the expected
author source snippets are absent, it raises instead of guessing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


LAUNCH_REL = Path("src/rt/launch_parameters.h")
SHADER_REL = Path("src/rt/shaders/shaders_nn_uniform_grid.cu")
RT_REL = Path("src/hd_impl/hausdorff_distance_rt.h")

MARKER = "RTDL_GOAL5385_LB_STATUS_TRACE_V2"
SCHEMA = "rtdl.goal5385.author.lb_status_trace.v2"


def _replace_once(text: str, old: str, new: str, *, path: Path) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one match in {path}, found {count}: {old[:120]!r}")
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
  // RTDL_GOAL5385_LB_STATUS_TRACE_V2: optional app-owned oracle counters.
  uint64_t* status_offloading_count;
  uint64_t* status_cmax2_abort_count;
  uint64_t* status_point_loop_abort_count;
  uint64_t* status_miss_count;
  uint64_t* status_completed_count;
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
    text = _replace_once(
        text,
        """      if (cmin2 != std::numeric_limits<coord_t>::max()) {
        atomicMax(params.cmax2, cmin2);
      } else {
        params.miss_queue.Append(point_id_a);
      }
""",
        """      if (cmin2 != std::numeric_limits<coord_t>::max()) {
        if (params.status_completed_count != nullptr) {
          atomicAdd(reinterpret_cast<unsigned long long*>(params.status_completed_count), 1ULL);
        }
        atomicMax(params.cmax2, cmin2);
      } else {
        if (params.status_miss_count != nullptr) {
          atomicAdd(reinterpret_cast<unsigned long long*>(params.status_miss_count), 1ULL);
        }
        params.miss_queue.Append(point_id_a);
      }
""",
        path=path,
    )
    text = "// RTDL_GOAL5385_LB_STATUS_TRACE_V2\n" + text
    path.write_text(text, encoding="utf-8")
    return True


HELPER_SNIPPET = r"""    auto rtdl_goal5385_hash_bytes = [](const void* data, size_t byte_count) {
      const auto* bytes = reinterpret_cast<const unsigned char*>(data);
      uint64_t hash = 1469598103934665603ull;
      for (size_t i = 0; i < byte_count; ++i) {
        hash ^= static_cast<uint64_t>(bytes[i]);
        hash *= 1099511628211ull;
      }
      return hash;
    };
    auto rtdl_goal5385_hash_coord_vector =
        [&](const std::vector<coord_t>& values) -> uint64_t {
      if (values.empty()) return 1469598103934665603ull;
      return rtdl_goal5385_hash_bytes(values.data(), values.size() * sizeof(coord_t));
    };
    auto rtdl_goal5385_hash_u32_vectors =
        [&](const std::vector<uint32_t>& first, const std::vector<uint32_t>& second) -> uint64_t {
      uint64_t hash = 1469598103934665603ull;
      if (!first.empty()) {
        hash ^= rtdl_goal5385_hash_bytes(first.data(), first.size() * sizeof(uint32_t));
        hash *= 1099511628211ull;
      }
      if (!second.empty()) {
        hash ^= rtdl_goal5385_hash_bytes(second.data(), second.size() * sizeof(uint32_t));
        hash *= 1099511628211ull;
      }
      return hash;
    };
    auto rtdl_goal5385_sample_indices = [](uint32_t size) {
      std::vector<uint32_t> indices;
      if (size == 0) return indices;
      indices.push_back(0);
      if (size > 2) indices.push_back(size / 2);
      if (size > 1) indices.push_back(size - 1);
      indices.erase(std::unique(indices.begin(), indices.end()), indices.end());
      return indices;
    };
    auto rtdl_goal5385_sample_coord_values =
        [](const std::vector<coord_t>& values, const std::vector<uint32_t>& indices) {
      nlohmann::json out = nlohmann::json::array();
      for (auto idx : indices) {
        if (idx < values.size()) out.push_back(values[idx]);
      }
      return out;
    };
    auto rtdl_goal5385_sample_u32_values =
        [](const std::vector<uint32_t>& values, const std::vector<uint32_t>& indices) {
      nlohmann::json out = nlohmann::json::array();
      for (auto idx : indices) {
        if (idx < values.size()) out.push_back(values[idx]);
      }
      return out;
    };
"""


def patch_rt_impl(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False

    text = _replace_once(
        text,
        """    stats["Profiling"] = config_.profiling;
    if (config_.profiling) {
""",
        f"""    stats["Profiling"] = config_.profiling;
{HELPER_SNIPPET}
    if (config_.profiling) {{
""",
        path=path,
    )
    text = _replace_once(
        text,
        """      rmm::device_uvector<coord_t> cmin2(batch_size, stream);
      stream.synchronize();
""",
        """      rmm::device_uvector<coord_t> cmin2(batch_size, stream);
      rmm::device_uvector<uint64_t> rtdl_goal5385_status_trace_counts(5, stream);
      rmm::device_uvector<uint64_t> rtdl_goal5385_load_balance_feedback_count(1, stream);
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
      uint64_t rtdl_goal5385_total_status_offloading_count = 0;
      uint64_t rtdl_goal5385_total_status_aborted_count = 0;
      uint64_t rtdl_goal5385_total_status_miss_count = 0;
      uint64_t rtdl_goal5385_total_status_completed_count = 0;
      uint64_t rtdl_goal5385_total_cmax2_abort_count = 0;
      uint64_t rtdl_goal5385_total_point_loop_abort_count = 0;
      uint64_t rtdl_goal5385_total_load_balance_feedback_update_count = 0;
      nlohmann::json rtdl_goal5385_batch_trace = nlohmann::json::array();
      // Batch process to reduce peak memory usage
""",
        path=path,
    )
    text = _replace_once(
        text,
        """        thrust::fill(rmm::exec_policy_nosync(stream), cmin2.begin(), cmin2.end(),
                     std::numeric_limits<coord_t>::max());

        ArrayView<uint32_t> v_in_queue(in_queue.data() + batch_begin, valid_batch_size);
""",
        """        thrust::fill(rmm::exec_policy_nosync(stream), cmin2.begin(), cmin2.end(),
                     std::numeric_limits<coord_t>::max());
        thrust::fill(rmm::exec_policy_nosync(stream),
                     rtdl_goal5385_status_trace_counts.begin(),
                     rtdl_goal5385_status_trace_counts.end(), uint64_t{0});
        thrust::fill(rmm::exec_policy_nosync(stream),
                     rtdl_goal5385_load_balance_feedback_count.begin(),
                     rtdl_goal5385_load_balance_feedback_count.end(), uint64_t{0});

        std::vector<coord_t> rtdl_goal5385_cmin2_initial_host(valid_batch_size);
        if (valid_batch_size > 0) {
          CUDA_CHECK(cudaMemcpyAsync(rtdl_goal5385_cmin2_initial_host.data(), cmin2.data(),
                                     sizeof(coord_t) * valid_batch_size,
                                     cudaMemcpyDeviceToHost, stream.value()));
        }
        stream.synchronize();
        auto rtdl_goal5385_cmin2_sample_indices =
            rtdl_goal5385_sample_indices(valid_batch_size);

        ArrayView<uint32_t> v_in_queue(in_queue.data() + batch_begin, valid_batch_size);
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
        params.status_offloading_count = rtdl_goal5385_status_trace_counts.data();
        params.status_cmax2_abort_count = rtdl_goal5385_status_trace_counts.data() + 1;
        params.status_point_loop_abort_count = rtdl_goal5385_status_trace_counts.data() + 2;
        params.status_miss_count = rtdl_goal5385_status_trace_counts.data() + 3;
        params.status_completed_count = rtdl_goal5385_status_trace_counts.data() + 4;
        params.prune = config_.prune;
""",
        path=path,
    )
    text = _replace_once(
        text,
        """        CUDA_CHECK(cudaMemcpyAsync(params_buffer.data(), &params, params_buffer.size(),
                                   cudaMemcpyHostToDevice, stream.value()));

        config_.rt_engine->Render(stream.value(), params_buffer.data(),
""",
        """        CUDA_CHECK(cudaMemcpyAsync(params_buffer.data(), &params, params_buffer.size(),
                                   cudaMemcpyHostToDevice, stream.value()));

        const coord_t rtdl_goal5385_cmax2_before_ray = cmax2_.value(stream);
        config_.rt_engine->Render(stream.value(), params_buffer.data(),
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
            stream, ArrayView<point_t>(points_a), ArrayView<point_t>(points_b),
            ArrayView<uint32_t>(offloading_point_ids_.data(), offloading_size),
            ArrayView<uint32_t>(offloading_cell_ids_.data(), offloading_size),
            ArrayView<coord_t>(cmin2.data(), valid_batch_size), v_in_queue, grid,
            ArrayView<mbr_t>(mbrs_b.data(), mbrs_b.size()), radius);
        stream.synchronize();
        sw.stop();
        cuda_time += sw.ms();
""",
        """        auto offloading_size = offloading_point_ids_.size(stream);
        uint64_t rtdl_goal5385_status_counts_host[5] = {0, 0, 0, 0, 0};
        CUDA_CHECK(cudaMemcpyAsync(
            rtdl_goal5385_status_counts_host, rtdl_goal5385_status_trace_counts.data(),
            sizeof(rtdl_goal5385_status_counts_host), cudaMemcpyDeviceToHost, stream.value()));
        std::vector<coord_t> rtdl_goal5385_cmin2_after_ray_host(valid_batch_size);
        if (valid_batch_size > 0) {
          CUDA_CHECK(cudaMemcpyAsync(rtdl_goal5385_cmin2_after_ray_host.data(), cmin2.data(),
                                     sizeof(coord_t) * valid_batch_size,
                                     cudaMemcpyDeviceToHost, stream.value()));
        }
        std::vector<uint32_t> rtdl_goal5385_offload_point_ids_host(offloading_size);
        std::vector<uint32_t> rtdl_goal5385_offload_cell_ids_host(offloading_size);
        if (offloading_size > 0) {
          CUDA_CHECK(cudaMemcpyAsync(rtdl_goal5385_offload_point_ids_host.data(),
                                     offloading_point_ids_.data(),
                                     sizeof(uint32_t) * offloading_size,
                                     cudaMemcpyDeviceToHost, stream.value()));
          CUDA_CHECK(cudaMemcpyAsync(rtdl_goal5385_offload_cell_ids_host.data(),
                                     offloading_cell_ids_.data(),
                                     sizeof(uint32_t) * offloading_size,
                                     cudaMemcpyDeviceToHost, stream.value()));
        }
        stream.synchronize();
        const coord_t rtdl_goal5385_cmax2_after_ray = cmax2_.value(stream);
        const uint64_t rtdl_goal5385_raw_offload_hash =
            rtdl_goal5385_hash_u32_vectors(rtdl_goal5385_offload_point_ids_host,
                                           rtdl_goal5385_offload_cell_ids_host);
        auto rtdl_goal5385_offload_sample_indices =
            rtdl_goal5385_sample_indices(static_cast<uint32_t>(offloading_size));

        wl_heavy_peak_bytes = std::max(
            wl_heavy_peak_bytes,
            (uint32_t)(offloading_size * 2 *
                       sizeof(uint32_t)));  // offloading_point_ids_+offloading_cell_ids_
        total_offloading_size += offloading_size;
        auto rtdl_goal5385_load_balance_group_count = loadBalanceProcessing(
            stream, ArrayView<point_t>(points_a), ArrayView<point_t>(points_b),
            ArrayView<uint32_t>(offloading_point_ids_.data(), offloading_size),
            ArrayView<uint32_t>(offloading_cell_ids_.data(), offloading_size),
            ArrayView<coord_t>(cmin2.data(), valid_batch_size), v_in_queue, grid,
            ArrayView<mbr_t>(mbrs_b.data(), mbrs_b.size()), radius,
            rtdl_goal5385_load_balance_feedback_count.data());
        stream.synchronize();
        uint64_t rtdl_goal5385_load_balance_feedback_update_count_host = 0;
        CUDA_CHECK(cudaMemcpyAsync(&rtdl_goal5385_load_balance_feedback_update_count_host,
                                   rtdl_goal5385_load_balance_feedback_count.data(),
                                   sizeof(uint64_t), cudaMemcpyDeviceToHost,
                                   stream.value()));
        std::vector<coord_t> rtdl_goal5385_cmin2_after_load_balance_host(valid_batch_size);
        if (valid_batch_size > 0) {
          CUDA_CHECK(cudaMemcpyAsync(rtdl_goal5385_cmin2_after_load_balance_host.data(),
                                     cmin2.data(), sizeof(coord_t) * valid_batch_size,
                                     cudaMemcpyDeviceToHost, stream.value()));
        }
        stream.synchronize();
        const coord_t rtdl_goal5385_cmax2_after_load_balance = cmax2_.value(stream);

        const uint64_t rtdl_goal5385_status_aborted_count =
            rtdl_goal5385_status_counts_host[1] + rtdl_goal5385_status_counts_host[2];
        rtdl_goal5385_total_status_offloading_count += rtdl_goal5385_status_counts_host[0];
        rtdl_goal5385_total_status_aborted_count += rtdl_goal5385_status_aborted_count;
        rtdl_goal5385_total_status_miss_count += rtdl_goal5385_status_counts_host[3];
        rtdl_goal5385_total_status_completed_count += rtdl_goal5385_status_counts_host[4];
        rtdl_goal5385_total_cmax2_abort_count += rtdl_goal5385_status_counts_host[1];
        rtdl_goal5385_total_point_loop_abort_count += rtdl_goal5385_status_counts_host[2];
        rtdl_goal5385_total_load_balance_feedback_update_count +=
            rtdl_goal5385_load_balance_feedback_update_count_host;

        rtdl_goal5385_batch_trace.push_back({
            {"batch_index", batch},
            {"iteration_index", iter + 1},
            {"radius", radius},
            {"active_in_queue_size", valid_batch_size},
            {"cmax2_before_ray", rtdl_goal5385_cmax2_before_ray},
            {"cmax2_after_ray", rtdl_goal5385_cmax2_after_ray},
            {"cmax2_after_load_balance", rtdl_goal5385_cmax2_after_load_balance},
            {"cmin2_initial_hash", rtdl_goal5385_hash_coord_vector(rtdl_goal5385_cmin2_initial_host)},
            {"cmin2_after_ray_hash", rtdl_goal5385_hash_coord_vector(rtdl_goal5385_cmin2_after_ray_host)},
            {"cmin2_after_load_balance_hash", rtdl_goal5385_hash_coord_vector(rtdl_goal5385_cmin2_after_load_balance_host)},
            {"cmin2_sample_indices", rtdl_goal5385_cmin2_sample_indices},
            {"cmin2_initial_samples", rtdl_goal5385_sample_coord_values(rtdl_goal5385_cmin2_initial_host, rtdl_goal5385_cmin2_sample_indices)},
            {"cmin2_after_ray_samples", rtdl_goal5385_sample_coord_values(rtdl_goal5385_cmin2_after_ray_host, rtdl_goal5385_cmin2_sample_indices)},
            {"cmin2_after_load_balance_samples", rtdl_goal5385_sample_coord_values(rtdl_goal5385_cmin2_after_load_balance_host, rtdl_goal5385_cmin2_sample_indices)},
            {"raw_offload_rows_before_sort_reduce", offloading_size},
            {"raw_offload_row_hash", rtdl_goal5385_raw_offload_hash},
            {"raw_offload_row_sample_point_ids", rtdl_goal5385_sample_u32_values(rtdl_goal5385_offload_point_ids_host, rtdl_goal5385_offload_sample_indices)},
            {"raw_offload_row_sample_cell_ids", rtdl_goal5385_sample_u32_values(rtdl_goal5385_offload_cell_ids_host, rtdl_goal5385_offload_sample_indices)},
            {"status_count_init", valid_batch_size},
            {"status_count_offloading", rtdl_goal5385_status_counts_host[0]},
            {"status_count_aborted", rtdl_goal5385_status_aborted_count},
            {"status_count_miss", rtdl_goal5385_status_counts_host[3]},
            {"status_count_completed", rtdl_goal5385_status_counts_host[4]},
            {"cmax2_mbr_abort_count", rtdl_goal5385_status_counts_host[1]},
            {"point_loop_early_break_count", rtdl_goal5385_status_counts_host[2]},
            {"load_balance_input_row_count", offloading_size},
            {"load_balance_group_count", rtdl_goal5385_load_balance_group_count},
            {"load_balance_feedback_update_count", rtdl_goal5385_load_balance_feedback_update_count_host}
        });
        sw.stop();
        cuda_time += sw.ms();
""",
        path=path,
    )
    text = _replace_once(
        text,
        """      json_iter["OffloadingSize"] = total_offloading_size;
      json_iter["CUDATime"] = cuda_time;
      json_iter["Radius"] = radius;
""",
        f"""      json_iter["OffloadingSize"] = total_offloading_size;
      json_iter["LBTraceV2"] = {{
          {{"Schema", "{SCHEMA}"}},
          {{"ActiveInQueueSize", in_size}},
          {{"RawOffloadRowsBeforeSortReduce", total_offloading_size}},
          {{"StatusInitCount", in_size}},
          {{"StatusOffloadingAppendCount", rtdl_goal5385_total_status_offloading_count}},
          {{"StatusAbortedCount", rtdl_goal5385_total_status_aborted_count}},
          {{"StatusMissCount", rtdl_goal5385_total_status_miss_count}},
          {{"StatusCompletedCount", rtdl_goal5385_total_status_completed_count}},
          {{"StatusCmax2MbrAbortCount", rtdl_goal5385_total_cmax2_abort_count}},
          {{"StatusPointLoopEarlyBreakCount", rtdl_goal5385_total_point_loop_abort_count}},
          {{"LoadBalanceFeedbackUpdateCount", rtdl_goal5385_total_load_balance_feedback_update_count}},
          {{"Batches", rtdl_goal5385_batch_trace}}
      }};
      json_iter["CUDATime"] = cuda_time;
      json_iter["Radius"] = radius;
""",
        path=path,
    )
    text = _replace_once(
        text,
        """  void loadBalanceProcessing(rmm::cuda_stream_view stream, ArrayView<point_t> points_a,
                             ArrayView<point_t> points_b,
                             ArrayView<uint32_t> offloading_point_ids,
                             ArrayView<uint32_t> offloading_cell_ids,
                             ArrayView<coord_t> cmin2, ArrayView<uint32_t> point_a_ids,
                             const grid_t& grid, ArrayView<mbr_t> mbrs_b,
                             coord_t radius) {
""",
        """  uint32_t loadBalanceProcessing(rmm::cuda_stream_view stream, ArrayView<point_t> points_a,
                                 ArrayView<point_t> points_b,
                                 ArrayView<uint32_t> offloading_point_ids,
                                 ArrayView<uint32_t> offloading_cell_ids,
                                 ArrayView<coord_t> cmin2, ArrayView<uint32_t> point_a_ids,
                                 const grid_t& grid, ArrayView<mbr_t> mbrs_b,
                                 coord_t radius,
                                 uint64_t* rtdl_goal5385_load_balance_feedback_update_count = nullptr) {
""",
        path=path,
    )
    text = _replace_once(
        text,
        """          atomicMax(p_cmax2, curr_cmin2);
""",
        """          if (rtdl_goal5385_load_balance_feedback_update_count != nullptr) {
            atomicAdd(reinterpret_cast<unsigned long long*>(
                          rtdl_goal5385_load_balance_feedback_update_count),
                      1ULL);
          }
          atomicMax(p_cmax2, curr_cmin2);
""",
        path=path,
    )
    text = _replace_once(
        text,
        """    });
  }
""",
        """    });
    return uniq_np;
  }
""",
        path=path,
    )
    text = "// RTDL_GOAL5385_LB_STATUS_TRACE_V2\n" + text
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
        "schema": "rtdl.paper_reproduction.xhd.goal5387.author_lb_status_trace_v2_patch.v1",
        "author_root": str(args.author_root),
        "changed": changed,
        "marker": MARKER,
        "trace_schema": SCHEMA,
        "patched": True,
        "claim_boundary": {
            "author_v2_trace_implemented": True,
            "author_v2_trace_executed_on_pod": False,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "rtdl_author_performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

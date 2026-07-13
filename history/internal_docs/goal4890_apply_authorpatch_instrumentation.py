from pathlib import Path


def replace(path: str, old: str, new: str) -> None:
    p = Path(path)
    s = p.read_text()
    if old not in s:
        raise SystemExit(f"pattern not found in {path}: {old[:120]!r}")
    p.write_text(s.replace(old, new, 1))


replace(
    "src/algo/launch_parameters.h",
    """#ifndef NDEBUG
  uint32_t *n_tests;
#endif
};""",
    """#ifndef NDEBUG
  uint32_t *n_tests;
#endif
  unsigned long long* goal4890_total_tests;
};""",
)
replace(
    "src/algo/launch_parameters.h",
    """#ifndef NDEBUG
  uint32_t* hit_count;
  uint32_t* closer_count;
  uint32_t* last_update_count;
  uint32_t* fail_update_count;
#endif
};""",
    """#ifndef NDEBUG
  uint32_t* hit_count;
  uint32_t* closer_count;
  uint32_t* last_update_count;
  uint32_t* fail_update_count;
#endif
  unsigned long long* goal4890_total_tests;
};""",
)
replace(
    "src/algo/rt_lsi_custom.cu",
    """  auto begin_eid = params.eid_range[prim_idx].first;
  auto end_eid = params.eid_range[prim_idx].second;

  for (auto base_eid = begin_eid; base_eid < end_eid; base_eid++) {""",
    """  auto begin_eid = params.eid_range[prim_idx].first;
  auto end_eid = params.eid_range[prim_idx].second;
  if (params.goal4890_total_tests != nullptr) {
    atomicAdd(params.goal4890_total_tests,
              static_cast<unsigned long long>(end_eid - begin_eid));
  }

  for (auto base_eid = begin_eid; base_eid < end_eid; base_eid++) {""",
)
replace(
    "src/algo/rt_pip_custom.cu",
    """  auto begin_eid = params.eid_range[prim_idx].first;
  auto end_eid = params.eid_range[prim_idx].second;

  unpack64(best_y_storage.x, best_y_storage.y, &best_y);""",
    """  auto begin_eid = params.eid_range[prim_idx].first;
  auto end_eid = params.eid_range[prim_idx].second;
  if (params.goal4890_total_tests != nullptr) {
    atomicAdd(params.goal4890_total_tests,
              static_cast<unsigned long long>(end_eid - begin_eid));
  }

  unpack64(best_y_storage.x, best_y_storage.y, &best_y);""",
)
replace(
    "src/app/lsi_rt.h",
    """#ifndef NDEBUG
    params.n_tests = n_tests_.data();
    n_tests_.set(0, stream);
#endif
    xsects_queue.Clear(stream);""",
    """#ifndef NDEBUG
    params.n_tests = n_tests_.data();
    n_tests_.set(0, stream);
#endif
    goal4890_total_tests_.resize(1, 0);
    thrust::fill(goal4890_total_tests_.begin(), goal4890_total_tests_.end(), 0ull);
    params.goal4890_total_tests =
        thrust::raw_pointer_cast(goal4890_total_tests_.data());
    xsects_queue.Clear(stream);""",
)
replace(
    "src/app/lsi_rt.h",
    """#endif
  }

  const QueryConfigRT& get_config() const { return config_; }""",
    """#endif
    thrust::host_vector<unsigned long long> goal4890_total_tests =
        goal4890_total_tests_;
    LOG(INFO) << "GOAL4890_AUTHOR_LSI_TOTAL_TESTS query_map_id="
              << query_map_id
              << " query_edges=" << d_query_map.get_edges().size()
              << " emitted_xsects=" << n_xsects
              << " total_tests=" << goal4890_total_tests[0];
  }

  const QueryConfigRT& get_config() const { return config_; }""",
)
replace(
    "src/app/lsi_rt.h",
    """  QueryConfigRT config_;
  SharedValue<uint32_t> n_tests_;
};""",
    """  QueryConfigRT config_;
  SharedValue<uint32_t> n_tests_;
  thrust::device_vector<unsigned long long> goal4890_total_tests_;
};""",
)
replace(
    "src/app/pip_rt.h",
    """#ifndef NDEBUG
    hit_count_.resize(points_num, 0);
    closer_count_.resize(points_num, 0);
    last_update_count_.resize(points_num, 0);
    fail_update_count_.resize(points_num, 0);

    params.hit_count = ArrayView<uint32_t>(hit_count_).data();
    params.closer_count = ArrayView<uint32_t>(closer_count_).data();
    params.last_update_count = ArrayView<uint32_t>(last_update_count_).data();
    params.fail_update_count = ArrayView<uint32_t>(fail_update_count_).data();
#endif
    rt_engine_->CopyLaunchParams(stream, params);""",
    """#ifndef NDEBUG
    hit_count_.resize(points_num, 0);
    closer_count_.resize(points_num, 0);
    last_update_count_.resize(points_num, 0);
    fail_update_count_.resize(points_num, 0);

    params.hit_count = ArrayView<uint32_t>(hit_count_).data();
    params.closer_count = ArrayView<uint32_t>(closer_count_).data();
    params.last_update_count = ArrayView<uint32_t>(last_update_count_).data();
    params.fail_update_count = ArrayView<uint32_t>(fail_update_count_).data();
#endif
    goal4890_total_tests_.resize(1, 0);
    thrust::fill(goal4890_total_tests_.begin(), goal4890_total_tests_.end(), 0ull);
    params.goal4890_total_tests =
        thrust::raw_pointer_cast(goal4890_total_tests_.data());
    rt_engine_->CopyLaunchParams(stream, params);""",
)
replace(
    "src/app/pip_rt.h",
    """#endif
  }

  void DumpStatistics(const char* path) {""",
    """#endif
    thrust::host_vector<unsigned long long> goal4890_total_tests =
        goal4890_total_tests_;
    LOG(INFO) << "GOAL4890_AUTHOR_PIP_TOTAL_TESTS query_map_id="
              << query_map_id
              << " point_count=" << points_num
              << " total_tests=" << goal4890_total_tests[0];
  }

  void DumpStatistics(const char* path) {""",
)
replace(
    "src/app/pip_rt.h",
    """  thrust::device_vector<uint32_t> last_update_count_;
  thrust::device_vector<uint32_t> fail_update_count_;
#endif
};""",
    """  thrust::device_vector<uint32_t> last_update_count_;
  thrust::device_vector<uint32_t> fail_update_count_;
#endif
  thrust::device_vector<unsigned long long> goal4890_total_tests_;
};""",
)

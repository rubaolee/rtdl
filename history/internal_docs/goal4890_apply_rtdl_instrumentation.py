from pathlib import Path


def replace(path: str, old: str, new: str) -> None:
    p = Path(path)
    s = p.read_text()
    if old not in s:
        raise SystemExit(f"pattern not found in {path}: {old[:120]!r}")
    p.write_text(s.replace(old, new, 1))


core = "src/native/optix/rtdl_optix_core.cpp"
work = "src/native/optix/rtdl_optix_workloads.cpp"

replace(
    core,
    """    unsigned int* face_id_output;
    unsigned long long* positive_face_count;
    unsigned int point_count;""",
    """    unsigned int* face_id_output;
    unsigned long long* positive_face_count;
    unsigned long long* candidate_test_count;
    unsigned int point_count;""",
)
replace(
    core,
    """    const GpuRayjoinCdbPoint point = params.points[point_index];
    const GpuRayjoinCdbSegmentRange range = params.ranges[optixGetPrimitiveIndex()];
    const float eps = 1.0e-7f;""",
    """    const GpuRayjoinCdbPoint point = params.points[point_index];
    const GpuRayjoinCdbSegmentRange range = params.ranges[optixGetPrimitiveIndex()];
    if (params.candidate_test_count != nullptr) {
        atomicAdd(params.candidate_test_count,
                  static_cast<unsigned long long>(range.end - range.begin));
    }
    const float eps = 1.0e-7f;""",
)
replace(
    work,
    """thread_local size_t g_optix_last_rayjoin_cdb_positive_face_count = 0;
thread_local uint32_t g_optix_last_rayjoin_cdb_mode = 0;""",
    """thread_local size_t g_optix_last_rayjoin_cdb_positive_face_count = 0;
thread_local size_t g_optix_last_rayjoin_cdb_raw_candidate_count = 0;
thread_local uint32_t g_optix_last_rayjoin_cdb_mode = 0;""",
)
replace(
    work,
    """    if (mode) *mode = g_optix_last_rayjoin_cdb_mode;
    return 0;
}

extern "C" int rtdl_optix_directed_segment_point_location_get_last_phase_timings(""",
    """    if (mode) *mode = g_optix_last_rayjoin_cdb_mode;
    return 0;
}

extern "C" int rtdl_optix_rayjoin_cdb_point_location_get_last_work_count(
        size_t* raw_candidate_count)
{
    if (raw_candidate_count) {
        *raw_candidate_count = g_optix_last_rayjoin_cdb_raw_candidate_count;
    }
    return 0;
}

extern "C" int rtdl_optix_directed_segment_point_location_get_last_phase_timings(""",
)
replace(
    work,
    """    g_optix_last_rayjoin_cdb_positive_face_count = 0;
    g_optix_last_rayjoin_cdb_mode = mode;""",
    """    g_optix_last_rayjoin_cdb_positive_face_count = 0;
    g_optix_last_rayjoin_cdb_raw_candidate_count = 0;
    g_optix_last_rayjoin_cdb_mode = mode;""",
)
replace(
    work,
    """    uint32_t* face_id_output;
    unsigned long long* positive_face_count;
    uint32_t point_count;""",
    """    uint32_t* face_id_output;
    unsigned long long* positive_face_count;
    unsigned long long* candidate_test_count;
    uint32_t point_count;""",
)
replace(
    work,
    """    if (d_positive_count_ptr) {
        unsigned long long zero64 = 0ull;
        upload<unsigned long long>(d_positive_count_ptr, &zero64, 1);
    }

    RayjoinCdbPointLocationLaunchParams lp;""",
    """    if (d_positive_count_ptr) {
        unsigned long long zero64 = 0ull;
        upload<unsigned long long>(d_positive_count_ptr, &zero64, 1);
    }
    DevPtr d_candidate_test_count(sizeof(unsigned long long));
    {
        unsigned long long zero64 = 0ull;
        upload<unsigned long long>(d_candidate_test_count.ptr, &zero64, 1);
    }

    RayjoinCdbPointLocationLaunchParams lp;""",
)
replace(
    work,
    """    lp.face_id_output = reinterpret_cast<uint32_t*>(d_face_id_output_ptr);
    lp.positive_face_count = reinterpret_cast<unsigned long long*>(d_positive_count_ptr);
    lp.point_count = static_cast<uint32_t>(point_count);""",
    """    lp.face_id_output = reinterpret_cast<uint32_t*>(d_face_id_output_ptr);
    lp.positive_face_count = reinterpret_cast<unsigned long long*>(d_positive_count_ptr);
    lp.candidate_test_count = reinterpret_cast<unsigned long long*>(d_candidate_test_count.ptr);
    lp.point_count = static_cast<uint32_t>(point_count);""",
)
replace(
    work,
    """    const auto t_launch_end = std::chrono::steady_clock::now();
    g_optix_last_rayjoin_cdb_traversal_s += seconds_between(t_launch_start, t_launch_end);
}
""",
    """    const auto t_launch_end = std::chrono::steady_clock::now();
    g_optix_last_rayjoin_cdb_traversal_s += seconds_between(t_launch_start, t_launch_end);
    unsigned long long host_candidate_test_count = 0ull;
    download<unsigned long long>(&host_candidate_test_count, d_candidate_test_count.ptr, 1);
    g_optix_last_rayjoin_cdb_raw_candidate_count =
        static_cast<size_t>(host_candidate_test_count);
}
""",
)

p = Path(work)
s = p.read_text()
needle = """        predicate_mode,
        false);"""
if s.count(needle) < 2:
    raise SystemExit(f"expected at least two grouped-range false callsites, saw {s.count(needle)}")
p.write_text(s.replace(needle, """        predicate_mode,
        true);""", 2))

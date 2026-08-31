# rtdl.v4.generated_formal_numba_leaf.v1
# callback_ir_sha256=627df36820b8d18cd3a3d0202d4d617ffa913444caff29d91af9a0613ba1fe7c
# callback_abi_sha256=a47fad0d52f082df8f34c5432a6b6092d08593becb92a70bb0b3c8ef04d7bc8a
def rtdl_v4_make_ray_627df36820b8d18c(in_context_launch_index, in_launch_id, in_queries_columns_start_x, in_queries_columns_start_y, in_queries_columns_start_z, in_queries_columns_end_x, in_queries_columns_end_y, in_queries_columns_end_z, in_queries_length, status_ok, status_error_code, status_stage, status_role, status_launch_index, status_error_site, status_effect_tag, status_nonce_word, status_invocation_mask, status_first_error_claimed, out_effect_tag, out_trace_request_direction_x, out_trace_request_direction_y, out_trace_request_direction_z, out_trace_request_origin_x, out_trace_request_origin_y, out_trace_request_origin_z, out_trace_request_payload_application_id, out_trace_request_payload_hit, out_trace_request_payload_toi, out_trace_request_tmax, out_trace_request_tmin):
    status_ok[0] = 0
    status_error_code[0] = 0
    status_stage[0] = 2
    status_role[0] = 2
    status_launch_index[0] = in_context_launch_index
    status_error_site[0] = 0
    status_effect_tag[0] = 0
    status_nonce_word[0] = 1704232214
    status_invocation_mask[0] = 2
    status_first_error_claimed[0] = 0
    out_effect_tag[0] = 0
    out_trace_request_direction_x[0] = 0.0
    out_trace_request_direction_y[0] = 0.0
    out_trace_request_direction_z[0] = 0.0
    out_trace_request_origin_x[0] = 0.0
    out_trace_request_origin_y[0] = 0.0
    out_trace_request_origin_z[0] = 0.0
    out_trace_request_payload_application_id[0] = 0
    out_trace_request_payload_hit[0] = 0
    out_trace_request_payload_toi[0] = 0.0
    out_trace_request_tmax[0] = 0.0
    out_trace_request_tmin[0] = 0.0
    status_error_code[0] = 0
    if in_launch_id < 0 or in_launch_id >= in_queries_length:
        status_ok[0] = 0
        status_error_code[0] = 7
        status_error_site[0] = 1
        return
    if not math.isfinite(in_queries_columns_start_x[in_launch_id]):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 2
        return
    if not math.isfinite(in_queries_columns_start_y[in_launch_id]):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 3
        return
    if not math.isfinite(in_queries_columns_start_z[in_launch_id]):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 4
        return
    if not math.isfinite(in_queries_columns_end_x[in_launch_id]):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 5
        return
    if not math.isfinite(in_queries_columns_end_y[in_launch_id]):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 6
        return
    if not math.isfinite(in_queries_columns_end_z[in_launch_id]):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 7
        return
    _rtdl_local_query = (in_queries_columns_start_x[in_launch_id], in_queries_columns_start_y[in_launch_id], in_queries_columns_start_z[in_launch_id], in_queries_columns_end_x[in_launch_id], in_queries_columns_end_y[in_launch_id], in_queries_columns_end_z[in_launch_id],)
    _rtdl_numeric_1 = _f32((_rtdl_local_query[3] - _rtdl_local_query[0]))
    if not math.isfinite(_rtdl_numeric_1):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 8
        return
    _rtdl_numeric_2 = _f32((_rtdl_local_query[4] - _rtdl_local_query[1]))
    if not math.isfinite(_rtdl_numeric_2):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 9
        return
    _rtdl_numeric_3 = _f32((_rtdl_local_query[5] - _rtdl_local_query[2]))
    if not math.isfinite(_rtdl_numeric_3):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 10
        return
    _rtdl_local_direction = (_rtdl_numeric_1, _rtdl_numeric_2, _rtdl_numeric_3,)
    _rtdl_local_initial = (0, _f32(1.0), 4294967295,)
    if not math.isfinite(_rtdl_local_query[0]):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 11
        return
    if not math.isfinite(_rtdl_local_query[1]):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 12
        return
    if not math.isfinite(_rtdl_local_query[2]):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 13
        return
    if not math.isfinite(_rtdl_local_direction[0]):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 14
        return
    if not math.isfinite(_rtdl_local_direction[1]):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 15
        return
    if not math.isfinite(_rtdl_local_direction[2]):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 16
        return
    if not math.isfinite(_f32(0.0)):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 17
        return
    if not math.isfinite(_f32(1.0)):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 18
        return
    if not math.isfinite(_rtdl_local_initial[1]):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 19
        return
    if ((_rtdl_local_direction[0] == 0.0) and (_rtdl_local_direction[1] == 0.0) and (_rtdl_local_direction[2] == 0.0)) or (not (0.0 <= _f32(0.0) < _f32(1.0))): 
        status_ok[0] = 0
        status_error_code[0] = 9
        status_error_site[0] = 20
        return
    out_trace_request_origin_x[0] = _rtdl_local_query[0]
    out_trace_request_origin_y[0] = _rtdl_local_query[1]
    out_trace_request_origin_z[0] = _rtdl_local_query[2]
    out_trace_request_direction_x[0] = _rtdl_local_direction[0]
    out_trace_request_direction_y[0] = _rtdl_local_direction[1]
    out_trace_request_direction_z[0] = _rtdl_local_direction[2]
    out_trace_request_tmin[0] = _f32(0.0)
    out_trace_request_tmax[0] = _f32(1.0)
    out_trace_request_payload_hit[0] = _rtdl_local_initial[0]
    out_trace_request_payload_toi[0] = _rtdl_local_initial[1]
    out_trace_request_payload_application_id[0] = _rtdl_local_initial[2]
    out_effect_tag[0] = 2
    status_effect_tag[0] = 2
    status_error_code[0] = 0
    status_ok[0] = 1
    return

# rtdl.v4.generated_formal_numba_leaf.v1
# callback_ir_sha256=daf61a8371e76956a291604c59449ae80e577772baf5175637b31fc857e0e394
# callback_abi_sha256=fa91b6bd0672f5fe79e6189d40ca248325c7811be3d1529226beec12f61bc154
def rtdl_v4_miss_daf61a8371e76956(in_context_launch_index, in_ray_origin_x, in_ray_origin_y, in_ray_origin_z, in_ray_direction_x, in_ray_direction_y, in_ray_direction_z, in_ray_tmin, in_ray_tmax, in_payload_hit, status_ok, status_error_code, status_stage, status_role, status_launch_index, status_error_site, status_effect_tag, status_nonce_word, status_invocation_mask, status_first_error_claimed, out_effect_tag, out_payload_payload_hit):
    status_ok[0] = 0
    status_error_code[0] = 0
    status_stage[0] = 3
    status_role[0] = 6
    status_launch_index[0] = in_context_launch_index
    status_error_site[0] = 0
    status_effect_tag[0] = 0
    status_nonce_word[0] = 1281424282
    status_invocation_mask[0] = 32
    status_first_error_claimed[0] = 0
    out_effect_tag[0] = 0
    out_payload_payload_hit[0] = 0
    if not math.isfinite(in_ray_origin_x):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 1
        return
    if not math.isfinite(in_ray_origin_y):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 2
        return
    if not math.isfinite(in_ray_origin_z):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 3
        return
    if not math.isfinite(in_ray_direction_x):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 4
        return
    if not math.isfinite(in_ray_direction_y):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 5
        return
    if not math.isfinite(in_ray_direction_z):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 6
        return
    if not math.isfinite(in_ray_tmin):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 7
        return
    if not math.isfinite(in_ray_tmax):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 8
        return
    status_error_code[0] = 0
    out_payload_payload_hit[0] = in_payload_hit
    out_effect_tag[0] = 8
    status_effect_tag[0] = 8
    status_error_code[0] = 0
    status_ok[0] = 1
    return

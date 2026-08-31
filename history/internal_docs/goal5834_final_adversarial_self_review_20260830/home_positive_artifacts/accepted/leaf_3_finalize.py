# rtdl.v4.generated_formal_numba_leaf.v1
# callback_ir_sha256=627df36820b8d18cd3a3d0202d4d617ffa913444caff29d91af9a0613ba1fe7c
# callback_abi_sha256=a47fad0d52f082df8f34c5432a6b6092d08593becb92a70bb0b3c8ef04d7bc8a
def rtdl_v4_finalize_627df36820b8d18c(in_context_launch_index, in_payload_hit, in_payload_toi, in_payload_application_id, status_ok, status_error_code, status_stage, status_role, status_launch_index, status_error_site, status_effect_tag, status_nonce_word, status_invocation_mask, status_first_error_claimed, out_effect_tag, out_output_value_application_id, out_output_value_hit, out_output_value_toi):
    status_ok[0] = 0
    status_error_code[0] = 0
    status_stage[0] = 2
    status_role[0] = 7
    status_launch_index[0] = in_context_launch_index
    status_error_site[0] = 0
    status_effect_tag[0] = 0
    status_nonce_word[0] = 3433962126
    status_invocation_mask[0] = 64
    status_first_error_claimed[0] = 0
    out_effect_tag[0] = 0
    out_output_value_application_id[0] = 0
    out_output_value_hit[0] = 0
    out_output_value_toi[0] = 0.0
    if not math.isfinite(in_payload_toi):
        status_ok[0] = 0
        status_error_code[0] = 2
        status_error_site[0] = 1
        return
    status_error_code[0] = 0
    _rtdl_local_result = (in_payload_hit, in_payload_toi, in_payload_application_id,)
    if not math.isfinite(_rtdl_local_result[1]):
        status_ok[0] = 0
        status_error_code[0] = 3
        status_error_site[0] = 2
        return
    out_output_value_hit[0] = _rtdl_local_result[0]
    out_output_value_toi[0] = _rtdl_local_result[1]
    out_output_value_application_id[0] = _rtdl_local_result[2]
    out_effect_tag[0] = 9
    status_effect_tag[0] = 9
    status_error_code[0] = 0
    status_ok[0] = 1
    return

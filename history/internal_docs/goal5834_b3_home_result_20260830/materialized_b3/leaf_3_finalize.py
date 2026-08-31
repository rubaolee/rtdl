# rtdl.v4.generated_formal_numba_leaf.v1
# callback_ir_sha256=daf61a8371e76956a291604c59449ae80e577772baf5175637b31fc857e0e394
# callback_abi_sha256=fa91b6bd0672f5fe79e6189d40ca248325c7811be3d1529226beec12f61bc154
def rtdl_v4_finalize_daf61a8371e76956(in_context_launch_index, in_payload_hit, status_ok, status_error_code, status_stage, status_role, status_launch_index, status_error_site, status_effect_tag, status_nonce_word, status_invocation_mask, status_first_error_claimed, out_effect_tag, out_output_value_hit):
    status_ok[0] = 0
    status_error_code[0] = 0
    status_stage[0] = 2
    status_role[0] = 7
    status_launch_index[0] = in_context_launch_index
    status_error_site[0] = 0
    status_effect_tag[0] = 0
    status_nonce_word[0] = 4164633680
    status_invocation_mask[0] = 64
    status_first_error_claimed[0] = 0
    out_effect_tag[0] = 0
    out_output_value_hit[0] = 0
    status_error_code[0] = 0
    _rtdl_local_result = in_payload_hit
    out_output_value_hit[0] = _rtdl_local_result
    out_effect_tag[0] = 9
    status_effect_tag[0] = 9
    status_error_code[0] = 0
    status_ok[0] = 1
    return

#pragma once

#include <cstddef>
#include <cstdint>

// Shared, compiler-checked layout used by the OptiX translation unit and the
// precompiled CUDA status reducer.  The generated device wrappers own the
// corresponding PTX declaration; rtdl_optix_v4_callback_poc.cpp has exact
// sizeof/offsetof assertions against this layout.
struct RtdlV4FormalLaunchStatusLayout {
    uint32_t first_error_claimed;
    uint32_t error_code;
    uint32_t stage;
    uint32_t role;
    uint64_t launch_index;
    uint32_t error_site;
    uint32_t effect_tag;
    uint32_t nonce_word;
    uint32_t invocation_mask;
};

// Constant-size product status. ``role_counters`` follows CallbackRole order:
// bounds, make_ray, intersection, any_hit, closest_hit, miss, finalize (tags
// 1..7). A successful product execution transfers exactly one summary,
// irrespective of launch width.
struct RtdlV4CallbackProductStatusSummary {
    uint32_t schema_version;
    uint32_t ok;
    uint32_t first_error_claimed;
    uint32_t error_code;
    uint64_t validated_row_count;
    uint32_t required_invocation_mask;
    uint32_t terminal_invocation_mask;
    uint32_t invalid_row_count;
    uint64_t first_invalid_row;
    uint64_t role_counters[7];
    uint64_t success_status_d2h_bytes;
};

struct RtdlV4CheckedU64ProductResult {
    uint64_t value;
    uint32_t overflowed;
    uint32_t schema_version;
    uint64_t input_count;
    uint64_t success_result_d2h_bytes;
};

// Goal5801/5802 application fast-path envelopes.  The complete 112-byte
// product summary and seven role counters remain device-resident and are
// validated before either envelope can report success.  They are materialized
// only by the diagnostic v4 ABIs.  The application v5 ABIs transfer exactly
// one compact control boundary followed by one result boundary.  The receipt
// also counts dynamic input-generation work so first execution cannot be
// misreported as equivalent to an exact prepared-input reuse.
struct RtdlV4FastRelationControl {
    uint32_t raw_event_count;
    uint32_t unique_event_count;
    uint32_t overflowed;
    uint32_t status;
    uint32_t legacy_error_seen;
    uint32_t error_code;
    uint32_t validated_row_count;
};

// Application-fast triangle execution validates each completed callback
// lifecycle in the generated raygen program.  The control is zeroed before
// optixLaunch and receives only status/counter evidence; the checked scalar
// remains in a distinct allocation and is copied only after this control has
// been accepted on the host.
struct RtdlV4FastTriangleControl {
    uint32_t error_code;
    uint32_t validated_row_count;
    uint32_t overflowed;
    uint32_t reserved;
    uint64_t event_count;
    uint64_t per_ray_sum;
    uint64_t role_counters[7];
};

struct RtdlV4FastPathReceipt {
    uint32_t schema_version;
    uint32_t optix_launch_count;
    uint32_t host_blocking_boundary_count;
    uint32_t control_d2h_bytes;
    uint64_t output_d2h_bytes;
    uint32_t status_before_output;
    uint32_t output_d2h_after_status_failure;
    uint32_t role_counters_materialized;
    uint32_t prepared_input_reused;
    uint32_t dynamic_device_upload_call_count;
    uint32_t dynamic_accel_build_count;
    uint32_t dynamic_explicit_sync_count;
    uint32_t dynamic_blocking_upload_call_count;
    uint64_t dynamic_device_upload_bytes;
    uint64_t dynamic_input_generation;
    uint32_t semantic_compaction_launch_count;
    uint32_t semantic_compaction_key_capacity;
    uint64_t semantic_compaction_scratch_bytes;
    uint32_t callback_status_kernel_launch_count;
    uint32_t checked_product_kernel_launch_count;
    uint32_t compact_control_finalizer_kernel_launch_count;
    uint32_t total_auxiliary_cuda_kernel_launch_count;
    uint64_t execution_parameter_h2d_bytes;
    uint32_t execution_parameter_h2d_copy_call_count;
    uint32_t stream_ordered_memset_call_count;
    uint32_t status_d2h_copy_call_count;
    uint32_t output_d2h_copy_call_count;
};

// Goal5814 matched Particle closest-face family.  The device writes this
// constant-size gate during the sole OptiX launch.  Host execution must copy
// and synchronize these 16 bytes before it may copy any application output.
// ``first_error`` is UINT32_MAX on success and the first device claimant's
// launch index on failure.
struct RtdlV4ParticleControl {
    uint32_t validated_row_count;
    uint32_t first_error;
    uint32_t error_code;
    uint32_t status;
};

// Exact transfer/launch accounting returned by the reusable Particle ABI.
// Query bytes exclude the control reset and launch-parameter envelope, which
// are separately counted.  This prevents either matched arm from hiding work
// inside an aggregate H2D number.
struct RtdlV4ParticleFastReceipt {
    uint32_t schema_version;
    uint32_t optix_launch_count;
    uint32_t query_count;
    uint32_t query_h2d_copy_call_count;
    uint32_t control_reset_h2d_copy_call_count;
    uint32_t parameter_h2d_copy_call_count;
    uint32_t control_d2h_copy_call_count;
    uint32_t output_d2h_copy_call_count;
    uint32_t host_blocking_boundary_count;
    uint32_t status_before_output;
    uint64_t query_h2d_bytes;
    uint64_t control_reset_h2d_bytes;
    uint64_t parameter_h2d_bytes;
    uint64_t control_d2h_bytes;
    uint64_t output_d2h_bytes;
    uint64_t output_d2h_after_status_failure;
    uint64_t boundary_owner_table_bytes;
};

static_assert(sizeof(RtdlV4FastRelationControl) == 28,
              "V4 fast relation control must remain 28 bytes");
static_assert(sizeof(RtdlV4FastTriangleControl) == 88,
              "V4 fast triangle control must remain 88 bytes");
static_assert(sizeof(RtdlV4FastPathReceipt) == 128,
              "V4 fast-path receipt layout changed");
static_assert(sizeof(RtdlV4ParticleControl) == 16,
              "V4 Particle control must remain 16 bytes");
static_assert(sizeof(RtdlV4ParticleFastReceipt) == 96,
              "V4 Particle fast receipt layout changed");

// Both modes validate the execution-coupled status mask written by the device
// producer.  Mode 1 additionally reduces exact bounded-relation
// intersection/any-hit multiplicities from their device columns.  It never
// manufactures required or terminal phase bits. ``reset_summary`` begins a
// product execution; two-pass relation execution accumulates both launches
// before the sole D2H.
void rtdl_cuda_reduce_v4_callback_product_status_precompiled(
    const void* status_device,
    const uint32_t* intersection_count_device,
    const uint32_t* hit_count_device,
    const uint64_t* per_ray_u64_device,
    const uint32_t* error_seen_device,
    const uint64_t* role_counters_device,
    uint64_t row_count,
    uint64_t row_offset,
    uint32_t mode,
    uint32_t required_invocation_mask,
    uint32_t terminal_invocation_mask,
    void* summary_device,
    uint32_t reset_summary,
    uint32_t copy_summary_to_host,
    RtdlV4CallbackProductStatusSummary* summary_host,
    uint64_t cuda_stream);

void rtdl_cuda_checked_u64_product_sum_precompiled(
    const uint64_t* values_device,
    const uint64_t* multipliers_host,
    uint64_t* multipliers_device,
    uint64_t count,
    void* result_device,
    uint32_t use_multipliers,
    uint32_t upload_multipliers,
    RtdlV4CheckedU64ProductResult* result_host,
    uint64_t cuda_stream);

// Enqueue-only fast-path finalizers.  ``cuda_stream`` is the exact driver
// stream used by the preceding OptiX launch and reducers.  Neither function
// synchronizes or copies to host.
void rtdl_cuda_finalize_v4_triangle_fast_status_precompiled(
    const void* summary_device,
    const uint64_t* event_count_device,
    uint64_t event_capacity,
    const void* checked_result_device,
    uint64_t expected_row_count,
    uint32_t* status_device,
    uint64_t cuda_stream);

void rtdl_cuda_finalize_v4_relation_fast_control_precompiled(
    const void* summary_device,
    const uint32_t* event_count_device,
    const uint32_t* unique_count_device,
    const uint32_t* overflowed_device,
    uint32_t raw_event_capacity,
    uint32_t semantic_capacity,
    uint64_t expected_row_count,
    RtdlV4FastRelationControl* control_device,
    uint64_t cuda_stream);

// Compact the two diagonal OptiX passes into unique semantic rows entirely on
// the execution stream.  This is part of admission, not a diagnostic: a K+1
// unique result sets ``overflowed_device`` before the compact control D2H.
void rtdl_cuda_compact_v4_relation_rows_precompiled(
    const void* raw_rows_device,
    const uint32_t* raw_count_device,
    uint32_t raw_capacity,
    uint32_t semantic_capacity,
    uint64_t* dedup_keys_device,
    uint32_t dedup_key_capacity,
    uint32_t* max_key_seen_device,
    void* unique_rows_device,
    uint32_t* unique_count_device,
    uint32_t* overflowed_device,
    uint64_t cuda_stream);

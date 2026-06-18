#include "rtdl/rtdl.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

static rtdl_context_desc make_cpu_desc(void) {
  rtdl_context_desc desc;
  memset(&desc, 0, sizeof(desc));
  desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  desc.backend = RTDL_BACKEND_CPU;
  desc.external_runtime.device_type = RTDL_DEVICE_HOST;
  desc.external_runtime.device_id = 0;
  return desc;
}

static rtdl_buffer_view make_host_f32_aabb2_view(float* data, uint64_t count) {
  rtdl_buffer_view view;
  memset(&view, 0, sizeof(view));
  view.data = data;
  view.byte_count = count * 4u * (uint64_t)sizeof(float);
  view.device_type = RTDL_DEVICE_HOST;
  view.dtype = RTDL_DTYPE_F32;
  view.ndim = 2u;
  view.shape[0] = (int64_t)count;
  view.shape[1] = 4;
  view.strides[0] = (int64_t)(4 * sizeof(float));
  view.strides[1] = (int64_t)sizeof(float);
  return view;
}

static int require_last_error_contains(rtdl_context* context, const char* needle, const char* case_name) {
  const char* error = rtdl_context_last_error(context);
  if (error == NULL || strstr(error, needle) == NULL) {
    fprintf(stderr, "%s failed: expected last-error containing '%s', got '%s'\n",
            case_name, needle, error == NULL ? "<null>" : error);
    return 1;
  }
  return 0;
}

static int require_last_error_empty(rtdl_context* context, const char* case_name) {
  const char* error = rtdl_context_last_error(context);
  if (error == NULL || error[0] != '\0') {
    fprintf(stderr, "%s failed: expected empty last-error, got '%s'\n",
            case_name, error == NULL ? "<null>" : error);
    return 1;
  }
  return 0;
}

int main(void) {
  if (strcmp(rtdl_status_string(RTDL_STATUS_OK), "ok") != 0 ||
      strcmp(rtdl_status_string(RTDL_STATUS_ERROR_INVALID_ARGUMENT), "invalid argument") != 0 ||
      strcmp(rtdl_status_string(RTDL_STATUS_ERROR_UNSUPPORTED), "unsupported") != 0 ||
      strcmp(rtdl_status_string((rtdl_status)9999), "unknown status") != 0) {
    fprintf(stderr, "status string diagnostics mismatch\n");
    return 1;
  }
  printf("case status_string_diagnostics_ok: ok\n");

  if (strcmp(rtdl_context_last_error(NULL), "context is null") != 0) {
    fprintf(stderr, "NULL context diagnostic mismatch\n");
    return 2;
  }
  printf("case null_context_last_error_ok: ok\n");

  rtdl_context_desc desc = make_cpu_desc();
  rtdl_context* context = NULL;
  rtdl_status status = rtdl_context_create(&desc, &context);
  if (status != RTDL_STATUS_OK || context == NULL ||
      require_last_error_empty(context, "initial_last_error_empty")) {
    fprintf(stderr, "context create failed: %s\n", rtdl_status_string(status));
    return 3;
  }
  printf("case initial_last_error_empty: ok\n");

  float payload[4] = {0.0f, 0.0f, 1.0f, 1.0f};
  rtdl_buffer_view bad_view = make_host_f32_aabb2_view(payload, 1u);
  bad_view.ndim = 9u;
  rtdl_buffer* bad_buffer = NULL;
  status = rtdl_buffer_import(context, &bad_view, &bad_buffer);
  if (status != RTDL_STATUS_ERROR_INVALID_ARGUMENT || bad_buffer != NULL ||
      require_last_error_contains(
          context,
          "buffer import requires known device/dtype metadata",
          "invalid_buffer_sets_last_error")) {
    rtdl_context_destroy(context);
    return 4;
  }
  printf("case invalid_buffer_sets_last_error: ok\n");

  rtdl_buffer_view good_view = make_host_f32_aabb2_view(payload, 1u);
  rtdl_buffer* good_buffer = NULL;
  status = rtdl_buffer_import(context, &good_view, &good_buffer);
  if (status != RTDL_STATUS_OK || good_buffer == NULL ||
      require_last_error_empty(context, "successful_buffer_import_clears_last_error")) {
    fprintf(stderr, "good buffer import failed: %s\n", rtdl_status_string(status));
    rtdl_context_destroy(context);
    return 5;
  }
  printf("case successful_buffer_import_clears_last_error: ok\n");

  rtdl_external_runtime cuda_runtime;
  memset(&cuda_runtime, 0, sizeof(cuda_runtime));
  cuda_runtime.device_type = RTDL_DEVICE_CUDA;
  cuda_runtime.device_id = 0;
  status = rtdl_context_set_external_runtime(context, &cuda_runtime);
  if (status != RTDL_STATUS_ERROR_UNSUPPORTED ||
      require_last_error_contains(
          context,
          "only host external runtime metadata",
          "unsupported_runtime_sets_last_error")) {
    rtdl_buffer_destroy(good_buffer);
    rtdl_context_destroy(context);
    return 6;
  }
  printf("case unsupported_runtime_sets_last_error: ok\n");

  rtdl_external_runtime host_runtime;
  memset(&host_runtime, 0, sizeof(host_runtime));
  host_runtime.device_type = RTDL_DEVICE_HOST;
  host_runtime.device_id = -1;
  status = rtdl_context_set_external_runtime(context, &host_runtime);
  if (status != RTDL_STATUS_OK ||
      require_last_error_empty(context, "successful_runtime_clears_last_error")) {
    fprintf(stderr, "host runtime update failed: %s\n", rtdl_status_string(status));
    rtdl_buffer_destroy(good_buffer);
    rtdl_context_destroy(context);
    return 7;
  }
  printf("case successful_runtime_clears_last_error: ok\n");

  rtdl_buffer_destroy(good_buffer);
  rtdl_context_destroy(context);
  printf("validated_last_error_diagnostics_cases=7\n");
  return 0;
}

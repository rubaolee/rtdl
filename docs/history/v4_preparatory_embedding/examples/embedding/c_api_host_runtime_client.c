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

static int require_last_error(rtdl_context* context, const char* case_name) {
  const char* error = rtdl_context_last_error(context);
  if (error == NULL || error[0] == '\0') {
    fprintf(stderr, "%s failed: expected last-error text\n", case_name);
    return 1;
  }
  return 0;
}

int main(void) {
  rtdl_context_desc desc = make_cpu_desc();
  rtdl_context* context = NULL;
  rtdl_status status = rtdl_context_create(&desc, &context);
  if (status != RTDL_STATUS_OK || context == NULL) {
    fprintf(stderr, "context create failed: %d\n", (int)status);
    return 1;
  }

  rtdl_external_runtime host_runtime;
  memset(&host_runtime, 0, sizeof(host_runtime));
  host_runtime.device_type = RTDL_DEVICE_HOST;
  host_runtime.device_id = 0;
  host_runtime.user_data = (void*)(uintptr_t)0x1234u;
  status = rtdl_context_set_external_runtime(context, &host_runtime);
  if (status != RTDL_STATUS_OK) {
    fprintf(stderr, "host runtime metadata rejected: %d\n", (int)status);
    rtdl_context_destroy(context);
    return 2;
  }
  if (rtdl_context_last_error(context)[0] != '\0') {
    fprintf(stderr, "host runtime metadata left stale last-error text\n");
    rtdl_context_destroy(context);
    return 3;
  }
  printf("case host_external_runtime_metadata_ok: ok\n");

  rtdl_external_runtime malformed_host = host_runtime;
  malformed_host.stream = (void*)(uintptr_t)0x1u;
  status = rtdl_context_set_external_runtime(context, &malformed_host);
  if (status != RTDL_STATUS_ERROR_INVALID_ARGUMENT ||
      require_last_error(context, "malformed_host_runtime_rejected")) {
    rtdl_context_destroy(context);
    return 4;
  }
  printf("case malformed_host_runtime_rejected: ok\n");

  rtdl_external_runtime cuda_runtime;
  memset(&cuda_runtime, 0, sizeof(cuda_runtime));
  cuda_runtime.device_type = RTDL_DEVICE_CUDA;
  cuda_runtime.device_id = 0;
  cuda_runtime.context = (void*)(uintptr_t)0x1u;
  cuda_runtime.stream = (void*)(uintptr_t)0x2u;
  status = rtdl_context_set_external_runtime(context, &cuda_runtime);
  if (status != RTDL_STATUS_ERROR_UNSUPPORTED ||
      require_last_error(context, "cuda_runtime_rejected")) {
    rtdl_context_destroy(context);
    return 5;
  }
  printf("case cuda_runtime_rejected: ok\n");

  rtdl_context_destroy(context);
  printf("validated_host_external_runtime_cases=3\n");
  return 0;
}

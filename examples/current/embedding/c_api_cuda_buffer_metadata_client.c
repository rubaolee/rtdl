#include "rtdl/rtdl.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void release_marker(void* data, void* user_data) {
  (void)data;
  int* count = (int*)user_data;
  *count += 1;
}

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

static rtdl_buffer_view make_cuda_aabb2_metadata(int* release_count) {
  rtdl_buffer_view view;
  memset(&view, 0, sizeof(view));
  view.data = (void*)(uintptr_t)0x1000u;
  view.byte_count = 3u * 4u * (uint64_t)sizeof(float);
  view.device_type = RTDL_DEVICE_CUDA;
  view.device_id = 0;
  view.dtype = RTDL_DTYPE_F32;
  view.ndim = 2u;
  view.shape[0] = 3;
  view.shape[1] = 4;
  view.strides[0] = 4 * (int64_t)sizeof(float);
  view.strides[1] = (int64_t)sizeof(float);
  view.release = release_marker;
  view.user_data = release_count;
  return view;
}

int main(void) {
  rtdl_context_desc desc = make_cpu_desc();
  rtdl_context* context = NULL;
  if (rtdl_context_create(&desc, &context) != RTDL_STATUS_OK || context == NULL) {
    fprintf(stderr, "context create failed\n");
    return 1;
  }

  int release_count = 0;
  rtdl_buffer_view cuda_view = make_cuda_aabb2_metadata(&release_count);
  rtdl_buffer* cuda_buffer = NULL;
  rtdl_status status = rtdl_buffer_import(context, &cuda_view, &cuda_buffer);
  if (status != RTDL_STATUS_OK || cuda_buffer == NULL) {
    fprintf(stderr, "cuda metadata import failed: %d\n", (int)status);
    rtdl_context_destroy(context);
    return 2;
  }

  rtdl_buffer_view exported;
  memset(&exported, 0, sizeof(exported));
  if (rtdl_buffer_export(cuda_buffer, &exported) != RTDL_STATUS_OK ||
      exported.data != cuda_view.data ||
      exported.device_type != RTDL_DEVICE_CUDA ||
      exported.device_id != 0 ||
      exported.dtype != RTDL_DTYPE_F32 ||
      exported.ndim != 2u ||
      exported.shape[0] != 3 ||
      exported.shape[1] != 4 ||
      exported.strides[0] != cuda_view.strides[0] ||
      exported.strides[1] != cuda_view.strides[1]) {
    fprintf(stderr, "cuda metadata export mismatch\n");
    rtdl_buffer_destroy(cuda_buffer);
    rtdl_context_destroy(context);
    return 3;
  }
  printf("case cuda_buffer_metadata_roundtrip_ok: ok\n");

  rtdl_index_desc index_desc;
  memset(&index_desc, 0, sizeof(index_desc));
  index_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  index_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  index_desc.primitive_kind = RTDL_PRIMITIVE_AABB2;
  index_desc.primitives = cuda_buffer;
  index_desc.primitive_count = 3u;
  rtdl_index* index = NULL;
  status = rtdl_index_build(context, &index_desc, &index);
  if (status != RTDL_STATUS_ERROR_INVALID_ARGUMENT || index != NULL) {
    fprintf(stderr, "cuda buffer query route was not rejected: %d\n", (int)status);
    if (index != NULL) {
      rtdl_index_destroy(index);
    }
    rtdl_buffer_destroy(cuda_buffer);
    rtdl_context_destroy(context);
    return 4;
  }
  printf("case cuda_query_route_rejected: ok\n");

  rtdl_buffer_destroy(cuda_buffer);
  if (release_count != 1) {
    fprintf(stderr, "release callback count mismatch: %d\n", release_count);
    rtdl_context_destroy(context);
    return 5;
  }
  printf("case cuda_buffer_release_callback_ok: ok\n");

  rtdl_buffer_view invalid = cuda_view;
  invalid.ndim = 9u;
  invalid.release = NULL;
  invalid.user_data = NULL;
  rtdl_buffer* invalid_buffer = NULL;
  status = rtdl_buffer_import(context, &invalid, &invalid_buffer);
  if (status != RTDL_STATUS_ERROR_INVALID_ARGUMENT || invalid_buffer != NULL) {
    fprintf(stderr, "invalid metadata was not rejected: %d\n", (int)status);
    if (invalid_buffer != NULL) {
      rtdl_buffer_destroy(invalid_buffer);
    }
    rtdl_context_destroy(context);
    return 6;
  }
  printf("case invalid_cuda_buffer_metadata_rejected: ok\n");

  rtdl_context_destroy(context);
  printf("validated_cuda_buffer_metadata_cases=4\n");
  return 0;
}

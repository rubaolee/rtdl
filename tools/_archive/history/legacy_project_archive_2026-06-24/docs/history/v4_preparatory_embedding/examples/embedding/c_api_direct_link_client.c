#include "rtdl/rtdl.h"

#include <stdio.h>

int main(void) {
  if (!rtdl_abi_is_compatible(
          RTDL_ABI_VERSION_MAJOR,
          RTDL_ABI_VERSION_MINOR,
          RTDL_ABI_VERSION_PATCH)) {
    return 2;
  }
  if (!rtdl_backend_is_supported(RTDL_BACKEND_CPU)) {
    return 3;
  }
  if (!rtdl_route_is_supported(
          RTDL_PRIMITIVE_AABB2,
          RTDL_QUERY_AABB_OVERLAP,
          RTDL_DEVICE_HOST)) {
    return 4;
  }

  rtdl_context_desc desc = {0};
  desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  desc.backend = RTDL_BACKEND_CPU;
  rtdl_context* context = 0;
  rtdl_status status = rtdl_context_create(&desc, &context);
  if (status != RTDL_STATUS_OK || context == 0) {
    return 5;
  }

  printf(
      "direct_link_ok %u.%u.%u %s\n",
      rtdl_abi_version_major(),
      rtdl_abi_version_minor(),
      rtdl_abi_version_patch(),
      rtdl_status_string(status));
  rtdl_context_destroy(context);
  return 0;
}

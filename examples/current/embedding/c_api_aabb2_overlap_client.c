#include "rtdl/rtdl.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#if defined(_WIN32)
#include <windows.h>
typedef HMODULE rtdl_example_library;
static rtdl_example_library open_library(const char* path) { return LoadLibraryA(path); }
static void* load_symbol(rtdl_example_library library, const char* name) {
  return (void*)GetProcAddress(library, name);
}
static void close_library(rtdl_example_library library) { FreeLibrary(library); }
#else
#include <dlfcn.h>
typedef void* rtdl_example_library;
static rtdl_example_library open_library(const char* path) { return dlopen(path, RTLD_NOW | RTLD_LOCAL); }
static void* load_symbol(rtdl_example_library library, const char* name) { return dlsym(library, name); }
static void close_library(rtdl_example_library library) { dlclose(library); }
#endif

typedef rtdl_status (*context_create_fn)(const rtdl_context_desc*, rtdl_context**);
typedef void (*context_destroy_fn)(rtdl_context*);
typedef rtdl_status (*buffer_import_fn)(rtdl_context*, const rtdl_buffer_view*, rtdl_buffer**);
typedef rtdl_status (*buffer_export_fn)(const rtdl_buffer*, rtdl_buffer_view*);
typedef void (*buffer_destroy_fn)(rtdl_buffer*);
typedef rtdl_status (*index_build_fn)(rtdl_context*, const rtdl_index_desc*, rtdl_index**);
typedef void (*index_destroy_fn)(rtdl_index*);
typedef rtdl_status (*query_execute_fn)(rtdl_context*, const rtdl_index*, const rtdl_query_desc*, rtdl_buffer**);

#define LOAD_REQUIRED(name, type) \
  type name = (type)load_symbol(library, "rtdl_" #name); \
  if (name == NULL) { \
    fprintf(stderr, "missing rtdl_%s\n", #name); \
    close_library(library); \
    return 20; \
  }

static rtdl_buffer_view host_f32_aabb2_view(float* data, uint64_t count) {
  rtdl_buffer_view view;
  memset(&view, 0, sizeof(view));
  view.data = data;
  view.byte_count = count * 4u * sizeof(float);
  view.device_type = RTDL_DEVICE_HOST;
  view.dtype = RTDL_DTYPE_F32;
  view.ndim = 2u;
  view.shape[0] = (int64_t)count;
  view.shape[1] = 4;
  view.strides[0] = (int64_t)(4u * sizeof(float));
  view.strides[1] = (int64_t)sizeof(float);
  return view;
}

int main(int argc, char** argv) {
  if (argc != 2) {
    fprintf(stderr, "usage: %s <librtdl_c_api.so>\n", argv[0]);
    return 2;
  }

  rtdl_example_library library = open_library(argv[1]);
  if (library == NULL) {
    fprintf(stderr, "could not open RTDL C ABI library\n");
    return 3;
  }

  LOAD_REQUIRED(context_create, context_create_fn);
  LOAD_REQUIRED(context_destroy, context_destroy_fn);
  LOAD_REQUIRED(buffer_import, buffer_import_fn);
  LOAD_REQUIRED(buffer_export, buffer_export_fn);
  LOAD_REQUIRED(buffer_destroy, buffer_destroy_fn);
  LOAD_REQUIRED(index_build, index_build_fn);
  LOAD_REQUIRED(index_destroy, index_destroy_fn);
  LOAD_REQUIRED(query_execute, query_execute_fn);

  rtdl_context_desc context_desc;
  memset(&context_desc, 0, sizeof(context_desc));
  context_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  context_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  context_desc.backend = RTDL_BACKEND_CPU;

  rtdl_context* context = NULL;
  if (context_create(&context_desc, &context) != RTDL_STATUS_OK || context == NULL) {
    close_library(library);
    return 4;
  }

  float primitives[8] = {0.0f, 0.0f, 1.0f, 1.0f, 10.0f, 10.0f, 11.0f, 11.0f};
  float queries[4] = {0.25f, 0.25f, 0.75f, 0.75f};

  rtdl_buffer_view primitive_view = host_f32_aabb2_view(primitives, 2);
  rtdl_buffer_view query_view = host_f32_aabb2_view(queries, 1);
  rtdl_buffer* primitive_buffer = NULL;
  rtdl_buffer* query_buffer = NULL;
  if (buffer_import(context, &primitive_view, &primitive_buffer) != RTDL_STATUS_OK ||
      buffer_import(context, &query_view, &query_buffer) != RTDL_STATUS_OK) {
    context_destroy(context);
    close_library(library);
    return 5;
  }

  rtdl_index_desc index_desc;
  memset(&index_desc, 0, sizeof(index_desc));
  index_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  index_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  index_desc.primitive_kind = RTDL_PRIMITIVE_AABB2;
  index_desc.primitives = primitive_buffer;
  index_desc.primitive_count = 2;

  rtdl_index* index = NULL;
  if (index_build(context, &index_desc, &index) != RTDL_STATUS_OK || index == NULL) {
    buffer_destroy(query_buffer);
    buffer_destroy(primitive_buffer);
    context_destroy(context);
    close_library(library);
    return 6;
  }

  rtdl_query_desc query_desc;
  memset(&query_desc, 0, sizeof(query_desc));
  query_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  query_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  query_desc.query_kind = RTDL_QUERY_AABB_OVERLAP;
  query_desc.inputs = query_buffer;
  query_desc.input_count = 1;

  rtdl_buffer* result_buffer = NULL;
  if (query_execute(context, index, &query_desc, &result_buffer) != RTDL_STATUS_OK || result_buffer == NULL) {
    index_destroy(index);
    buffer_destroy(query_buffer);
    buffer_destroy(primitive_buffer);
    context_destroy(context);
    close_library(library);
    return 7;
  }

  rtdl_buffer_view result_view;
  memset(&result_view, 0, sizeof(result_view));
  if (buffer_export(result_buffer, &result_view) != RTDL_STATUS_OK) {
    buffer_destroy(result_buffer);
    index_destroy(index);
    buffer_destroy(query_buffer);
    buffer_destroy(primitive_buffer);
    context_destroy(context);
    close_library(library);
    return 8;
  }

  uint64_t* rows = (uint64_t*)result_view.data;
  if (result_view.shape[0] != 1 || result_view.shape[1] != 2 || rows == NULL ||
      rows[0] != 0u || rows[1] != 0u) {
    buffer_destroy(result_buffer);
    index_destroy(index);
    buffer_destroy(query_buffer);
    buffer_destroy(primitive_buffer);
    context_destroy(context);
    close_library(library);
    return 9;
  }

  printf("hit_count=%lld first_pair=(%llu,%llu)\n",
         (long long)result_view.shape[0],
         (unsigned long long)rows[0],
         (unsigned long long)rows[1]);

  buffer_destroy(result_buffer);
  index_destroy(index);
  buffer_destroy(query_buffer);
  buffer_destroy(primitive_buffer);
  context_destroy(context);
  close_library(library);
  return 0;
}

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stddef.h>
#include <stdint.h>
#include <stdatomic.h>
#include <string.h>

typedef int CUresult;
typedef void* CUstream;
typedef void* CUcontext;
typedef unsigned long long CUdeviceptr;
typedef int cudaError_t;
typedef int cudaMemcpyKind;

enum {
    RTDL_COPY_HOST_TO_DEVICE = 1,
    RTDL_COPY_DEVICE_TO_HOST = 2,
    RTDL_COPY_DEVICE_TO_DEVICE = 3,
    RTDL_COPY_UNKNOWN = 4,
};

typedef struct RtdlCudaTransferCounterSnapshot {
    uint64_t enabled;
    uint64_t total_calls;
    uint64_t total_bytes;
    uint64_t host_to_device_calls;
    uint64_t host_to_device_bytes;
    uint64_t device_to_host_calls;
    uint64_t device_to_host_bytes;
    uint64_t device_to_device_calls;
    uint64_t device_to_device_bytes;
    uint64_t unknown_calls;
    uint64_t unknown_bytes;
} RtdlCudaTransferCounterSnapshot;

static _Atomic uint64_t g_enabled = 0;
static _Atomic uint64_t g_total_calls = 0;
static _Atomic uint64_t g_total_bytes = 0;
static _Atomic uint64_t g_htod_calls = 0;
static _Atomic uint64_t g_htod_bytes = 0;
static _Atomic uint64_t g_dtoh_calls = 0;
static _Atomic uint64_t g_dtoh_bytes = 0;
static _Atomic uint64_t g_dtod_calls = 0;
static _Atomic uint64_t g_dtod_bytes = 0;
static _Atomic uint64_t g_unknown_calls = 0;
static _Atomic uint64_t g_unknown_bytes = 0;

static void rtdl_count_copy(int direction, size_t byte_count) {
    if (!atomic_load_explicit(&g_enabled, memory_order_relaxed)) {
        return;
    }
    atomic_fetch_add_explicit(&g_total_calls, 1, memory_order_relaxed);
    atomic_fetch_add_explicit(&g_total_bytes, (uint64_t)byte_count, memory_order_relaxed);
    if (direction == RTDL_COPY_HOST_TO_DEVICE) {
        atomic_fetch_add_explicit(&g_htod_calls, 1, memory_order_relaxed);
        atomic_fetch_add_explicit(&g_htod_bytes, (uint64_t)byte_count, memory_order_relaxed);
    } else if (direction == RTDL_COPY_DEVICE_TO_HOST) {
        atomic_fetch_add_explicit(&g_dtoh_calls, 1, memory_order_relaxed);
        atomic_fetch_add_explicit(&g_dtoh_bytes, (uint64_t)byte_count, memory_order_relaxed);
    } else if (direction == RTDL_COPY_DEVICE_TO_DEVICE) {
        atomic_fetch_add_explicit(&g_dtod_calls, 1, memory_order_relaxed);
        atomic_fetch_add_explicit(&g_dtod_bytes, (uint64_t)byte_count, memory_order_relaxed);
    } else {
        atomic_fetch_add_explicit(&g_unknown_calls, 1, memory_order_relaxed);
        atomic_fetch_add_explicit(&g_unknown_bytes, (uint64_t)byte_count, memory_order_relaxed);
    }
}

void rtdl_cuda_transfer_counter_reset(void) {
    atomic_store_explicit(&g_total_calls, 0, memory_order_relaxed);
    atomic_store_explicit(&g_total_bytes, 0, memory_order_relaxed);
    atomic_store_explicit(&g_htod_calls, 0, memory_order_relaxed);
    atomic_store_explicit(&g_htod_bytes, 0, memory_order_relaxed);
    atomic_store_explicit(&g_dtoh_calls, 0, memory_order_relaxed);
    atomic_store_explicit(&g_dtoh_bytes, 0, memory_order_relaxed);
    atomic_store_explicit(&g_dtod_calls, 0, memory_order_relaxed);
    atomic_store_explicit(&g_dtod_bytes, 0, memory_order_relaxed);
    atomic_store_explicit(&g_unknown_calls, 0, memory_order_relaxed);
    atomic_store_explicit(&g_unknown_bytes, 0, memory_order_relaxed);
}

void rtdl_cuda_transfer_counter_set_enabled(int enabled) {
    atomic_store_explicit(&g_enabled, enabled ? 1u : 0u, memory_order_relaxed);
}

uint64_t rtdl_cuda_transfer_counter_is_enabled(void) {
    return atomic_load_explicit(&g_enabled, memory_order_relaxed);
}

void rtdl_cuda_transfer_counter_snapshot(RtdlCudaTransferCounterSnapshot* out) {
    if (!out) {
        return;
    }
    memset(out, 0, sizeof(*out));
    out->enabled = atomic_load_explicit(&g_enabled, memory_order_relaxed);
    out->total_calls = atomic_load_explicit(&g_total_calls, memory_order_relaxed);
    out->total_bytes = atomic_load_explicit(&g_total_bytes, memory_order_relaxed);
    out->host_to_device_calls = atomic_load_explicit(&g_htod_calls, memory_order_relaxed);
    out->host_to_device_bytes = atomic_load_explicit(&g_htod_bytes, memory_order_relaxed);
    out->device_to_host_calls = atomic_load_explicit(&g_dtoh_calls, memory_order_relaxed);
    out->device_to_host_bytes = atomic_load_explicit(&g_dtoh_bytes, memory_order_relaxed);
    out->device_to_device_calls = atomic_load_explicit(&g_dtod_calls, memory_order_relaxed);
    out->device_to_device_bytes = atomic_load_explicit(&g_dtod_bytes, memory_order_relaxed);
    out->unknown_calls = atomic_load_explicit(&g_unknown_calls, memory_order_relaxed);
    out->unknown_bytes = atomic_load_explicit(&g_unknown_bytes, memory_order_relaxed);
}

const char* rtdl_cuda_transfer_counter_version(void) {
    return "rtdl.cuda_transfer_counter.v3_m11";
}

static void* rtdl_next_symbol(const char* name) {
    return dlsym(RTLD_NEXT, name);
}

#define RTDL_ORIGINAL(name, type) ((type)rtdl_next_symbol(name))

CUresult cuMemcpyHtoD(CUdeviceptr dstDevice, const void* srcHost, size_t ByteCount) {
    typedef CUresult (*Fn)(CUdeviceptr, const void*, size_t);
    rtdl_count_copy(RTDL_COPY_HOST_TO_DEVICE, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyHtoD", Fn);
    return fn(dstDevice, srcHost, ByteCount);
}

CUresult cuMemcpyHtoD_v2(CUdeviceptr dstDevice, const void* srcHost, size_t ByteCount) {
    typedef CUresult (*Fn)(CUdeviceptr, const void*, size_t);
    rtdl_count_copy(RTDL_COPY_HOST_TO_DEVICE, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyHtoD_v2", Fn);
    return fn(dstDevice, srcHost, ByteCount);
}

CUresult cuMemcpyHtoDAsync(CUdeviceptr dstDevice, const void* srcHost, size_t ByteCount, CUstream hStream) {
    typedef CUresult (*Fn)(CUdeviceptr, const void*, size_t, CUstream);
    rtdl_count_copy(RTDL_COPY_HOST_TO_DEVICE, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyHtoDAsync", Fn);
    return fn(dstDevice, srcHost, ByteCount, hStream);
}

CUresult cuMemcpyHtoDAsync_v2(CUdeviceptr dstDevice, const void* srcHost, size_t ByteCount, CUstream hStream) {
    typedef CUresult (*Fn)(CUdeviceptr, const void*, size_t, CUstream);
    rtdl_count_copy(RTDL_COPY_HOST_TO_DEVICE, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyHtoDAsync_v2", Fn);
    return fn(dstDevice, srcHost, ByteCount, hStream);
}

CUresult cuMemcpyDtoH(void* dstHost, CUdeviceptr srcDevice, size_t ByteCount) {
    typedef CUresult (*Fn)(void*, CUdeviceptr, size_t);
    rtdl_count_copy(RTDL_COPY_DEVICE_TO_HOST, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyDtoH", Fn);
    return fn(dstHost, srcDevice, ByteCount);
}

CUresult cuMemcpyDtoH_v2(void* dstHost, CUdeviceptr srcDevice, size_t ByteCount) {
    typedef CUresult (*Fn)(void*, CUdeviceptr, size_t);
    rtdl_count_copy(RTDL_COPY_DEVICE_TO_HOST, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyDtoH_v2", Fn);
    return fn(dstHost, srcDevice, ByteCount);
}

CUresult cuMemcpyDtoHAsync(void* dstHost, CUdeviceptr srcDevice, size_t ByteCount, CUstream hStream) {
    typedef CUresult (*Fn)(void*, CUdeviceptr, size_t, CUstream);
    rtdl_count_copy(RTDL_COPY_DEVICE_TO_HOST, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyDtoHAsync", Fn);
    return fn(dstHost, srcDevice, ByteCount, hStream);
}

CUresult cuMemcpyDtoHAsync_v2(void* dstHost, CUdeviceptr srcDevice, size_t ByteCount, CUstream hStream) {
    typedef CUresult (*Fn)(void*, CUdeviceptr, size_t, CUstream);
    rtdl_count_copy(RTDL_COPY_DEVICE_TO_HOST, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyDtoHAsync_v2", Fn);
    return fn(dstHost, srcDevice, ByteCount, hStream);
}

CUresult cuMemcpyDtoD(CUdeviceptr dstDevice, CUdeviceptr srcDevice, size_t ByteCount) {
    typedef CUresult (*Fn)(CUdeviceptr, CUdeviceptr, size_t);
    rtdl_count_copy(RTDL_COPY_DEVICE_TO_DEVICE, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyDtoD", Fn);
    return fn(dstDevice, srcDevice, ByteCount);
}

CUresult cuMemcpyDtoD_v2(CUdeviceptr dstDevice, CUdeviceptr srcDevice, size_t ByteCount) {
    typedef CUresult (*Fn)(CUdeviceptr, CUdeviceptr, size_t);
    rtdl_count_copy(RTDL_COPY_DEVICE_TO_DEVICE, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyDtoD_v2", Fn);
    return fn(dstDevice, srcDevice, ByteCount);
}

CUresult cuMemcpyDtoDAsync(CUdeviceptr dstDevice, CUdeviceptr srcDevice, size_t ByteCount, CUstream hStream) {
    typedef CUresult (*Fn)(CUdeviceptr, CUdeviceptr, size_t, CUstream);
    rtdl_count_copy(RTDL_COPY_DEVICE_TO_DEVICE, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyDtoDAsync", Fn);
    return fn(dstDevice, srcDevice, ByteCount, hStream);
}

CUresult cuMemcpyDtoDAsync_v2(CUdeviceptr dstDevice, CUdeviceptr srcDevice, size_t ByteCount, CUstream hStream) {
    typedef CUresult (*Fn)(CUdeviceptr, CUdeviceptr, size_t, CUstream);
    rtdl_count_copy(RTDL_COPY_DEVICE_TO_DEVICE, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyDtoDAsync_v2", Fn);
    return fn(dstDevice, srcDevice, ByteCount, hStream);
}

CUresult cuMemcpy(CUdeviceptr dst, CUdeviceptr src, size_t ByteCount) {
    typedef CUresult (*Fn)(CUdeviceptr, CUdeviceptr, size_t);
    rtdl_count_copy(RTDL_COPY_UNKNOWN, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpy", Fn);
    return fn(dst, src, ByteCount);
}

CUresult cuMemcpy_v2(CUdeviceptr dst, CUdeviceptr src, size_t ByteCount) {
    typedef CUresult (*Fn)(CUdeviceptr, CUdeviceptr, size_t);
    rtdl_count_copy(RTDL_COPY_UNKNOWN, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpy_v2", Fn);
    return fn(dst, src, ByteCount);
}

CUresult cuMemcpyAsync(CUdeviceptr dst, CUdeviceptr src, size_t ByteCount, CUstream hStream) {
    typedef CUresult (*Fn)(CUdeviceptr, CUdeviceptr, size_t, CUstream);
    rtdl_count_copy(RTDL_COPY_UNKNOWN, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyAsync", Fn);
    return fn(dst, src, ByteCount, hStream);
}

CUresult cuMemcpyAsync_v2(CUdeviceptr dst, CUdeviceptr src, size_t ByteCount, CUstream hStream) {
    typedef CUresult (*Fn)(CUdeviceptr, CUdeviceptr, size_t, CUstream);
    rtdl_count_copy(RTDL_COPY_UNKNOWN, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyAsync_v2", Fn);
    return fn(dst, src, ByteCount, hStream);
}

CUresult cuMemcpyPeer(CUdeviceptr dstDevice, CUcontext dstContext, CUdeviceptr srcDevice, CUcontext srcContext, size_t ByteCount) {
    typedef CUresult (*Fn)(CUdeviceptr, CUcontext, CUdeviceptr, CUcontext, size_t);
    rtdl_count_copy(RTDL_COPY_DEVICE_TO_DEVICE, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyPeer", Fn);
    return fn(dstDevice, dstContext, srcDevice, srcContext, ByteCount);
}

CUresult cuMemcpyPeerAsync(CUdeviceptr dstDevice, CUcontext dstContext, CUdeviceptr srcDevice, CUcontext srcContext, size_t ByteCount, CUstream hStream) {
    typedef CUresult (*Fn)(CUdeviceptr, CUcontext, CUdeviceptr, CUcontext, size_t, CUstream);
    rtdl_count_copy(RTDL_COPY_DEVICE_TO_DEVICE, ByteCount);
    Fn fn = RTDL_ORIGINAL("cuMemcpyPeerAsync", Fn);
    return fn(dstDevice, dstContext, srcDevice, srcContext, ByteCount, hStream);
}

static int rtdl_runtime_direction(cudaMemcpyKind kind) {
    if (kind == 1) {
        return RTDL_COPY_HOST_TO_DEVICE;
    }
    if (kind == 2) {
        return RTDL_COPY_DEVICE_TO_HOST;
    }
    if (kind == 3) {
        return RTDL_COPY_DEVICE_TO_DEVICE;
    }
    return RTDL_COPY_UNKNOWN;
}

cudaError_t cudaMemcpy(void* dst, const void* src, size_t count, cudaMemcpyKind kind) {
    typedef cudaError_t (*Fn)(void*, const void*, size_t, cudaMemcpyKind);
    rtdl_count_copy(rtdl_runtime_direction(kind), count);
    Fn fn = RTDL_ORIGINAL("cudaMemcpy", Fn);
    return fn(dst, src, count, kind);
}

cudaError_t cudaMemcpyAsync(void* dst, const void* src, size_t count, cudaMemcpyKind kind, CUstream stream) {
    typedef cudaError_t (*Fn)(void*, const void*, size_t, cudaMemcpyKind, CUstream);
    rtdl_count_copy(rtdl_runtime_direction(kind), count);
    Fn fn = RTDL_ORIGINAL("cudaMemcpyAsync", Fn);
    return fn(dst, src, count, kind, stream);
}

// Application-owned CUDA continuation for the public-PyOptiX baseline.
#define RTDL_INT_MAX 2147483647

extern "C" __global__ void initialize(
    int* parent,
    int* border,
    int* roots,
    int* first,
    int* markers,
    int* labels,
    unsigned int count) {
    const unsigned int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < count) {
        parent[i] = (int)i;
        border[i] = RTDL_INT_MAX;
        roots[i] = -1;
        first[i] = RTDL_INT_MAX;
        markers[i] = 0;
        labels[i] = -1;
    }
}

extern "C" __global__ void extract_core_roots(
    const int* parent,
    const unsigned char* core,
    int* roots,
    unsigned int* status,
    unsigned int count) {
    const unsigned int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= count || !core[i]) {
        return;
    }
    int root = (int)i;
    for (unsigned int step = 0; step < count; ++step) {
        const int next = parent[root];
        if (next == root) {
            roots[i] = root;
            return;
        }
        if (next < 0 || next >= root) {
            atomicCAS(status, 0u, 2u);
            return;
        }
        root = next;
    }
    atomicCAS(status, 0u, 2u);
}

extern "C" __global__ void assign_roots_and_first(
    const unsigned char* core,
    const int* border,
    int* roots,
    int* first,
    unsigned int* status,
    unsigned int count) {
    const unsigned int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= count) {
        return;
    }
    if (!core[i]) {
        roots[i] = border[i] == RTDL_INT_MAX ? -1 : border[i];
    }
    const int root = roots[i];
    if (root >= 0) {
        if ((unsigned int)root >= count) {
            roots[i] = -1;
            atomicCAS(status, 0u, 3u);
            return;
        }
        atomicMin(first + root, (int)i);
    } else if (core[i]) {
        atomicCAS(status, 0u, 3u);
    }
}

extern "C" __global__ void mark_first(
    const int* roots,
    const int* first,
    int* markers,
    unsigned int count) {
    const unsigned int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < count) {
        markers[i] = roots[i] >= 0 && (unsigned int)roots[i] < count &&
            first[roots[i]] == (int)i ? 1 : 0;
    }
}

extern "C" __global__ void write_labels(
    const int* roots,
    const int* first,
    const int* prefix,
    int* labels,
    unsigned int count) {
    const unsigned int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < count) {
        const int root = roots[i];
        labels[i] = root < 0 || (unsigned int)root >= count || first[root] < 0 ||
                (unsigned int)first[root] >= count
            ? -1
            : prefix[first[root]] - 1;
    }
}

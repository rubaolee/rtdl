struct RelationRow {
    unsigned int source_id;
    unsigned int item_id;
};

static constexpr unsigned int GOAL5802_RELATION_CAPACITY_STATUS = 0xffff5102u;

static __forceinline__ __device__ unsigned long long relation_key(
        const RelationRow row) {
    return (static_cast<unsigned long long>(row.source_id) << 32) |
        static_cast<unsigned long long>(row.item_id);
}

static __forceinline__ __device__ unsigned long long mix_u64(
        unsigned long long value) {
    value ^= value >> 33;
    value *= 0xff51afd7ed558ccdull;
    value ^= value >> 33;
    value *= 0xc4ceb9fe1a85ec53ull;
    return value ^ (value >> 33);
}

// Exact parallel distinct-row admission.  keys[] is initialized to
// UINT64_MAX.  The legitimate all-ones row key uses max_key_seen instead of
// colliding with that sentinel.  unique_count is copied device-to-device into
// control[1] before the 16-byte status boundary reaches the host.
extern "C" __global__ void goal5802_relation_unique_compact(
        const RelationRow* raw_rows,
        RelationRow* unique_rows,
        unsigned int* control,
        unsigned long long* keys,
        unsigned int* max_key_seen,
        unsigned int* unique_count,
        unsigned int raw_capacity,
        unsigned int semantic_capacity,
        unsigned int key_capacity) {
    const unsigned int index = blockIdx.x * blockDim.x + threadIdx.x;
    const unsigned int raw_count = control[0];
    if (index >= raw_count || index >= raw_capacity) return;
    const RelationRow row = raw_rows[index];
    const unsigned long long key = relation_key(row);
    bool inserted = false;
    if (key == ~0ull) {
        inserted = atomicCAS(max_key_seen, 0u, 1u) == 0u;
    } else if (key_capacity != 0u &&
               (key_capacity & (key_capacity - 1u)) == 0u) {
        const unsigned int mask = key_capacity - 1u;
        unsigned int slot = static_cast<unsigned int>(mix_u64(key)) & mask;
        for (unsigned int probe = 0u; probe < key_capacity; ++probe) {
            const unsigned long long prior = atomicCAS(
                keys + slot, ~0ull, key);
            if (prior == ~0ull) {
                inserted = true;
                break;
            }
            if (prior == key) break;
            slot = (slot + 1u) & mask;
        }
    } else {
        atomicExch(control + 2, 1u);
        atomicExch(control + 3, GOAL5802_RELATION_CAPACITY_STATUS);
        return;
    }
    if (!inserted) return;
    const unsigned int unique_slot = atomicAdd(unique_count, 1u);
    if (unique_slot < semantic_capacity) {
        unique_rows[unique_slot] = row;
    } else {
        atomicExch(control + 2, 1u);
        atomicExch(control + 3, GOAL5802_RELATION_CAPACITY_STATUS);
    }
}

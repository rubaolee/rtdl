I will begin by reading the key documents to understand the scope and objectives of Goal 18.
I will now examine the current implementation in `src/rtdsl/embree_runtime.py` and the available kernel types in `src/rtdsl/api.py` to determine which workloads are candidates for the low-overhead path extension.
I will now examine `src/native/rtdl_embree.cpp` to verify if there are any additional predicates or functions that should be included in the low-overhead path extension.
I will now check `src/rtdsl/types.py` to confirm the available geometry types and ensure they align with the planned extensions for the low-overhead path.

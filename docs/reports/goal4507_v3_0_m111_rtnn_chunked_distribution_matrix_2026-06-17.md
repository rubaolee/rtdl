# Goal4507 / V3 M111 RTNN Chunked Distribution Matrix

## Conclusion

The M19 chunked partner-continuation route now has measured 1,048,576-query runtime evidence across the current uniform, shell, and clustered synthetic distribution family. All three rows execute 16 chunks, reuse the prepared scene, match CuPy/Numba signatures, pass the hot no-hidden-column-copy gate, and keep materialization after the hot window. Clustered is the expected slowest row and uniform is the fastest. These rows are still not official RTNN paper-dataset reproduction and not aggregate-only full-batch direct comparison rows.

## Matrix

| Distribution | Chunks | CuPy hot median-sum | Numba hot median-sum | Signature | No hidden copy |
| --- | ---: | ---: | ---: | --- | --- |
| uniform | 16 | 0.082908s | 0.083390s | `True` | `True` |
| shell | 16 | 0.609413s | 0.609404s | `True` | `True` |
| clustered | 16 | 2.041410s | 2.036964s | `True` | `True` |

## Boundary

- This matrix is for the current synthetic M19 distribution family: uniform, shell, clustered.
- It does not replace official RTNN paper datasets.
- It does not authorize public speedup, RT-core speedup, whole-app speedup, automatic partner selection, or aggregate-only full-batch direct comparison wording.

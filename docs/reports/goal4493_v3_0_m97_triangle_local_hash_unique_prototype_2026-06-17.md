# Goal4493 / V3 M97 Triangle Local-Hash Unique Prototype

## Conclusion

Goal4493 tests the next concrete Triangle Counting idea from Goal4492: a bounded source-group local unique-count kernel for the small-group side of a future hybrid/two-pass route.

The prototype is correct and becomes useful at realistic segment scale. On 20M selected two-hop rows per paper dataset, the Numba CUDA local-hash path matches the duplicate-key fill plus sort/RLE reference and is 1.01x-1.43x faster. The strongest row is `com_orkut`, where the local hash path is 1.43x faster for the selected small source groups.

This is not a route change. The prototype only handles source groups with at most 2,048 two-hop rows. From Goal4492, that bound covers 64.77% of `com_lj`, 53.87% of `soc_livejournal1`, and only 21.21% of `com_orkut` two-hop rows. The next real optimization must combine this small-group local branch with a large-tail sort/RLE fallback.

## Evidence

Hardware: RTX 4000 Ada pod, driver 550.127.08.

Numba CUDA toolchain: packaged CUDA 12.4 `ptxas`:

```text
Build cuda_12.4.r12.4/compiler.34097967_0
```

Artifacts:

- `docs/reports/goal4493_v3_0_m97_triangle_local_hash_unique_prototype_2026-06-17.json`
- `docs/reports/goal4493_v3_0_m97_triangle_local_hash_unique_prototype_2026-06-17.jsonl`

Parameters:

- target rows per dataset: 20,000,000 selected two-hop rows;
- local hash bound: 2,048 rows per source group;
- local hash capacity: 4,096 slots;
- repeats: 3;
- threads per block: 256.

| Dataset | Selected groups | Selected rows | Unique rows | Local hash median | Fill + sort/RLE median | Speedup | Validated |
|---|---:|---:|---:|---:|---:|---:|---|
| `com_lj` | 40,478 | 20,001,337 | 12,700,711 | 0.013936s | 0.015688s | 1.13x | yes |
| `soc_livejournal1` | 50,277 | 20,000,810 | 15,048,018 | 0.016000s | 0.016109s | 1.01x | yes |
| `com_orkut` | 18,448 | 20,000,038 | 14,657,253 | 0.010661s | 0.015255s | 1.43x | yes |

## Reading

This resolves the immediate question from Goal4492: local unique-count is not fantasy, but it is also not enough by itself.

The useful shape is now sharper:

- keep `numba_direct_sort_rle` as the current complete route;
- add an explicit hybrid candidate that sends source groups `<=2048` to the local-hash branch;
- compact large source groups into the existing duplicate-key fill plus sort/RLE fallback;
- preserve the generic prepared ray/triangle weighted any-hit primitive after ray construction.

Claim boundary:

- prototype only;
- selected small source groups only;
- route changed: false;
- large-tail fallback implemented: false;
- public speedup claim authorized: false;
- native engine customization: false;
- app-specific native engine callback: false.

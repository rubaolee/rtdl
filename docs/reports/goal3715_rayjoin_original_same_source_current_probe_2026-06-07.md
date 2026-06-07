# Goal3715 RayJoin Original Same-Source Current Probe

Date: 2026-06-07

Status: internal diagnostic evidence against the original RayJoin executable. This is not a RayJoin paper reproduction, not a release packet, not a public speedup claim, not an RTDL-beats-RayJoin claim, not a broad RT-core speedup claim, not a true zero-copy claim, and not a native default-route authorization.

## Purpose

Goal3691 compared RTDL with the original RayJoin executable on RayJoin's bundled Brazil sample files. That older packet found:

- PIP query time was promising for RTDL, but RayJoin did not print a PIP count.
- LSI was a blocker: RTDL reported `20859`, RayJoin reported `20860`.

Goals3696-3708 repaired the segment-pair exact-count contract and moved LSI to a prepared-left one-pass exact-count route.

Goal3715 reruns the original-RayJoin same-source probe on current `main` to answer:

> Did the LSI repair fix the original-RayJoin same-source correctness gap, and what is the current query-time comparison?

## Evidence

Pod:

- NVIDIA RTX A5000, driver `580.126.09`
- RTDL source commit `5951f35853ad09d3873926ad4c2012e0837fa16b`
- RayJoin source commit `02bf622`
- runner `scripts/goal3691_rayjoin_original_same_source_probe.py`
- artifact `docs/reports/goal3715_rayjoin_original_same_source_current_a5000/summary.json`

Datasets:

- county: `/root/RayJoin/test/dataset/br_county_clean_25_odyssey_final.txt`
- soil: `/root/RayJoin/test/dataset/br_soil_ascii_odyssey_final.txt`

Run shape:

- RayJoin repeat `3`, warmup `2`
- RTDL repeat `5`, warmup `3`
- RayJoin `-mode=rt`
- RayJoin `-xsect_factor=0.1`

## Result

| Query | RayJoin Query Sec | RTDL Query Sec | RTDL / RayJoin Speedup | Count Status |
| --- | ---: | ---: | ---: | --- |
| PIP | `0.000872374` | `0.000469153` | `1.859x` | RayJoin PIP count not printed |
| LSI | `0.000873963` | `0.001100961` | `0.794x` | both report `20860` |

The important change from Goal3691 is LSI correctness:

| Packet | RayJoin LSI | RTDL LSI | Delta |
| --- | ---: | ---: | ---: |
| Goal3691 | `20860` | `20859` | `-1` |
| Goal3715 | `20860` | `20860` | `0` |

RayJoin's `-check=true` LSI run also reports `20860`.

## Interpretation

This is a stronger state than Goal3691:

- The LSI correctness blocker is fixed for the same-source RayJoin Brazil sample.
- RTDL's PIP query time remains faster than RayJoin on this sample, but the PIP count still cannot be compared because RayJoin `query_exec` timing output does not print the PIP hit count.
- RTDL's LSI query is now close to RayJoin but still slower: `0.794x`, or about `1.26x` longer latency than RayJoin for the measured query phase.

The current RayJoin-facing performance gap is now precise:

- PIP needs a RayJoin-count oracle before any correctness-backed same-source claim.
- LSI needs about a `1.26x` query-latency improvement to reach same-source parity with RayJoin's executable on this sample.

## Boundary

This report does not authorize:

- release,
- public speedup wording,
- RTDL-beats-RayJoin wording,
- RayJoin paper reproduction wording,
- broad RT-core speedup wording,
- true zero-copy wording,
- native default-route promotion.

It records internal evidence that the current RTDL LSI route now matches original RayJoin's LSI count on the bundled Brazil sample, while still trailing RayJoin's query time.

## Next Work

1. Investigate whether the remaining LSI gap is Python/ctypes overhead, OptiX launch overhead, exact-predicate overhead, or RayJoin's app-specialized primitive layout.
2. Add a RayJoin PIP count-output path or another trusted PIP count oracle for the original sample.
3. Preserve Goal3713 as the all-CuPy same-contract comparison packet; keep Goal3715 separate as original-RayJoin executable evidence.

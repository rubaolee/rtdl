# V4 long-workload performance matrix

Date: 2026-09-08, America/New_York. Status: formal successor transaction and
independent recount complete; manuscript and public claim review remain open.

## Registered matrix and disposition

The frozen transaction contains five units: four retained original operation
units and one C-only-preselected long graph scale. Each unit has `complete` and
`prepared` endpoints, three arms, and eight paired fresh-process blocks. The
primary engineering comparison is successor RTDL (`new_v4`) divided by
competent public PyOptiX (`pyoptix`). Lower is better.

| Unit | Natural work and exact output | Complete A/C | Prepared A/C | Long prepared computation? | Disposition |
| --- | --- | ---: | ---: | --- | --- |
| Particle cell transition | Real mesh encoding with 3,392,530 faces; 5,000 valid queries; ordered `5000 x 3` U32 matrix | 0.1855 [0.1116--0.2011] | 0.7726 [0.6838--0.8403] | No; 0.402 ms A, 0.542 ms C | Original-input fixed-cost regression passes; fixed 5,000-query specialization only |
| Graph RT-2A1, com-dblp/1M | 8 segments; 1,006,685 total segment primitives; 3,413,500 total segment queries; checked U64 count 2,224,385 | 1.0548 [0.9521--1.1654] | 1.0995 [1.0497--1.1829] | No; 0.478 s A, 0.435 s C | Original-input graph regression passes |
| LibRTS Parks point | 11,544,398 indexed boxes; 100,000 point queries; exact count 112,729 | 0.3231 [0.2921--0.3575] | 0.9987 [0.7329--1.1104] | No; 0.256 ms A, 0.251 ms C | Original-input fixed-cost regression passes |
| LibRTS Parks range | 11,544,398 indexed boxes; 100,000 range queries; exact count 105,826 | 0.3652 [0.3307--0.4203] | 0.9849 [0.6116--1.2433] | No; 0.252 ms A, 0.259 ms C | Original-input fixed-cost regression passes |
| Graph RT-2A1, cit-Patents/4M | 28 segments; 15,853,615 total segment primitives; 69,850,749 total segment queries; checked U64 count 7,515,023 | 1.0381 [1.0029--1.0575] | 1.0574 [1.0378--1.0837] | Yes; 9.348 s A, 8.802 s C | Preselected multi-second natural graph computation passes |

All ten rows satisfy paired median `<= 1.20` and every block `<= 1.35`. This is
an engineering acceptance result, not a statement that RTDL is faster in
general. The arm times are medians of worker medians; paired ratios are medians
of eight within-block ratios, so dividing displayed arm medians need not
reproduce the paired estimator exactly.

## Separate Particle natural-scale transaction

The current `110dee7aa` transaction is separate from the ten-row matrix and is
not pooled into it. It uses the same real mesh with 160,000,000 distinct
strict-interior transition queries and a complete ordered 1.92 GB U32x3
output. Its prepared paired median is `0.994109x` with a `1.062304x` worst
block, so all eight blocks meet the same engineering envelope. Both arms take
approximately 0.35 seconds per action; this is materially larger and more
stable than the original 5,000-query regression but still below one second.
RTDL/PyOptiX preparation is `8.984/10.463` seconds. This closes the measured
setup disadvantage in its same-machine `c06fd73a5` predecessor, whose RTDL
preparation median was `24.259` seconds. The current transaction remains
internal and lead review is pending.

## What the matrix closes

- The original Particle and LibRTS prepared gaps of roughly 38--39x are not
  hidden by a larger workload. Their successor prepared rows are within the
  registered envelope on the same GPU and original inputs.
- Both original and long graph rows use the same RT-2A1 application contract.
  The cit-Patents/4M prepared action is a genuine 8.8--9.3 second computation,
  not sleep, repeated copies, or initialization time.
- All 240 workers produced the registered output, used distinct process IDs,
  observed CPU affinity `{8}` before and after execution, and completed with
  zero retry, discard, or timeout.
- A project-independent clean checkout reconstructed all 80 cells and all ten
  evaluations directly from journals and raw files.

## What remains open

- Particle now has a 160M distinct-query natural-scale prepared transaction,
  but it remains subsecond; LibRTS still lacks a distinct-query multi-second
  prepared scale. Preparation exceeding one second does not satisfy the
  strong-C natural-compute criterion.
- Six of the nine historical application mappings have no frozen,
  output-equivalent public-PyOptiX owner in this transaction. They are not
  silently counted as measured.
- Particle uses a checked but app-shaped fixed standard-library
  specialization. It does not establish an app-independent native engine or
  arbitrary callback performance.
- CPU 8 was chosen after a scheduling diagnostic. The formal comparison is
  fair under that registered condition, but does not prove CPU-invariant
  timing. GPU application-clock locking was unavailable.
- A fixed post-formal scan completed 384/384 fresh workers over all 48 logical
  CPUs for the two shortest prepared units. It is not pooled with formal
  evidence. CPU-8 Particle reversed from a `0.772559x` formal median to
  `1.399874x`; only 36/48 Particle and 41/48 LibRTS CPUs kept both scan blocks
  at or below `1.35x`. These sub-millisecond rows are not stable performance
  guarantees.
- Formal GPU peak-memory measurements were not captured. Static input and
  segment sizes are available; no peak-memory value should be invented from
  them.

## Custody

The formal archive is
`raw/rtdl-v4-long-perf-successor-02e84374f-affinity-final.tar.gz`, SHA-256
`ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc`.
The earlier unlocked successor remains adverse evidence and is never pooled:
`raw/rtdl-v4-long-perf-successor-0c3420f42-unlocked-adverse.tar.gz`, SHA-256
`924f970e4d29778b8c53d81c57bbb725e2641bd66be54c6a6584c343760bdf09`.

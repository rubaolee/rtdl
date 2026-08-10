# Arkade Paper App

This directory implements the ninth RTDL Paper App candidate from the pinned
Arkade ICS 2024 source.  The application owns two mandatory algorithms:

- `FR_LINF`: Filter–Refine with 3-D L-infinity distance;
- `MT_COSINE`: unit-normalized monotone transformation for cosine kNN.

Both are exposed in two lanes:

- `v2_direct_true_optix_backport`: an independent legacy adapter that owns
  preprocessing/packing and calls the generic native ABI directly; it does
  not import the V3 metric-kNN compiler module;
- `v3_compiler_true_optix`: canonical semantic resolution followed by the same
  physical executor.

The V3 DEFAULT never chooses between FR and MT.  The caller selects the paper
algorithm.  The production compiled front door has one canonical OptiX plan
and exposes no provider callback.  A separately named CPU model exists only
for functional validation and is never a selectable production provider.

The physical family implements the paper algorithm rather than merely its
output relation: one persistent refittable GAS, radius doubling, device-side
exact FR or normalized-MT metric filtering, deterministic bounded top-k, and a
fixed `query_count * k` download.  It never materializes the unbounded
query-by-data candidate relation on the host.

The paper's two reductions are implementable.  The pinned public artifact is
not a complete exact oracle: its output path is commented, binary32 top-k has
no item-ID tie rule, and its TrueKNN loop has no fail-closed round bound.  RTDL
therefore preserves the paper reductions while adding an explicit binary32
metric-key/U32-ID ordering and bounded failure; it does not relabel that
stricter output as the public executable's byte behavior.

Goal5745 starts from the exact author source archive frozen by Goal5744.  Home
functional evidence covers both V2/V3 lanes, both paper algorithms, the full
10,000-point author sample, a real RTNN second consumer, and adversarial
precision/capacity/fail-closed cases.  Modern-RTX performance remains a
separate, not-yet-authorized measurement.

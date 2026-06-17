# Goal4513 / V3 M117 Primitive App Clean-Target Audit

## Conclusion

Robot Collision, Contact Manifold, RayDB-style, LibRTS Spatial Index, and Hausdorff/X-HD are closed as primitive/no-partner V3 clean targets. Their current routes are explicit primitive-first or no-partner-needed paths, M113 is not their current performance path, and public broad speedup wording remains blocked.

## App Matrix

| App | Decision | Partner policy | Current route | M113 current path |
| --- | --- | --- | --- | --- |
| Robot Collision | `no_partner_needed` | `none` | prepared grouped-segment any-hit primitive with NumPy vectorized query lowering | `False` |
| Contact Manifold | `no_partner_needed` | `none` | prepared bounded contact-witness collect primitive | `False` |
| RayDB-style | `primitive_first` | `primitive_only` | primitive-first RTDL/OptiX grouped count/sum reductions | `False` |
| LibRTS Spatial Index | `no_partner_needed` | `none` | prepared RTDL/OptiX AABB spatial-index query primitive | `False` |
| Hausdorff / X-HD | `primitive_first` | `primitive_only` | RTDL/OptiX active-frontier nearest-witness plus generic grouped max continuation | `False` |

## Boundaries

- No app in this packet authorizes public speedup wording.
- No app in this packet authorizes broad RT-core or whole-application acceleration wording.
- No app in this packet authorizes automatic partner selection.
- No app in this packet needs M113 as its current performance path.
- RayJoin is intentionally excluded and handled in a separate mixed-explicit audit.

## Per-App Reading

### Robot Collision

- Primitive contract: `PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1`.
- Current reader decision: Use the prepared grouped-segment any-hit primitive. For large prepared timing or summary probes, use Goal4446's NumPy vectorized query lowering; no partner continuation is needed on the promoted path.
- Next runtime action: preserve the prepared-buffer and device-buffer/count split; do not turn the sampled grouped-segment contract into robot-planner wording; validate AMD functional parity later
- M113 reading: The promoted path is a prepared grouped-segment any-hit primitive with NumPy vectorized query lowering. It does not need prepared graph chunks or partner continuation.

### Contact Manifold

- Primitive contract: `fail-closed bounded witness collection`.
- Current reader decision: Use bounded RTDL/OptiX witness collection; no promoted partner continuation is needed.
- Next runtime action: keep as primitive-only unless richer exact refinement becomes a benchmark pressure point
- M113 reading: The promoted path is bounded witness collection. Its pressure point is bounded collect semantics, not chunked partner continuation.

### RayDB-style

- Primitive contract: `columnar grouped count/sum/min/max/avg reduction`.
- Current reader decision: Use primitive-first RTDL/OptiX fused grouped reductions when the fused primitive fits.
- Next runtime action: preserve primitive-first route and avoid partner work for exact fused scalar reductions
- M113 reading: The promoted path is primitive-first grouped reduction. Fused scalar count/sum/min/max/avg reductions should stay inside the primitive when they fit.

### LibRTS Spatial Index

- Primitive contract: `prepared AABB index query`.
- Current reader decision: Use prepared generic AABB index query; no promoted partner continuation is needed.
- Next runtime action: keep as no-regression prepared-index row and validate AMD functional parity later
- M113 reading: The promoted path is a prepared AABB index query, not a chunked partner-continuation graph.

### Hausdorff / X-HD

- Primitive contract: `directed max-of-nearest-distance witness computation`.
- Current reader decision: Use RTDL/OptiX nearest-witness primitives for the promoted exact route.
- Next runtime action: preserve primitive-first route; future work is broader residency and AMD validation
- M113 reading: The promoted path is nearest-witness computation plus grouped max continuation. It needs primitive residency and backend parity work, not prepared graph chunk execution.

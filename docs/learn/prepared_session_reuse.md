# Prepared Session Reuse

RTDL v2.14 supports an explicit prepared-session reuse pattern for workloads
where setup is expensive and repeated hot queries are small.

The short version:

```text
make a stable key -> prepare once on a miss -> reuse the prepared handle -> invalidate visibly
```

This is caller-owned reuse. RTDL does not choose a backend, does not choose a
partner, does not create a hidden global cache, and does not turn the pattern
into a public speedup or general zero-copy/device-residency claim.

## When To Use It

Use prepared-session reuse when the app has a stable scene, index, payload, or
prepared primitive handle and then runs many related queries over it.

Current measured examples include:

| App family | Generic primitive shape | Why reuse matters |
| --- | --- | --- |
| Hausdorff-style threshold probes | `fixed_radius_threshold_2d` | One prepared point scene can answer many threshold checks. |
| LibRTS-style spatial index queries | `aabb_index_query_2d` | One prepared AABB index can serve repeated query batches. |
| RTNN-style ranked summaries | `fixed_radius_neighbors_3d_ranked_summary` | One prepared 3D point scene can serve repeated radius/K requests. |
| Triangle-counting-style summaries | `ray_triangle_weighted_any_hit_sum_3d` | One prepared triangle scene can serve repeated weighted ray summaries. |

Those names are generic primitive shapes. App interpretation remains in Python
or partner code.

## Minimal Pattern

```python
import rtdsl as rt

cache = rt.ExplicitPreparedSessionCache(max_entries=4)

key = rt.make_prepared_session_cache_key(
    primitive="fixed_radius_threshold_summary_3d",
    backend="optix",
    input_fingerprints={"points": {"rows": 65536, "source": "stable-fixture"}},
    parameters={"radius": 0.02, "k": 32},
    partner="numba",
    device="cuda:0",
)


def prepare_session():
    # Build or load the prepared backend handle chosen by your application.
    # RTDL does not select this backend or partner for you.
    return {"prepared_handle": "user-owned-handle"}


first = rt.get_or_prepare_explicit_session(cache, key, prepare_session)
second = rt.get_or_prepare_explicit_session(cache, key, prepare_session)

assert first.cache_hit is False
assert second.cache_hit is True

metadata = second.to_metadata()
assert metadata["automatic_partner_selection_authorized"] is False
assert metadata["true_zero_copy_claim_authorized"] is False
```

The important parts are visible in user code:

- the primitive name is generic;
- the backend and partner are explicit;
- the input and parameter fingerprints define the cache key;
- the cache is passed by the caller;
- the prepare function is passed by the caller;
- cache hits, misses, and invalidations are recorded in metadata.

## Try A Live App Idiom

The RTNN benchmark front door includes a non-performance teaching mode that
invokes the same helper twice and prints the visible `miss`, `put`, `hit`
event log:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py \
  --mode prepared_session_reuse_idiom \
  --point-count 16 \
  --radius 0.02 \
  --k 8
```

This mode is intentionally not the promoted OptiX benchmark path. It is a
small app-level idiom check for `get_or_prepare_explicit_session`, and its
payload sets `native_runner_invoked = false` and `performance_evidence = false`.

## Invalidation

Invalidate when the prepared handle is no longer valid:

```python
cache.invalidate(key, event="explicit_invalidate")
cache.clear(event="close")
```

Supported invalidation events include:

- `explicit_invalidate`
- `input_fingerprint_change`
- `parameter_change`
- `backend_context_reset`
- `memory_pressure`
- `failure_cleanup`
- `close`

If the cached value has a `close()` method, the cache calls it during eviction,
invalidation, or clear.

## Reading App Metadata

Prepared benchmark apps that use this pattern emit a
`prepared_session_residency` field in their JSON payload. A learner should look
for:

| Field | Meaning |
| --- | --- |
| `cache_key` | The primitive, backend, partner, device, input fingerprints, and parameter fingerprints. |
| `policy` | Lifetime, reuse scope, invalidation events, and cold/hot phase names. |
| `cache_enabled_by_default` | Whether the app enables explicit reuse automatically. |
| `cold_hot_phase_split_required` | Whether timing must separate cold preparation from hot query. |
| `automatic_partner_selection_authorized` | Must remain `False`; the user chooses. |
| `true_zero_copy_claim_authorized` | Must remain `False` unless a separate reviewed path proves that exact zero-copy/device-residency claim. |
| `public_speedup_claim_authorized` | Must remain `False` unless reviewed release evidence authorizes that wording. |

## Claim Boundary

Prepared-session reuse is a useful programming pattern. It does not authorize:

- release action;
- public speedup wording;
- broad RT-core speedup wording;
- general zero-copy or device-residency wording;
- automatic partner or backend selection;
- app-specific native-engine logic.

The native engine stays app-agnostic. Prepared sessions describe reuse of
generic primitive handles; the application still decides what the result means.

## Related Pages

- [Prepared Execution Pattern](prepared_execution_pattern.md)
- [Primitive Discovery Workflow](primitive_discovery_workflow.md)
- [Choosing A Partner For Custom Logic](partner_choice_for_custom_logic.md)
- [Benchmark Partner Reference Matrix](benchmark_partner_reference_matrix.md)

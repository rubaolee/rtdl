# Tutorial: Inspect a V3 Canonical Lowering

This tutorial answers a narrow question: given one application-selected
semantic statement and an NVIDIA OptiX backend contract, which physical
provider is V3 authorized to materialize?

The first exercise is static and runs without a GPU.  It does not claim that a
kernel executed.  The second exercise points to the clean Linux artifact
validator, which supplies the separate behavioral evidence.

## 1. Run the static example

From the repository root:

```bash
PYTHONPATH=src:. python3 examples/current/v3_canonical_mapping.py
```

Expected shape:

```text
status: RESOLVED
statement: metric_knn.filter_refine_linf_3d.v1
backend: nvidia.optix_traversal.v1
provider: canonical_standalone/metric_knn_linf_filter_refine_3d/optix/prepared_metric_knn_3d_optix
cost input used: False
candidate executed: False
behavioral receipt still required: True
```

Arkade selected its FR-L-infinity algorithm before this call.  V3 did not
choose FR over MT.  V3 resolved the canonical OptiX provider for the already
selected L-infinity semantic statement.

## 2. Read what is bound

Open `examples/current/v3_canonical_mapping.py`.  The call supplies dynamic
facts such as cardinality and memory limits, but it does not supply a provider
name, callback, timing result, app name, or learned score.  The closed registry
supplies the provider's source, ABI, proof, resource, reuse, and template
identities.

Try changing `memory_limit_bytes` to `1`.  The call must fail closed rather than
silently choosing a route that violates its resource contract.

Try changing the statement to an unknown stable ID.  It must report an
unsupported semantic statement.  This is the intended answer when V3 lacks a
primitive: it does not invent a callback.

## 3. Separate static authority from physical evidence

The example reports `candidate executed: False`.  That is important.  Static
resolution proves what may execute; it does not prove that OptiX actually ran.
The portable Linux qualification separately requires:

- complete context-bound OptiX launches;
- zero failed, incomplete, unbound, pending, or session-error launches;
- nonzero traversable and ray-generation evidence where required;
- exact output against an independent oracle.

Follow [V3 release and installation](../docs/v3/release.md) to run
that target-specific validation.

## 4. Follow the source

Read these functions in order:

1. `registered_semantic_statement`;
2. `registered_backend_contract`;
3. `resolve_canonical_standalone_provider_for_contract`;
4. `resolve_canonical_provider`;
5. `bind_canonical_provider_to_direct_provider`.

They live in `src/rtdsl/canonical_physical_resolution.py`.  The common Action
front door is `compile_bound_action_for_target` in `src/rtdsl/action_api.py`.

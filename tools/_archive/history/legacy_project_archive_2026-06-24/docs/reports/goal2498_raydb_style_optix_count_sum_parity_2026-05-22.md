# Goal2498: RayDB-Style OptiX Count/Sum Parity

Date: 2026-05-22

## Verdict

Goal2498 adds the RayDB-style benchmark app's OptiX backend surface for the same
generic columnar grouped aggregate slice completed for Embree in Goal2497:
grouped `count` and grouped `sum` over a tiny denormalized columnar fixture.

This is a contract-parity step, not a RayDB reproduction and not a performance
claim.

## Implementation

Updated files:

- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `examples/v2_0/research_benchmarks/raydb_style/README.md`
- `examples/v2_0/research_benchmarks/README.md`

The app now accepts:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --backend optix --mode all
```

The OptiX path uses the existing high-level generic wrapper:

```python
rt.prepare_optix_db_dataset(
    rows,
    primary_fields=("ship_year", "discount", "quantity"),
    transfer="columnar",
)
```

Then it calls the existing dataset methods:

- `dataset.grouped_count(query)`
- `dataset.grouped_sum(query)`

## Native ABI Boundary

Goal2498 does not add native code and does not add any RayDB-specific native
symbol. The required native surface already exists as generic OptiX columnar
payload functions:

- `rtdl_optix_columnar_payload_create_from_columns`
- `rtdl_optix_columnar_payload_grouped_reduction_count`
- `rtdl_optix_columnar_payload_grouped_reduction_sum`

The Python app keeps RayDB-style/domain naming outside the engine. The RTDL
runtime path remains the generic columnar payload compatibility wrapper.

## Result Modes

Supported now:

- CPU reference: `count`, `sum`, `min`, `max`, `avg_as_sum_count`
- Embree: `count`, `sum`
- OptiX: `count`, `sum`

Unsupported native modes fail closed before backend loading.

## Claim Boundary

Allowed wording:

- OptiX count/sum parity for the synthetic RayDB-style columnar aggregate
  contract.
- Uses existing generic RTDL columnar payload capability through a compatibility
  wrapper.

Blocked wording:

- RayDB reproduction.
- Authors-code timing or comparison.
- SQL engine or DBMS behavior.
- Whole-app or public speedup claim.
- New native RayDB ABI.

## Validation Plan

Local validation should pass without OptiX by skipping runtime-only tests when
`rt.optix_version()` is unavailable.

Pod validation, when NVIDIA runtime is available:

```bash
PYTHONPATH=src:. python -m unittest tests.goal2498_raydb_style_optix_count_sum_parity_test
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --backend optix --mode all
```

The expected app payload must include:

- `"backend": "optix"`
- `"all_match_cpu_reference": true`
- `"native_abi_added": false`
- `"contract": "columnar_grouped_aggregate_optix_columnar_payload"`

Fresh pod evidence is still required before making any runtime-performance or
RTX wording claim.

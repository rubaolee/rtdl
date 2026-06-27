# V4 Goal4691 Tier-3 Callback Overhead Measurement

Status: measured overhead gate, not Tier-3 support and not release authorization

- status: `tier3_overhead_measured_not_support`
- primary ratio: `1.6705538933080346`
- classification: `yellow_overhead_between_pass_and_kill`

## Variants

### `inline_formula`

- status: `passed`
- median ms: `25.3571`
- sample count: `30`
- output matches expected: `True`

### `direct_device`

- status: `passed`
- median ms: `137.03`
- sample count: `30`
- output matches expected: `True`

### `direct_callable`

- status: `passed`
- median ms: `228.916`
- sample count: `30`
- output matches expected: `True`

## Boundary

This measurement does not authorize public Tier-3 callback support. It only classifies the overhead of the minimal scalar callback shape against the frozen Goal4690 denominator.

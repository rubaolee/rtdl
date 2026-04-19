# Goal596: Apple RT Prepared Closest-Hit Performance

Date: 2026-04-19

Status: local measurement artifact

## Methodology

- Workload: 3D `ray_triangle_closest_hit` on the same 256-ray / 256-triangle fixture used by Goal595.
- Warmups: `5`.
- Repeats: `20`.
- Stability threshold: coefficient of variation <= `0.15`.
- Prepared timing excludes one-time acceleration-structure build; `prepare_seconds` is reported separately.
- Unstable medians are engineering-triage evidence only, not public speedup wording.

## Versions

```json
{
  "apple_rt": [
    0,
    9,
    2
  ],
  "apple_rt_context": "Apple M4",
  "embree": [
    4,
    4,
    0
  ]
}
```

Prepare time: `0.043467334 s`.

## Results

| Backend path | Median | CV | Stable | Rows | Matches CPU |
| --- | ---: | ---: | --- | ---: | --- |
| `apple_rt_one_shot` | 0.002771604 s | 0.651 | False | 256 | True |
| `apple_rt_prepared` | 0.000441375 s | 0.646 | False | 256 | True |
| `embree` | 0.002656104 s | 0.111 | True | 256 | True |

## Ratios

- Prepared / one-shot Apple RT median ratio: `0.159x`.
- Prepared / Embree median ratio: `0.166x`.

## Interpretation

The prepared API reduces repeated-call median latency for this fixture, but Apple RT variance remains above the stability threshold.
This closes the prepared-handle functionality and optimization direction; public performance wording still requires stable follow-up evidence.

# Goal595: Apple RT Repeatable Performance Harness

Date: 2026-04-19

Status: local measurement artifact

## Methodology

- Cold time is the first measured backend call in this process before harness warmups.
- Warmups before sample window: `5`.
- Measured repeats: `20`.
- Stability threshold: coefficient of variation <= `0.15`.
- Reported statistics are min, median, mean, max, standard deviation, and coefficient of variation over the measured repeat window.
- CPU reference is used for parity; Embree is the mature RTDL local backend baseline.

## Host

```json
{
  "platform": "macOS-26.3-arm64-arm-64bit-Mach-O",
  "machine": "arm64",
  "processor": "arm"
}
```

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

## Results

| Workload | Input sizes | Rows | Embree median | Apple RT median | Apple/Embree | Parity | Stability |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `ray_triangle_closest_hit_3d` | `{'rays': 256, 'triangles': 256}` | 256 | 0.002749208 s | 0.001546417 s | 0.562x | True | False |
| `ray_triangle_hit_count_3d` | `{'rays': 128, 'triangles': 512}` | 128 | 0.002508270 s | 0.329233396 s | 131.259x | True | False |
| `segment_intersection_2d` | `{'left': 128, 'right': 128}` | 16384 | 0.007795938 s | 0.092515083 s | 11.867x | True | True |

## Stability Warnings

```json
[
  {
    "workload": "ray_triangle_closest_hit_3d",
    "backend": "apple_rt",
    "coefficient_of_variation": 0.9862270572001823,
    "threshold": 0.15
  },
  {
    "workload": "ray_triangle_hit_count_3d",
    "backend": "apple_rt",
    "coefficient_of_variation": 0.17130337852865118,
    "threshold": 0.15
  }
]
```

## Interpretation

This harness is the v0.9.2 baseline gate. It is not a final performance claim.
If any backend/workload cell is marked unstable, its median is evidence for engineering triage only and must not be used as public speedup wording.
The next Apple RT optimization goals should compare against this artifact and only update public wording after repeatable parity and timing evidence exists.

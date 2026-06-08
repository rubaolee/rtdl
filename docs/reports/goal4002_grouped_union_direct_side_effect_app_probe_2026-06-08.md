# Goal4002 Grouped-Union Direct-Side-Effect App Probe

Date: 2026-06-08

## Verdict

`reject-as-default`

Goal4001 showed that direct side effects inside the grouped-union intersection
program can reduce any-hit report overhead in raw extended telemetry. Goal4002
checked the next necessary question: should this mode become the default route
for the RT-DBSCAN benchmark app?

The answer is no. The app-level column-signature probe confirms correctness, but
the performance is mixed and too small to justify changing the default. Keep
direct side effects as an explicit experimental execution option.

Artifacts:

- `docs/reports/goal4002_direct_side_effect_app_probe_pod/clustered3d_default.json`
- `docs/reports/goal4002_direct_side_effect_app_probe_pod/clustered3d_direct.json`
- `docs/reports/goal4002_direct_side_effect_app_probe_pod/road3d_default.json`
- `docs/reports/goal4002_direct_side_effect_app_probe_pod/road3d_direct.json`
- `docs/reports/goal4002_direct_side_effect_app_probe_pod/ngsim_dense_default.json`
- `docs/reports/goal4002_direct_side_effect_app_probe_pod/ngsim_dense_direct.json`

## Pod Setup

- GPU: NVIDIA RTX 4000 Ada Generation
- Source commit: `1373a3b34f31446b70cb06534b1814070e06dac1`
- Mode: `optix_rt_core_grouped_stream_cupy_column_signature_3d`
- Point count: `65,536`
- Warmup: `1`
- Repeat: `3`
- Validation: disabled for timing; output signatures compared between default
  and direct-side-effect mode.

## Results

| Profile | Radius | Default elapsed sec | Direct elapsed sec | Direct / default | Default native sec | Direct native sec | Signature match |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `clustered3d` | `0.055` | `0.120874` | `0.117675` | `0.974x` | `0.080231` | `0.081390` | yes |
| `road3d` | `0.030` | `0.069482` | `0.069539` | `1.001x` | `0.032397` | `0.033743` | yes |
| `ngsim_dense` | `0.012` | `0.045522` | `0.047535` | `1.044x` | `0.009557` | `0.009474` | yes |

## Interpretation

Direct side effects are correct on these three app-level signatures, but they
are not a reliable default improvement:

- `clustered3d` improves end-to-end by only about `2.6%`;
- `road3d` is essentially parity;
- `ngsim_dense` slows end-to-end by about `4.4%`.

The result reconciles Goal4001 with the app runner. The raw native telemetry
knob is real, but the full app path also includes prepared adapter work and
column-signature materialization. At this scale, direct side effects do not
change the larger root-read/candidate traversal problem.

## Decision

Do not promote `grouped_union_direct_side_effect=True` as the default for the
fixed-radius grouped-union front door or the RT-DBSCAN benchmark app.

Keep it available as an explicit user-selected option because it can be useful
for future experiments, but the next real performance target remains the
generic partition/convergence hybrid from Goals3999-4001.

## Boundary

Goal4002 does not authorize release, public speedup wording, broad RT-core
speedup wording, whole-app acceleration wording, paper-reproduction wording,
true-zero-copy wording, automatic partner/backend selection, or app-specific
native-engine logic.

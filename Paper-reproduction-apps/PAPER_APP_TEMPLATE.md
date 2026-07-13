# Paper App Template

Use this template when adding a paper-reproduction app under
`Paper-reproduction-apps/<paper-name>/`.

The app should make two boundaries clear:

- what RTDL language/system features it exercises;
- what remains paper-specific application code.

## Required Directory Shape

```text
Paper-reproduction-apps/<paper-name>/
  README.md
  data/
    README.md
    manifest.json
  scripts/
  results/
    README.md
```

Applications may add source modules, adapters, or author patches as needed, but
the README and manifest must keep their scope explicit.

## README Sections

Every paper app README should include these sections.

### Paper And Artifact

- paper title, venue, and DOI or URL;
- author repository or artifact source;
- exact commit, branch, release, or archive identifier when available;
- build and runtime requirements for the author artifact.

### RTDL Program

List the RTDL public APIs exercised by the app.

Example:

```text
RTDL APIs exercised:
- prepare_planar_map_lsi_2d_optix
- prepare_planar_map_point_location_2d_optix
```

or:

```text
RTDL APIs exercised:
- aggregate_hierarchy_3d
- prepare_aggregate_hierarchy_3d
- SizeDistanceOpening
- aggregate_frontier_reduce_reference_3d
```

### App-Owned Code

List paper-specific pieces that are not RTDL language features.

Examples:

```text
App-owned:
- author artifact build patches
- paper workload selection
- paper-specific parser
- author comparator wrapper
- text output formatting
```

### Reproduction Scope

State exactly what is reproduced.

Use one of:

```text
not_started
bounded_same_input
bounded_workload
representative_workload
full_paper_claimed
blocked
```

Explain the input source, comparator source, and output tolerance.

### Performance Scope

State which regime is being measured.

Examples:

```text
cold process
warm long-lived process
fresh per-overlay computation
prepared replay diagnostic
prepared base with distinct queries
```

Also state whether the number includes:

- author or RTDL preprocessing;
- RTDL prepare/setup;
- output writer or text formatting;
- device-to-host materialization;
- downstream consumer work.

### Boundary

List forbidden claims.

Examples:

```text
Not claimed:
- full paper reproduction
- independent author pipeline reconstruction
- whole-program speedup
- author-performance parity
- native backend completion
```

## Manifest

Each app should provide:

```text
data/manifest.json
```

The manifest should follow:

```text
Paper-reproduction-apps/paper_app_manifest.schema.json
```

The manifest is intentionally descriptive rather than a runtime input format.
It exists so a reader can understand the app's paper source, RTDL surface,
comparator, reproduction scope, and performance boundary without reading the
whole codebase.

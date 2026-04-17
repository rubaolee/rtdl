# Goal 214: v0.4 Application Examples And SQL Comparisons

## Goal

Turn the nearest-neighbor `v0.4` line into a small application-facing package:

- write several app-style RTDL examples using `fixed_radius_neighbors` and
  `knn_rows`
- write docs that explain them to users
- write PostgreSQL/PostGIS scripts that implement the same application logic
- run a bounded Linux performance pass and summarize the good and bad aspects

## Scope

This goal is bounded to three small deterministic applications:

- service coverage gaps
- event hotspot screening
- facility k-nearest assignment

## Acceptance

- three application examples exist under `examples/`
- each application has a documented use case and a linked SQL comparison script
- the public docs surface these applications clearly
- local tests cover the new application examples
- a bounded Linux performance report exists and honestly states good and bad
  aspects

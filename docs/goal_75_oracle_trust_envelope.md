# Goal 75: Oracle Trust Envelope

Date: 2026-04-04
Status: complete

## Goal

Establish a trust envelope for the internal RTDL oracles used for quick verification and demos:

- Python reference oracle: trusted on deterministic mini-level workloads
- native C oracle: trusted on deterministic small workloads

PostGIS is used as the external truth source for the geometry workloads that matter most to RTDL correctness:

- `lsi`
- `pip`
- overlay-seed semantics

## Acceptance

Goal 75 is accepted if:

- the Python reference oracle matches PostGIS on a comprehensive deterministic mini-case sweep
- the native C oracle matches PostGIS on a deterministic small-case sweep
- the package records the exact audited envelope and does not overclaim beyond it

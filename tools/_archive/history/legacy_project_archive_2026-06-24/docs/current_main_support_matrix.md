# RTDL Current Support Matrix

Status: suspended for V3 rebuild on 2026-06-20.

There is no current public support matrix while V3 is being rebuilt. The
previous matrix described old release assumptions and must not be used as a
current user promise.

## Current Rule

No backend, partner, feature, or benchmark row is public or release-authorized
until it passes the V3 rebuild gate, receives a row classification, and the
aggregate release gate is opened.

Allowed classifications:

- `m7-qualified-row-scoped`;
- `needs-repair`;
- `internal-only`;
- `removed`.

## Before This Matrix Returns

The rebuilt support matrix must show:

- exact programming surface;
- backend support level;
- partner support level, if any;
- correctness evidence;
- performance artifact path, if performance is discussed;
- known unsupported paths.

Current authority:

- [V3 Rebuild Control](rebuild/v3/README.md)
- [Current Claim Boundaries](learn/current_claim_boundaries.md)

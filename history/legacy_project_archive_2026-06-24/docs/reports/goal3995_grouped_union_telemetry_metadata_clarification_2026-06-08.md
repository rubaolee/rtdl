# Goal3995 Grouped-Union Telemetry Metadata Clarification

Date: 2026-06-08

## Verdict

`accept`

Goal3995 closes the non-blocking observation from the Goal3994 Claude review of the Goal3992 extended grouped-union telemetry path.

The runtime now distinguishes two facts in metadata:

- `grouped_union_telemetry_buffer_length`: the caller-provided telemetry buffer capacity.
- `grouped_union_telemetry_counter_count`: the number of native counters the selected ABI will populate.

This matters for intermediate buffer sizes. A 5-, 6-, or 7-counter buffer is accepted for compatibility, but still routes to the old 4-counter ABI, so only counters 0-3 are populated. An 8+ counter buffer selects the extended ABI and populates counters 0-7.

## Scope

- No native ABI change.
- No change to the old 4-counter telemetry symbols.
- No change to the extended telemetry symbol introduced in Goal3992.
- No performance claim, release claim, or app-specific native behavior claim.

## Boundary

This is a metadata-contract clarification only. It does not authorize public speedup wording, release readiness, true-zero-copy wording, partner-selection claims, or app-specific native-engine logic.

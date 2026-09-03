# Goal5839 discovery execution deviations

Machine authority: `DISCOVERY_EXECUTION_DEVIATIONS.json`

Status: `RECORDED_NONFATAL_EXECUTION_DEVIATIONS__NO_FIELD_CLASSIFICATION_OR_PAPER_CLAIM`

## What happened

The frozen discovery procedure said to inspect bibliography and canonical
paper/publisher evidence before the fixed GitHub and general-web searches. The
GitHub result collection instead ran first. The 29-work denominator and query
bytes remained frozen, and no candidate source or protocol property had been
inspected, but literal preregistered execution order was not followed. Every
Goal5839 closeout must report that fact.

The first DuckDuckGo HTML collection then emitted 26 terminal-failure progress
rows before an unhandled `http.client.RemoteDisconnected` terminated query 27.
The collector serialized only after all 29 rows, so it created no result file;
the detailed in-memory attempt ledger is unrecoverable. This aborted run is not
an empty result set and must never enter the census denominator as one.

One attempted relaunch omitted `PYTHONPATH=src:.` and failed during import
before issuing a network request. It consumed no frozen provider attempt.

## Narrow repair

Commit `9c32aa3387fdefbfea4d2b9b379eb1d90aa76faf` adds
`http.client.HTTPException` to the existing recorded transport-failure path.
It does not change the provider, endpoint, query, parser, result ordering,
HTTP-200 success definition, or three-attempt 0/5/30-second retry schedule. A
test requires `RemoteDisconnected` to traverse exactly those three attempts.

The repair permits one complete rerun of the unchanged query set. It does not
restore a claim of perfectly preregistered execution, and it does not authorize
a provider/query substitution, artifact eligibility, protocol classification,
field prevalence, a paper result, external review, or consensus.

# V4 Goal4693 Specialized Hit Callback Probe

Status: hit-program-shaped correctness probe only, not Tier-3 support and not release authorization

- status: `specialized_hit_callback_correctness_passed_not_support`
- expected output: `5.0`
- uses OptiX trace: `True`
- uses hit program: `True`
- uses SBT direct callable: `False`
- pipeline launch attempted: `True`
- pipeline launch succeeded: `True`
- callback output matches expected: `True`

## Boundary

This probe checks direct device-function callback composition inside an OptiX hit-program-shaped wrapper. It does not authorize arbitrary callbacks, overhead claims, app-level speed claims, or V4 release.

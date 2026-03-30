Gemini 3.1 review attempt status

Model:
- `gemini-3.1-pro-preview`

Outcome:
- review did not complete

Observed failure:
- server returned `429 RESOURCE_EXHAUSTED`
- detailed reason: `MODEL_CAPACITY_EXHAUSTED`

Interpretation:
- this was an availability/capacity failure, not a content or policy rejection
- no substantive Gemini 3.1 review report was produced in this attempt

Next action if Gemini 3.1 is required:
- retry later when model capacity is available

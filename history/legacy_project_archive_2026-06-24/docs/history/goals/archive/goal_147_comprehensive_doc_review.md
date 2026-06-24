# Goal 147: Comprehensive Doc Review

## Why

RTDL now has a larger live surface than the archived v0.1 trust anchor. The
docs need one explicit consistency pass that treats the language and feature
docs as a first-class product surface.

## Scope

- verify that every currently supported feature still has a canonical feature
  home directory under `docs/features/`
- verify that each feature home still has the expected usage sections:
  - purpose
  - docs
  - code
  - example
  - best practices
  - try
  - try not
  - limitations
- verify that high-level docs still route readers into the feature-home layer
- fix any doc drift caused by the newer Jaccard goals, especially Goal 146
- get both Claude and Gemini review on the final package

## Acceptance

- every supported feature has a feature-home directory and README
- every feature home contains the expected sections
- high-level docs remain consistent with the live feature surface
- Jaccard backend wording is honest and consistent after Goal 146
- Claude review saved
- Gemini review saved
- Codex consensus saved

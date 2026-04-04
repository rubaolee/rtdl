# Goal 82 Plan: OptiX Pre-Embree Audit

Date: 2026-04-04
Status: in progress

## Purpose

The project now has two stronger OptiX performance claims:

- Goal 80: repeated raw-input win on the selected top4 CDB surface
- Goal 81: repeated raw-input win on the accepted long exact-source surface

Before moving to Embree, this audit revalidates the OptiX slice so the project
does not carry forward an unverified performance story.

## Planned Checks

1. local focused static validation
2. local focused unit tests
3. Linux focused static validation on a clean clone at the published head
4. Linux focused unit tests on that clean clone
5. Linux prepared-execution rerun on the long exact-source county/zipcode case
6. Linux repeated raw-input rerun on the same long exact-source case
7. report consistency review
8. external AI review before publish

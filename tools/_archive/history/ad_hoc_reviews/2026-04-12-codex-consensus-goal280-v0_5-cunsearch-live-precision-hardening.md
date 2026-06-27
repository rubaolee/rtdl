# Codex Consensus: Goal 280

Date: 2026-04-12
Goal: 280
Status: pass

## Judgment

Goal 280 is closed.

## Basis

- the larger-radius real KITTI failure was traced to a concrete bridge defect:
  - the generated cuNSearch driver wrote distances with default stream precision
- the fix is narrow and correct:
  - `std::setprecision(17)` for double builds
  - `std::setprecision(9)` for float builds
- unit tests now cover the emitted precision settings
- the real Linux KITTI bounded comparison now passes at:
  - `radius = 1.0`
  - `radius = 2.0`
  - `radius = 5.0`

## Boundary

Goal 280 closes output-precision hardening for the current live bridge. It does not claim that all future external baseline mismatches will reduce to formatting issues.

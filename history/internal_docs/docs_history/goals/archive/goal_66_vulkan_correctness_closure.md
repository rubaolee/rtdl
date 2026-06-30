# Goal 66: Vulkan Correctness Closure on the Accepted Linux Surface

## Objective

Repair the Vulkan backend so that it matches the accepted native C oracle on the
same bounded Linux validation surface used in Goal 65, then rerun that entire
surface on `192.168.1.20`.

## Scope

- `County ⊲⊳ Zipcode` bounded ladder:
  - `1x4`
  - `1x5`
  - `1x6`
  - `1x8`
  - `1x10`
  - `1x12`
- `BlockGroup ⊲⊳ WaterBodies` bounded ladder:
  - `county2300_s04`
  - `county2300_s05`
- bounded `LKAU ⊲⊳ PKAU` `sunshine_tiny` `overlay-seed analogue`

## Required outcome

- Vulkan parity-clean against the native C oracle across the entire accepted
  Goal 65 bounded surface.
- Updated evidence from the Linux GPU host.
- Honest boundaries preserved around Vulkan capacity limits and larger-package
  non-closure.

## Constraints

- correctness is more important than preserving the previous Vulkan timing shape
- no false claim that Vulkan is fully mature beyond the validated bounded
  surface
- no publish before 2-AI consensus

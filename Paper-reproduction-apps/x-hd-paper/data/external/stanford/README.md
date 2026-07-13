# Stanford Graphics Same-Source Data

Goal5132 acquired public Stanford 3D Scanning Repository graphics meshes as the
first same-source candidate for X-HD Level B representative reproduction.

Acquired source archives:

| Dataset | URL | Bytes | SHA256 |
| --- | --- | ---: | --- |
| Dragon | `https://graphics.stanford.edu/pub/3Dscanrep/dragon/dragon_recon.tar.gz` | 11197764 | `74AC1D90989C9B1732EDEE82D57E9CE71452144CF4355F108D8C9C616D28D02F` |
| HappyBuddha | `https://graphics.stanford.edu/pub/3Dscanrep/happy/happy_recon.tar.gz` | 14456495 | `409CD294EFBFD8244E15A382B95A9423F153B7776E736C9B09F19EC9D3C10ED0` |
| AsianDragon | `https://graphics.stanford.edu/data/3Dscanrep/xyzrgb/xyzrgb_dragon.ply.gz` | 70527166 | `8AA449F1966CBB50E5896ECC32CF57AB5F0CDFD3C3E37D3E6F60B948997DA5C1` |
| ThaiStatuette | `https://graphics.stanford.edu/data/3Dscanrep/xyzrgb/xyzrgb_statuette.ply.gz` | 106051627 | `1D867B6540C02935CAA777BD6746429A62D4A5D23F11C9BFDFEBBAA90C05CA8B` |

Full-resolution extracted PLY files:

| Dataset | File | Vertices | Faces | Bytes | SHA256 |
| --- | --- | ---: | ---: | ---: | --- |
| Dragon | `dragon_recon/dragon_vrip.ply` | 437645 | 871414 | 33831477 | `FEA87FF48F2ABA22FB53E7B67C3FF3F7B8C2A3B3A0653AF62C48BBA67C6D5744` |
| HappyBuddha | `happy_recon/happy_vrip.ply` | 543652 | 1087716 | 42619420 | `2283371216D748A08376A3C88698E283CC8F18D10CED348D6D133051BCF217AB` |
| AsianDragon | `asian_dragon.ply` | 3609600 | 7219045 | 137162963 | `4A31C6B8951B0F9F4B351D183CB5D5D27E2D1A5916B27E6516ACFB9A91AD7F85` |
| ThaiStatuette | `thai_statuette.ply` | 4999996 | 10000000 | 190000131 | `01470DA9FC1241DCB4B075CC057FF6BF88D8DC721CE24B5847B9EFDFBB8C0345` |

Scaled app-owned candidates:

| Dataset | File | Scale | Vertices | Bytes | SHA256 |
| --- | --- | ---: | ---: | ---: | --- |
| AsianDragon | `asian_dragon_scaled_1e-3.ply` | 0.001 | 3609600 | 43315372 | `4F98D1F809CFB6DCB448E469FDD94A606DE17B45CCB160F5CD1A5423508F01FE` |
| ThaiStatuette | `thai_statuette_scaled_1e-3.ply` | 0.001 | 4999996 | 60000124 | `047024CF12FC541634D02612F0D72EA03EF9BABB8239F4CA6A1A6A9422DA272E` |

Claim boundary:

- This is Level B same-source source acquisition, not Level C exact paper input.
- The vertex counts match the paper Table 1 scale (`0.4M` / `0.5M`) but count
  matching is not sufficient for exact paper reproduction.
- The AsianDragon vertex count matches the author paper-branch
  `dragon.ply -> asian_dragon.ply` log count (`3,609,600`), but count matching
  is still not sufficient for exact paper reproduction.
- The ThaiStatuette vertex count matches the author paper-branch graphics logs
  (`4,999,996`), and the `1e-3` scaled coordinate extents match the log scale,
  but this remains Level B same-source evidence unless exact author input bytes
  or deterministic conversion provenance are found.
- The current X-HD paper app gates consume WKT fixtures; PLY route support is a
  next app-owned input bridge task.
- The current RTDL exact route materializes pairwise candidate rows and is not
  suitable for full-resolution Dragon x HappyBuddha scale.

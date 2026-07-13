from __future__ import annotations

from pathlib import Path


author = Path("/workspace/goal4875_section57_au_representative/author_patch_au_overlay.txt")
rtdl = Path("/workspace/goal4875_section57_au_representative/public_route/rtdl_public_overlay.txt")

with author.open("r", encoding="utf-8") as fa, rtdl.open("r", encoding="utf-8") as fb:
    for line_no, (a, b) in enumerate(zip(fa, fb), 1):
        if a != b:
            print("first_diff_line", line_no)
            print("author", a.rstrip("\n"))
            print("rtdl", b.rstrip("\n"))
            break
    else:
        print("no_diff_in_common_prefix")

print("author_lines", sum(1 for _ in author.open("r", encoding="utf-8")))
print("rtdl_lines", sum(1 for _ in rtdl.open("r", encoding="utf-8")))

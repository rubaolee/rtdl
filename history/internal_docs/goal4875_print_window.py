from pathlib import Path

paths = {
    "author": Path("/workspace/goal4875_section57_au_representative/author_patch_au_overlay.txt"),
    "rtdl": Path("/workspace/goal4875_section57_au_representative/public_route/rtdl_public_overlay.txt"),
}

for name, path in paths.items():
    print("---", name)
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if 230 <= line_no <= 285:
                print(line_no, line.rstrip("\n"))

from pathlib import Path


path = Path("src/run_query.cu")
lines = path.read_text().splitlines(True)

if not any("#include <cstdlib>" in line for line in lines):
    lines.insert(1, "#include <cstdlib>\n")
if not any("#include <fstream>" in line for line in lines):
    lines.insert(2, "#include <fstream>\n")

if not any("RAYJOIN_LSI_DUMP_PAIRS" in line for line in lines):
    anchor = None
    for index, line in enumerate(lines):
        if 'timer_next("Cleanup")' in line and index > 250:
            anchor = index
            break
    if anchor is None:
        raise SystemExit("cleanup anchor not found")
    block = [
        "\n",
        '  if (const char* dump_path = std::getenv("RAYJOIN_LSI_DUMP_PAIRS")) {\n',
        "    thrust::host_vector<typename LSI<context_t>::xsect_t> xsects_host;\n",
        "    lsi->CopyTo(xsects_host);\n",
        "    std::ofstream ofs(dump_path);\n",
        "    for (const auto& xsect : xsects_host) {\n",
        '      ofs << xsect.eid[0] << " " << xsect.eid[1] << "\\n";\n',
        "    }\n",
        '    LOG(INFO) << "Dumped LSI pairs: " << xsects_host.size() << " to " << dump_path;\n',
        "  }\n",
        "\n",
    ]
    lines[anchor:anchor] = block

path.write_text("".join(lines))

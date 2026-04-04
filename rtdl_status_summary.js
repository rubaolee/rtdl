const pptxgen = require("./deck_status/node_modules/pptxgenjs");
const {
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require("./deck_status/pptxgenjs_helpers/layout");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "OpenAI Codex";
pptx.company = "OpenAI";
pptx.subject = "RTDL project status summary";
pptx.title = "RTDL Project Status Summary";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US",
};

const COLORS = {
  ink: "102032",
  blue: "1E5A7A",
  teal: "1E7D77",
  green: "4B8B3B",
  gold: "C4892D",
  rust: "B85C38",
  plum: "5B4E91",
  pale: "F7F4EE",
  white: "FFFFFF",
  mist: "E9F1F4",
  mint: "E6F2EC",
  sand: "F5EAD7",
  rose: "F7E6DF",
  gray: "5C6B77",
  lightGray: "D8E0E5",
  dark: "0D1720",
};

const SLIDE_COUNT = 15;

function addBackground(slide, accent = COLORS.blue) {
  slide.background = { color: COLORS.pale };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 0.34,
    line: { color: accent, transparency: 100 },
    fill: { color: accent },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 7.14,
    w: 13.333,
    h: 0.36,
    line: { color: COLORS.dark, transparency: 100 },
    fill: { color: COLORS.dark },
  });
}

function addTitle(slide, title, subtitle) {
  slide.addText(title, {
    x: 0.7,
    y: 0.5,
    w: 9.4,
    h: 0.46,
    fontFace: "Aptos Display",
    fontSize: 24,
    bold: true,
    color: COLORS.ink,
    margin: 0,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.72,
      y: 1.02,
      w: 10.8,
      h: 0.3,
      fontFace: "Aptos",
      fontSize: 10.5,
      color: COLORS.gray,
      margin: 0,
    });
  }
}

function addPanel(slide, x, y, w, h, title, body, fill = COLORS.white, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.05,
    line: { color: opts.lineColor ?? fill, pt: opts.linePt ?? 0.8, transparency: 100 },
    fill: { color: fill },
  });
  slide.addText(title, {
    x: x + 0.16,
    y: y + 0.12,
    w: w - 0.32,
    h: 0.24,
    fontFace: "Aptos Display",
    fontSize: opts.titleSize ?? 14,
    bold: true,
    color: opts.titleColor ?? COLORS.ink,
    margin: 0,
  });
  slide.addText(body, {
    x: x + 0.16,
    y: y + 0.42,
    w: w - 0.32,
    h: h - 0.54,
    fontFace: "Aptos",
    fontSize: opts.bodySize ?? 10.8,
    color: opts.bodyColor ?? COLORS.ink,
    margin: 0,
    valign: "top",
    breakLine: false,
  });
}

function addBullets(slide, items, opts = {}) {
  const runs = [];
  items.forEach((text, idx) => {
    runs.push({ text, options: { bullet: { indent: 14 } } });
    if (idx !== items.length - 1) {
      runs.push({ text: "", options: { breakLine: true } });
    }
  });
  slide.addText(runs, {
    x: opts.x ?? 0.9,
    y: opts.y ?? 1.6,
    w: opts.w ?? 5.8,
    h: opts.h ?? 4.5,
    fontFace: "Aptos",
    fontSize: opts.fontSize ?? 14,
    color: opts.color ?? COLORS.ink,
    margin: 0.04,
    valign: "top",
    paraSpaceAfterPt: opts.spaceAfter ?? 9,
  });
}

function addCodeBox(slide, x, y, w, h, text, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.04,
    line: { color: opts.lineColor ?? COLORS.lightGray, pt: 1 },
    fill: { color: opts.fill ?? "F4F7FA" },
  });
  slide.addText(text, {
    x: x + 0.15,
    y: y + 0.12,
    w: w - 0.3,
    h: h - 0.24,
    fontFace: "Courier New",
    fontSize: opts.fontSize ?? 9.8,
    color: opts.color ?? COLORS.ink,
    margin: 0,
    breakLine: false,
    valign: "top",
  });
}

function addMetric(slide, x, y, w, title, value, fill) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h: 0.95,
    rectRadius: 0.04,
    line: { color: fill, transparency: 100 },
    fill: { color: fill },
  });
  slide.addText(title, {
    x: x + 0.12,
    y: y + 0.12,
    w: w - 0.24,
    h: 0.18,
    fontFace: "Aptos",
    fontSize: 9,
    color: COLORS.gray,
    bold: true,
    margin: 0,
  });
  slide.addText(value, {
    x: x + 0.12,
    y: y + 0.35,
    w: w - 0.24,
    h: 0.34,
    fontFace: "Aptos Display",
    fontSize: 18,
    bold: true,
    color: COLORS.ink,
    margin: 0,
  });
}

function addFooter(slide, page) {
  slide.addText(`RTDL summary · ${page}/${SLIDE_COUNT}`, {
    x: 11,
    y: 7.18,
    w: 1.8,
    h: 0.14,
    align: "right",
    fontFace: "Aptos",
    fontSize: 8.5,
    color: "D7E0E6",
    margin: 0,
  });
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

// 1. Title and snapshot
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.teal);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.72,
    y: 1.02,
    w: 3.25,
    h: 0.4,
    rectRadius: 0.04,
    line: { color: COLORS.mist, transparency: 100 },
    fill: { color: COLORS.mist },
  });
  slide.addText("PROJECT STATUS DECK", {
    x: 0.9,
    y: 1.11,
    w: 2.5,
    h: 0.14,
    fontFace: "Aptos",
    fontSize: 10.5,
    bold: true,
    color: COLORS.teal,
    margin: 0,
  });
  slide.addText("RTDL: A Python-Hosted Ray Tracing DSL", {
    x: 0.72,
    y: 1.58,
    w: 6.7,
    h: 0.8,
    fontFace: "Aptos Display",
    fontSize: 27,
    bold: true,
    color: COLORS.ink,
    margin: 0,
  });
  slide.addText("Research status as of April 3, 2026", {
    x: 0.75,
    y: 2.42,
    w: 4.5,
    h: 0.28,
    fontFace: "Aptos",
    fontSize: 14,
    color: COLORS.gray,
    margin: 0,
  });
  addPanel(
    slide,
    7.8,
    1.08,
    4.7,
    2.55,
    "Project Thesis",
    "Whole-project goal: a DSL for non-graphical, re-purposed RT-based applications across multiple backends and ecosystems.\n\nCurrent v0.1 slice: RayJoin-style workloads validated through a native oracle plus Embree and OptiX, with bounded PostGIS-backed ground truth and a first bounded overlay-seed closure.",
    COLORS.sand
  );
  addMetric(slide, 0.8, 4.0, 1.7, "Workloads", "6", COLORS.white);
  addMetric(slide, 2.7, 4.0, 1.9, "Tests", "273", COLORS.white);
  addMetric(slide, 4.8, 4.0, 2.1, "Review", "57+", COLORS.white);
  addMetric(slide, 7.1, 4.0, 2.1, "Validated RT", "CPU + GPU", COLORS.white);
  addMetric(slide, 9.45, 4.0, 2.8, "Backends", "3 core", COLORS.white);
  addFooter(slide, 1);
}

// 2. Vision and problem
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.gold);
  addTitle(slide, "Vision and Problem", "Broad multi-backend project vision, with RayJoin as the current v0.1 vertical slice.");
  addPanel(slide, 0.75, 1.55, 4.0, 4.95, "Why Ray Tracing Is Hard Today",
    "Application developers must understand GPU launch structure, acceleration structures, payload packing, intersection programs, and numerical behavior at the same time.\n\nFor non-graphics workloads, the programming tax is usually far higher than the conceptual query itself.",
    COLORS.white);
  addPanel(slide, 4.95, 1.55, 4.0, 4.95, "Why RayJoin First",
    "RayJoin proves RT cores can accelerate spatial joins, but its programming model still leaks OptiX and CUDA details. That makes it a strong first target for a DSL: the performance idea is good, but the interface is too costly.",
    COLORS.white);
  addPanel(slide, 9.15, 1.55, 3.45, 4.95, "RTDL Thesis",
    "Expose geometry, traversal intent, predicates, and outputs in a language users can author directly.\n\nKeep the real compiler boundary in an IR so the same program can target reference execution, native local backends, and future GPU backends.",
    COLORS.white);
  addFooter(slide, 2);
}

// 3. Current scope
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.blue);
  addTitle(slide, "Current Scope", "What RTDL can express and run today.");
  addPanel(slide, 0.8, 1.55, 3.0, 2.2, "Language Surface",
    "Python-hosted DSL with @rt.kernel, rt.input, rt.traverse, rt.refine, and rt.emit.\n\nDocumented for human and LLM authoring.", COLORS.white);
  addPanel(slide, 4.05, 1.55, 3.0, 2.2, "Workloads",
    "lsi\npip\noverlay\nray_tri_hitcount\nsegment_polygon_hitcount\npoint_nearest_segment", COLORS.white);
  addPanel(slide, 7.3, 1.55, 2.55, 2.2, "Execution",
    "Native C++ oracle\nEmbree runtime\nOptiX runtime\nVulkan (provisional)", COLORS.white);
  addPanel(slide, 10.1, 1.55, 2.4, 2.2, "Codegen",
    "RayJoin lowering\nplan.json schema\nPostGIS comparison\nGPU backend plumbing", COLORS.white);
  addBullets(slide, [
    "Implemented precision mode is float_approx. Exact or robust geometry remains future work.",
    "The Mac backend is real: current RTDL programs can return results through Embree.",
    "The OptiX path is a real controlled runtime on 192.168.1.20, with bounded accepted real-data validation.",
    "PostGIS is now a closed external checker on accepted bounded packages.",
    "The Vulkan path is present in-repo but still provisional.",
    "Language docs, cookbook, and authored examples are in the repo and validated by tests.",
  ], { x: 0.95, y: 4.2, w: 11.7, h: 2.0, fontSize: 13.5, spaceAfter: 8 });
  addFooter(slide, 3);
}

// 4. Language example
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.plum);
  addTitle(slide, "Language Example", "A finite 2D ray-vs-triangle hit-count workload in RTDL.");
  addCodeBox(slide, 0.78, 1.55, 6.1, 4.9,
`import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def ray_triangle_hits():
    rays = rt.input("rays", rt.Rays, role="probe")
    triangles = rt.input("triangles", rt.Triangles, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.ray_triangle_hit_count(exact=False),
    )
    return rt.emit(hits, fields=["ray_id", "hit_count"])`);
  addPanel(slide, 7.15, 1.55, 5.35, 2.2, "Language Intent",
    "The kernel describes query semantics, not backend programs. It says what the workload is: rays probe triangles, the predicate is hit counting, and the output is one record per ray.", COLORS.mist);
  addPanel(slide, 7.15, 4.0, 5.35, 2.45, "Authoring Sources",
    "Repo docs:\n- docs/rtdl/dsl_reference.md\n- docs/rtdl/programming_guide.md\n- docs/rtdl/workload_cookbook.md\n- docs/rtdl/llm_authoring_guide.md\n\nExamples:\n- language_reference.py\n- codex_authored.py\n- gemini_authored.py", COLORS.white);
  addFooter(slide, 4);
}

// 5. Architecture
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.teal);
  addTitle(slide, "Current Architecture", "One language surface, multiple execution and backend-planning paths.");
  addPanel(slide, 0.7, 2.1, 2.1, 1.2, "Python DSL", "@rt.kernel\nrt.input\nrt.traverse\nrt.refine\nrt.emit", COLORS.white);
  slide.addShape(pptx.ShapeType.chevron, {
    x: 2.95, y: 2.45, w: 0.6, h: 0.55, line: { color: COLORS.teal, transparency: 100 }, fill: { color: COLORS.teal }
  });
  addPanel(slide, 3.65, 2.1, 2.1, 1.2, "CompiledKernel IR", "backend-independent workload meaning", COLORS.white);
  slide.addShape(pptx.ShapeType.chevron, {
    x: 5.9, y: 2.45, w: 0.6, h: 0.55, line: { color: COLORS.teal, transparency: 100 }, fill: { color: COLORS.teal }
  });
  addPanel(slide, 6.6, 2.1, 2.2, 1.2, "Lowering", "RayJoin backend plan\npayloads\nlaunch params", COLORS.white);
  slide.addShape(pptx.ShapeType.chevron, {
    x: 8.95, y: 2.45, w: 0.6, h: 0.55, line: { color: COLORS.teal, transparency: 100 }, fill: { color: COLORS.teal }
  });
  addPanel(slide, 9.65, 2.1, 2.95, 1.2, "Outputs", "Oracle runtime\nEmbree runtime\nOptiX runtime\nVulkan runtime (provisional)", COLORS.white);
  addPanel(slide, 0.8, 4.1, 3.8, 1.75, "Key modules",
    "api.py\nir.py\ntypes.py\nlowering.py\ncodegen.py\nruntime.py\nembree_runtime.py\nreference.py\ndatasets.py", COLORS.mint);
  addPanel(slide, 4.85, 4.1, 3.8, 1.75, "Execution contract",
    "The same kernel can be compiled, lowered, and then either executed locally or used to generate backend artifacts. That keeps language semantics and backend strategy separate.", COLORS.white);
  addPanel(slide, 8.9, 4.1, 3.6, 1.75, "Validated runtime surface",
    "Embree-backed local validation on this Mac, plus larger Linux validation and OptiX execution on 192.168.1.20.\n\nPublic APIs: rt.run_embree(...), rt.run_optix(...)", COLORS.sand);
  addFooter(slide, 5);
}

// 6. Workloads and data
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.green);
  addTitle(slide, "Workloads and Data Pipeline", "RTDL now covers six workload families and includes RayJoin-aligned fixture support.");
  addPanel(slide, 0.8, 1.55, 2.85, 3.15, "lsi",
    "Segment vs segment intersection.\n\nEmit:\nleft_id\nright_id\nintersection_point_x\nintersection_point_y", COLORS.white);
  addPanel(slide, 3.95, 1.55, 2.85, 3.15, "pip",
    "Point in polygon.\n\nEmit:\npoint_id\npolygon_id\ncontains", COLORS.white);
  addPanel(slide, 7.1, 1.55, 2.85, 3.15, "overlay",
    "Polygon overlay preparation / seed generation.\n\nEmit:\nleft_polygon_id\nright_polygon_id\nrequires_lsi\nrequires_pip", COLORS.white);
  addPanel(slide, 10.25, 1.55, 2.3, 3.15, "ray_tri_hitcount",
    "Finite 2D rays against triangles.\n\nEmit:\nray_id\nhit_count", COLORS.white);
  addPanel(slide, 0.8, 4.95, 3.8, 1.3, "Goal 10 extensions",
    "segment_polygon_hitcount\npoint_nearest_segment\n\nThese execute through audited native_loop local cases.", COLORS.mint);
  addPanel(slide, 4.85, 4.95, 3.7, 1.3, "Dataset support",
    "datasets.py parses RayJoin-style CDB chains and derives segment, polygon, and point-probe views for oracle, Embree, OptiX, and PostGIS comparison.", COLORS.white);
  addPanel(slide, 8.8, 4.95, 3.7, 1.3, "Example data sources",
    "tests/fixtures/rayjoin/, exact-source public datasets, bounded Linux validation slices, and synthetic generators.", COLORS.mist);
  addFooter(slide, 6);
}

// 7. Run paths and output
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.rust);
  addTitle(slide, "How You Can Run It Today", "Three useful ways to work with the current RTDL repository.");
  addPanel(slide, 0.82, 1.55, 3.8, 1.5, "1. Compiler / codegen demo",
    "make run-rtdsl-py\n\nCompiles kernels, prints lowering plans, and emits generated backend files under generated/.", COLORS.white);
  addPanel(slide, 4.77, 1.55, 3.8, 1.5, "2. Native oracle",
    "Use rt.run_cpu(...)\n\nRuns the current workload surface through the native C/C++ ground-truth path.", COLORS.white);
  addPanel(slide, 8.72, 1.55, 3.8, 1.5, "3. Native Embree runtime",
    "Use rt.run_embree(...)\n\nRuns the same workloads through the controlled Embree backend; OptiX runs on the Linux GPU host.", COLORS.white);
  addCodeBox(slide, 0.84, 3.35, 5.95, 2.65,
`Embree Version: (4, 4, 0)
LSI: ({'left_id': 1, 'right_id': 10, ...})
PIP: ({'point_id': 100, 'polygon_id': 200, 'contains': 1}, ...)
OVERLAY: ({'left_polygon_id': 300, ...})
RAY HITCOUNT: ({'ray_id': 0, 'hit_count': 0}, ...)`);
  addCodeBox(slide, 7.08, 3.35, 5.45, 2.65,
`Gemini-authored Embree example:

PYTHONPATH=src:. python3 examples/rtdl_gemini_embree_program.py

({'point_id': 0, 'polygon_id': 10, 'contains': 1},
 {'point_id': 1, 'polygon_id': 10, 'contains': 0})`);
  addFooter(slide, 7);
}

// 8. Review history
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.gold);
  addTitle(slide, "Review and Revision History", "The project has been advanced through explicit multi-round Codex, Gemini, and Claude review loops.");
  addPanel(slide, 0.8, 1.55, 12.0, 0.75, "History system",
    "history/history.db stores structured metadata. revision_dashboard.html is the manager-facing view. revision_dashboard.md is the GitHub-readable companion.", COLORS.white);
  addPanel(slide, 0.8, 2.55, 2.0, 3.55, "Round 1",
    "Baseline verification and correction.\n\nOutcome: precision claims corrected from exact to float_approx.", COLORS.mist);
  addPanel(slide, 3.0, 2.55, 2.0, 3.55, "Goal 1",
    "Deterministic codegen and validation.\n\nOutcome: stable plan schema, goldens, stronger negative tests.", COLORS.white);
  addPanel(slide, 5.2, 2.55, 2.0, 3.55, "Goal 2",
    "Multi-workload coverage and dataset pipeline.\n\nOutcome: lsi, pip, overlay, RayJoin-style fixtures.", COLORS.mist);
  addPanel(slide, 7.4, 2.55, 2.0, 3.55, "Goals 3-5",
    "Gemini re-review gate, formal language docs, and ray-triangle hit counts.", COLORS.white);
  addPanel(slide, 9.6, 2.55, 2.0, 3.55, "Goals 6-57",
    "Native oracle, Embree maturity, OptiX bring-up, three-backend checks, docs rewrite, full audit, PostGIS closure, first bounded overlay-seed four-system result, and the status/test refresh package.", COLORS.mist);
  addPanel(slide, 11.8, 2.55, 1.0, 3.55, "Stats",
    "57+ goals\n2-3 AI review\nclean audited repo", COLORS.white, { bodySize: 10.2 });
  addFooter(slide, 8);
}

// 9. Backend choices
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.blue);
  addTitle(slide, "Backend Choices", "Current and planned execution targets for the same RTDL language.");
  addPanel(slide, 0.8, 1.55, 3.0, 2.15, "Reference CPU",
    "Purpose: semantic oracle and portable execution.\n\nStatus: implemented as rt.run_cpu(...).", COLORS.white);
  addPanel(slide, 4.05, 1.55, 3.0, 2.15, "Embree",
    "Purpose: controlled CPU backend for validated real-data work.\n\nStatus: implemented as rt.run_embree(...).", COLORS.white);
  addPanel(slide, 7.3, 1.55, 2.75, 2.15, "OptiX / RayJoin",
    "Purpose: NVIDIA GPU backend for the RayJoin-style target slice.\n\nStatus: implemented and validated on bounded accepted workloads.", COLORS.white);
  addPanel(slide, 10.3, 1.55, 2.2, 2.15, "Future Mac GPU",
    "Vulkan KHR path is in-repo but provisional.\n\nApple/Metal work is still future.", COLORS.white);
  addBullets(slide, [
    "RTDL is designed so backend specifics live under the IR and lowering boundary, not in user kernels.",
    "Embree is the strongest validated backend today.",
    "OptiX is real and correctness-checked on bounded real-data workloads.",
    "Vulkan is retained as provisional backend code, not as an equally accepted backend.",
    "A broader future architecture can still support CPU, NVIDIA, Vulkan-class, and future Apple/mobile RT targets.",
  ], { x: 0.95, y: 4.2, w: 11.6, h: 2.0, fontSize: 13.4 });
  addFooter(slide, 9);
}

// 10. Proven and not yet done
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.rust);
  addTitle(slide, "What Is Proven vs. What Is Not", "Keep the current system’s claims honest.");
  addPanel(slide, 0.8, 1.55, 5.75, 4.9, "Proven now",
    "RTDL is a real language surface for six workloads.\n\nThe same kernels can compile to IR and execute through the native oracle, Embree, and accepted bounded OptiX paths.\n\nBounded four-system checks now exist across PostGIS, the oracle, Embree, and OptiX on accepted real-data packages.\n\nThe review history is reproducible and archived.", COLORS.mint);
  addPanel(slide, 6.8, 1.55, 5.75, 4.9, "Not done yet",
    "No exact / robust geometry implementation.\n\nNo final bounded full RayJoin-style reproduction package across all current targets yet.\n\nOverlay remains a seed analogue, not full polygon materialization.\n\nVulkan is not yet validated to the same level as Embree or OptiX.", COLORS.rose);
  addFooter(slide, 10);
}

// 11. Roadmap
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.green);
  addTitle(slide, "Roadmap to a Fully Functional DSL", "The next steps after the current multi-backend bring-up milestone.");
  addPanel(slide, 0.8, 1.55, 2.85, 3.95, "Step 1\nStabilize current surface",
    "Keep improving docs, examples, negative validation, and authored-program testing.", COLORS.white);
  addPanel(slide, 3.95, 1.55, 2.85, 3.95, "Step 2\nWiden workload support",
    "Add more geometry/query forms beyond the current RayJoin-aligned six-workload surface.", COLORS.white);
  addPanel(slide, 7.1, 1.55, 2.85, 3.95, "Step 3\nClose external truth and matrix",
    "Extend the PostGIS-backed bounded matrix and close more RayJoin-style families across the current accepted backends.", COLORS.white);
  addPanel(slide, 10.25, 1.55, 2.3, 3.95, "Step 4\nPrecision and performance",
    "Add robust arithmetic strategy, continue apples-to-apples backend comparisons, and refine backend specialization.", COLORS.white);
  addPanel(slide, 0.8, 5.8, 11.75, 0.62, "Key research transition",
    "The project has moved from a language sketch to an executable system. The next phase is backend maturity, not basic feasibility.", COLORS.mint);
  addFooter(slide, 11);
}

// 12. Current status and next action
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.plum);
  addTitle(slide, "Current Status", "RTDL is ready for the next development phase.");
  addPanel(slide, 0.8, 1.6, 4.0, 2.15, "Repository status",
    "GitHub and local repo are in sync through the current audited multi-backend state.\n\nEmbree and OptiX are real; Vulkan is provisional; bounded PostGIS closure is established on accepted packages.\n\nPrimary workspace: /Users/rl2025/rtdl_python_only", COLORS.white);
  addPanel(slide, 5.05, 1.6, 3.6, 2.15, "What a new contributor can do",
    "Read docs/rtdl/*, run make test, validate kernels against the oracle, and compare them against Embree and OptiX on accepted targets.", COLORS.white);
  addPanel(slide, 8.9, 1.6, 3.6, 2.15, "What the GPU machine unlocks",
    "Bounded real-data GPU validation, apples-to-apples backend comparison, and progress toward a bounded RayJoin-style reproduction package.", COLORS.white);
  addCodeBox(slide, 0.82, 4.15, 11.7, 1.75,
`Current repo snapshot:
- Six supported workloads
- Native oracle + Embree + OptiX
- Bounded PostGIS ground-truth closure on accepted packages
- First bounded overlay-seed four-system closure
- Vulkan retained as provisional backend code
- 273 full-matrix tests
- 57+ reviewed goal rounds
- First-class raw + prepared raw runtime modes
- Language docs for human + LLM authoring`);
  addFooter(slide, 12);
}

// 13. AI collaboration loop
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.teal);
  addTitle(slide, "How the AIs Work Together", "RTDL uses a staged multi-agent loop instead of a one-pass coding workflow.");
  addPanel(slide, 0.8, 1.55, 2.3, 4.65, "1. Goal setup",
    "Codex writes the goal, scope, deliverables, and acceptance bar before code changes are treated as valid progress.", COLORS.white);
  addPanel(slide, 3.35, 1.55, 2.3, 4.65, "2. Pre-review",
    "Gemini or Claude reviews the goal first, checks whether the scope is sound, and states how completion should be verified.", COLORS.mist);
  addPanel(slide, 5.9, 1.55, 2.3, 4.65, "3. Implement + validate",
    "Codex updates code, tests, docs, reports, and examples, then runs the actual evidence path.", COLORS.white);
  addPanel(slide, 8.45, 1.55, 2.3, 4.65, "4. Review + revise",
    "Another agent reviews the implemented state. Findings trigger a direct response and another revision pass if needed.", COLORS.mist);
  addPanel(slide, 11.0, 1.55, 1.55, 4.65, "5. Close + archive",
    "Only after consensus does the round move into history, dashboards, and main.", COLORS.white, { bodySize: 10.2 });
  addPanel(slide, 0.85, 6.45, 11.7, 0.58, "Why this matters",
    "This process turns each accepted goal into an auditable repo state instead of a one-model opinion.", COLORS.mint);
  addFooter(slide, 13);
}

// 14. Agent roles and closure rules
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.blue);
  addTitle(slide, "Agent Roles and Closure Rules", "Different models play different roles so the project gets structured disagreement before publication.");
  addPanel(slide, 0.8, 1.55, 3.75, 2.8, "Codex",
    "Primary implementation driver.\n\nOwns code changes, validation runs, doc updates, rebuttals, and final repo coherence.", COLORS.white);
  addPanel(slide, 4.8, 1.55, 3.75, 2.8, "Gemini",
    "Fast secondary reviewer.\n\nUsually checks scope, evidence, semantic honesty, and whether a round is really ready to close.", COLORS.mist);
  addPanel(slide, 8.8, 1.55, 3.75, 2.8, "Claude",
    "Audit and critique pressure.\n\nOften used for deeper plan criticism, trust audits, and narrower comparison goals.", COLORS.white);
  addBullets(slide, [
    "Consensus means the agents agree on the final goal state, not that they produce identical reports.",
    "A goal can close as complete, complete-for-slice, canceled-superseded, or blocked, as long as the wording matches the evidence.",
    "The archive keeps prompts, reviews, responses, and final closure notes so future contributors can inspect why a decision was made.",
    "This is now a core part of RTDL’s engineering method, not an ad hoc side process.",
  ], { x: 0.95, y: 4.55, w: 11.5, h: 2.0, fontSize: 13.1 });
  addFooter(slide, 14);
}

// 15. Runtime overhead architecture
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.rust);
  addTitle(slide, "RTDL vs Native Runtime Path", "Goal 19 sharpened the conclusion: the DSL is viable, but only the low-overhead runtime modes are close to native.");
  addPanel(slide, 0.8, 1.55, 5.75, 4.35, "Current RTDL + Embree path",
    "1. Python DSL kernel\n2. compile / validate / lower\n3. Python input normalization\n4. ctypes marshaling\n5. native Embree backend\n6. native rows\n7. Python dict rows\n\nGoal 19 larger-profile gap:\n- lsi dict path: about 101.6x slower than native\n- pip dict path: about 225.3x slower than native", COLORS.white);
  addPanel(slide, 6.8, 1.55, 5.75, 4.35, "Pure C++ + Embree path",
    "1. native input arrays\n2. direct native call\n3. native rows\n4. output serialization\n\nGoal 19 larger-profile result:\n- lsi raw/prepared-raw: about 0.98x / 0.89x of native\n- pip raw/prepared-raw: about 0.87x / 0.83x of native", COLORS.mist);
  addPanel(slide, 0.85, 6.1, 11.7, 0.68, "Design implication",
    "Keep the Python-like DSL. Treat dict-return execution as a convenience mode, and treat raw / prepared-raw execution as the serious performance path. Python should remain the control plane, not the main data plane.", COLORS.sand);
  addFooter(slide, 15);
}

pptx.writeFile({ fileName: "/Users/rl2025/rtdl_python_only/rtdl_status_summary.pptx" });

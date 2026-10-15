# Hitbox 🎯

> Zero-selector visual localization and canvas QA engine for Playwright and Selenium, powered by **TypeSafe Jev**.

[![Powered by TypeSafe Jev](https://img.shields.io/badge/Powered%20by-TypeSafe%20Jev-6366f1.svg)](https://typesafe.ai)
[![Status: Building](https://img.shields.io/badge/Status-Building%20%F0%9F%8F%97%EF%B8%8F-amber.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Status:** 🏗️ Actively Building (Core Engine & Driver Adapters in Progress)

---

## Overview

Traditional end-to-end testing relies on brittle CSS selectors and XPath queries that break whenever component classes or markup change. Worse, applications built on **HTML5 `<canvas>`, WebGL (Three.js), Flutter Web, and interactive maps** render zero DOM nodes—leaving standard Playwright and Selenium locators completely blind.

**Hitbox** brings vision-driven interaction to modern test runners by utilizing **TypeSafe Jev** as its core decision engine. Instead of slow, generative vision models that hallucinate coordinates, Hitbox leverages Jev's **System One visual primitives** (`bbox`, `noul`, `score`) to evaluate raw viewports in ~150–200 ms with calibrated certainty.

Built on a **driver-agnostic adapter architecture**, Hitbox resolves clickable target regions from visual reference crops or semantic descriptions and executes sub-pixel clicks directly on raw canvas surfaces across Playwright and Selenium.

---

## Why TypeSafe Jev Powers Hitbox

| Feature | Standard Locators | Generative VLMs (GPT / Claude) | **Hitbox (TypeSafe Jev)** |
| :--- | :--- | :--- | :--- |
| **Canvas & WebGL Targeting** | ❌ Blind (No DOM elements) | ⚠️ Slow (~3–6s latency) | **✅ Fast (~150–200 ms single pass)** |
| **Execution Surface** | Brittle CSS/XPath selectors | Markdown coordinate guesses | **Sub-pixel normalized `bbox` primitives** |
| **Actionability Verification** | DOM-level only (`isVisible`) | Text explanation of visibility | **Parallel `noul` checks (`is_unobstructed`)** |
| **Output Guarantees** | Native boolean assertions | Unstructured JSON strings | **Zero type errors + calibrated probabilities** |

---

## Core Capabilities We Are Building

- **Zero-DOM Canvas & WebGL Testing:** Target, click, and drag canvas-rendered buttons, data points, map pins, and 3D gizmos without requiring underlying DOM elements.
- **Single-Pass Actionability Fan-Out:** Evaluates target bounding box localization (`bbox`), modal/toast occlusion (`is_unobstructed: noul`), clickable state (`is_visually_enabled: noul`), and visual rendering health (`score`) in a single parallel Jev forward pass.
- **2x Micro-Zoom Sub-Pixel Refinement:** Automatically crops a padded high-resolution window around ambiguous candidate boxes (`0.70 <= confidence < gate`) and reprojects refined coordinates back to the global viewport.
- **Perceptual L1 Caching (`dHash`):** Uses 64-bit difference hashing with Hamming distance tolerance to skip redundant full-frame API calls on static layouts.
- **Annotated Visual Receipts:** Automatically renders bounding boxes, center crosshairs, and Jev probability badges (`conf`, `unobstructed`, `enabled`, `[2x-ZOOM]`) onto PNG trace receipts for instant failure debugging.
- **Multi-Driver Adapter Core:** A unified vision engine that plugs into Playwright (`page`) and Selenium (`driver`) out of the box via a single auto-detecting `pytest` fixture.
- **Upcoming Potential Extensions:**
  - **Scoped Region Auditing (`audit_region`):** Run multi-rubric visual regression and semantic layout assertions inside a localized bounding box without brittle pixel-diffing.
  - **Figma-to-Hitbox Reference Sync:** Pull golden component crops directly from Figma node IDs to serve as live visual instruction references in CI.
  - **Runtime Agent Click Firewall:** Intercept and validate autonomous browser-agent clicks against visual prompt injection and dark-pattern UI overlays before pointer execution.

---

## Target Usage Preview

```python
def test_cad_canvas_export(page, hitbox):
    page.goto("https://app.example.com/cad")

    # 1. Image-as-Instruction: Locate via golden reference crop + verify unobstructed state via Jev
    hitbox.locate_by_image(
        "fixtures/export_button.png",
        context={"active_view": "perspective", "selection_count": 1},
        confidence_gate=0.88,
    ).click()

    # 2. Semantic BBox: Locate and drag directly on a raw WebGL canvas
    hitbox.locate_by_description("Active mesh Z-axis rotation gizmo").drag_to_offset(dx=40, dy=0)
```

Using Selenium instead of Playwright?

Just pass the driver fixture (`def test_canvas(driver, hitbox):`)—Hitbox auto-detects the active browser driver.

---

## Build Roadmap

### Phase 1: Python Core Engine, Playwright & Selenium (pytest-hitbox) — In Progress

- [x] Multi-Driver Adapter Architecture: Base protocol supporting both Playwright (Page) and Selenium (WebDriver) W3C pointer actions.
- [x] Core Client & Affine Projection: `/v1/systemone` vision payload builders, DPI-safe coordinate math, and 2x Micro-Zoom reprojection.
- [x] Perceptual Cache & Visual Annotator: dHash L1 cache and Pillow-based HUD receipt renderer (`.hitbox-traces/`).
- [ ] Live Calibration & Prompt Tuning: Tune parallel noul and score criteria against obstructed modals, toasts, and disabled controls.
- [ ] Canvas Torture Testbed & Benchmarks: Benchmark IoU, Center-Point Hit Rate, and Expected Calibration Error (ECE) across Three.js, Mapbox/Leaflet, and HTML5 `<canvas>` surfaces.

### Phase 2: Scoped Visual Auditing & CI Integrations

- [ ] Region Auditing API (`hitbox.audit_region`): Parallel score and noul visual assertions for semantic layout drift, text truncation, and rendering defects.
- [ ] Playwright HTML Report & Trace Viewer Hooks: Embed annotated visual receipts directly into native Playwright `trace.zip` timelines.
- [ ] Figma Reference Sync CLI: Automated CLI for syncing golden component thumbnails as Jev visual instructions.

### Phase 3: TypeScript & NPM Ecosystem (`@hitbox-qa/*`)

- [ ] TypeScript Core Port (`@hitbox-qa/core`): Port the `/v1/systemone` vision client, coordinate transforms, and perceptual caching to Node.js/TypeScript.
- [ ] Native `@playwright/test` & WebDriverIO Packages: Publish `@hitbox-qa/playwright` and `@hitbox-qa/selenium` to npm with `test.extend()` and `expect.extend()` visual matchers.

---

## Local Development Setup

Set your TypeSafe AI API key:

```bash
export TYPESAFE_API_KEY="your-typesafe-api-key"
```

Clone the repository and install in editable mode (with Playwright and Selenium dev extras):

```bash
git clone https://github.com/<your-org>/hitbox.git
cd hitbox
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest tests/ -v
```

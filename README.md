# Hitbox 🎯⚡

> Zero-selector visual localization and canvas QA engine for Playwright, powered by **TypeSafe Jev**.

[![Powered by TypeSafe Jev](https://img.shields.io/badge/Powered%20by-TypeSafe%20Jev-6366f1.svg)](https://typesafe.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI version](https://img.shields.io/badge/PyPI-pytest--hitbox-orange.svg)]()

**Status:** 🚧 Active Development (Pre-release)

---

## Overview

Traditional end-to-end testing relies on brittle CSS selectors and XPath queries that break whenever component classes or markup change. Worse, applications built on **HTML5 `<canvas>`, WebGL (Three.js), Flutter Web, and interactive maps** render zero DOM nodes—leaving standard Playwright locators completely blind.

**Hitbox** brings vision-driven interaction to Playwright by utilizing **TypeSafe Jev** as its core decision engine. Instead of slow, generative vision models that hallucinate coordinates, Hitbox leverages Jev's **System One visual primitives** (`bbox`, `noul`, `score`) to evaluate raw viewports in ~150–200 ms with calibrated certainty. 

Hitbox resolves clickable target regions from visual reference crops or semantic descriptions and executes sub-pixel clicks directly on raw canvas surfaces.

---

## Why TypeSafe Jev Powers Hitbox

| Feature | Standard Playwright | Generative VLMs (GPT / Claude) | **Hitbox (TypeSafe Jev)** |
| :--- | :--- | :--- | :--- |
| **Canvas & WebGL Targeting** | ❌ Blind (No DOM elements) | ⚠️ Slow (~3–6s latency) | **✅ Fast (~150–200 ms single pass)** |
| **Execution Surface** | Brittle CSS/XPath selectors | Markdown coordinate guesses | **Sub-pixel normalized `bbox` primitives** |
| **Actionability Verification** | DOM-level only (`isVisible`) | Text explanation of visibility | **Parallel `noul` checks (`is_unobstructed`)** |
| **Output Guarantees** | Native boolean assertions | Unstructured JSON strings | **Zero type errors + calibrated probabilities** |

---

## Core Capabilities

* **Zero-DOM Canvas & WebGL Testing:** Target and interact with canvas-rendered buttons, data points, and 3D gizmos without requiring underlying DOM elements.
* **Single-Pass Actionability Gating:** Evaluates target bounding box localization, occlusion (`is_unobstructed`), and clickable styling (`is_visually_enabled`) in a single parallel Jev forward pass.
* **Calibrated Confidence Thresholds:** Takes advantage of Jev's honest probability distributions—automatically halting or escalating when a visual match falls below confidence thresholds.
* **2x Micro-Zoom Refinement:** Automatically crops and zooms into ambiguous candidate regions to lock onto dense toolbar icons with sub-pixel precision.
* **Perceptual L1 Caching:** Employs difference hashing (`dHash`) to skip redundant visual resolutions across unchanged frames.
* **Drop-in Pytest Fixture:** Extends `pytest-playwright` out of the box with annotated bounding-box visual receipts attached to test reports.

---

## Usage Preview

```python
import pytest

def test_cad_canvas_export(page, hitbox):
    page.goto("[https://app.example.com/cad](https://app.example.com/cad)")

    # Locate and click via golden reference crop + verify unobstructed state via Jev
    hitbox.locate_by_image("fixtures/export_button.png").click()

    # Locate via semantic description directly on a WebGL canvas
    hitbox.locate_by_description("Active mesh rotation gizmo").drag_to_offset(dx=40, dy=0)

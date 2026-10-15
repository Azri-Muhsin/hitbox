from __future__ import annotations
import os
from typing import Any
import httpx
from PIL import Image
from hitbox.schemas import NormalizedBBox, ResolutionResult
from hitbox.transforms import image_to_data_url


class JevVisionClient:
    """Low-latency HTTP client for TypeSafe Jev /v1/systemone vision primitives."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.typesafe.ai/v1/systemone",
        model: str = "jev-vision-latest",
        timeout: float = 10.0,
    ):
        self.api_key = api_key or os.environ.get("TYPESAFE_API_KEY", "")
        self.base_url = base_url
        self.model = model
        self._http = httpx.Client(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    def resolve_target(
        self,
        scene_img: Image.Image,
        *,
        reference_img: Image.Image | None = None,
        description: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ResolutionResult:
        """Executes a single-pass BBox localization + parallel Noul actionability check."""
        if not reference_img and not description:
            raise ValueError("Provide either `reference_img` or `description`.")

        state: dict[str, Any] = {
            "target_scene": {
                "type": "image_url",
                "image_url": image_to_data_url(scene_img, fmt="JPEG"),
            },
            "runtime_context": context or {},
        }

        if reference_img is not None:
            state["instruction_reference"] = {
                "type": "image_url",
                "image_url": image_to_data_url(reference_img, fmt="PNG"),
            }
            bbox_question = {
                "type": "bbox",
                "mode": "image_reference",
                "instructions": (
                    description
                    or "Locate the UI element in target_scene that matches instruction_reference."
                ),
            }
        else:
            bbox_question = {
                "type": "bbox",
                "mode": "semantic_description",
                "instructions": f"Locate the bounding box for: {description}",
            }

        payload = {
            "model": self.model,
            "state": state,
            "questions": {
                "target_bbox": bbox_question,
                "is_unobstructed": {
                    "type": "noul",
                    "region_ref": "target_bbox",
                    "instructions": (
                        "Is target_bbox completely unobstructed by modal backdrops, "
                        "cookie banners, toast notifications, or loading spinners?"
                    ),
                },
                "is_visually_enabled": {
                    "type": "noul",
                    "region_ref": "target_bbox",
                    "instructions": (
                        "Does the control inside target_bbox appear active and clickable "
                        "rather than disabled or grayed-out?"
                    ),
                },
            },
        }

        resp = self._http.post(self.base_url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        answers = data.get("answers", {})

        bbox_ans = answers["target_bbox"]
        unob_ans = answers.get("is_unobstructed", {"value": True, "probability": 1.0})
        enab_ans = answers.get("is_visually_enabled", {"value": True, "probability": 1.0})

        return ResolutionResult(
            bbox=NormalizedBBox.from_list(bbox_ans["box_2d"]),
            confidence=float(bbox_ans.get("confidence", 0.0)),
            is_unobstructed=bool(unob_ans.get("value", True)),
            unobstructed_prob=float(unob_ans.get("probability", 1.0)),
            is_visually_enabled=bool(enab_ans.get("value", True)),
            enabled_prob=float(enab_ans.get("probability", 1.0)),
            raw_answers=answers,
        )
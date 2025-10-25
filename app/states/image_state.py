import reflex as rx
from typing import TypedDict
import os
import requests
import json
import logging
import base64
import time


class GeneratedImage(TypedDict):
    prompt: str
    image_b64: str
    timestamp: str


IMAGE_MODELS = {
    "Stable Diffusion XL Base": "@cf/stabilityai/stable-diffusion-xl-base-1.0",
    "Stable Diffusion XL Lightning": "@cf/bytedance/stable-diffusion-xl-lightning",
    "Flux-1 Schnell": "@cf/black-forest-labs/flux-1-schnell",
    "Phoenix-1.0": "@cf/leonardo/phoenix-1.0",
    "Lucid-Origin": "@cf/leonardo/lucid-origin",
    "Dreamshaper-8-LCM": "@cf/lykon/dreamshaper-8-lcm",
}


class ImageGenerationState(rx.State):
    is_generating: bool = False
    selected_model: str = "Flux-1 Schnell"
    image_history: list[GeneratedImage] = []
    error_message: str = ""
    selected_style: str = "photorealistic"
    selected_size: str = "1024x1024"
    quality_steps: int = 20

    @rx.var
    def styles(self) -> list[dict[str, str]]:
        return [
            {"name": "photorealistic", "label": "Photorealistic", "icon": "camera"},
            {"name": "anime", "label": "Anime", "icon": "swords"},
            {"name": "digital-art", "label": "Digital Art", "icon": "paintbrush-2"},
            {"name": "oil-painting", "label": "Oil Painting", "icon": "palette"},
            {"name": "watercolor", "label": "Watercolor", "icon": "paint-bucket"},
            {"name": "sketch", "label": "Sketch", "icon": "pencil"},
        ]

    @rx.var
    def sizes(self) -> list[dict[str, str]]:
        return [
            {"value": "1024x1024", "label": "Square"},
            {"value": "1024x768", "label": "Landscape"},
            {"value": "768x1024", "label": "Portrait"},
        ]

    @rx.var
    def model_options(self) -> list[str]:
        return list(IMAGE_MODELS.keys())

    @rx.var
    def latest_image(self) -> GeneratedImage | None:
        if self.image_history:
            return self.image_history[-1]
        return None

    @rx.event(background=True)
    async def generate_image(self, form_data: dict):
        async with self:
            prompt = form_data.get("prompt", "").strip()
            if not prompt:
                yield rx.toast("Please enter a prompt.", duration=3000)
                return
            full_prompt = f"{prompt}, {self.selected_style} style"
            self.is_generating = True
            self.error_message = ""
        yield
        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        token = os.getenv("CLOUDFLARE_AUTH_TOKEN")
        if not all([account_id, token]):
            async with self:
                self.error_message = "API credentials not configured."
                self.is_generating = False
            return
        width, height = map(int, self.selected_size.split("x"))
        model_id = IMAGE_MODELS.get(self.selected_model)
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model_id}"
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "prompt": full_prompt,
            "num_steps": self.quality_steps,
            "width": width,
            "height": height,
        }
        try:
            with requests.post(
                url, headers=headers, json=data, timeout=120
            ) as response:
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "")
                if "image/png" in content_type:
                    image_b64 = f"data:image/png;base64,{base64.b64encode(response.content).decode('utf-8')}"
                elif "application/json" in content_type:
                    json_response = response.json()
                    image_b64 = (
                        f"data:image/png;base64,{json_response['result']['image']}"
                    )
                else:
                    raise Exception(f"Unexpected content type: {content_type}")
                new_image = GeneratedImage(
                    prompt=full_prompt,
                    image_b64=image_b64,
                    timestamp=str(int(time.time())),
                )
                async with self:
                    self.image_history.append(new_image)
        except requests.exceptions.RequestException as e:
            logging.exception(f"Image generation error: {e}")
            async with self:
                self.error_message = f"API Error: {str(e)}"
        except Exception as e:
            logging.exception(f"An unexpected error occurred: {e}")
            async with self:
                self.error_message = str(e)
        finally:
            async with self:
                self.is_generating = False

    async def _generate_image_from_prompt(
        self, prompt: str, style: str
    ) -> tuple[str | None, str | None]:
        full_prompt = f"{prompt}, {style} style"
        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        token = os.getenv("CLOUDFLARE_AUTH_TOKEN")
        if not all([account_id, token]):
            error_msg = "API credentials not configured for image generation."
            logging.error(error_msg)
            return (None, error_msg)
        width, height = map(int, self.selected_size.split("x"))
        model_id = IMAGE_MODELS.get(self.selected_model)
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model_id}"
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "prompt": full_prompt,
            "num_steps": 20,
            "width": width,
            "height": height,
        }
        try:
            with requests.post(
                url, headers=headers, json=data, timeout=120
            ) as response:
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "")
                if "image/png" in content_type:
                    image_b64 = f"data:image/png;base64,{base64.b64encode(response.content).decode('utf-8')}"
                elif "application/json" in content_type:
                    json_response = response.json()
                    image_b64 = (
                        f"data:image/png;base64,{json_response['result']['image']}"
                    )
                else:
                    raise Exception(f"Unexpected content type: {content_type}")
                new_image = GeneratedImage(
                    prompt=full_prompt,
                    image_b64=image_b64,
                    timestamp=str(int(time.time())),
                )
                async with self:
                    self.image_history.append(new_image)
                return (image_b64, None)
        except requests.exceptions.RequestException as e:
            error_msg = f"API Error: {e}"
            logging.exception(f"Image generation error from tool call: {e}")
            return (None, error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            logging.exception(error_msg)
            return (None, error_msg)
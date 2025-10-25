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
    "Stable Diffusion XL Lightning": "@cf/bytedance/stable-diffusion-xl-lightning",
    "Flux-1 Schnell": "@cf/black-forest-labs/flux-1-schnell",
}


class ImageGenerationState(rx.State):
    is_generating: bool = False
    selected_model: str = "Stable Diffusion XL Lightning"
    image_history: list[GeneratedImage] = []
    error_message: str = ""

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
        prompt = form_data.get("prompt", "").strip()
        if not prompt:
            yield rx.toast("Please enter a prompt.", duration=3000)
            return
        async with self:
            self.is_generating = True
            self.error_message = ""
        yield
        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        gateway_id = os.getenv("CLOUDFLARE_AI_GATEWAY")
        token = os.getenv("CLOUDFLARE_AI_GATEWAY_TOKEN")
        if not all([account_id, gateway_id, token]):
            async with self:
                self.error_message = "API credentials not configured."
                self.is_generating = False
            return
        model_id = IMAGE_MODELS.get(self.selected_model)
        url = f"https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/workers-ai/{model_id}"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"prompt": prompt}
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
                    prompt=prompt, image_b64=image_b64, timestamp=str(int(time.time()))
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
import reflex as rx
from typing import TypedDict, Optional
import os
import requests
import json
import logging


class Message(TypedDict):
    role: str
    content: str
    is_initial_greeting: Optional[bool]


CLOUDFLARE_MODELS = {
    "Llama 3.1 8B Instruct": "@cf/meta/llama-3.1-8b-instruct",
    "Llama 2 7B Chat": "@cf/meta/llama-2-7b-chat-int8",
    "Mistral 7B Instruct": "@cf/mistral/mistral-7b-instruct-v0.1",
}


class ChatState(rx.State):
    messages: list[Message] = []
    is_streaming: bool = False
    selected_model: str = "Llama 3.1 8B Instruct"
    error_message: str = ""

    @rx.var
    def model_options(self) -> list[str]:
        return list(CLOUDFLARE_MODELS.keys())

    @rx.event
    def go_back_and_clear_chat(self):
        self.messages = []
        self.is_streaming = False
        self.error_message = ""
        return rx.redirect("/")

    @rx.event
    def submit_suggestion_as_prompt(self, suggestion_text: str):
        prompt = f"Help me {suggestion_text.lower()}"
        form_data = {"prompt_input": prompt}
        yield ChatState.send_initial_message_and_navigate(form_data)

    @rx.event
    def send_initial_message_and_navigate(self, form_data: dict):
        prompt = form_data.get("prompt_input", "").strip()
        if not prompt or self.is_streaming:
            if not prompt:
                yield rx.toast("Please enter a message.", duration=3000)
            return
        self.messages = []
        self.messages.append({"role": "user", "content": prompt})
        self.messages.append(
            {"role": "assistant", "content": "", "is_initial_greeting": False}
        )
        self.is_streaming = True
        self.error_message = ""
        yield ChatState.stream_cloudflare_response
        yield rx.redirect("/chat")

    @rx.event
    def send_chat_page_message(self, form_data: dict):
        prompt = form_data.get("chat_page_prompt_input", "").strip()
        if not prompt or self.is_streaming:
            if not prompt:
                yield rx.toast("Please enter a message.", duration=3000)
            return
        self.messages.append({"role": "user", "content": prompt})
        self.messages.append(
            {"role": "assistant", "content": "", "is_initial_greeting": False}
        )
        self.is_streaming = True
        self.error_message = ""
        yield ChatState.stream_cloudflare_response

    @rx.event(background=True)
    async def stream_cloudflare_response(self):
        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        gateway_id = os.getenv("CLOUDFLARE_AI_GATEWAY")
        token = os.getenv("CLOUDFLARE_AI_GATEWAY_TOKEN")
        if not all([account_id, gateway_id, token]):
            async with self:
                self.messages[-1]["content"] = "Cloudflare credentials are not set."
                self.is_streaming = False
                self.error_message = "API credentials not configured."
            return
        model_id = CLOUDFLARE_MODELS.get(self.selected_model)
        if not model_id:
            async with self:
                self.messages[-1]["content"] = "Invalid model selected."
                self.is_streaming = False
                self.error_message = "Invalid model."
            return
        prompt = self.messages[-2]["content"]
        url = f"https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/workers-ai/{model_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        data = {"prompt": prompt, "stream": True}
        accumulated_content = ""
        try:
            with requests.post(
                url, headers=headers, json=data, stream=True, timeout=120
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode("utf-8")
                        if line_str.startswith("data: "):
                            json_str = line_str[6:].strip()
                            if not json_str or json_str == "[DONE]":
                                continue
                            try:
                                json_data = json.loads(json_str)
                                if not isinstance(json_data, dict):
                                    continue
                                text_chunk = json_data.get("response")
                                accumulated_content += text_chunk or ""
                                async with self:
                                    if not self.is_streaming:
                                        break
                                    self.messages[-1]["content"] = accumulated_content
                            except json.JSONDecodeError as e:
                                logging.exception(
                                    f"JSON Decode Error for line: {json_str}"
                                )
                                continue
        except requests.exceptions.RequestException as e:
            logging.exception(f"Error: {e}")
            error_detail = f"API Error: {str(e)}"
            async with self:
                self.messages[-1]["content"] = (
                    f"Sorry, I encountered an error. {error_detail}"
                )
                self.error_message = error_detail
        except Exception as e:
            logging.exception(f"Error: {e}")
            async with self:
                self.messages[-1]["content"] = f"An unexpected error occurred: {str(e)}"
                self.error_message = str(e)
        finally:
            async with self:
                self.is_streaming = False
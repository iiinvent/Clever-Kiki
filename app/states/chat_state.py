import reflex as rx
from typing import TypedDict, Optional
import os
import requests
import json
import logging
import ast


class Message(TypedDict):
    role: str
    content: str
    is_initial_greeting: Optional[bool]
    image_b64: Optional[str]
    tool_call_info: Optional[str]
    tool_call_status: Optional[str]
    tool_call_error: Optional[str]


CLOUDFLARE_MODELS = {
    "Llama 3.1 8B Instruct Fast": "@cf/meta/llama-3.1-8b-instruct-fast",
    "Hermes 2 Pro Mistral 7B": "@hf/nousresearch/hermes-2-pro-mistral-7b",
    "Llama 3.1 8B Instruct": "@cf/meta/llama-3.1-8b-instruct",
    "Llama 2 7B Chat": "@cf/meta/llama-2-7b-chat-int8",
    "Mistral 7B Instruct": "@cf/mistral/mistral-7b-instruct-v0.1",
}


class ChatState(rx.State):
    messages: list[Message] = []
    is_streaming: bool = False
    selected_model: str = "Hermes 2 Pro Mistral 7B"
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
        tools = [
            {
                "name": "generate_image",
                "description": "Generate an image based on a user prompt.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The prompt for the image to be generated.",
                        },
                        "style": {
                            "type": "string",
                            "description": "The style of the image, e.g., 'photorealistic', 'anime'.",
                        },
                    },
                    "required": ["prompt"],
                },
            }
        ]
        api_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.messages[:-1]
        ]
        data = {"messages": api_messages, "stream": True, "tools": tools}
        accumulated_content = ""
        tool_call_dict = None
        in_tool_call = False
        tool_call_str = ""
        tool_call_completed = False
        try:
            with requests.post(
                url, headers=headers, json=data, stream=True, timeout=120
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if tool_call_completed:
                        break
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
                                if json_data.get("type") == "tool_use":
                                    tool_call_completed = True
                                    tool_call_dict = {
                                        "name": json_data.get("name"),
                                        "arguments": json_data.get("input", {}),
                                    }
                                    break
                                if "response" in json_data:
                                    text_chunk = json_data.get("response", "")
                                    if not text_chunk:
                                        continue
                                    accumulated_content += text_chunk
                                    if "<tool_call>" in accumulated_content and (
                                        not in_tool_call
                                    ):
                                        in_tool_call = True
                                        start_index = accumulated_content.find(
                                            "<tool_call>"
                                        )
                                        text_before_tool_call = accumulated_content[
                                            :start_index
                                        ].strip()
                                        accumulated_content = accumulated_content[
                                            start_index:
                                        ]
                                        async with self:
                                            self.messages[-1]["content"] = (
                                                text_before_tool_call
                                            )
                                            self.messages[-1]["tool_call_status"] = (
                                                "loading"
                                            )
                                    if (
                                        in_tool_call
                                        and "</tool_call>" in accumulated_content
                                    ):
                                        start_index = accumulated_content.find(
                                            "<tool_call>"
                                        ) + len("<tool_call>")
                                        end_index = accumulated_content.find(
                                            "</tool_call>"
                                        )
                                        tool_call_str = accumulated_content[
                                            start_index:end_index
                                        ].strip()
                                        try:
                                            tool_call_dict = ast.literal_eval(
                                                tool_call_str
                                            )
                                            tool_call_completed = True
                                        except (ValueError, SyntaxError) as e:
                                            logging.exception(
                                                f"Failed to parse tool call string: {tool_call_str} with error: {e}"
                                            )
                                            async with self:
                                                self.messages[-1]["content"] = (
                                                    "Sorry, there was an error processing the tool call."
                                                )
                                                self.messages[-1][
                                                    "tool_call_status"
                                                ] = "error"
                                        break
                                    if not in_tool_call:
                                        async with self:
                                            if not self.is_streaming:
                                                break
                                            self.messages[-1]["content"] = (
                                                accumulated_content
                                            )
                            except json.JSONDecodeError:
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
            logging.exception(f"An unexpected error occurred: {e}")
            async with self:
                self.messages[-1]["content"] = f"An unexpected error occurred: {str(e)}"
                self.error_message = str(e)
        finally:
            async with self:
                self.is_streaming = False
        if tool_call_dict:
            yield ChatState.execute_tool_call(tool_call_dict)

    @rx.event(background=True)
    async def execute_tool_call(self, tool_call: dict):
        from app.states.image_state import ImageGenerationState
        import time

        logging.info(f"Executing tool call: {tool_call}")
        tool_name = tool_call.get("name")
        arguments = tool_call.get("arguments", tool_call.get("parameters"))
        if arguments is None:
            logging.error(
                f"Invalid tool call received: missing 'arguments' or 'parameters'. Full call: {tool_call}"
            )
            async with self:
                self.messages[-1]["content"] = (
                    "Sorry, I received an invalid request to generate an image (missing arguments)."
                )
                self.messages[-1]["tool_call_status"] = "error"
            return
        prompt = arguments.get("prompt")
        style = arguments.get("style", "photorealistic")
        if tool_name == "generate_image" and prompt:
            async with self:
                self.messages[-1]["content"] = ""
                self.messages[-1]["tool_call_status"] = "loading"
                self.messages[-1]["image_b64"] = None
                image_state = await self.get_state(ImageGenerationState)
            image_b64, error = await image_state._generate_image_from_prompt(
                prompt, style
            )
            async with self:
                if image_b64:
                    self.messages[-1]["image_b64"] = image_b64
                    self.messages[-1]["content"] = "Here is the generated image:"
                    self.messages[-1]["tool_call_status"] = "success"
                else:
                    self.messages[-1]["content"] = (
                        f"Sorry, I couldn't generate the image. Reason: {error}"
                    )
                    self.messages[-1]["tool_call_status"] = "error"
        else:
            logging.error(
                f"Invalid tool call received or prompt missing. Full call: {tool_call}"
            )
            async with self:
                self.messages[-1]["content"] = (
                    "Sorry, I received an invalid request to generate an image."
                )
                self.messages[-1]["tool_call_status"] = "error"
import reflex as rx
from app.states.chat_state import ChatState, Message


def user_message_bubble(message_content: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    message_content,
                    class_name="text-neutral-200 whitespace-pre-wrap break-words leading-relaxed",
                ),
                class_name="bg-[#353740] p-3 rounded-lg shadow",
            ),
            rx.el.div(
                "NR",
                class_name="flex items-center justify-center w-8 h-8 bg-neutral-700 text-neutral-300 rounded-full text-sm font-medium ml-3 sm:ml-4 shrink-0",
            ),
            class_name="flex items-start flex-row-reverse max-w-[85%] sm:max-w-[75%]",
        ),
        class_name="w-full flex justify-end",
    )


def _tool_call_ui(message: Message) -> rx.Component:
    status = message.get("tool_call_status")
    return rx.el.div(
        rx.cond(
            message.get("tool_call_info") != None,
            rx.el.div(
                rx.el.div(
                    rx.icon("bot", size=16, class_name="mr-2 text-neutral-400"),
                    rx.el.p(
                        message.get("tool_call_info"),
                        class_name="text-xs text-neutral-400 font-mono",
                    ),
                    class_name="flex items-center",
                ),
                rx.cond(
                    status == "error",
                    rx.el.div(
                        rx.el.p(
                            message.get("tool_call_error"),
                            class_name="text-xs text-red-400 mt-1",
                        ),
                        rx.el.button(
                            "Retry Generation",
                            rx.icon("refresh-cw", size=14, class_name="ml-2"),
                            on_click=ChatState.retry_image_generation,
                            class_name="mt-2 text-xs flex items-center px-2 py-1 bg-red-900/50 text-red-300 hover:bg-red-800/50 rounded-md",
                        ),
                        class_name="mt-2",
                    ),
                    None,
                ),
                class_name="bg-[#202123] p-2 rounded-md mt-3 border border-neutral-700",
            ),
            None,
        ),
        rx.cond(
            status == "loading",
            rx.el.div(
                rx.icon(
                    "loader-circle",
                    class_name="animate-spin text-[#E97055] w-8 h-8 mx-auto",
                ),
                rx.el.p(
                    "Generating image...",
                    class_name="text-center text-sm text-neutral-400 mt-2",
                ),
                class_name="mt-3 p-4 bg-[#202123] rounded-lg",
            ),
            None,
        ),
        rx.cond(
            message.get("image_b64") != None,
            rx.el.div(
                rx.el.img(
                    src=message["image_b64"],
                    class_name="rounded-lg mt-2 max-w-full h-auto",
                ),
                class_name="mt-2",
            ),
            None,
        ),
    )


def ai_message_bubble(message: Message) -> rx.Component:
    is_initial = message["is_initial_greeting"]
    return rx.el.div(
        rx.el.div(
            rx.cond(
                is_initial,
                rx.el.div(
                    "NR",
                    class_name="flex items-center justify-center w-8 h-8 bg-neutral-600 text-neutral-200 rounded-full text-sm font-medium mr-3 sm:mr-4 shrink-0",
                ),
                rx.icon(
                    "sparkle",
                    class_name="text-[#E97055] w-8 h-8 mr-3 sm:mr-4 shrink-0 p-1",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    message["content"],
                    class_name=rx.cond(
                        is_initial,
                        "font-medium text-neutral-100 whitespace-pre-wrap break-words leading-relaxed",
                        "text-neutral-200 whitespace-pre-wrap break-words leading-relaxed",
                    ),
                ),
                _tool_call_ui(message),
                rx.cond(
                    is_initial == False,
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "copy",
                                size=18,
                                class_name="text-neutral-400 hover:text-neutral-200 cursor-pointer p-1",
                            ),
                            rx.icon(
                                "thumbs-up",
                                size=18,
                                class_name="text-neutral-400 hover:text-neutral-200 cursor-pointer p-1",
                            ),
                            rx.icon(
                                "thumbs-down",
                                size=18,
                                class_name="text-neutral-400 hover:text-neutral-200 cursor-pointer p-1",
                            ),
                            class_name="flex items-center space-x-2",
                        ),
                        rx.el.p(
                            "Claude can make mistakes. Please double-check responses.",
                            class_name="text-xs text-neutral-500 hidden sm:block",
                        ),
                        class_name="flex flex-wrap items-center justify-between mt-3 w-full gap-2",
                    ),
                    rx.el.div(),
                ),
                class_name="bg-[#2A2B2E] p-3 rounded-lg shadow flex-grow min-w-0",
            ),
            class_name="flex items-start w-full",
        ),
        class_name="w-full",
    )


def chat_message_bubble_component(message: Message, index: int) -> rx.Component:
    return rx.cond(
        message["role"] == "user",
        user_message_bubble(message["content"]),
        ai_message_bubble(message),
    )
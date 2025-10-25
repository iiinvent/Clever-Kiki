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
    return rx.el.div(
        rx.cond(
            message.get("tool_call_status") == "loading",
            rx.el.div(
                rx.icon(
                    "loader-circle", class_name="animate-spin text-[#E97055] w-6 h-6"
                ),
                class_name="mt-3 p-4 flex justify-center items-center",
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
    )


def ai_message_bubble(message: Message) -> rx.Component:
    is_initial = message["is_initial_greeting"]
    has_tool_call = message.get("tool_call_status") != None
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
                rx.cond(
                    message["content"] != "",
                    rx.el.p(
                        message["content"],
                        class_name=rx.cond(
                            is_initial,
                            "font-medium text-neutral-100 whitespace-pre-wrap break-words leading-relaxed",
                            "text-neutral-200 whitespace-pre-wrap break-words leading-relaxed",
                        ),
                    ),
                    None,
                ),
                rx.cond(has_tool_call, _tool_call_ui(message), None),
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
                    None,
                ),
                class_name="bg-[#2A2B2E] p-3 rounded-lg shadow flex-grow min-w-0 space-y-3",
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
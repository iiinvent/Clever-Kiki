import reflex as rx
from app.states.chat_state import ChatState


def chat_input_bar() -> rx.Component:
    return rx.el.div(
        rx.el.form(
            rx.el.div(
                rx.el.div(
                    rx.el.button(
                        rx.icon("plus", size=20, class_name="text-neutral-400"),
                        type="button",
                        class_name="p-2.5 bg-[#40414F] hover:bg-[#50515f] rounded-md min-w-[44px] min-h-[44px] flex items-center justify-center",
                    ),
                    rx.el.button(
                        rx.icon("disc_3", size=20, class_name="text-neutral-400"),
                        type="button",
                        class_name="p-2.5 bg-[#40414F] hover:bg-[#50515f] rounded-md min-w-[44px] min-h-[44px] flex items-center justify-center",
                    ),
                    class_name="flex items-center space-x-2 pl-2",
                ),
                rx.el.textarea(
                    name="chat_page_prompt_input",
                    placeholder="Reply to Claude...",
                    class_name="flex-grow bg-transparent text-neutral-200 placeholder-neutral-500 focus:outline-none resize-none p-3 leading-tight text-base w-full h-full",
                    rows=1,
                    auto_height=True,
                    max_height="25vh",
                    enter_key_submit=True,
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("arrow-up", size=20, class_name="text-white"),
                        type="submit",
                        class_name="p-2.5 bg-[#E97055] hover:bg-[#d3654c] rounded-md aspect-square min-w-[44px] min-h-[44px] flex items-center justify-center",
                        is_disabled=ChatState.is_streaming,
                    ),
                    class_name="flex items-center p-2",
                ),
                class_name="bg-[#2A2B2E] rounded-xl shadow-lg w-full flex items-end p-1",
            ),
            on_submit=ChatState.send_chat_page_message,
            reset_on_submit=True,
            class_name="w-full max-w-4xl",
        ),
        class_name="sticky bottom-0 w-full flex justify-center px-3 sm:px-4 md:px-6 py-4 bg-[#202123] border-t border-neutral-700",
    )
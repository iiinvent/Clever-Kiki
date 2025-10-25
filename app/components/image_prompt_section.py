import reflex as rx
from app.states.image_state import ImageGenerationState


def image_prompt_section() -> rx.Component:
    return rx.el.form(
        rx.el.div(
            rx.el.textarea(
                name="prompt",
                placeholder="Describe the image you want to create...",
                class_name="w-full bg-transparent text-neutral-300 placeholder-neutral-500 focus:outline-none resize-none text-lg p-4 min-h-[120px]",
                rows=4,
            ),
            rx.el.div(
                rx.el.div(),
                rx.el.div(
                    rx.el.button(
                        rx.icon("sparkles", size=20, class_name="text-white"),
                        "Generate",
                        type="submit",
                        class_name="flex items-center gap-2 p-2 px-4 bg-[#E97055] hover:bg-[#d3654c] rounded-md font-medium text-white disabled:opacity-50 disabled:cursor-not-allowed",
                        is_disabled=ImageGenerationState.is_generating,
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex items-center justify-between p-2 pt-0",
            ),
            class_name="bg-[#353740] rounded-xl shadow-lg w-full flex flex-col",
        ),
        on_submit=ImageGenerationState.generate_image,
        reset_on_submit=True,
        class_name="w-full max-w-xl",
    )
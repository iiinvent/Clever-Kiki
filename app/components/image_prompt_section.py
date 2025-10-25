import reflex as rx
from app.states.image_state import ImageGenerationState
from app.components.image_settings_panel import image_settings_panel


def image_prompt_section() -> rx.Component:
    return rx.el.form(
        rx.el.div(
            rx.el.h2(
                "Image Generation",
                class_name="text-2xl font-['Lora'] text-neutral-100 mb-6",
            ),
            rx.el.div(
                rx.el.label(
                    "Prompt",
                    class_name="block text-sm font-medium text-neutral-300 mb-2",
                ),
                rx.el.textarea(
                    name="prompt",
                    placeholder="A cinematic shot of a raccoon astronaut in a futuristic city...",
                    class_name="w-full bg-[#2A2B2E] text-neutral-300 placeholder-neutral-500 focus:outline-none focus:ring-1 focus:ring-[#E97055] resize-none text-base p-3 rounded-lg min-h-[100px] border border-neutral-600",
                ),
                class_name="w-full",
            ),
            image_settings_panel(),
            rx.el.button(
                rx.icon("sparkles", size=20, class_name="mr-2"),
                "Generate Image",
                type="submit",
                class_name="w-full flex items-center justify-center gap-2 py-3 px-4 bg-[#E97055] hover:bg-[#d3654c] rounded-lg font-semibold text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors",
                is_disabled=ImageGenerationState.is_generating,
            ),
            class_name="bg-[#353740] rounded-xl shadow-lg w-full flex flex-col p-6 space-y-6",
        ),
        on_submit=ImageGenerationState.generate_image,
        class_name="w-full h-full",
    )
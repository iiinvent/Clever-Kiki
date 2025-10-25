import reflex as rx
from app.states.image_state import ImageGenerationState
from app.components.image_prompt_section import image_prompt_section
from app.components.image_display import image_display
from app.components.image_history import image_history


def _image_page_header() -> rx.Component:
    return rx.el.div(
        rx.el.a(
            rx.icon("arrow-left", size=20, class_name="mr-1 text-neutral-300"),
            "Back",
            href="/",
            class_name="flex items-center text-neutral-300 hover:text-neutral-100 bg-[#2A2B2E] hover:bg-[#3a3b3e] px-3 py-1.5 rounded-md text-sm font-medium",
        ),
        rx.el.div(
            rx.el.span("Model:", class_name="text-neutral-400 text-xs mr-2"),
            rx.el.select(
                rx.foreach(
                    ImageGenerationState.model_options,
                    lambda m: rx.el.option(m, value=m),
                ),
                value=ImageGenerationState.selected_model,
                on_change=ImageGenerationState.set_selected_model,
                class_name="bg-[#2A2B2E] border border-neutral-600 rounded-md text-xs text-neutral-200 focus:ring-1 focus:ring-[#E97055] focus:border-[#E97055]",
                size="1",
            ),
            class_name="ml-auto flex items-center",
        ),
        class_name="sticky top-0 z-10 flex items-center justify-between p-3 bg-[#202123] border-b border-neutral-700 h-14 w-full",
    )


def image_page() -> rx.Component:
    return rx.el.div(
        _image_page_header(),
        rx.el.main(
            image_prompt_section(),
            rx.el.div(class_name="h-12"),
            image_display(),
            image_history(),
            class_name="flex flex-col items-center w-full px-4 space-y-6 pt-8 pb-16",
        ),
        class_name="bg-[#202123] min-h-screen flex flex-col items-center text-neutral-200 font-['Inter'] selection:bg-[#E97055] selection:text-white",
    )
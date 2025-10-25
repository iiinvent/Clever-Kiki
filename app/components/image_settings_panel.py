import reflex as rx
from app.states.image_state import ImageGenerationState


def _style_selector() -> rx.Component:
    return rx.el.div(
        rx.el.label(
            "Style", class_name="block text-sm font-medium text-neutral-300 mb-2"
        ),
        rx.el.div(
            rx.foreach(
                ImageGenerationState.styles,
                lambda style: rx.el.button(
                    rx.icon(style["icon"], size=20, class_name="mr-2"),
                    style["label"],
                    on_click=lambda: ImageGenerationState.set_selected_style(
                        style["name"]
                    ),
                    class_name=rx.cond(
                        ImageGenerationState.selected_style == style["name"],
                        "flex items-center text-sm px-3 py-1.5 rounded-lg bg-[#E97055] text-white",
                        "flex items-center text-sm px-3 py-1.5 rounded-lg bg-[#40414F] text-neutral-300 hover:bg-[#50515f]",
                    ),
                    type="button",
                ),
            ),
            class_name="flex flex-wrap gap-2",
        ),
        class_name="w-full",
    )


def _size_selector() -> rx.Component:
    return rx.el.div(
        rx.el.label(
            "Size", class_name="block text-sm font-medium text-neutral-300 mb-2"
        ),
        rx.el.div(
            rx.foreach(
                ImageGenerationState.sizes,
                lambda size: rx.el.button(
                    size["label"],
                    on_click=lambda: ImageGenerationState.set_selected_size(
                        size["value"]
                    ),
                    class_name=rx.cond(
                        ImageGenerationState.selected_size == size["value"],
                        "text-sm px-4 py-1.5 rounded-lg bg-[#E97055] text-white",
                        "text-sm px-4 py-1.5 rounded-lg bg-[#40414F] text-neutral-300 hover:bg-[#50515f]",
                    ),
                    type="button",
                ),
            ),
            class_name="flex items-center gap-2",
        ),
        class_name="w-full",
    )


def _quality_slider() -> rx.Component:
    return rx.el.div(
        rx.el.label(
            f"Quality: {ImageGenerationState.quality_steps} steps",
            class_name="block text-sm font-medium text-neutral-300 mb-2",
        ),
        rx.el.input(
            type="range",
            min=10,
            max=50,
            default_value=ImageGenerationState.quality_steps.to_string(),
            on_change=ImageGenerationState.set_quality_steps.throttle(100),
            key=ImageGenerationState.quality_steps.to_string(),
            class_name="w-full h-2 bg-[#40414F] rounded-lg appearance-none cursor-pointer accent-[#E97055]",
        ),
        class_name="w-full",
    )


def image_settings_panel() -> rx.Component:
    return rx.el.div(
        _style_selector(), _size_selector(), _quality_slider(), class_name="space-y-6"
    )
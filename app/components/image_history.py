import reflex as rx
from app.states.image_state import GeneratedImage, ImageGenerationState


def image_history_item(image: GeneratedImage) -> rx.Component:
    return rx.el.div(
        rx.el.img(
            src=image.image_b64,
            class_name="aspect-square w-full rounded-lg object-cover group-hover:opacity-80 transition-opacity",
        ),
        rx.el.div(
            rx.el.p(image.prompt, class_name="text-xs text-neutral-200 truncate"),
            class_name="absolute bottom-0 left-0 right-0 bg-black/50 p-2",
        ),
        class_name="relative group overflow-hidden rounded-lg",
    )


def image_history() -> rx.Component:
    return rx.el.div(
        rx.el.h3("History", class_name="text-lg font-['Lora'] text-neutral-100 mb-4"),
        rx.cond(
            ImageGenerationState.image_history.length() > 0,
            rx.el.div(
                rx.foreach(
                    ImageGenerationState.image_history.reverse(), image_history_item
                ),
                class_name="grid grid-cols-2 md:grid-cols-3 gap-4",
            ),
            rx.el.p(
                "Your generated images will appear here.",
                class_name="text-neutral-500 text-center py-4",
            ),
        ),
        class_name="w-full",
    )
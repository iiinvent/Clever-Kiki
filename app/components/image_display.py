import reflex as rx
from app.states.image_state import ImageGenerationState, GeneratedImage


def image_display() -> rx.Component:
    return rx.el.div(
        rx.cond(
            ImageGenerationState.is_generating,
            rx.el.div(
                rx.icon(
                    "loader-circle",
                    class_name="animate-spin text-[#E97055] w-12 h-12 mx-auto",
                ),
                rx.el.p(
                    "Generating your image...",
                    class_name="text-center text-neutral-400 mt-4",
                ),
                class_name="flex flex-col items-center justify-center bg-[#2A2B2E] rounded-xl w-full aspect-square border-2 border-dashed border-neutral-600",
            ),
            rx.cond(
                ImageGenerationState.latest_image,
                rx.el.div(
                    rx.el.img(
                        src=ImageGenerationState.latest_image.image_b64,
                        class_name="rounded-lg object-contain w-full h-full",
                    ),
                    rx.el.a(
                        rx.icon("download", size=20),
                        "Download",
                        href=ImageGenerationState.latest_image.image_b64,
                        download=f"generated_image_{ImageGenerationState.latest_image.timestamp}.png",
                        class_name="absolute bottom-3 right-3 flex items-center gap-2 bg-[#2A2B2E] text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-[#3a3b3e] transition-colors",
                    ),
                    class_name="relative w-full aspect-square bg-black rounded-xl overflow-hidden",
                ),
                rx.el.div(
                    rx.icon("image", class_name="text-neutral-500 w-12 h-12 mx-auto"),
                    rx.el.p(
                        "Your generated image will appear here.",
                        class_name="text-center text-neutral-500 mt-4",
                    ),
                    class_name="flex flex-col items-center justify-center bg-[#2A2B2E] rounded-xl w-full aspect-square border-2 border-dashed border-neutral-600",
                ),
            ),
        ),
        class_name="w-full mb-12",
    )
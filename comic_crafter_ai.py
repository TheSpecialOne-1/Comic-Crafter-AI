import streamlit as st
import torch
import re
from transformers import pipeline
from diffusers import StableDiffusionPipeline
from PIL import Image


# ---------------------------
# Model Loading Functions
# ---------------------------
text_generator = None
image_generator = None

def load_text_generator():
    """Load and cache the text generation pipeline (GPT-Neo)."""
    global text_generator
    if text_generator is None:
        st.info("Loading text generator (GPT-Neo)...")
        text_generator = pipeline("text-generation", model="EleutherAI/gpt-neo-125M", device=-1)
    return text_generator

def load_image_generator():
    """Load and cache the Stable Diffusion pipeline for image generation."""
    global image_generator
    if image_generator is None:
        st.info("Loading image generator (Stable Diffusion)...")
        device = "cpu"
        image_generator = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5", 
            torch_dtype=torch.float32,  # Ensuring compatibility with CPU
            safety_checker=None  # Avoid filtering images
        ).to(device)
    return image_generator


# ---------------------------
# Phase 1: Story Generation
# ---------------------------
def generate_story(user_prompt, text_generator, max_length=300):
    """
    Generates a comic-style story divided into four parts:
    Introduction, Storyline, Climax, and Moral.
    """
    prompt = (
        f"Write a short comic-style story based on: {user_prompt}.\n"
        "Format it as follows:\n"
        "Introduction:\n"
        "Storyline:\n"
        "Climax:\n"
        "Moral:\n"
    )
    
    generated = text_generator(prompt, max_length=max_length, do_sample=True, temperature=0.8, num_return_sequences=1)
    story_text = generated[0]['generated_text']

    # Improved regex to handle missing sections
    pattern = r"Introduction:(.*?)(?:Storyline:|$)(.*?)(?:Climax:|$)(.*?)(?:Moral:|$)(.*)"
    match = re.search(pattern, story_text, re.DOTALL | re.IGNORECASE)

    if match:
        parts = {
            "Introduction": match.group(1).strip(),
            "Storyline": match.group(2).strip(),
            "Climax": match.group(3).strip(),
            "Moral": match.group(4).strip()
        }
    else:
        st.warning("Could not parse story. Returning empty sections.")
        parts = {"Introduction": "", "Storyline": "", "Climax": "", "Moral": ""}
    
    return parts



# ---------------------------
# Phase 2: Image Generation
# ---------------------------
def generate_image(text, image_generator):
    """
    Generates a comic book-style image based on the provided text.
    """
    prompt = f"Comic book style, vibrant and detailed: {text}"
    
    try:
        image = image_generator(prompt, guidance_scale=5.0).images[0]
        return image
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None
# ---------------------------
# Streamlit UI
# ---------------------------
st.title("AI ComicCrafter")
st.write("Generate AI-driven comic stories with illustrations!")

user_prompt = st.text_area("Enter a comic story prompt:", "", height=100)
if st.button("Generate Comic"):
    if not user_prompt.strip():
        st.warning("Please enter a valid prompt.")
    else:
        text_gen = load_text_generator()
        img_gen = load_image_generator()

        st.info("Generating story...")
        story_parts = generate_story(user_prompt, text_gen)

        for part_label in ["Introduction", "Storyline", "Climax", "Moral"]:
            st.subheader(part_label)
            st.write(story_parts.get(part_label, "[No content generated]"))

        st.info("Generating images...")
        for part_label in ["Introduction", "Storyline", "Climax", "Moral"]:
            image = generate_image(story_parts.get(part_label, ""), img_gen)
            if image:
                st.image(image, caption=f"{part_label} Illustration", use_column_width=True)
            else:
                st.warning(f"Failed to generate image for {part_label}.")

st.success("Comic generation complete!")

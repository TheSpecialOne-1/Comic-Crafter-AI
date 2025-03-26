import streamlit as st

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

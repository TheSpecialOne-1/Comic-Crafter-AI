import streamlit as st
from models import load_text_generator, load_image_generator
from story_generator import generate_story
from image_generator import generate_image

# Streamlit UI
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

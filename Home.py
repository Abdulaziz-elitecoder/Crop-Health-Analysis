import streamlit as st
import base64

# Convert image file to base64 string
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Path to your local background image
img_path = "model\Crop health analysis_\green.jpg"  # Make sure this image is in the same directory
img_base64 = get_base64_image(img_path)

# Set page config
st.set_page_config(page_title="Crop Health Analysis", layout="centered")

# Inject custom CSS
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .title {{
        font-size: 60px;
        font-weight: 900;
        color: white;
        text-align: center;
        margin-top: 50px;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
    }}

    .subtitle {{
        font-size: 28px;
        color: #f8f8f8;
        text-align: center;
        margin-bottom: 50px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
    }}

    .stButton > button {{
        font-size: 26px;
        font-weight: 600;
        padding: 1.25em 2.5em;
        border-radius: 14px;
        background-color: white;
        color: #c1502e;
        border: none;
        transition: 0.3s;
        box-shadow: 3px 3px 6px rgba(0,0,0,0.2);
    }}

    .stButton > button:hover {{
        background-color: #e3d5ce;
        color: #a8401d;
        transform: scale(1.08);
    }}

    .button-container {{
        display: flex;
        justify-content: center;
        gap: 60px;
        margin-top: 60px;
    }}
    </style>
""", unsafe_allow_html=True)

# Page content
st.markdown('<div class="title">🌿 Crop Health Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Select your role to get started</div>', unsafe_allow_html=True)

# Button section
st.markdown('<div class="button-container">', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    if st.button("🙎‍♂️  User"):
        st.switch_page("Pages/ui.py")

with col2:
    if st.button("👷 Admin"):
        st.switch_page("Pages/Admin.py")

st.markdown('</div>', unsafe_allow_html=True)

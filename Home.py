# BIBLIOTECAS
# --------------------------------------
import streamlit as st
from PIL import Image
# --------------------------------------


# PAGE LAYOUT
st.set_page_config(page_title="Home", page_icon="🟥", layout='wide')


# BARRA LATERAL
# ============================================

# Imagem da barra lateral
image_path = r'img/'
image_sidebar = Image.open(image_path + "zomato_logo.png")
st.sidebar.image(image_sidebar, width=160)


st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)


st.sidebar.markdown("""---""")



# Primeira seção da barra lateral
st.sidebar.markdown('# Welcome! ')
st.sidebar.markdown("Let's take a tour around the company.")
st.sidebar.markdown("""---""")


# Segunda seção da barra lateral
# My LinkedIn URL
linkedin_url = "https://www.linkedin.com/in/victor-bongestab/"
name = "Victor Bongestab"

st.sidebar.markdown(f"[![LinkedIn](https://img.icons8.com/color/48/000000/linkedin.png)]({linkedin_url}) {name}")



# MAIN PAGE
st.write("# Zomato Tour - Company Overview")

st.markdown("""
            ##### This Dashboard was made as a way for brand new collaborators to have an all rounded view of Zomato.
            ### Here you'll see
            ##### General Overview
                - Key Indicators
            
            
            ##### Geographic Overview
                - How Zomato works around the world
            
            
            ##### Restaurants and Cuisines Overview
                - What we bring to the table
            """)
import streamlit as st

from utils import nav_bar


st.set_page_config(layout="wide", page_title="FlagML | Documentație", page_icon="assets/logo.png")
nav_bar()

st.title("Documentație")

st.write("Aici puteți citi documentația aplicației.")

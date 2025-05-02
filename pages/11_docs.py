import streamlit as st

from utils import nav_bar


st.set_page_config(layout="wide", page_title="Documentație", page_icon="📚")
nav_bar()

st.title("Documentație")

st.write("Aici puteți citi documentația aplicației.")

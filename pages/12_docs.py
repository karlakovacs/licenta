import streamlit as st

from database import get_id_utilizator
from ui import nav_bar


st.set_page_config(layout="wide", page_title="FlagML | Documentație", page_icon="assets/logo.png")
nav_bar()
st.session_state.setdefault("id_utilizator", get_id_utilizator(st.user.sub))

st.title("Documentație")

st.write("Aici puteți citi documentația aplicației.")

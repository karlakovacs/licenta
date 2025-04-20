import streamlit as st

from database import *
from utils import nav_bar


st.set_page_config(layout="wide", page_title="Detectarea fraudei bancare", page_icon="🔥")

# st.title("🚨 Detectarea fraudei bancare 💳")
st.title("Binary Classification Toolkit")
nav_bar()

st.session_state.id_utilizator = get_utilizator(id_google="ADMIN")

import streamlit as st

from database import *
from nav_bar import nav_bar


st.set_page_config(layout="wide", page_title="Detectarea fraudei bancare", page_icon="🔥")

# st.title("🚨 Detectarea fraudei bancare 💳")
st.title("Binary Classification Toolkit")
nav_bar()

id_utilizator = 1
st.session_state.id_utilizator = id_utilizator
# get_utilizator(id_utilizator)

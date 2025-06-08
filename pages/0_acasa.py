import streamlit as st

from database import get_id_utilizator
from utils import nav_bar


st.set_page_config(layout="wide", page_title="FlagML | Acasă", page_icon="assets/logo.png")

nav_bar()

st.session_state.setdefault("id_utilizator", get_id_utilizator(st.user.sub))

st.title("Acasă")

st.write(
	"""
	Bun venit în cadrul aplicației dedicate clasificării binare!
	
	Puteți lucra folosind seturi proprii de date sau date referitoare la detectarea fraudei bancare.
	"""
)

if st.button("Clear session state"):
	st.session_state.clear()

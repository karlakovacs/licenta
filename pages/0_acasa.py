import streamlit as st

from utils import nav_bar


st.set_page_config(layout="wide", page_title="Acasă", page_icon="🏠")

nav_bar()

st.session_state.clear()

st.title("Acasă")

st.write(
	"""
	Bun venit în cadrul aplicației dedicate clasificării binare!
	
	Puteți lucra folosind seturi proprii de date sau date referitoare la detectarea fraudei bancare.
	"""
)

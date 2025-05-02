import streamlit as st

from utils import nav_bar


st.set_page_config(layout="wide", page_title="Detectarea fraudei bancare", page_icon="🔥")

nav_bar()

st.title("Acasă")

st.write(
	"Bun venit în cadrul aplicației dedicate clasificării binare!"
	"Puteți lucra folosind seturi proprii de date sau date referitoare la detectarea fraudei bancare."
)

import streamlit as st

from utils import nav_bar
from streamlit_google_auth import Authenticate


st.set_page_config(layout="wide", page_title="Datele mele", page_icon="📑")
nav_bar()

user_info: dict = st.session_state.user_info
authenticator: Authenticate = st.session_state.authenticator
st.markdown(
	f'<img src="{user_info.get("picture")}" width="100" style="border-radius: 50%;">',
	unsafe_allow_html=True,
)
st.write(user_info.get("name"))
st.write(user_info.get("email"))
if st.button("Deconectare"):
	authenticator.logout()
	st.switch_page("app.py")

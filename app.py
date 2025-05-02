from keras.api.models import Sequential  # necesar pentru functionarea keras  # noqa: I001

import json
import tempfile

import streamlit as st
from streamlit_google_auth import Authenticate

from database import login_utilizator


st.set_page_config(page_title="Autentificare", page_icon="🔐", layout="centered")

temp_credentials_path = tempfile.gettempdir() + "/" + "google_credentials" + ".json"
json_data = json.loads(st.secrets["google"]["GOOGLE_CREDENTIALS"])
with open(temp_credentials_path, "w") as f:
	json.dump(json_data, f)

authenticator = Authenticate(
	secret_credentials_path=temp_credentials_path,
	cookie_name=st.secrets["google"]["COOKIE_NAME"],
	cookie_key=st.secrets["google"]["COOKIE_KEY"],
	redirect_uri="http://localhost:8501",  # https://your-app-name.streamlit.app"
)
# os.remove(temp_credentials_path)

authenticator.check_authentification()

if not st.session_state.get("connected"):
	st.markdown(
		"<h1 style='font-size: 3em; font-weight: bold; text-align: center;'>Bun venit!</h1>",
		unsafe_allow_html=True,
	)
	st.markdown(
		"""
		Această aplicație educațională este concepută pentru a ajuta utilizatorii să înțeleagă și să exerseze clasificarea binară, adică probleme în care rezultatul are doar două valori posibile (de exemplu, o tranzacție bancară poate fi frauduloasă sau legitimă).

		Scopul principal este prezentarea fluxului complet al unui proiect de machine learning, de la încărcarea datelor până la antrenarea, evaluarea și interpretarea modelelor predictive. Aplicația oferă suport pentru:
		
		- Încărcarea unui dataset propriu (local sau de pe Kaggle) sau utilizarea unor seturi de date reale referitoare la detectarea fraudei bancare;
		- Analiza exploratorie a datelor pentru a înțelege setul de date;
		- Rularea a 14 algoritmi populari pentru clasificare binară;
		- Vizualizarea performanței modelelor prin metrici clasice și grafice utile;
		- Explainable AI (XAI) pentru a analiza modul în care modelele de machine learning iau decizii;
		- Generarea de rapoarte în format interactiv (HTML) sau clasic (PDF).
		"""
	)

	st.markdown('<div class="login-box">', unsafe_allow_html=True)
	authenticator.login()

else:
	with st.spinner("Logare..."):
		user_info: dict = st.session_state["user_info"]
		id_google: str = user_info["id"]
		st.session_state.authenticator = authenticator
		st.session_state.id_utilizator = login_utilizator(id_google)
		st.switch_page("pages/0_acasa.py")

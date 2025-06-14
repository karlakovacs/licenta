import random

import pandas as pd
import streamlit as st

from database import get_id_utilizator
from dataset import citire_date_temp, citire_metadate
from preprocessing import procesare_instanta
from ui import nav_bar
from xai import ui_predictii


st.set_page_config(layout="wide", page_title="FlagML | Predicții", page_icon="assets/logo.png")
nav_bar()
st.session_state.setdefault("id_utilizator", get_id_utilizator(st.user.sub))

st.title("Realizarea de predicții")


modele_antrenate = st.session_state.get("modele_antrenate", {})
X_train, X_test, y_train = (
	citire_date_temp("X_train"),
	citire_date_temp("X_test"),
	citire_date_temp("y_train"),
)
metadate: dict = citire_metadate()
tinta = st.session_state.get("set_date").get("tinta", "")
st.session_state.setdefault("valori_random", {})
st.session_state.setdefault("counter_idx", -1)

valori_introduse = {}

col1, col2 = st.columns([1, 3])
with col1:
	st.header("Introdu datele")

	if st.button("**🎲 Generare valori random**", type="primary", use_container_width=True):
		for coloana, info in metadate.items():
			if coloana == tinta:
				continue

			tip = info["tip"]
			if tip == "NC":
				mini = info.get("min", 0)
				maxi = info.get("max", 1)
				st.session_state.valori_random[coloana] = round(random.uniform(mini, maxi), 2)

			if tip == "ND":
				mini = info.get("min", 0)
				maxi = info.get("max", 1)
				st.session_state.valori_random[coloana] = random.randint(int(mini), int(maxi))

			elif tip == "B":
				st.session_state.valori_random[coloana] = bool(random.getrandbits(1))

			elif tip == "C":
				st.session_state.valori_random[coloana] = random.choice(info.get("valori", []))

			elif tip == "T":
				st.session_state.valori_random[coloana] = f"Text_{random.randint(100, 999)}"

	valori_introduse = {}

	with st.form("date_predictie"):
		for coloana, info in metadate.items():
			if coloana == tinta:
				continue

			tip = info["tip"]
			valoare_implicita = st.session_state.valori_random.get(coloana)

			if tip in ("NC", "ND"):
				step = 1 if tip == "ND" else 0.01
				valoare_min = info.get("min", 0)

				valori_introduse[coloana] = st.number_input(
					label=coloana,
					value=valoare_implicita if valoare_implicita is not None else valoare_min,
					help=f"**Interval**: {info.get('min')} - {info.get('max')}",
					step=step,
				)

			elif tip == "B":
				valori_introduse[coloana] = st.checkbox(
					label=coloana, value=valoare_implicita if valoare_implicita is not None else False
				)

			elif tip == "C":
				optiuni = info.get("valori", [])
				valori_introduse[coloana] = st.selectbox(
					label=coloana,
					options=optiuni,
					index=optiuni.index(valoare_implicita) if valoare_implicita in optiuni else 0,
				)

			elif tip == "T":
				valori_introduse[coloana] = st.text_input(label=coloana, value=valoare_implicita or "")

			else:
				st.warning(f"Tip necunoscut pentru coloana: {coloana}")

		if st.form_submit_button("Selectează", type="primary", use_container_width=True):
			st.session_state.counter_idx += 1
			st.session_state.instanta_procesata = procesare_instanta(
				pd.DataFrame([valori_introduse]), st.session_state.procesare
			)

with col2:
	st.header("Analizează observația")
	if st.session_state.get("instanta_procesata", None) is not None:
		ui_predictii(
			modele_antrenate, X_train, y_train, st.session_state.instanta_procesata, st.session_state.counter_idx
		)

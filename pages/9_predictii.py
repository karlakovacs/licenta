import datetime
import random

import pandas as pd
import streamlit as st

from dataset import citire_date_temp
from preprocessing import preprocesare_instanta
from ui import *
from xai import ui_predictii


initializare_pagina(
	"Predicții", "wide", "Realizarea de predicții", {"xai_predictii": {}, "valori_random": {}, "counter_idx": -1}
)


def generare_valori_random(metadate: dict, tinta: str):
	coloane_irelevante = obtinere_cheie_imbricata("preprocesare", "coloane_eliminate", [])
	valori_random: dict = {}
	for coloana, info in metadate.items():
		if coloana == tinta or coloana in coloane_irelevante:
			continue

		tip = info["tip"]

		if tip == "NC":
			mini = info.get("min", 0)
			maxi = info.get("max", 1)
			valori_random[coloana] = round(random.uniform(mini, maxi), 2)

		if tip == "ND":
			mini = info.get("min", 0)
			maxi = info.get("max", 1)
			valori_random[coloana] = random.randint(int(mini), int(maxi))

		elif tip == "B":
			valori_random[coloana] = bool(random.getrandbits(1))

		elif tip == "C":
			valori_random[coloana] = random.choice(info.get("valori", []))

		elif tip == "T":
			valori_random[coloana] = random.choice(info.get("valori", []))

		elif tip == "D":
			try:
				start_date = datetime.datetime.strptime(info.get("min"), "%Y-%m-%d %H:%M:%S")
				end_date = datetime.datetime.strptime(info.get("max"), "%Y-%m-%d %H:%M:%S")
			except Exception:
				start_date = datetime.datetime(2000, 1, 1, 0, 0)
				end_date = datetime.datetime(2024, 12, 31, 23, 59)

			total_seconds = int((end_date - start_date).total_seconds())
			random_offset = random.randint(0, total_seconds)
			valori_random[coloana] = start_date + datetime.timedelta(seconds=random_offset)

	return valori_random


def formular_predictie(metadate: dict, tinta: str, valori_random: dict = None):
	valori_introduse = {}
	valori_random = valori_random or {}

	with st.form("date_predictie"):
		coloane_irelevante = obtinere_cheie_imbricata("preprocesare", "coloane_eliminate", [])

		for coloana, info in metadate.items():
			if coloana == tinta or coloana in coloane_irelevante:
				continue

			tip = info["tip"]
			valoare_implicita = valori_random.get(coloana)

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

			elif tip == "D":
				valoare_data = st.date_input(
					label=f"{coloana} - dată",
					value=valoare_implicita.date()
					if isinstance(valoare_implicita, datetime.datetime)
					else (valoare_implicita or datetime.date.today()),
				)
				valoare_ora = st.time_input(
					label=f"{coloana} - oră",
					value=valoare_implicita.time()
					if isinstance(valoare_implicita, datetime.datetime)
					else datetime.time(0, 0),
					step=60,
				)

				valori_introduse[coloana] = datetime.datetime.combine(valoare_data, valoare_ora)

			else:
				st.warning(f"Tip necunoscut pentru coloana: {coloana}")

		if st.form_submit_button("Selectează", type="primary", use_container_width=True):
			st.session_state.counter_idx += 1
			st.session_state.instanta_procesata = preprocesare_instanta(
				pd.DataFrame([valori_introduse]), st.session_state.preprocesare
			)


@require_auth
@require_selected_dataset
@require_processed_dataset
@require_selected_models
@require_trained_models
def main():
	modele_antrenate = st.session_state.get("modele_antrenate", {})
	X_train, y_train = citire_date_temp("X_train"), citire_date_temp("y_train")
	metadate: dict = st.session_state.metadate
	tinta = st.session_state.get("set_date", {}).get("tinta", "")

	col1, col2 = st.columns([1, 3])
	with col1:
		st.header("Introdu datele")
		if st.button("**🎲 Generare valori random**", type="primary", use_container_width=True):
			st.session_state.valori_random = generare_valori_random(metadate, tinta)
		formular_predictie(metadate, tinta, st.session_state.valori_random)

	with col2:
		st.header("Analizează observația")
		if st.session_state.get("instanta_procesata", None) is not None:
			ui_predictii(
				modele_antrenate, X_train, y_train, st.session_state.instanta_procesata, st.session_state.counter_idx
			)


if __name__ == "__main__":
	main()

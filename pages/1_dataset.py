import streamlit as st

from database import *
from dataset import (
	citire_date_predefinite,
	citire_date_temp,
	citire_fisier_local,
	descarcare_kaggle,
	generare_metadate,
	salvare_date_temp,
)
from storage import *
from ui import nav_bar


st.set_page_config(layout="wide", page_title="FlagML | Set de date", page_icon="assets/logo.png")
nav_bar()
st.session_state.setdefault("id_utilizator", get_id_utilizator(st.user.sub))
st.session_state.setdefault("set_date", {})
st.session_state.setdefault("set_existent", False)

st.title("Setul de date")

if not st.session_state.set_date:
	df = None
	sursa = None
	denumire = None
	tinta = None
	st.session_state.setdefault("id_utilizator", get_id_utilizator(st.user.sub))

	sursa = st.selectbox(
		"📂 Alege sursa setului de date",
		["Fișier local", "Link Kaggle", "Seturi predefinite", "Seturile mele", "Seturile mele procesate"],
	)

	if sursa == "Fișier local":
		df = citire_fisier_local()
		denumire = st.text_input("📄 Denumirea setului de date")
		st.session_state.set_existent = False

	elif sursa == "Link Kaggle":
		link = st.text_input("🔗 Link Kaggle")
		if link:
			df = descarcare_kaggle(link)
		denumire = st.text_input("📄 Denumirea setului de date")
		st.session_state.set_existent = False

	elif sursa == "Seturi predefinite":
		set_predefinit = st.selectbox("📁 Alege un set predefinit", ["MLG-ULB"])
		df = citire_date_predefinite(set_predefinit)
		denumire = set_predefinit
		st.session_state.set_existent = False

	elif sursa == "Seturile mele":
		seturi = get_seturi_date_brute(st.session_state.id_utilizator)
		if not seturi:
			st.info("Nu ai încărcat niciun set de date.")
		else:
			selectie = st.selectbox(
				"📁 Alege un set de date existent", options=seturi, format_func=lambda s: s.denumire
			)
			if selectie:
				df = get_dataset_sample_from_storage(selectie.url)
				denumire = st.text_input("📄 Denumirea setului de date", value=selectie.denumire)
				sursa = get_sursa_by_id_set_date_brut(selectie.id)
				st.session_state.set_existent = True

	elif sursa == "Seturile mele procesate":
		seturi_procesate = get_seturi_date_procesate(st.session_state.id_utilizator)
		if not seturi_procesate:
			st.info("Nu ai niciun set de date procesat. Încearcă să alegi unul brut.")
		else:
			selectie = st.selectbox(
				"📁 Alege un set de date procesat", options=seturi_procesate, format_func=lambda s: s.denumire
			)
			if selectie:
				df = get_dataset_sample_from_storage(selectie.url)
				denumire = st.text_input(
					"📄 Denumirea setului de date procesat", value=selectie.denumire, disabled=True
				)
				sursa = get_sursa_by_id_set_date_procesat(selectie.id)
				st.session_state.set_existent = True

	if df is not None:
		st.header("Setul de date selectat")
		st.dataframe(df.head(), use_container_width=False)

		st.header("🎯 Selectează variabila țintă (binară)")
		coloane_binare = [col for col in df.columns if df[col].nunique(dropna=False) == 2]

		if coloane_binare:
			if sursa == "Seturi predefinite":
				default_index = coloane_binare.index("isFraud")
			elif sursa == "Seturile mele":
				tinta_set_brut = get_tinta_by_id_set_date_brut(selectie.id)
				default_index = coloane_binare.index(tinta_set_brut) if tinta_set_brut in coloane_binare else 0
			elif sursa == "Seturile mele procesate":
				tinta_set_procesat = get_tinta_by_id_set_date_procesat(selectie.id)
				default_index = coloane_binare.index(tinta_set_procesat) if tinta_set_procesat in coloane_binare else 0
			else:
				default_index = 0

			tinta = st.selectbox(
				"Variabilă țintă", coloane_binare, index=default_index, disabled=sursa == "Seturile mele procesate"
			)
		else:
			st.error("Nicio coloană binară disponibilă.")
			tinta = None

		if st.button("Confirmă selecția"):
			if tinta is None:
				st.error("Selectează o variabilă țintă validă.")
			elif not denumire:
				st.error("Introdu denumirea setului de date.")
			elif not st.session_state.set_existent and check_denumire_set_date_brut(
				st.session_state.id_utilizator, denumire
			):
				st.error("Un set de date cu această denumire există deja. Te rugăm să alegi alt nume.")
			else:
				st.session_state.set_date = {
					"denumire": denumire,
					"sursa": sursa,
					"tinta": tinta,
				}

				if not st.session_state.set_existent and sursa != "Seturi predefinite":
					st.session_state.id_set_date = create_set_date_brut(st.session_state.id_utilizator, sursa, denumire, tinta, df)
					st.toast("Setul de date a fost încărcat în baza de date", icon="✅")
				elif st.session_state.set_existent:
					if selectie.denumire != denumire or selectie.tinta != tinta:
						rezultat, mesaj = update_set_date_brut(
							st.session_state.id_utilizator, selectie.id, denumire=denumire, tinta=tinta
						)
						st.toast(mesaj, icon="✅" if rezultat else "❌")
					st.session_state.id_set_date = selectie.id

				if sursa != "Seturi predefinite":
					salvare_date_temp(df, denumire)

				generare_metadate(df)
				st.toast("Setul de date este gata de utilizare", icon="✅")

	else:
		st.warning("Niciun set de date încărcat.")

else:
	set_date: dict = st.session_state.get("set_date", None)
	st.header(f"Setul de date selectat")
	st.markdown(
		f"""
		- **Denumire**: `{set_date["denumire"]}`
		- **Sursa:** {set_date["sursa"]}
		- **Variabilă țintă:** `{set_date["tinta"]}`
		"""
	)
	if set_date["sursa"] != "Seturi predefinite":
		df = citire_date_temp(set_date["denumire"])
	else:
		df = citire_date_predefinite(set_date["denumire"])

	st.dataframe(df.head(), use_container_width=True)

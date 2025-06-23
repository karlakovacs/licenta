import streamlit as st

from database import *
from dataset import (
	citire_date_predefinite,
	citire_fisier_local,
	citire_kaggle,
	citire_set_date,
	generare_metadate,
	salvare_date_temp,
)
from storage import *
from ui import *


initializare_pagina("Set de date", "centered", "Setul de date", {"set_date": {}})


def handle_fisier_local():
	df = citire_fisier_local()
	return "Fișier local", df, None


def handle_kaggle():
	link = st.text_input("🔗 Link Kaggle")
	df = citire_kaggle(link) if link else None
	return "Link Kaggle", df, None


def handle_predefinite():
	seturi = get_seturi_date_predefinite()

	if not seturi:
		st.info("Nu există seturi predefinite disponibile.")
		return "Seturi predefinite", None, None

	selectie = st.selectbox("📁 Alege un set predefinit", options=seturi, format_func=lambda s: s.denumire)
	df = citire_date_predefinite(selectie.denumire)
	# sursa = get_sursa_by_id_set_date_brut(selectie.id)
	return "Seturi predefinite", df, selectie


def handle_seturi_brute():
	seturi = get_seturi_date_brute(st.session_state.id_utilizator)
	if not seturi:
		st.info("Nu ai încărcat niciun set de date.")
		return "Seturile mele", None, None

	selectie = st.selectbox("📁 Alege un set de date existent", options=seturi, format_func=lambda s: s.denumire)
	if not selectie:
		return "Seturile mele", None, None

	df = get_dataset_from_storage(selectie.url)
	# sursa = get_sursa_by_id_set_date_brut(selectie.id)
	return "Seturile mele", df, selectie


def handle_seturi_procesate():
	seturi = get_seturi_date_procesate(st.session_state.id_utilizator)
	if not seturi:
		st.info("Nu ai niciun set de date procesat. Încearcă să alegi unul brut.")
		return "Seturile mele procesate", None, None

	selectie = st.selectbox("📁 Alege un set de date procesat", options=seturi, format_func=lambda s: s.denumire)
	if not selectie:
		return "Seturile mele procesate", None, None

	df = get_dataset_from_storage(selectie.url)
	# sursa = get_sursa_by_id_set_date_procesat(selectie.id)
	return "Seturile mele procesate", df, selectie


def afisare_set_date(df: pd.DataFrame):
	st.header("Setul de date selectat")
	st.dataframe(df.head(), hide_index=True, use_container_width=True)


def extragere_coloane_binare(df: pd.DataFrame) -> list[str]:
	return [col for col in df.columns if df[col].nunique(dropna=False) == 2]


def obtinere_tinta_implicita(sursa: str, selectie=None) -> str | None:
	if sursa in ["Seturi predefinite", "Seturile mele"]:
		return selectie.tinta
	elif sursa == "Seturile mele procesate":
		return get_tinta_by_id_set_date_procesat(selectie.id)
	return None


def selectie_denumire_si_tinta(df: pd.DataFrame, sursa: str, selectie) -> tuple[str, str]:
	col1, col2 = st.columns(2)
	disabled = sursa in ["Seturi predefinite", "Seturile mele procesate"]

	with col1:
		denumire = st.text_input(
			"📄 Denumirea setului de date",
			value=getattr(selectie, "denumire", None),
			disabled=disabled,
		)

	with col2:
		coloane_binare = extragere_coloane_binare(df)
		if not coloane_binare:
			st.error("Nicio coloană binară disponibilă.")
			tinta = None
		else:
			tinta_implicita = obtinere_tinta_implicita(sursa, selectie)
			index = coloane_binare.index(tinta_implicita) if tinta_implicita in coloane_binare else 0
			tinta = st.selectbox(
				"🎯 Selectează variabila țintă (binară)",
				coloane_binare,
				index=index,
				disabled=disabled,
			)

	return denumire, tinta


def validare_selectie(denumire: str, tinta: str, sursa: str) -> bool:
	if not tinta:
		st.error("Selectează o variabilă țintă validă.")
		return False
	if not denumire:
		st.error("Introdu denumirea setului de date.")
		return False
	if sursa in ["Fișier local", "Link Kaggle"] and check_denumire_set_date_brut(
		st.session_state.id_utilizator, denumire
	):
		st.error("Un set de date cu această denumire există deja.")
		return False
	return True


def actualizare_bd(df, id, denumire, tinta, sursa, selectie):
	if id is None:
		st.session_state.id_set_date = create_set_date_brut(st.session_state.id_utilizator, sursa, denumire, tinta, df)
		st.toast("Setul de date a fost încărcat în baza de date", icon="✅")
	else:
		if selectie.denumire != denumire or selectie.tinta != tinta:
			rezultat, mesaj = update_set_date_brut(
				st.session_state.id_utilizator, selectie.id, denumire=denumire, tinta=tinta
			)
			st.toast(mesaj, icon="✅" if rezultat else "❌")
		st.session_state.id_set_date = selectie.id


def selectie_set_date():
	df, sursa = None, None

	handler_map = {
		"Fișier local": handle_fisier_local,
		"Link Kaggle": handle_kaggle,
		"Seturi predefinite": handle_predefinite,
		"Seturile mele": handle_seturi_brute,
		"Seturile mele procesate": handle_seturi_procesate,
	}

	optiune = st.selectbox("🌱 Alege sursa setului de date", handler_map.keys())

	handler = handler_map.get(optiune)

	if handler:
		sursa, df, selectie = handler()

	return sursa, df, selectie


def procesare_selectie_set_date(sursa, df, selectie=None):
	afisare_set_date(df)
	id = getattr(selectie, "id", None)
	denumire, tinta = selectie_denumire_si_tinta(df, sursa, selectie)

	if st.button("Confirmă selecția", type="primary", use_container_width=True):
		if not validare_selectie(denumire, tinta, sursa):
			return

		setare_cheie("set_date", {"denumire": denumire, "sursa": sursa, "tinta": tinta})

		actualizare_bd(df, id, denumire, tinta, sursa, selectie)

		if sursa != "Seturi predefinite":
			salvare_date_temp(df, denumire)

		initializare_cheie("metadate", generare_metadate(df))
		setare_flag("selected_dataset")
		st.toast("Setul de date este gata de utilizare", icon="✅")


def afisare_date():
	set_date: dict = st.session_state.get("set_date", {})

	with st.container(border=True):
		st.header(":green-background[Informații generale]")

		st.markdown(
			f"""
			Denumirea setului de date: `{set_date.get("denumire", "N/A")}`

			Sursa datelor: `{set_date.get("sursa", "N/A")}`

			Variabila țintă: `{set_date.get("tinta", "N/A")}`
			"""
		)

	with st.container(border=True):
		st.header(":blue-background[Primele înregistrări]")
		df = citire_set_date(set_date)
		st.dataframe(df.head(), hide_index=True, use_container_width=True)


@require_auth
def main():
	if not st.session_state.set_date:
		sursa, df, selectie = selectie_set_date()

		if df is not None:
			procesare_selectie_set_date(sursa, df, selectie)

	else:
		afisare_date()


if __name__ == "__main__":
	main()

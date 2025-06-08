import streamlit as st

from database import (
	citire_dataset_supabase,
	creare_set_date,
	get_id_utilizator,
	get_seturi_date_utilizator,
	incarcare_dataset_supabase,
	modificare_set_date,
	verificare_denumire_set_date,
)
from dataset import (
	citire_date_predefinite,
	citire_fisier_local,
	descarcare_kaggle,
	generare_metadate_json,
	salvare_date_temp,
)
from utils import nav_bar


st.set_page_config(layout="wide", page_title="FlagML | Set de date", page_icon="assets/logo.png")
st.title("Alegerea setului de date")
nav_bar()

st.session_state.setdefault("set_date", {})
st.session_state.setdefault("set_existent", False)

df = None
sursa = None
denumire = None
tinta = None
st.session_state.setdefault("id_utilizator", get_id_utilizator(st.user.sub))

sursa = st.selectbox(
	"📂 Alege sursa setului de date", ["Fișier local", "Link Kaggle", "Seturi predefinite", "Seturile mele"]
)

if sursa == "Fișier local":
	df = citire_fisier_local()
	denumire = st.text_input("📄 Denumirea setului de date", key="denumire_local")
	st.session_state.set_existent = False

elif sursa == "Link Kaggle":
	link = st.text_input("🔗 Link Kaggle")
	if link:
		df = descarcare_kaggle(link)
	denumire = st.text_input("📄 Denumirea setului de date", key="denumire_kaggle")
	st.session_state.set_existent = False

elif sursa == "Seturi predefinite":
	set_predefinit = st.selectbox("📁 Alege un set predefinit", ["MLG-ULB", "VESTA"])
	df = citire_date_predefinite(set_predefinit)
	denumire = set_predefinit
	st.session_state.set_existent = False

elif sursa == "Seturile mele":
	seturi = get_seturi_date_utilizator(st.session_state.id_utilizator)
	if not seturi:
		st.info("Nu ai încărcat niciun set de date.")
	else:
		selectie = st.selectbox("📁 Alege un set de date existent", options=seturi, format_func=lambda s: s.denumire)
		if selectie:
			df = citire_dataset_supabase(selectie.url)
			denumire = st.text_input(
				"📄 Denumirea setului de date", value=selectie.denumire, key="denumire_seturile_mele"
			)
			sursa = selectie.sursa
			st.session_state.set_existent = True

if df is not None:
	st.header(f"📊 {denumire}")
	st.dataframe(df.head())

	memorie = df.memory_usage(deep=True).sum() / (1024 * 1024)
	st.metric("Dimensiune", f"{memorie:.2f} MB")

	st.subheader("🎯 Selectează variabila țintă (binară)")
	coloane_binare = [col for col in df.columns if df[col].nunique(dropna=False) == 2]

	if coloane_binare:
		if sursa == "Seturi predefinite":
			default_index = coloane_binare.index("isFraud")
		elif st.session_state.set_existent:
			default_index = coloane_binare.index(selectie.tinta) if selectie.tinta in coloane_binare else 0
		else:
			default_index = 0

		tinta = st.selectbox("Variabilă țintă", coloane_binare, index=default_index)
	else:
		st.error("Nicio coloană binară disponibilă.")
		tinta = None

	if st.button("Confirmă selecția"):
		if tinta is None:
			st.error("Selectează o variabilă țintă validă.")
		elif not denumire:
			st.error("Introdu denumirea setului de date.")
		elif not st.session_state.set_existent and verificare_denumire_set_date(
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
				cale_dataset = incarcare_dataset_supabase(df, st.session_state.id_utilizator, denumire)
				st.toast("Setul de date a fost încărcat în baza de date", icon="✅")
				id_set_date = creare_set_date(st.session_state.id_utilizator, denumire, sursa, cale_dataset, tinta)
			elif st.session_state.set_existent:
				if selectie.denumire != denumire or selectie.tinta != tinta:
					rezultat, mesaj = modificare_set_date(
						st.session_state.id_utilizator, selectie.id, denumire=denumire, tinta=tinta
					)
					st.toast(mesaj, icon="✅" if rezultat else "❌")

			if sursa != "Seturi predefinite":
				salvare_date_temp(df, denumire)
			generare_metadate_json(df)
			st.session_state.get("pagini").update({2: True, 3: True})
			st.toast("Setul de date este gata de utilizare", icon="✅")
			# st.rerun()

else:
	st.warning("Niciun set de date încărcat.")

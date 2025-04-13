import pandas as pd
import streamlit as st

from utils import citire_date_predefinite, descarcare_kaggle, nav_bar, salvare_date_temp


st.set_page_config(layout="wide", page_title="Set de date", page_icon="💳")
st.title("Alegerea setului de date")
nav_bar()

optiuni_dataset = ["MLG-ULB", "VESTA"]

st.header("Sursa datelor")
sursa = st.radio(
	"Alege sursa pentru încărcarea setului de date",
	["Fișier local", "Link Kaggle", "Seturi de date predefinite"],
)

df: pd.DataFrame = None

if sursa == "Seturi de date predefinite":
	set_date_predefinit = st.selectbox(
		"Alege un set de date",
		optiuni_dataset,
		index=0
	)
	df = citire_date_predefinite(set_date_predefinit)
	st.session_state.nume_dataset = set_date_predefinit
	st.session_state.sursa_date = "predefinit"

elif sursa == "Link Kaggle":
	link = st.text_input("Introdu linkul către fișierul de pe Kaggle")
	if link:
		df, nume_dataset = descarcare_kaggle(link)
		st.session_state.nume_dataset = nume_dataset
		st.session_state.sursa_date = "kaggle"

elif sursa == "Fișier local":
	fisier = st.file_uploader("Încarcă un fișier", type=["csv", "excel"])
	if fisier is not None:
		df = pd.read_csv(fisier)
		st.session_state.nume_dataset = fisier.name
		st.session_state.sursa_date = "local"

if df is not None:
	st.header(f"📑 {st.session_state.nume_dataset}")
	st.dataframe(df.head())

	memorie_totala_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
	st.metric(label="**📂 Memorie ocupată de DataFrame**", value=f"{memorie_totala_mb:.2f} MB")

	st.subheader("Selectează variabila țintă")
	tinta = st.selectbox("Alege coloana țintă", df.columns)
	# daca avem seturile de baza, variabila selectata este isFraud

	if df[tinta].nunique() > 2:
		st.error("Variabila țintă trebuie să fie binară (doar 2 valori unice).")
	else:
		st.success(f"Variabila țintă selectată: `{tinta}` (valori: {df[tinta].unique().tolist()})")
		st.session_state.tinta = tinta

	if st.session_state.sursa_date != "predefinit":
		salvare_date_temp(df, st.session_state.nume_dataset)
		st.success("Datele au fost salvate.")

else:
	st.warning("Setul de date nu a fost încărcat sau este invalid.")

# verificare sa avem mai mult de 1 coloana (gen sa fie aia binara si minim alta)

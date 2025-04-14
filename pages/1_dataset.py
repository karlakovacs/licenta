import pandas as pd
import streamlit as st

from database import citire_dataset_supabase, creare_set_date, get_seturi_date_utilizator, incarcare_dataset_supabase
from utils import citire_date_predefinite, descarcare_kaggle, nav_bar, salvare_date_temp


st.set_page_config(layout="wide", page_title="Set de date", page_icon="💳")
st.title("Alegerea setului de date")
nav_bar()

st.session_state.setdefault("set_date", {})

optiuni_sursa = ["Fișier local", "Link Kaggle", "Seturi de date predefinite", "Seturile mele"]
sursa_dataset = st.segmented_control(
	"Alege sursa pentru încărcarea setului de date", optiuni_sursa, selection_mode="single"
)

df: pd.DataFrame = None

if sursa_dataset == "Fișier local":
	fisier = st.file_uploader("Încarcă un fișier", type=["csv", "xlsx"])
	if fisier is not None:
		if fisier.name.endswith(".csv"):
			df = pd.read_csv(fisier)
		elif fisier.name.endswith(".xlsx"):
			df = pd.read_excel(fisier)
		else:
			st.error("Format de fișier necunoscut!")

		st.session_state.set_date["denumire"] = fisier.name.rsplit(".", 1)[0]
		st.session_state.set_date["sursa"] = "local"

elif sursa_dataset == "Link Kaggle":
	link = st.text_input("Introdu linkul către fișierul de pe Kaggle")
	if link:
		df, denumire_dataset = descarcare_kaggle(link)
		st.session_state.set_date["denumire"] = denumire_dataset
		st.session_state.set_date["sursa"] = "kaggle"

elif sursa_dataset == "Seturi de date predefinite":
	optiuni_dataset = ["MLG-ULB", "VESTA"]
	set_date_predefinit = st.selectbox("Alege un set de date", optiuni_dataset, index=0)
	df = citire_date_predefinite(set_date_predefinit)
	st.session_state.set_date["denumire"] = set_date_predefinit
	st.session_state.set_date["sursa"] = "predefinit"

elif sursa_dataset == "Seturile mele":
	seturi_date = get_seturi_date_utilizator(st.session_state.id_utilizator)

	df_seturi_date = pd.DataFrame(
		[
			{
				"ID": s.id,
				"Denumire": s.denumire,
				"Sursa": s.sursa,
				"Creat la": s.data_creare,
				"URL": s.url,
			}
			for s in seturi_date
		]
	)

	df_seturi_date["Selectează"] = False

	df_vizual = df_seturi_date[["Selectează", "Denumire", "Sursa", "Creat la"]].copy()

	edited_df = st.data_editor(
		df_vizual,
		use_container_width=False,
		num_rows="fixed",
		hide_index=True,
		key="editor_seturi",
		column_config={"Selectează": st.column_config.CheckboxColumn("Selectează")},
		disabled=["Denumire", "Sursa", "Creat la"],
	)

	selectie = edited_df[edited_df["Selectează"] == True]

	if len(selectie) > 1:
		st.warning("Te rog selectează un singur set de date.")
	elif len(selectie) == 1:
		set_date_selectat = df_seturi_date[
			(df_seturi_date["Denumire"] == selectie.iloc[0]["Denumire"])
			& (df_seturi_date["Creat la"] == selectie.iloc[0]["Creat la"])
		].iloc[0]

		df = citire_dataset_supabase(set_date_selectat["URL"])
		st.session_state.set_date["denumire"] = set_date_selectat["Denumire"]
		st.session_state.set_date["sursa"] = "seturile_mele"
		st.session_state.set_date["id"] = set_date_selectat["ID"]

if df is not None:
	st.header(f"📑 {st.session_state.set_date['denumire']}")
	st.dataframe(df.head())

	memorie_totala_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
	st.metric(label="**📂 Memorie ocupată de DataFrame**", value=f"{memorie_totala_mb:.2f} MB")

	st.subheader("Selectează variabila țintă")
	coloane = df.columns.tolist()
	tinta = st.selectbox(
		"Alege coloana țintă",
		coloane,
		index=coloane.index("isFraud") if st.session_state.set_date["sursa"] == "predefinit" else None,
	)

	if df[tinta].nunique() > 2:
		st.error("Variabila țintă trebuie să fie binară (doar 2 valori unice).")
		st.session_state.set_date["tinta"] = None
	else:
		st.success(f"Variabila țintă selectată: `{tinta}` (valori: {df[tinta].unique().tolist()})")
		st.session_state.set_date["tinta"] = tinta

	if st.session_state.set_date["sursa"] not in ["predefinit", "seturile_mele"]:
		cale_dataset = incarcare_dataset_supabase(
			df, st.session_state.id_utilizator, st.session_state.set_date["denumire"]
		)
		id_set_date = creare_set_date(
			st.session_state.id_utilizator,
			st.session_state.set_date["denumire"],
			st.session_state.set_date["sursa"],
			cale_dataset,
		)
		st.session_state.set_date["id"] = id_set_date

		salvare_date_temp(df, st.session_state.set_date["denumire"])
		st.success("Datele au fost salvate.")

else:
	st.warning("Setul de date nu a fost încărcat sau este invalid.")

# verificare sa avem mai mult de 1 coloana (gen sa fie aia binara si minim alta)

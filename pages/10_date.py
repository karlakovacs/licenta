import pandas as pd
import streamlit as st
from supabase import create_client

from database import (
	citire_sample_dataset_supabase,
	get_rapoarte_utilizator,
	get_seturi_date_utilizator,
	stergere_raport,
	stergere_set_date,
)
from utils import nav_bar


st.set_page_config(layout="wide", page_title="Datele mele", page_icon="📑")
nav_bar()

st.title("Datele mele")

st.header("Profilul meu")
st.markdown(
	f'<img src="{st.user.picture}" width="100" style="border-radius: 50%;">',
	unsafe_allow_html=True,
)
st.write(st.user.name)
st.write(st.user.email)
if st.button("Deconectare", type="primary"):
	st.session_state.clear()
	st.logout()

SUPABASE_URL = st.secrets.supabase.SUPABASE_URL
SUPABASE_KEY = st.secrets.supabase.SUPABASE_KEY
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_RAPOARTE = "reports"
BUCKET_DATASETS = "datasets"
id_utilizator = st.session_state.id_utilizator

st.header("📊 Seturile mele de date")
seturi_date = get_seturi_date_utilizator(id_utilizator)

if not seturi_date:
	st.info("Nu ai seturi de date încărcate.")
else:
	for set_date in seturi_date:
		with st.expander(f"📁 {set_date.denumire}"):
			st.markdown(f"- **Sursa**: {set_date.sursa}")
			st.markdown(f"- **Ținta**: `{set_date.tinta}`")
			st.markdown(f"- **Data creării**: {set_date.data_creare.strftime('%Y-%m-%d %H:%M')}")
			df: pd.DataFrame = citire_sample_dataset_supabase(set_date.url)
			st.dataframe(df)

			if st.button(f"🗑️ Ștergere", type="primary", key=f"stergere_set_{set_date.id}"):
				stergere_set_date(id_utilizator, set_date.id)
				st.success(f"Setul `{set_date.denumire}` a fost șters.")
				st.rerun()

			# if st.button("📥 Descarcă", type="primary", key=f"descarcare_set_{set_data.id}"):
			# 	pass

st.divider()

st.header("📄 Rapoartele mele")
rapoarte = get_rapoarte_utilizator(id_utilizator)

if not rapoarte:
	st.info("Nu ai generat niciun raport.")
else:
	for raport in rapoarte:
		base_path = raport.url
		html_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_RAPOARTE}/{base_path}/raport_{base_path.split('/')[-1]}.html"
		pdf_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_RAPOARTE}/{base_path}/raport_{base_path.split('/')[-1]}.pdf"

		with st.expander(f"📝 Raport generat pe {raport.data_generare.strftime('%Y-%m-%d %H:%M')}"):
			st.markdown(f"[🌐 Descarcă HTML]({html_url})", unsafe_allow_html=True)
			st.markdown(f"[📄 Descarcă PDF]({pdf_url})", unsafe_allow_html=True)

			if st.button(f"🗑️ Ștergere", type="primary", key=f"stergere_raport_{raport.id}"):
				folder_prefix = base_path + "/"
				files = supabase.storage.from_(BUCKET_RAPOARTE).list(folder_prefix)
				for file in files:
					supabase.storage.from_(BUCKET_RAPOARTE).remove(f"{folder_prefix}{file['name']}")

				stergere_raport(id_utilizator, raport.id)
				st.success("Raportul a fost șters.")
				st.rerun()

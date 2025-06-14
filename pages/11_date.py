import streamlit as st

from database import *
from storage import *
from ui import nav_bar


st.set_page_config(layout="wide", page_title="FlagML | Datele mele", page_icon="assets/logo.png")
nav_bar()
st.session_state.setdefault("id_utilizator", get_id_utilizator(st.user.sub))
id_utilizator = st.session_state.get("id_utilizator", "")

st.title("Datele mele")

st.header("Profilul meu")
st.markdown(
	f'<img src="{st.user.picture}" width="100" style="border-radius: 50%;">',
	unsafe_allow_html=True,
)
st.write(st.user.email)
if st.button("Deconectare", type="primary"):
	st.session_state.clear()
	st.logout()

st.divider()

st.header("📊 Seturile mele de date")
seturi_date = get_seturi_date_brute(id_utilizator)

if not seturi_date:
	st.info("Nu ai seturi de date încărcate.")
else:
	for set_date in seturi_date:
		with st.expander(f"📁 {set_date.denumire}"):
			st.markdown(f"- **Sursa**: {set_date.sursa_date.denumire}")
			st.markdown(f"- **Ținta**: `{set_date.tinta}`")
			st.markdown(f"- **Data creării**: {set_date.data_creare.strftime('%Y-%m-%d %H:%M')}")
			df: pd.DataFrame = get_dataset_sample_from_storage(set_date.url)
			st.dataframe(df)

			st.download_button(
				"💾 Descarcă",
				type="primary",
				key=f"descarcare_set_{set_date.id}",
				data=get_dataset_from_storage(set_date.url).to_csv(index=False),
				file_name=f"{set_date.denumire}.csv",
				mime="text/csv",
			)

			if st.button(f"🗑️ Șterge", type="primary", key=f"stergere_set_{set_date.id}"):
				rezultat, mesaj = delete_set_date_brut(id_utilizator, set_date.id)
				st.toast(mesaj, icon="✅" if rezultat else "❌")
				st.rerun()

			st.header("Seturi de date procesate")
			seturi_date_procesate = get_seturi_date_procesate(set_date.id)
			for set_date_procesat in seturi_date_procesate:
				st.write(set_date_procesat.id, set_date_procesat.denumire, set_date_procesat.configuratie)
				date_modele = get_modele(set_date_procesat.id)
				df_modele = pd.DataFrame(date_modele)
				st.dataframe(df_modele)
				
				rapoarte = get_rapoarte(set_date_procesat.id)
				for raport in rapoarte:
					st.write(raport.id, raport.data_generare)

st.divider()

st.header("📄 Rapoartele mele")
rapoarte = get_rapoarte(id_utilizator)

if not rapoarte:
	st.info("Nu ai generat niciun raport.")
else:
	for raport in rapoarte:
		with st.expander(f"📝 Raport generat pe {raport.data_generare.strftime('%Y-%m-%d %H:%M')}"):
			html_url, pdf_url = get_report_urls_from_storage(raport)
			st.markdown(f"[🌐 Descarcă HTML]({html_url})", unsafe_allow_html=True)
			st.markdown(f"[📄 Vizualizează PDF]({pdf_url})", unsafe_allow_html=True)

			if st.button(f"🗑️ Ștergere", type="primary", key=f"stergere_raport_{raport.id}"):
				respuns_storage, mesaj_storage = delete_reports_from_storage(id_utilizator, raport.id)
				if respuns_storage:
					respuns_db, mesaj_db = delete_raport(raport.id)
					st.toast(mesaj_db)
					st.rerun()

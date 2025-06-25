import streamlit as st

from database import *
from storage import *
from ui import *


initializare_pagina("Datele mele", "wide", "Datele mele")


def afisare_set_date_brut(id_utilizator: int, set_date):
	st.header(f"Set brut - `{set_date.denumire}`")
	st.markdown(
		f"""
		- **Sursa**: `{set_date.sursa_date.denumire}`\n
		- **Ținta**: `{set_date.tinta}`\n
		- **Data creării**: `{set_date.data_creare.strftime("%Y-%m-%d %H:%M")}`
	"""
	)

	df: pd.DataFrame = get_dataset_sample_from_storage(set_date.url)
	st.dataframe(df)

	st.download_button(
		"💾 Descarcă",
		type="primary",
		key=f"descarcare_set_brut_{set_date.id}",
		data=get_dataset_from_storage(set_date.url).to_csv(index=False),
		file_name=f"{set_date.denumire}.csv",
		mime="text/csv",
	)

	if st.button(f"🗑️ Șterge", type="primary", key=f"stergere_set_brut_{set_date.id}"):
		succes, mesaj = delete_set_date_brut(id_utilizator, set_date.id)
		st.toast(mesaj, icon="✅" if succes else "❌")
		st.rerun()

	afisare_seturi_date_procesate(set_date)


def afisare_seturi_date_procesate(set_date):
	seturi_date_procesate = get_seturi_date_procesate(set_date.id)

	if seturi_date_procesate:
		st.divider()

		for set_date_procesat in seturi_date_procesate:
			afisare_set_date_procesat(set_date_procesat)


def afisare_set_date_procesat(set_date_procesat):
	st.subheader(f"Set procesat - `{set_date_procesat.denumire}`")
	st.write("**Configurație**")
	st.json(set_date_procesat.configuratie, expanded=False)

	st.download_button(
		"💾 Descarcă",
		type="primary",
		key=f"descarcare_set_procesat_{set_date_procesat.id}",
		data=get_dataset_from_storage(set_date_procesat.url).to_csv(index=False),
		file_name=f"{set_date_procesat.denumire}.csv",
		mime="text/csv",
	)

	if st.button(f"🗑️ Șterge", type="primary", key=f"stergere_set_procesat_{set_date_procesat.id}"):
		succes, mesaj = delete_set_date_procesat(set_date_procesat.id)
		st.toast(mesaj, icon="✅" if succes else "❌")
		st.rerun()

	afisare_modele_ml(set_date_procesat)

	st.divider()


def afisare_modele_ml(set_date_procesat):
	st.markdown("**🧠 Modele ML:**")
	date_modele = get_modele(set_date_procesat.id)
	if date_modele:
		df_modele = pd.DataFrame(date_modele)
		st.dataframe(
			df_modele,
			column_config={
				"URL": st.column_config.LinkColumn("URL", display_text="Descarcă 📥"),
				"Hiperparametri": st.column_config.JsonColumn("Hiperparametri", width="large"),
			},
			hide_index=True,
		)
	else:
		st.info("Nu există modele ML pentru acest set procesat.")


def afisare_rapoarte(rapoarte: list):
	for raport in rapoarte:
		with st.expander(f"Raport generat pe {raport.data_generare.strftime('%Y-%m-%d %H:%M')}"):
			html_url = get_report_url_from_storage(raport)
			st.markdown(f"[🌐 Descarcă HTML]({html_url})", unsafe_allow_html=True)

			if st.button(f"🗑️ Șterge", type="primary", key=f"stergere_raport_{raport.id}"):
				succes, mesaj = delete_raport(st.session_state.id_utilizator, raport.id)
				st.toast(mesaj, icon="✅" if succes else "❌")
				if succes:
					st.rerun()


@require_auth
def main():
	id_utilizator = obtinere_cheie("id_utilizator")
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

	st.header("Seturile mele de date")
	seturi_date = get_seturi_date_brute(id_utilizator)

	if not seturi_date:
		st.info("Nu ai seturi de date încărcate.")
	else:
		for set_date in seturi_date:
			with st.expander(f"📁 {set_date.denumire}"):
				afisare_set_date_brut(st.session_state.id_utilizator, set_date)

	st.divider()

	st.header("📄 Rapoartele mele")
	rapoarte = get_rapoarte(id_utilizator)

	if not rapoarte:
		st.info("Nu ai generat niciun raport.")
	else:
		afisare_rapoarte(rapoarte)


if __name__ == "__main__":
	main()

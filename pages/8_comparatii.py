import streamlit as st

from database import get_id_utilizator
from ml import creare_df_metrici, grafic_comparativ
from ui import nav_bar


st.set_page_config(layout="wide", page_title="FlagML | Comparații", page_icon="assets/logo.png")
nav_bar()
st.session_state.setdefault("id_utilizator", get_id_utilizator(st.user.sub))

st.title("Compararea performanței modelelor")


rezultate_modele = st.session_state.get("rezultate_modele", None)

if rezultate_modele is None:
	st.warning("Antrenează modelele și vizualizează rezultatele mai întâi.")
else:
	del st.session_state.grafic_comparativ
	if "grafic_comparativ" not in st.session_state:
		st.session_state.df_metrici = creare_df_metrici(rezultate_modele)
		st.session_state.grafic_comparativ = grafic_comparativ(st.session_state.df_metrici)

	st.dataframe(st.session_state.df_metrici)
	st.plotly_chart(st.session_state.grafic_comparativ, use_container_width=False)

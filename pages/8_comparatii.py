import streamlit as st

from utils import creare_df_metrici, grafic_comparativ, nav_bar


st.set_page_config(layout="wide", page_title="Comparații", page_icon="⚖️")
nav_bar()
st.title("Compararea performanței modelelor")


rezultate_modele = st.session_state.get("rezultate_modele", None)

if rezultate_modele is None:
	st.warning("Antrenează modelele și vizualizează rezultatele mai întâi.")
else:
	if "grafic_comparativ" not in st.session_state:
		df_metrici = creare_df_metrici(rezultate_modele)
		st.session_state.grafic_comparativ = grafic_comparativ(df_metrici)
	st.plotly_chart(st.session_state.grafic_comparativ, use_container_width=False)

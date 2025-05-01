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

# from utils import citire_date_temp
# import pandas as pd
# X_train: pd.DataFrame = citire_date_temp("X_train")
# st.dataframe(X_train)
# # st.write(X_train.info())
# info_df = pd.DataFrame({"Coloană": X_train.columns, "Tip de date": [X_train[col].dtype for col in X_train.columns]})

# st.dataframe(info_df)

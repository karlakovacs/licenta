import time

import streamlit as st
import streamlit.components.v1 as components

from database import *
from utils import *
from xai import *


st.set_page_config(layout="wide", page_title="XAI", page_icon="💡")
nav_bar()
st.title("Explainable AI")

modele_antrenate = st.session_state.modele_antrenate
X_train, X_test, y_test = (
	citire_date_temp("X_train"),
	citire_date_temp("X_test"),
	citire_date_temp("y_test"),
)

for key in ["bar", "waterfall", "violin", "lime"]:
	st.session_state.setdefault(key, {})

tabs = st.tabs([f"💡 {key}" for key in modele_antrenate])
for tab, (key, model) in zip(tabs, modele_antrenate.items()):
	with tab:
		st.header(key)

		shap_results = None
		shap_results = model.get_shap_values(X_train, X_test)

		if shap_results is not None:
			st.subheader("SHAP Bar Plot")
			if key not in st.session_state.bar:
				bar_plot(shap_results, key)
				time.sleep(5)
			st.pyplot(st.session_state.bar[key], use_container_width=False)

			st.subheader("SHAP Waterfall Plot")
			if key not in st.session_state.waterfall:
				waterfall_plot(shap_results, key)
				time.sleep(5)
			st.pyplot(st.session_state.waterfall[key], use_container_width=False)

			st.subheader("SHAP Violin Plot")
			if key not in st.session_state.violin:
				violin_plot(shap_results, key)
				time.sleep(5)
			st.pyplot(st.session_state.violin[key], use_container_width=False)

		lime_results = None
		lime_results = get_explanation(model, X_train, X_test)

		if lime_results is not None:
			st.subheader("LIME Plot")
			if key not in st.session_state.lime:
				explanation_plot(lime_results, key)
				time.sleep(5)
			components.html(st.session_state.lime[key], height=600)

# if "incarcat_xai" not in st.session_state:
# 	id_rulari = st.session_state.id_rulari

# 	for key in id_rulari.keys():
# 		file_path = incarcare_grafic_plt_supabase(st.session_state.bar[key], "png")
# 		creare_grafic(id_rulari[key], "SHAP Bar", file_path)

# 		file_path = incarcare_grafic_plt_supabase(st.session_state.waterfall[key])
# 		creare_grafic(id_rulari[key], "SHAP Waterfall", file_path)

# 		file_path = incarcare_grafic_plt_supabase(st.session_state.violin[key])
# 		creare_grafic(id_rulari[key], "SHAP Violin", file_path)

# 		file_path = incarcare_grafic_html_supabase(st.session_state.lime[key])
# 		creare_grafic(id_rulari[key], "LIME", file_path)

# 	st.session_state.incarcat_xai = True

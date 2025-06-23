import pandas as pd
import streamlit as st

from ui import *


initializare_pagina("Documentație", "wide", "Documentație")


@require_auth
def main():
	st.write("Aici puteți citi documentația aplicației.")

	data_df = pd.DataFrame(
		{
			"apps": [
				"https://roadmap.streamlit.app",
				"https://extras.streamlit.app",
				"https://issues.streamlit.app",
				"https://30days.streamlit.app",
			],
			"creator": [
				"https://github.com/streamlit",
				"https://github.com/arnaudmiribel",
				"https://github.com/streamlit",
				"https://github.com/streamlit",
			],
		}
	)

	st.data_editor(
		data_df,
		column_config={
			"apps": st.column_config.LinkColumn(
				"Trending apps",
				help="The top trending Streamlit apps",
				validate=r"^https://[a-z]+\.streamlit\.app$",
				max_chars=100,
				display_text=r"https://(.*?)\.streamlit\.app",
			),
			"creator": st.column_config.LinkColumn("App Creator", display_text="Open profile"),
		},
		hide_index=True,
		use_container_width=False,
	)

	st.markdown("""
	### 📊 Rezultate model

	| Model | Acuratețe | F1 Score |
	|------------------|-----------|----------|
	| **Random Forest**     | 0.94      | 0.92     |
	| XGBoost           | 0.96      | 0.95     |
	""")


if __name__ == "__main__":
	main()

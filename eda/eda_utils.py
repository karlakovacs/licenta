import pandas as pd
import streamlit as st


def afisare_ploturi_grid(df: pd.DataFrame, functie_plot, coloane_rand: int = 4, is_grid=True, **kwargs):
	# df ul cuprinde doar 
	variabile = df.columns
	numar_ploturi = len(variabile)
	randuri = (numar_ploturi // coloane_rand) + (1 if numar_ploturi % coloane_rand != 0 else 0)

	for i in range(randuri):
		coloane = st.columns(coloane_rand)
		for j in range(coloane_rand):
			idx = i * coloane_rand + j
			if idx < numar_ploturi:
				variabila = variabile[idx]
				with coloane[j]:
					functie_plot(df[variabila], is_grid=is_grid, **kwargs)

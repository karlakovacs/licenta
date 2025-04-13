### USAGE


# st.set_page_config(page_title="Aplicație", layout="wide")
# st.title("EDA si procesare")

# st.header("Încărcare fișier")
# uploaded_file = st.file_uploader("Încarcă un fișier CSV", type=["csv"], accept_multiple_files=False)

# if uploaded_file is not None:
# 	df = pd.read_csv(uploaded_file)
# 	tabs = st.tabs(["Vizualizare dataset", "Valori lipsa", "Variabile numerice", "Variabile categoriale", "Outliers"])

# 	with tabs[0]:
# 		st.dataframe(df.head())

# 	with tabs[1]:
# 		st.header("Valori lipsa")
# 		plot_valori_lipsa(df)

# 	with tabs[2]:
# 		st.header("Histograme pentru variabile numerice")
# 		plot_histograme(df)

# 	with tabs[3]:
# 		st.header("Pie charts pentru variabile categoriale")
# 		afisare_nunique(df)
# 		plot_variabile_categoriale(df)

# 	with tabs[4]:
# 		st.header("Analiza outliers")
# 		afisare_outliers_data(df)
# 		plot_boxplots(df)

import pandas as pd
import streamlit as st
from streamlit_sortables import sort_items


st.title("🔧 Prelucrare automată a datelor")

TIPURI_NUMERICE = ["int64", "float64"]
TIPURI_CATEGORIALE = ["object", "bool", "category"]

# Upload file
uploaded_file = st.file_uploader("Încarcă un fișier CSV", type=["csv"])
if uploaded_file:
	df = pd.read_csv(uploaded_file)
	st.dataframe(df.head())

	st.selectbox(
		"Alege o coloană",
		options=df.columns,
		help="**Alege coloana** care conține valori de tip `datetime`.\n\nExemplu format: `%Y-%m-%d %H:%M:%S`\n\nMai multe [formate aici](https://strftime.org/)",
	)

	with st.expander("🕒 Procesare coloane datetime"):
		candidate_cols = df.select_dtypes(include="object").columns.tolist()
		col_datetime = st.selectbox("Alege o coloană de tip datetime", candidate_cols)

		if col_datetime:
			datetime_format = st.text_input(
				"Formatul datetime (ex: `%Y-%m-%d %H:%M:%S`, `%d/%m/%Y`, etc.)",
				value="%Y-%m-%d",
				help="Folosește formatul strftime. Exemple: %Y-%m-%d, %d/%m/%Y %H:%M",
			)

			try:
				df[col_datetime] = pd.to_datetime(df[col_datetime], format=datetime_format)
				st.success("✅ Conversie reușită!")

				componente = st.multiselect(
					"Ce componente vrei să extragi?",
					["an", "luna", "zi", "zi_sapt", "este_weekend", "ora", "minute"],
					default=["an", "luna", "zi"],
				)

				if "an" in componente:
					df[f"{col_datetime}_an"] = df[col_datetime].dt.year
				if "luna" in componente:
					df[f"{col_datetime}_luna"] = df[col_datetime].dt.month
				if "zi" in componente:
					df[f"{col_datetime}_zi"] = df[col_datetime].dt.day
				if "zi_sapt" in componente:
					df[f"{col_datetime}_zi_sapt"] = df[col_datetime].dt.weekday
				if "este_weekend" in componente:
					df[f"{col_datetime}_este_weekend"] = df[col_datetime].dt.weekday >= 5
				if "ora" in componente:
					df[f"{col_datetime}_ora"] = df[col_datetime].dt.hour
				if "minute" in componente:
					df[f"{col_datetime}_minute"] = df[col_datetime].dt.minute

			except Exception as e:
				st.error(f"Eroare la conversie: {e}")

	# with st.expander("🔢 1. Transformare coloane categorice"):
	# 	col_obj = df.select_dtypes(include="object").columns.tolist()
	# 	col_select = st.multiselect("Coloane de transformat în categorice", col_obj)
	# 	limita = st.slider("Limită valori categorice (grup restul ca OTHER)", min_value=2, max_value=20, value=10)

	# 	for col in col_select:
	# 		top_vals = df[col].value_counts().nlargest(limita).index
	# 		df[col] = df[col].apply(lambda x: x if x in top_vals else "OTHER")
	# 		df[col] = df[col].astype("category")
	# 	st.success("Coloane convertite și valori rare grupate în 'OTHER'.")

	with st.expander("🧼 2. Înlocuire valori lipsă"):
		st.markdown("**Alege cum vrei să completezi valorile lipsă:**")
		mod_completare = st.radio(
			"Mod de completare",
			["Automat pe tipuri", "Individual (pe fiecare coloană)"],
			help="fgfgteghte",
			horizontal=True,
		)

		numerice = df.select_dtypes(include=TIPURI_NUMERICE).columns[
			df.select_dtypes(include=TIPURI_NUMERICE).isnull().any()
		]
		categoriale = df.select_dtypes(include=TIPURI_CATEGORIALE).columns[
			df.select_dtypes(include=TIPURI_CATEGORIALE).isnull().any()
		]

		if mod_completare == "Automat pe tipuri":
			st.markdown("### 🔄 Completare automată pe categorii")

			strategie_num = st.selectbox(
				"Strategie pentru coloane **numerice**",
				["mean", "median", "mode", "valoare fixă"],
				key="fix_num_strategy",
			)
			strategie_cat = st.selectbox(
				"Strategie pentru coloane **categoriale**", ["mode", "valoare fixă"], key="fix_cat_strategy"
			)

			val_fix_num = None
			val_fix_cat = None

			if strategie_num == "valoare fixă":
				val_fix_num = st.number_input("Introdu valoarea fixă pentru numerice", key="fix_num_val")
			if strategie_cat == "valoare fixă":
				val_fix_cat = st.text_input("Introdu valoarea fixă pentru categoriale", key="fix_cat_val")

			if len(numerice) > 0:
				if strategie_num == "mean":
					df[numerice] = df[numerice].fillna(df[numerice].mean())
				elif strategie_num == "median":
					df[numerice] = df[numerice].fillna(df[numerice].median())
				elif strategie_num == "mode":
					df[numerice] = df[numerice].fillna(df[numerice].mode().iloc[0])
				elif strategie_num == "valoare fixă":
					df[numerice] = df[numerice].fillna(val_fix_num)

			if len(categoriale) > 0:
				if strategie_cat == "mode":
					df[categoriale] = df[categoriale].fillna(df[categoriale].mode().iloc[0])
				elif strategie_cat == "valoare fixă":
					df[categoriale] = df[categoriale].fillna(val_fix_cat)

		else:
			st.markdown("### 🛠️ Completare personalizată per coloană")

			for col in df.columns[df.isnull().any()]:
				dtype = df[col].dtype
				st.markdown(f"**Coloană: `{col}` ({dtype})**")
				if dtype in TIPURI_NUMERICE:
					strategie = st.selectbox(
						f"Strategie pentru `{col}`", ["mean", "median", "mode", "valoare fixă"], key=f"{col}_strategie"
					)
					if strategie == "mean":
						df[col] = df[col].fillna(df[col].mean())
					elif strategie == "median":
						df[col] = df[col].fillna(df[col].median())
					elif strategie == "mode":
						df[col] = df[col].fillna(df[col].mode()[0])
					elif strategie == "valoare fixă":
						val = st.number_input(f"Valoare fixă pentru `{col}`", key=f"{col}_val")
						df[col] = df[col].fillna(val)
				else:
					strategie = st.selectbox(
						f"Strategie pentru `{col}`", ["mode", "valoare fixă"], key=f"{col}_strategie_cat"
					)
					if strategie == "mode":
						df[col] = df[col].fillna(df[col].mode()[0])
					elif strategie == "valoare fixă":
						val = st.text_input(f"Valoare fixă pentru `{col}`", key=f"{col}_val_cat")
						df[col] = df[col].fillna(val)

		st.success("✅ Valorile lipsă au fost completate.")

	with st.expander("🔁 2. Transformare valori binare în True/False"):
		bin_cols = [col for col in df.columns if df[col].nunique() == 2 and df[col].dtype != "bool"]
		for col in bin_cols:
			unique_vals = df[col].dropna().unique().tolist()
			if len(unique_vals) == 2:
				true_val = st.selectbox(f"Ce valoare din `{col}` să fie considerată `True`?", unique_vals, key=col)
				df[col] = df[col].apply(lambda x: x == true_val)
		st.success("Valori binare convertite în bool.")

	with st.expander("🏷️ 3. Encoding"):
		col_cat = df.select_dtypes(include=["object", "category"]).columns.tolist()

		st.subheader("🔢 Label Encoding")
		label_cols = st.multiselect("Coloane pentru Label Encoding", col_cat, key="label_cols")

		for col in label_cols:
			unique_vals = df[col].dropna().unique().tolist()
			sorted_vals = sort_items(unique_vals)
			df[col] = df[col].astype(pd.CategoricalDtype(categories=sorted_vals, ordered=True)).cat.codes

		st.divider()

		st.subheader("📦 One-Hot Encoding")
		onehot_cols = st.multiselect("Coloane pentru One-Hot", col_cat, key="onehot_cols")
		drop_first = st.checkbox("Drop first dummy?", value=True)
		max_cats = st.slider("Max categorii per coloană", 2, 15, 10)

		for col in onehot_cols:
			if df[col].nunique() <= max_cats:
				dummies = pd.get_dummies(df[col], prefix=col, drop_first=drop_first)
				df = pd.concat([df.drop(columns=[col]), dummies], axis=1)

		st.success("✅ Encoding aplicat.")

	with st.expander("🧼 1. Eliminare coloane inutile"):
		coloane_drop = st.multiselect("Alege coloanele de eliminat", df.columns)
		if coloane_drop:
			df.drop(columns=coloane_drop, inplace=True)
			st.success(f"Am eliminat coloanele: {', '.join(coloane_drop)}")

	st.subheader("📊 Dataset prelucrat")
	st.dataframe(df.head())

	csv = df.to_csv(index=False).encode("utf-8")
	st.download_button("📥 Descarcă datasetul prelucrat", data=csv, file_name="prelucrat.csv", mime="text/csv")

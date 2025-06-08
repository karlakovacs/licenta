import streamlit as st


# (id, label, path, icon)
PAGES = [
	(0, "Acasă", "pages/0_acasa.py", "🏠"),
	(1, "Alegerea setului de date", "pages/1_dataset.py", "💳"),
	(2, "Analiza datelor", "pages/2_eda.py", "📊"),
	(3, "Procesarea datelor", "pages/3_procesare.py", "🛠️"),
	(4, "Alegerea modelelor ML", "pages/4_modele.py", "🧠"),
	(5, "Antrenarea modelelor ML", "pages/5_hiperparametri.py", "⚙️"),
	(6, "Rezultate", "pages/6_rezultate.py", "🎯"),
	(7, "Explainable AI", "pages/7_xai.py", "💡"),
	(8, "Compararea modelelor", "pages/8_comparatii.py", "⚖️"),
	(9, "Realizarea predicțiilor", "pages/9_predictii.py", "🔮"),
	(10, "Generarea raportului", "pages/10_raport.py", "⚡"),
	(11, "Datele mele", "pages/11_date.py", "📑"),
	(12, "Documentație", "pages/12_docs.py", "📚"),
]


def nav_bar():
	st.session_state.setdefault(
		"pagini",
		{
			0: True,
			1: True,
			2: False,
			3: False,
			4: False,
			5: False,
			6: False,
			7: False,
			8: False,
			9: False,
			10: False,
			11: True,
			12: True,
		},
	)

	st.sidebar.image("assets/logo-text.png", width=120)
	for page_id, label, path, icon in PAGES:
		st.sidebar.page_link(
			path,
			label=label,
			icon=icon,
			# disabled=not st.session_state.get("pagini").get(page_id)
		)

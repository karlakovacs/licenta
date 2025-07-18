import streamlit as st


# (id, label, path, icon)
PAGES = [
	(0, "Acasă", "pages/0_acasa.py", "🏠"),
	(1, "Alegerea setului de date", "pages/1_dataset.py", "💳"),
	(2, "Analiza datelor", "pages/2_eda.py", "📊"),
	(3, "Preprocesarea datelor", "pages/3_preprocesare.py", "🛠️"),
	(4, "Alegerea modelelor ML", "pages/4_modele.py", "🧠"),
	(5, "Antrenarea modelelor ML", "pages/5_antrenare.py", "⚙️"),
	(6, "Rezultate", "pages/6_rezultate.py", "🎯"),
	(7, "Compararea modelelor", "pages/7_comparatii.py", "⚖️"),
	(8, "Explainable AI", "pages/8_xai.py", "💡"),
	(9, "Realizarea predicțiilor", "pages/9_predictii.py", "🔮"),
	(10, "Generarea raportului", "pages/10_raport.py", "⚡"),
	(11, "Datele mele", "pages/11_date.py", "📑"),
]


def nav_bar():
	st.sidebar.image(f"assets/logo/logo-text.png", width=120)
	for _, label, path, icon in PAGES:
		st.sidebar.page_link(
			path,
			label=label,
			icon=icon,
		)

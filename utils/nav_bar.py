import streamlit as st


# (id, label, path, icon)
PAGES = [
	(0, "Acasă", "app.py", "🏠"),
	(1, "Set de date", "pages/1_dataset.py", "💳"),
	(2, "EDA", "pages/2_eda.py", "📊"),
	(3, "Procesare", "pages/3_procesare.py", "🛠️"),
	(4, "Modele", "pages/4_modele.py", "🧠"),
	(5, "Hiperparametri", "pages/5_hiperparametri.py", "⚙️"),
	(6, "Rezultate", "pages/6_rezultate.py", "🎯"),
	(7, "XAI", "pages/7_xai.py", "💡"),
	(8, "Comparații", "pages/8_comparatii.py", "⚖️"),
	(9, "Raport", "pages/9_raport.py", "⚡"),
	(10, "Rapoarte", "pages/10_rapoarte.py", "📑"),
	(11, "Teorie", "pages/11_teorie.py", "📚"),
	(12, "Test", "pages/12_test.py", "❤️"),
]


def nav_bar(allowed_pages: list[int] = None):
	if allowed_pages is None:
		allowed_pages = [page_id for (page_id, _, _, _) in PAGES]

	for page_id, label, path, icon in PAGES:
		st.sidebar.page_link(
			path,
			label=label,
			icon=icon,
			disabled=page_id not in allowed_pages,
		)


### OMG

# ALLOWED_PAGES -> dict cu id si id urile permise

### BUTOANE NAVIGARE PAGINI

# # inițializare
# if "allowed_pages" not in st.session_state:
# 	st.session_state.allowed_pages = ["Acasă", "Set de date"]

# # navbar afișat o singură dată
# nav_bar(st.session_state.allowed_pages)

# # trigger
# if st.button("lol"):
# 	st.session_state.allowed_pages = [p["label"] for p in PAGES]
# 	st.rerun()


# ### SWITCH PAGE (BUTON NAVIGARE SIMPLU)

# # if st.button("Rapoarte"):
# # 	st.switch_page("pages/10_rapoarte.py")

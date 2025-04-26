import streamlit as st

from utils import nav_bar


st.set_page_config(layout="wide", page_title="Modele", page_icon="🧠")
nav_bar()
st.title("Modele de Machine Learning")


CATEGORII_MODELE = [
	{
		"categorie": "Algoritmi de clasificare liniară",
		"modele": ["Logistic Regression", "Linear Discriminant Analysis"],
	},
	{
		"categorie": "Algoritmi de clasificare non-liniară",
		"modele": ["Quadratic Discriminant Analysis", "K-Nearest Neighbors", "Support Vector Classifier"],
	},
	{
		"categorie": "Algoritmi de clasificare pe bază de arbori și ansambluri",
		"modele": [
			"Decision Tree",
			"Random Forest",
			"Balanced Random Forest",
			"AdaBoost",
			"Gradient Boosting Classifier",
			"XGBoost",
			"LightGBM",
			"CatBoost",
		],
	},
	{"categorie": "Algoritmi de deep learning", "modele": ["Multilayer Perceptron"]},
]


MODELE_HINTURI = {
	"Logistic Regression": "Model liniar simplu. Oferă scoruri de probabilitate prin funcția sigmoidă.",
	"Linear Discriminant Analysis": "Separă clasele maximizând distanța dintre ele. Eficient când distribuția datelor este gaussiană.",
	"Quadratic Discriminant Analysis": "Similar cu LDA, dar permite frontiere de decizie curbe. Bun când clasele au varianțe diferite.",
	"K-Nearest Neighbors": "Clasifică în funcție de vecinii cei mai apropiați. Nu face presupuneri despre distribuția datelor.",
	"Support Vector Classifier": "Caută marginea optimă de separare între clase. Eficient în spații de dimensiuni mari.",
	"Decision Tree": "Împarte datele în funcție de reguli simple. Interpretabil, dar poate suferi de overfitting.",
	"Random Forest": "Ansamblu de arbori de decizie. Reduce overfitting-ul și crește performanța.",
	"Balanced Random Forest": "Versiune a Random Forest pentru date dezechilibrate. Echilibrează clasele prin sub-eșantionare.",
	"AdaBoost": "Combină mai mulți clasificatori simpli, adaptându-se la greșeli. Bun pentru date zgomotoase.",
	"Gradient Boosting Classifier": "Antrenează modele secvențial, corectând erorile anterioare. Puternic dar sensibil la overfitting.",
	"XGBoost": "Variantă optimizată de Gradient Boosting. Rapid, eficient și performant.",
	"LightGBM": "Boosting rapid pentru date mari. Consumă puține resurse și suportă multe caracteristici.",
	"CatBoost": "Specializat pentru variabile categoriale. Necesită minimă preprocesare și e robust.",
	"Multilayer Perceptron": "Rețea neuronală complet conectată. Captează relații complexe, dar necesită tuning atent.",
}


def main():
	st.session_state.setdefault("modele_selectate", [])
	st.subheader("Selectează modelele dorite")
	modele_selectate = []
	for grup in CATEGORII_MODELE:
		categorie = grup["categorie"]
		modele = grup["modele"]

		with st.container(border=True):
			st.subheader(categorie)

			selectii = []
			for model in modele:
				if st.checkbox(
					model,
					value=model in st.session_state.modele_selectate,
					help=MODELE_HINTURI[model],
					key=f"{categorie}_{model}",
				):
					selectii.append(model)

			modele_selectate += selectii

	if st.button("Salvează selecția", type="primary", disabled="modele_selectate" in st.session_state):
		st.session_state.modele_selectate = modele_selectate
		st.toast("Modelele au fost salvate!", icon="✅")


if __name__ == "__main__":
	main()

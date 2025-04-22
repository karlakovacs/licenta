from .modele import *


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

MODELE_OBIECTE = {
	"Logistic Regression": LR,
	"Linear Discriminant Analysis": LDA,
	"Quadratic Discriminant Analysis": QDA,
	"K-Nearest Neighbors": KNN,
	"Support Vector Classifier": SVM,
	"Decision Tree": DT,
	"Random Forest": RF,
	"Balanced Random Forest": BRF,
	"AdaBoost": AB,
	"Gradient Boosting Classifier": GBC,
	"XGBoost": XGB,
	"LightGBM": LGBM,
	"CatBoost": CB,
	"Multilayer Perceptron": MLP,
}

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

MODELE_ACRONIME = {
	"Logistic Regression": "LR",
	"Linear Discriminant Analysis": "LDA",
	"Quadratic Discriminant Analysis": "QDA",
	"K-Nearest Neighbors": "KNN",
	"Support Vector Classifier": "SVC",
	"Decision Tree": "DT",
	"Random Forest": "RF",
	"Balanced Random Forest": "BRF",
	"AdaBoost": "AB",
	"Gradient Boosting Classifier": "GBC",
	"XGBoost": "XGB",
	"LightGBM": "LGBM",
	"CatBoost": "CB",
	"Multilayer Perceptron": "MLP",
}


def get_model(denumire_model: str):
	if denumire_model not in MODELE_OBIECTE:
		raise ValueError(f"Modelul '{denumire_model}' nu există în mapare.")
	return MODELE_OBIECTE[denumire_model]()

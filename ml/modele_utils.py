from .modele import *


MODELE = [
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
	"Support Vector Classifier": SVC,
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


def get_model(denumire_model: str):
	if denumire_model not in MODELE_OBIECTE:
		raise ValueError(f"Modelul '{denumire_model}' nu există în mapare.")
	return MODELE_OBIECTE[denumire_model]()

# TODO: map cu acronime poate

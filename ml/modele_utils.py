from .modele import LR, LDA, QDA, KNN, SVM, DT, RF, BRF, AB, GBC, XGB, LGBM, CB, MLP


# MODELE_ACRONIME = {
# 	"Logistic Regression": "LR",
# 	"Linear Discriminant Analysis": "LDA",
# 	"Quadratic Discriminant Analysis": "QDA",
# 	"K-Nearest Neighbors": "KNN",
# 	"Support Vector Classifier": "SVC",
# 	"Decision Tree": "DT",
# 	"Random Forest": "RF",
# 	"Balanced Random Forest": "BRF",
# 	"AdaBoost": "AB",
# 	"Gradient Boosting Classifier": "GBC",
# 	"XGBoost": "XGB",
# 	"LightGBM": "LGBM",
# 	"CatBoost": "CB",
# 	"Multilayer Perceptron": "MLP",
# }


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


def get_model(denumire_model: str):
	if denumire_model not in MODELE_OBIECTE:
		raise ValueError(f"Modelul '{denumire_model}' nu există în mapare.")
	return MODELE_OBIECTE[denumire_model]()

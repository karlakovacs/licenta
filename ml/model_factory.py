from .hiperparametri import get_hiperparametri_default


def get_model(denumire: str, hiperparametri: dict, input_dim: int = None):
	if hiperparametri is None:
		hiperparametri = get_hiperparametri_default(denumire)

	match denumire:
		case "Logistic Regression":
			from sklearn.linear_model import LogisticRegression

			model = LogisticRegression(random_state=42)
			model.set_params(**hiperparametri)
			return model

		case "Linear Discriminant Analysis":
			from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

			model = LinearDiscriminantAnalysis()
			model.set_params(**hiperparametri)
			return model

		case "Quadratic Discriminant Analysis":
			from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

			model = QuadraticDiscriminantAnalysis()
			model.set_params(**hiperparametri)
			return model

		case "K-Nearest Neighbors":
			from sklearn.neighbors import KNeighborsClassifier

			model = KNeighborsClassifier()
			model.set_params(**hiperparametri)
			return model

		case "Support Vector Classifier":
			from sklearn.svm import SVC

			model = SVC(probability=True, shrinking=False, random_state=42)
			model.set_params(**hiperparametri)
			return model

		case "Decision Tree":
			from sklearn.tree import DecisionTreeClassifier

			model = DecisionTreeClassifier(random_state=42)
			model.set_params(**hiperparametri)
			return model

		case "Random Forest":
			from sklearn.ensemble import RandomForestClassifier

			model = RandomForestClassifier(random_state=42)
			model.set_params(**hiperparametri)
			return model

		case "Balanced Random Forest":
			from imblearn.ensemble import BalancedRandomForestClassifier

			model = BalancedRandomForestClassifier(random_state=42)
			model.set_params(**hiperparametri)
			return model

		case "AdaBoost":
			from sklearn.ensemble import AdaBoostClassifier

			model = AdaBoostClassifier(random_state=42)
			model.set_params(**hiperparametri)
			return model

		case "Gradient Boosting Classifier":
			from sklearn.ensemble import GradientBoostingClassifier

			model = GradientBoostingClassifier(random_state=42)
			model.set_params(**hiperparametri)
			return model

		case "XGBoost":
			from xgboost import XGBClassifier

			model = XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42)
			model.set_params(**hiperparametri)
			return model

		case "LightGBM":
			from lightgbm import LGBMClassifier

			model = LGBMClassifier(random_state=42)
			model.set_params(**hiperparametri)
			return model

		case "CatBoost":
			from catboost import CatBoostClassifier

			model = CatBoostClassifier(silent=True, random_seed=42)
			model.set_params(**hiperparametri)
			return model

		case "Multilayer Perceptron":
			from keras.api.layers import BatchNormalization, Dense, Dropout, Input
			from keras.api.metrics import AUC
			from keras.api.models import Sequential

			if input_dim is None:
				raise ValueError("Parametrul `input_dim` este necesar pentru a construi modelul MLP.")

			model = Sequential()
			for i in range(hiperparametri["n_layers"]):
				if i == 0:
					model.add(Input(shape=(input_dim,)))
				model.add(Dense(hiperparametri["units_per_layer"][i], activation=hiperparametri["activation"]))
				model.add(BatchNormalization())
				model.add(Dropout(hiperparametri["dropout_rates"][i]))

			model.add(Dense(1, activation="sigmoid"))

			model.compile(
				optimizer=hiperparametri["optimizer"],
				loss=hiperparametri["loss"],
				metrics=[AUC(name="auc")],
			)

			# time.sleep(10)

			return model

		case _:
			raise ValueError(f"Modelul `{denumire}` nu este recunoscut.")

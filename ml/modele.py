import time
import uuid

from catboost import CatBoostClassifier
from imblearn.ensemble import BalancedRandomForestClassifier
from lightgbm import LGBMClassifier
import shap
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
import streamlit as st
from xgboost import XGBClassifier


class Base:
	def __init__(self):
		self.model = None
		self.params = None
		self.hyperparams = self.get_hyperparams()
		self.y_pred = None
		self.y_prob = None

	def get_hyperparams(self):
		raise NotImplementedError()

	def get_shap_explainer(self, X_train, sample_size):
		if isinstance(self.model, (LogisticRegression, LinearDiscriminantAnalysis)):
			return shap.LinearExplainer(self.model, X_train)
		elif isinstance(
			self.model,
			(QuadraticDiscriminantAnalysis, KNeighborsClassifier, SVC, AdaBoostClassifier),
		):
			return shap.KernelExplainer(
				self.model.predict,
				X_train.sample(
					n=sample_size if X_train.shape[0] > sample_size else X_train.shape[0],
					random_state=42,
				),
			)
		elif isinstance(
			self.model,
			(
				DecisionTreeClassifier,
				RandomForestClassifier,
				GradientBoostingClassifier,
				XGBClassifier,
				LGBMClassifier,
				CatBoostClassifier,
			),
		):
			return shap.TreeExplainer(self.model)
		else:
			return shap.DeepExplainer(self.model, X_train)

	def get_shap_values(self, X_train, X_test, sample_size=25):
		shap_explainer = self.get_shap_explainer(X_train, sample_size)
		return shap_explainer(
			X_test.sample(
				n=sample_size if X_test.shape[0] > sample_size else X_test.shape[0], random_state=42
			)
		)

		# X_test_array = np.array(X_test) if isinstance(self.model, models.Sequential) else X_test
		# return shap_explainer(X_test_array[:sample_size])

	def get_params_utilizator(self):
		params = {}
		for param, details in self.hyperparams.items():
			unique_key = f"{param}_{uuid.uuid4()}"
			if details["type"] == "numerical":
				params[param] = st.slider(
					param,
					details["min"],
					details["max"],
					details["default"],
					details["step"],
					key=unique_key,
				)
			else:
				params[param] = st.selectbox(
					param,
					details["values"],
					index=details["values"].index(details["default"]),
					key=unique_key,
				)
		self.params = params
		return params

	def train(self, X_train, y_train, X_test, y_test=None):
		start_time = time.time()
		self.model.set_params(**self.params)
		self.model.fit(X_train, y_train)
		self.y_pred = self.model.predict(X_test)
		self.y_prob = self.model.predict_proba(X_test)[:, 1]
		training_time = time.time() - start_time
		return training_time


class LR(Base):
	def __init__(self):
		super().__init__()
		self.model = LogisticRegression()

	def get_hyperparams(self):
		return {
			"penalty": {
				"type": "categorical",
				"values": ["l1", "l2", "elasticnet", "none"],
				"default": "l2",
				"optimal": "l2",
			},
			"C": {
				"type": "numerical",
				"min": 0.0001,
				"max": 10.0,
				"step": 0.0001,
				"default": 1.0,
				"optimal": 0.1,
			},
			"solver": {
				"type": "categorical",
				"values": ["lbfgs", "liblinear", "sag", "saga"],
				"default": "lbfgs",
				"optimal": "lbfgs",
			},
			"max_iter": {
				"type": "numerical",
				"min": 100,
				"max": 10000,
				"step": 100,
				"default": 1000,
				"optimal": 5000,
			},
		}


class LDA(Base):
	def __init__(self):
		super().__init__()
		self.model = LinearDiscriminantAnalysis()

	def get_hyperparams(self):
		return {
			"solver": {
				"type": "categorical",
				"values": ["svd", "lsqr", "eigen"],
				"default": "svd",
				"optimal": "lsqr",
			},
			"shrinkage": {
				"type": "categorical",
				"values": [None, "auto"] + [round(i * 0.1, 1) for i in range(1, 10)],
				"default": None,
				"optimal": "auto",
			},
			"n_components": {
				"type": "numerical",
				"min": 1,
				"max": 10,
				"step": 1,
				"default": None,
				"optimal": 2,
			},
		}


class QDA(Base):
	def __init__(self):
		super().__init__()
		self.model = QuadraticDiscriminantAnalysis()

	def get_hyperparams(self):
		return {
			"reg_param": {
				"type": "numerical",
				"min": 0.0,
				"max": 1.0,
				"step": 0.01,
				"default": 0.0,
				"optimal": 0.1,
			},
			"store_covariance": {
				"type": "categorical",
				"values": [True, False],
				"default": False,
				"optimal": False,
			},
			"tol": {
				"type": "numerical",
				"min": 1e-5,
				"max": 1e-2,
				"step": 1e-5,
				"default": 1e-4,
				"optimal": 1e-3,
			},
		}


class KNN(Base):
	def __init__(self):
		super().__init__()
		self.model = KNeighborsClassifier()

	def get_hyperparams(self):
		return {
			"n_neighbors": {
				"type": "numerical",
				"min": 1,
				"max": 50,
				"step": 1,
				"default": 5,
				"optimal": 10,
			},
			"weights": {
				"type": "categorical",
				"values": ["uniform", "distance"],
				"default": "uniform",
				"optimal": "distance",
			},
			"metric": {
				"type": "categorical",
				"values": ["minkowski", "euclidean", "manhattan"],
				"default": "minkowski",
				"optimal": "euclidean",
			},
			"p": {"type": "numerical", "min": 1, "max": 5, "step": 1, "default": 2, "optimal": 2},
		}


class SVM(Base):
	def __init__(self):
		super().__init__()
		self.model = SVC(probability=True)

	def get_hyperparams(self):
		return {
			"C": {
				"type": "numerical",
				"min": 0.01,
				"max": 100.0,
				"step": 0.01,
				"default": 1.0,
				"optimal": 10.0,
			},
			"kernel": {
				"type": "categorical",
				"values": ["linear", "poly", "rbf", "sigmoid"],
				"default": "rbf",
				"optimal": "rbf",
			},
			"gamma": {
				"type": "categorical",
				"values": ["scale", "auto"] + [round(10**i, 5) for i in range(-4, 2)],
				"default": "scale",
				"optimal": "scale",
			},
			"degree": {
				"type": "numerical",
				"min": 2,
				"max": 6,
				"step": 1,
				"default": 3,
				"optimal": 3,
			},
			"tol": {
				"type": "numerical",
				"min": 1e-5,
				"max": 1e-2,
				"step": 1e-5,
				"default": 1e-3,
				"optimal": 1e-4,
			},
		}


class DT(Base):
	def __init__(self):
		super().__init__()
		self.model = DecisionTreeClassifier()

	def get_hyperparams(self):
		return {
			"criterion": {
				"type": "categorical",
				"values": ["gini", "entropy", "log_loss"],
				"default": "gini",
				"optimal": "entropy",
			},
			"max_depth": {
				"type": "numerical",
				"min": 1,
				"max": 50,
				"step": 1,
				"default": None,
				"optimal": 10,
			},
			"min_samples_split": {
				"type": "numerical",
				"min": 2,
				"max": 20,
				"step": 1,
				"default": 2,
				"optimal": 5,
			},
			"min_samples_leaf": {
				"type": "numerical",
				"min": 1,
				"max": 10,
				"step": 1,
				"default": 1,
				"optimal": 2,
			},
			"max_features": {
				"type": "categorical",
				"values": ["auto", "sqrt", "log2", None],
				"default": None,
				"optimal": "sqrt",
			},
		}


class RF(Base):
	def __init__(self):
		super().__init__()
		self.model = RandomForestClassifier()

	def get_hyperparams(self):
		return {
			"n_estimators": {
				"type": "numerical",
				"min": 10,
				"max": 500,
				"step": 10,
				"default": 100,
				"optimal": 200,
			},
			"max_depth": {
				"type": "numerical",
				"min": 1,
				"max": 50,
				"step": 1,
				"default": None,
				"optimal": 10,
			},
			"min_samples_split": {
				"type": "numerical",
				"min": 2,
				"max": 20,
				"step": 1,
				"default": 2,
				"optimal": 5,
			},
			"min_samples_leaf": {
				"type": "numerical",
				"min": 1,
				"max": 10,
				"step": 1,
				"default": 1,
				"optimal": 2,
			},
			"max_features": {
				"type": "categorical",
				"values": ["sqrt", "log2", None],
				"default": "sqrt",
				"optimal": "sqrt",
			},
			"bootstrap": {
				"type": "categorical",
				"values": [True, False],
				"default": True,
				"optimal": True,
			},
		}


class BRF(Base):
	def __init__(self):
		super().__init__()
		self.model = BalancedRandomForestClassifier()

	# TODO
	def get_hyperparams(self):
		return {
			"n_estimators": {
				"type": "numerical",
				"min": 10,
				"max": 500,
				"step": 10,
				"default": 100,
				"optimal": 200,
			},
			# "max_depth": {
			# 	"type": "numerical",
			# 	"min": 1,
			# 	"max": 50,
			# 	"step": 1,
			# 	"default": None,
			# 	"optimal": 10,
			# },
			# "min_samples_split": {
			# 	"type": "numerical",
			# 	"min": 2,
			# 	"max": 20,
			# 	"step": 1,
			# 	"default": 2,
			# 	"optimal": 5,
			# },
			# "min_samples_leaf": {
			# 	"type": "numerical",
			# 	"min": 1,
			# 	"max": 10,
			# 	"step": 1,
			# 	"default": 1,
			# 	"optimal": 2,
			# },
			# "max_features": {
			# 	"type": "categorical",
			# 	"values": ["sqrt", "log2", None],
			# 	"default": "sqrt",
			# 	"optimal": "sqrt",
			# },
			# "bootstrap": {
			# 	"type": "categorical",
			# 	"values": [True, False],
			# 	"default": True,
			# 	"optimal": True,
			# },
		}

class AB(Base):
	def __init__(self):
		super().__init__()
		self.model = AdaBoostClassifier()

	def get_hyperparams(self):
		return {
			"n_estimators": {
				"type": "numerical",
				"min": 10,
				"max": 500,
				"step": 10,
				"default": 50,
				"optimal": 200,
			},
			"learning_rate": {
				"type": "numerical",
				"min": 0.001,
				"max": 2.0,
				"step": 0.001,
				"default": 1.0,
				"optimal": 0.1,
			},
			"algorithm": {
				"type": "categorical",
				"values": ["SAMME"],
				"default": "SAMME",
				"optimal": "SAMME",
			},
		}


class GBC(Base):
	def __init__(self):
		super().__init__()
		self.model = GradientBoostingClassifier()

	def get_hyperparams(self):
		return {
			"n_estimators": {
				"type": "numerical",
				"min": 10,
				"max": 500,
				"step": 10,
				"default": 100,
				"optimal": 200,
			},
			"learning_rate": {
				"type": "numerical",
				"min": 0.001,
				"max": 1.0,
				"step": 0.001,
				"default": 0.1,
				"optimal": 0.05,
			},
			"max_depth": {
				"type": "numerical",
				"min": 1,
				"max": 50,
				"step": 1,
				"default": 3,
				"optimal": 5,
			},
			"min_samples_split": {
				"type": "numerical",
				"min": 2,
				"max": 20,
				"step": 1,
				"default": 2,
				"optimal": 5,
			},
			"min_samples_leaf": {
				"type": "numerical",
				"min": 1,
				"max": 10,
				"step": 1,
				"default": 1,
				"optimal": 2,
			},
			"subsample": {
				"type": "numerical",
				"min": 0.1,
				"max": 1.0,
				"step": 0.1,
				"default": 1.0,
				"optimal": 0.8,
			},
		}


class XGB(Base):
	def __init__(self):
		super().__init__()
		self.model = XGBClassifier()

	def get_hyperparams(self):
		return {
			"n_estimators": {
				"type": "numerical",
				"min": 10,
				"max": 500,
				"step": 10,
				"default": 100,
				"optimal": 200,
			},
			"learning_rate": {
				"type": "numerical",
				"min": 0.001,
				"max": 1.0,
				"step": 0.001,
				"default": 0.1,
				"optimal": 0.05,
			},
			"max_depth": {
				"type": "numerical",
				"min": 1,
				"max": 50,
				"step": 1,
				"default": 3,
				"optimal": 5,
			},
			"gamma": {
				"type": "numerical",
				"min": 0.0,
				"max": 10.0,
				"step": 0.1,
				"default": 0.0,
				"optimal": 0.1,
			},
			"subsample": {
				"type": "numerical",
				"min": 0.1,
				"max": 1.0,
				"step": 0.1,
				"default": 1.0,
				"optimal": 0.8,
			},
			"colsample_bytree": {
				"type": "numerical",
				"min": 0.1,
				"max": 1.0,
				"step": 0.1,
				"default": 1.0,
				"optimal": 0.8,
			},
		}


class LGBM(Base):
	def __init__(self):
		super().__init__()
		self.model = LGBMClassifier()

	def get_hyperparams(self):
		return {
			"num_leaves": {
				"type": "numerical",
				"min": 2,
				"max": 256,
				"step": 1,
				"default": 31,
				"optimal": 40,
			},
			"learning_rate": {
				"type": "numerical",
				"min": 0.001,
				"max": 1.0,
				"step": 0.001,
				"default": 0.1,
				"optimal": 0.05,
			},
			"n_estimators": {
				"type": "numerical",
				"min": 10,
				"max": 500,
				"step": 10,
				"default": 100,
				"optimal": 200,
			},
			"max_depth": {
				"type": "numerical",
				"min": -1,
				"max": 50,
				"step": 1,
				"default": -1,
				"optimal": 10,
			},
			"subsample": {
				"type": "numerical",
				"min": 0.1,
				"max": 1.0,
				"step": 0.1,
				"default": 1.0,
				"optimal": 0.8,
			},
			"colsample_bytree": {
				"type": "numerical",
				"min": 0.1,
				"max": 1.0,
				"step": 0.1,
				"default": 1.0,
				"optimal": 0.8,
			},
			"reg_alpha": {
				"type": "numerical",
				"min": 0.0,
				"max": 10.0,
				"step": 0.1,
				"default": 0.0,
				"optimal": 0.1,
			},
			"reg_lambda": {
				"type": "numerical",
				"min": 0.0,
				"max": 10.0,
				"step": 0.1,
				"default": 0.0,
				"optimal": 0.1,
			},
		}


class CB(Base):
	def __init__(self):
		super().__init__()
		self.model = CatBoostClassifier(silent=True)

	def get_hyperparams(self):
		return {
			"iterations": {
				"type": "numerical",
				"min": 10,
				"max": 1000,
				"step": 10,
				"default": 100,
				"optimal": 500,
			},
			"learning_rate": {
				"type": "numerical",
				"min": 0.001,
				"max": 1.0,
				"step": 0.001,
				"default": 0.1,
				"optimal": 0.05,
			},
			"depth": {
				"type": "numerical",
				"min": 1,
				"max": 16,
				"step": 1,
				"default": 6,
				"optimal": 8,
			},
			"l2_leaf_reg": {
				"type": "numerical",
				"min": 1.0,
				"max": 10.0,
				"step": 0.1,
				"default": 3.0,
				"optimal": 5.0,
			},
			"bootstrap_type": {
				"type": "categorical",
				"values": ["Bayesian", "Bernoulli", "MVS", "No"],
				"default": "Bayesian",
				"optimal": "Bayesian",
			},
			"grow_policy": {
				"type": "categorical",
				"values": ["SymmetricTree", "Depthwise", "Lossguide"],
				"default": "SymmetricTree",
				"optimal": "Lossguide",
			},
			# "subsample": {
			#     "type": "numerical",
			#     "min": 0.1,
			#     "max": 1.0,
			#     "step": 0.1,
			#     "default": 1.0,
			#     "optimal": 0.8,
			# },
		}


# TODO: afisare history (sauuu???)
class MLP(Base):
	def __init__(self):
		super().__init__()

	def get_hyperparams(self):
		return {
			"n_layers": {
				"type": "numerical",
				"min": 1,
				"max": 10,
				"step": 1,
				"default": 5,
				"optimal": 5,
			},
			"units_per_layer": {
				"type": "list_numerical",
				"min": 8,
				"max": 512,
				"step": 8,
				"default": [128, 64, 64, 32, 16],
				"optimal": [128, 64, 64, 32, 16],
			},
			"dropout_rates": {
				"type": "list_numerical",
				"min": 0.0,
				"max": 0.5,
				"step": 0.05,
				"default": [0.3, 0.3, 0.3, 0.3, 0.3],
				"optimal": [0.3, 0.3, 0.3, 0.3, 0.3],
			},
			"activation": {
				"type": "categorical",
				"values": ["relu", "tanh", "sigmoid", "leaky_relu"],
				"default": "relu",
				"optimal": "relu",
			},
			"optimizer": {
				"type": "categorical",
				"values": ["adam", "sgd", "rmsprop", "adamax"],
				"default": "adam",
				"optimal": "adam",
			},
			"loss": {
				"type": "categorical",
				"values": ["binary_crossentropy", "categorical_crossentropy", "mse"],
				"default": "binary_crossentropy",
				"optimal": "binary_crossentropy",
			},
			"batch_size": {
				"type": "numerical",
				"min": 8,
				"max": 256,
				"step": 8,
				"default": 32,
				"optimal": 64,
			},
			"epochs": {
				"type": "numerical",
				"min": 1,
				"max": 100,
				"step": 1,
				"default": 10,
				"optimal": 20,
			},
		}

	def get_params_utilizator(self):
		params = {}
		for param, details in self.hyperparams.items():
			if details["type"] == "numerical":
				params[param] = st.slider(
					param, details["min"], details["max"], details["default"], details["step"]
				)
			elif details["type"] == "list_numerical":
				params[param] = []
				for i in range(params.get("n_layers", details["default"])):
					value = st.slider(
						f"{param} (Strat {i + 1})",
						details["min"],
						details["max"],
						details["default"][min(i, len(details["default"]) - 1)],
						details["step"],
					)
					params[param].append(value)
			else:
				params[param] = st.selectbox(
					param, details["values"], index=details["values"].index(details["default"])
				)
		self.params = params
		return params

	def build_model(self, input_shape):
		from keras.layers import BatchNormalization, Dense, Dropout  # type: ignore
		from keras.metrics import AUC  # type: ignore
		from keras.models import Sequential  # type: ignore
		
		self.model = Sequential()
		for i in range(self.params["n_layers"]):
			if i == 0:
				self.model.add(
					Dense(
						self.params["units_per_layer"][i],
						activation=self.params["activation"],
						input_shape=input_shape,
					)
				)
			else:
				self.model.add(
					Dense(
						self.params["units_per_layer"][i], activation=self.params["activation"]
					)
				)

			self.model.add(BatchNormalization())
			self.model.add(Dropout(self.params["dropout_rates"][i]))

		self.model.add(Dense(1, activation="sigmoid"))

		self.model.compile(
			optimizer=self.params["optimizer"],
			loss=self.params["loss"],
			metrics=[AUC(name="auc")],
		)

	def train(self, X_train, y_train, X_val, y_val):
		self.build_model((X_train.shape[1],))
		start_time = time.time()

		history = self.model.fit(
			X_train,
			y_train,
			validation_data=(X_val, y_val),
			epochs=self.params["epochs"],
			batch_size=self.params["batch_size"],
			verbose=1,
		)

		# history_dict = history.history
		# final_loss = history_dict["loss"][-1]
		# final_auc = history_dict["auc"][-1] if "auc" in history_dict else None

		self.training_time = time.time() - start_time
		self.y_prob = self.model.predict(X_val)
		self.y_pred = (self.y_prob > 0.5).astype(int)
		training_time = time.time() - start_time
		return training_time

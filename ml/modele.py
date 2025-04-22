import time

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
			X_test.sample(n=sample_size if X_test.shape[0] > sample_size else X_test.shape[0], random_state=42)
		)

		# X_test_array = np.array(X_test) if isinstance(self.model, models.Sequential) else X_test
		# return shap_explainer(X_test_array[:sample_size])

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
				"help": "Tipul de regularizare aplicată pentru a preveni overfitting.",
			},
			"C": {
				"type": "numerical",
				"min": 0.0001,
				"max": 10.0,
				"step": 0.0001,
				"default": 1.0,
				"help": "Inversează puterea regularizării. Valori mai mici înseamnă regularizare mai puternică.",
			},
			"solver": {
				"type": "categorical",
				"values": ["lbfgs", "liblinear", "sag", "saga"],
				"default": "lbfgs",
				"help": "Algoritmul utilizat pentru optimizarea funcției de cost.",
			},
			"max_iter": {
				"type": "numerical",
				"min": 100,
				"max": 10000,
				"step": 100,
				"default": 1000,
				"help": "Numărul maxim de iterații pentru ca solverul să conveargă.",
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
				"help": "Algoritmul folosit pentru calculul LDA. `svd` nu suportă shrinkage.",
			},
			"shrinkage": {
				"type": "categorical",
				"values": [None, "auto"] + [round(i * 0.1, 1) for i in range(1, 10)],
				"default": None,
				"help": "Regularizare pentru stabilitate. Funcționează doar cu `lsqr` sau `eigen`.",
			},
			"n_components": {
				"type": "numerical",
				"min": 1,
				"max": 10,
				"step": 1,
				"default": None,
				"help": "Numărul de componente LDA păstrate (maxim = număr de clase - 1).",
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
				"help": "Coeficient de regularizare pentru covarianță. Valori > 0 reduc overfittingul.",
			},
			"store_covariance": {
				"type": "categorical",
				"values": [True, False],
				"default": False,
				"help": "Dacă se salvează matricea de covarianță pentru fiecare clasă (True = consum mai mare de memorie).",
			},
			"tol": {
				"type": "numerical",
				"min": 1e-5,
				"max": 1e-2,
				"step": 1e-5,
				"default": 1e-4,
				"help": "Toleranța pentru stabilitatea inversării matricei. Afectează clasificarea când datele sunt apropiate.",
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
				"help": "Numărul de vecini folosiți pentru clasificare. Valori mai mari pot netezi decizia.",
			},
			"weights": {
				"type": "categorical",
				"values": ["uniform", "distance"],
				"default": "uniform",
				"help": "`uniform` tratează toți vecinii egal, `distance` acordă mai multă importanță celor apropiați.",
			},
			"metric": {
				"type": "categorical",
				"values": ["minkowski", "euclidean", "manhattan"],
				"default": "minkowski",
				"help": "Funcția de distanță folosită. `euclidean` și `manhattan` sunt cazuri speciale ale `minkowski`.",
			},
			"p": {
				"type": "numerical",
				"min": 1,
				"max": 5,
				"step": 1,
				"default": 2,
				"help": "Parametru pentru distanța Minkowski: 1 = manhattan, 2 = euclidean.",
			},
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
				"help": "Controlul penalizării pentru clasificările greșite. Valori mari → overfitting.",
			},
			"kernel": {
				"type": "categorical",
				"values": ["linear", "poly", "rbf", "sigmoid"],
				"default": "rbf",
				"help": "Tipul de kernel folosit pentru a transforma datele. `rbf` e alegerea implicită.",
			},
			"gamma": {
				"type": "categorical",
				"values": ["scale", "auto"] + [round(10**i, 5) for i in range(-4, 2)],
				"default": "scale",
				"help": "Definirea influenței unui singur exemplu. `scale` e stabil și recomandat.",
			},
			"degree": {
				"type": "numerical",
				"min": 2,
				"max": 6,
				"step": 1,
				"default": 3,
				"help": "Gradul polinomului (doar dacă kernel='poly').",
			},
			"tol": {
				"type": "numerical",
				"min": 1e-5,
				"max": 1e-2,
				"step": 1e-5,
				"default": 1e-3,
				"help": "Toleranța pentru oprirea algoritmului. Valori mai mici = antrenare mai precisă.",
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
				"help": "Criteriul pentru a măsura calitatea unei împărțiri. `gini` este cel mai rapid.",
			},
			"max_depth": {
				"type": "numerical",
				"min": 1,
				"max": 50,
				"step": 1,
				"default": None,
				"help": "Adâncimea maximă a arborelui. Controlează complexitatea modelului.",
			},
			"min_samples_split": {
				"type": "numerical",
				"min": 2,
				"max": 20,
				"step": 1,
				"default": 2,
				"help": "Numărul minim de eșantioane necesare pentru a împărți un nod.",
			},
			"min_samples_leaf": {
				"type": "numerical",
				"min": 1,
				"max": 10,
				"step": 1,
				"default": 1,
				"help": "Numărul minim de eșantioane într-o frunză. Ajută la reducerea overfitting-ului.",
			},
			"max_features": {
				"type": "categorical",
				"values": ["auto", "sqrt", "log2", None],
				"default": None,
				"help": "Numărul de caracteristici luate în considerare la fiecare split. `sqrt` e frecvent folosit.",
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
				"help": "Numărul de arbori în pădure. Mai mulți arbori pot îmbunătăți performanța, dar cresc timpul de rulare.",
			},
			"max_depth": {
				"type": "numerical",
				"min": 1,
				"max": 50,
				"step": 1,
				"default": None,
				"help": "Adâncimea maximă a fiecărui arbore. Limitează complexitatea individuală.",
			},
			"min_samples_split": {
				"type": "numerical",
				"min": 2,
				"max": 20,
				"step": 1,
				"default": 2,
				"help": "Numărul minim de eșantioane necesare pentru a diviza un nod.",
			},
			"min_samples_leaf": {
				"type": "numerical",
				"min": 1,
				"max": 10,
				"step": 1,
				"default": 1,
				"help": "Numărul minim de eșantioane într-o frunză. Reduce overfitting-ul.",
			},
			"max_features": {
				"type": "categorical",
				"values": ["sqrt", "log2", None],
				"default": "sqrt",
				"help": "Numărul de caracteristici luate în considerare pentru split. `sqrt` este uzual pentru clasificare.",
			},
			"bootstrap": {
				"type": "categorical",
				"values": [True, False],
				"default": True,
				"help": "Dacă să se folosească bootstrap sampling. True este comportamentul standard.",
			},
		}


class BRF(Base):
	def __init__(self):
		super().__init__()
		self.model = BalancedRandomForestClassifier()

	def get_hyperparams(self):
		return {
			"n_estimators": {
				"type": "numerical",
				"min": 10,
				"max": 500,
				"step": 10,
				"default": 100,
				"help": "Numărul total de arbori în pădure. Mai mulți arbori pot îmbunătăți performanța, dar cresc timpul de antrenare.",
			},
			"max_depth": {
				"type": "numerical",
				"min": 1,
				"max": 50,
				"step": 1,
				"default": None,
				"help": "Adâncimea maximă a arborilor. Un `None` permite extinderea completă până la frunze pure.",
			},
			"min_samples_split": {
				"type": "numerical",
				"min": 2,
				"max": 20,
				"step": 1,
				"default": 2,
				"help": "Numărul minim de eșantioane pentru a împărți un nod.",
			},
			"min_samples_leaf": {
				"type": "numerical",
				"min": 1,
				"max": 10,
				"step": 1,
				"default": 1,
				"help": "Numărul minim de eșantioane necesare într-o frunză.",
			},
			"max_features": {
				"type": "categorical",
				"values": ["sqrt", "log2", None],
				"default": "sqrt",
				"help": "Numărul de caracteristici luate în calcul la fiecare split. `sqrt` este o alegere comună.",
			},
			"replacement": {
				"type": "categorical",
				"values": [True, False],
				"default": False,
				"help": "Dacă eșantionarea pentru fiecare arbore se face cu înlocuire. Poate afecta diversitatea arborilor.",
			},
			"bootstrap": {
				"type": "categorical",
				"values": [True, False],
				"default": True,
				"help": "Dacă să se folosească bootstrap sampling pentru eșantionare.",
			},
			"sampling_strategy": {
				"type": "categorical",
				"values": ["auto", "not majority", "all"],
				"default": "auto",
				"help": "Strategia de undersampling a clasei majore. `auto` înseamnă echilibrare completă.",
			},
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
				"help": "Numărul total de estimatori adăugați secvențial. Valori mai mari pot reduce bias-ul dar cresc timpul de antrenare.",
			},
			"learning_rate": {
				"type": "numerical",
				"min": 0.001,
				"max": 2.0,
				"step": 0.001,
				"default": 1.0,
				"help": "Factor de ponderare aplicat fiecărui estimator nou. Rate mai mici implică mai mulți estimatori.",
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
				"help": "Numărul de arbori de decizie antrenați secvențial. Un număr mai mare poate crește acuratețea, dar și riscul de overfitting.",
			},
			"learning_rate": {
				"type": "numerical",
				"min": 0.001,
				"max": 1.0,
				"step": 0.001,
				"default": 0.1,
				"help": "Cât de mult contribuie fiecare arbore la modelul final. Valori mai mici cer mai mulți arbori, dar pot duce la o generalizare mai bună.",
			},
			"max_depth": {
				"type": "numerical",
				"min": 1,
				"max": 50,
				"step": 1,
				"default": 3,
				"help": "Adâncimea maximă a fiecărui arbore. Controlează complexitatea individuală a arborilor.",
			},
			"min_samples_split": {
				"type": "numerical",
				"min": 2,
				"max": 20,
				"step": 1,
				"default": 2,
				"help": "Numărul minim de exemple necesare pentru a împărți un nod. Valori mai mari fac arborii mai puțin adânci.",
			},
			"min_samples_leaf": {
				"type": "numerical",
				"min": 1,
				"max": 10,
				"step": 1,
				"default": 1,
				"help": "Numărul minim de exemple într-o frunză. Ajută la regularizare și reduce overfitting-ul.",
			},
			"subsample": {
				"type": "numerical",
				"min": 0.1,
				"max": 1.0,
				"step": 0.1,
				"default": 1.0,
				"help": "Proporția din datele de antrenament folosită pentru fiecare arbore. Valori sub 1.0 introduc stochasticitate și pot îmbunătăți generalizarea.",
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
				"help": "Numărul total de arbori antrenați secvențial.",
			},
			"learning_rate": {
				"type": "numerical",
				"min": 0.001,
				"max": 1.0,
				"step": 0.001,
				"default": 0.1,
				"help": "Ratează cât de mult contribuie fiecare arbore la modelul final.",
			},
			"max_depth": {
				"type": "numerical",
				"min": 1,
				"max": 50,
				"step": 1,
				"default": 3,
				"help": "Adâncimea maximă a fiecărui arbore individual.",
			},
			"gamma": {
				"type": "numerical",
				"min": 0.0,
				"max": 10.0,
				"step": 0.1,
				"default": 0.0,
				"help": "Cerința minimă de reducere a pierderii pentru a face o împărțire.",
			},
			"subsample": {
				"type": "numerical",
				"min": 0.1,
				"max": 1.0,
				"step": 0.1,
				"default": 1.0,
				"help": "Proporția din datele de antrenament folosită pentru fiecare arbore.",
			},
			"colsample_bytree": {
				"type": "numerical",
				"min": 0.1,
				"max": 1.0,
				"step": 0.1,
				"default": 1.0,
				"help": "Proporția din caracteristici folosită pentru construirea fiecărui arbore.",
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
				"help": "Numărul maxim de frunze pe care le poate avea un arbore. Mai multe frunze pot duce la overfitting.",
			},
			"learning_rate": {
				"type": "numerical",
				"min": 0.001,
				"max": 1.0,
				"step": 0.001,
				"default": 0.1,
				"help": "Cât de mult contribuie fiecare arbore la predicția finală.",
			},
			"n_estimators": {
				"type": "numerical",
				"min": 10,
				"max": 500,
				"step": 10,
				"default": 100,
				"help": "Numărul total de arbori antrenați în model.",
			},
			"max_depth": {
				"type": "numerical",
				"min": -1,
				"max": 50,
				"step": 1,
				"default": -1,
				"help": "Adâncimea maximă a arborilor. -1 înseamnă fără limită.",
			},
			"subsample": {
				"type": "numerical",
				"min": 0.1,
				"max": 1.0,
				"step": 0.1,
				"default": 1.0,
				"help": "Proporția de date folosită pentru fiecare arbore. Reduce overfitting.",
			},
			"colsample_bytree": {
				"type": "numerical",
				"min": 0.1,
				"max": 1.0,
				"step": 0.1,
				"default": 1.0,
				"help": "Proporția de coloane folosită pentru construirea fiecărui arbore.",
			},
			"reg_alpha": {
				"type": "numerical",
				"min": 0.0,
				"max": 10.0,
				"step": 0.1,
				"default": 0.0,
				"help": "Regularizare L1 (Lasso). Controlează complexitatea modelului.",
			},
			"reg_lambda": {
				"type": "numerical",
				"min": 0.0,
				"max": 10.0,
				"step": 0.1,
				"default": 0.0,
				"help": "Regularizare L2 (Ridge). Ajută la prevenirea overfitting-ului.",
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
				"help": "Numărul total de arbori de decizie antrenați.",
			},
			"learning_rate": {
				"type": "numerical",
				"min": 0.001,
				"max": 1.0,
				"step": 0.001,
				"default": 0.1,
				"help": "Rata cu care modelul învață. Valori mai mici oferă antrenare mai lentă dar stabilă.",
			},
			"depth": {
				"type": "numerical",
				"min": 1,
				"max": 16,
				"step": 1,
				"default": 6,
				"help": "Adâncimea arborilor. Afectează complexitatea și riscul de overfitting.",
			},
			"l2_leaf_reg": {
				"type": "numerical",
				"min": 1.0,
				"max": 10.0,
				"step": 0.1,
				"default": 3.0,
				"help": "Regularizare L2 pentru frunze. Controlează cât de mult penalizează complexitatea.",
			},
			"bootstrap_type": {
				"type": "categorical",
				"values": ["Bayesian", "Bernoulli", "MVS", "No"],
				"default": "Bayesian",
				"help": "Strategia de sampling pentru bootstrap. Bayesian oferă rezultate stabile.",
			},
			"grow_policy": {
				"type": "categorical",
				"values": ["SymmetricTree", "Depthwise", "Lossguide"],
				"default": "SymmetricTree",
				"help": "Politica de creștere a arborilor. Lossguide e mai eficient pentru seturi mari.",
			},
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
				"help": "Numărul total de straturi ascunse.",
			},
			"units_per_layer": {
				"type": "list_numerical",
				"min": 8,
				"max": 512,
				"step": 8,
				"default": [128, 64, 64, 32, 16],
				"help": "Numărul de neuroni per strat. Lungimea listei trebuie să fie egală cu `n_layers`.",
			},
			"dropout_rates": {
				"type": "list_numerical",
				"min": 0.0,
				"max": 0.5,
				"step": 0.05,
				"default": [0.3, 0.3, 0.3, 0.3, 0.3],
				"help": "Ratele de dropout pentru regularizare. Trebuie să corespundă cu `n_layers`.",
			},
			"activation": {
				"type": "categorical",
				"values": ["relu", "tanh", "sigmoid", "leaky_relu"],
				"default": "relu",
				"help": "Funcția de activare aplicată după fiecare strat.",
			},
			"optimizer": {
				"type": "categorical",
				"values": ["adam", "sgd", "rmsprop", "adamax"],
				"default": "adam",
				"help": "Algoritmul folosit pentru optimizarea ponderilor.",
			},
			"loss": {
				"type": "categorical",
				"values": ["binary_crossentropy", "categorical_crossentropy", "mse"],
				"default": "binary_crossentropy",
				"help": "Funcția de loss care ghidează antrenarea.",
			},
			"batch_size": {
				"type": "numerical",
				"min": 8,
				"max": 256,
				"step": 8,
				"default": 32,
				"help": "Câte instanțe sunt procesate simultan în timpul antrenării.",
			},
			"epochs": {
				"type": "numerical",
				"min": 1,
				"max": 100,
				"step": 1,
				"default": 5,
				"help": "Numărul de treceri complete prin datele de antrenare.",
			},
		}

	def build_model(self, input_shape):
		from keras.layers import BatchNormalization, Dense, Dropout, Input  # type: ignore
		from keras.metrics import AUC  # type: ignore
		from keras.models import Sequential  # type: ignore

		self.model = Sequential()
		for i in range(self.params["n_layers"]):
			if i == 0:
				self.model.add(Input(shape=input_shape))
				self.model.add(
					Dense(
						self.params["units_per_layer"][0],
						activation=self.params["activation"],
					)
				)
			else:
				self.model.add(Dense(self.params["units_per_layer"][i], activation=self.params["activation"]))

			self.model.add(BatchNormalization())
			self.model.add(Dropout(self.params["dropout_rates"][i]))

		self.model.add(Dense(1, activation="sigmoid"))

		self.model.compile(
			optimizer=self.params["optimizer"],
			loss=self.params["loss"],
			metrics=[AUC(name="auc")],
		)

	def train(self, X_train, y_train, X_val, y_val):
		import gc

		from tensorflow.keras import backend as K  # type: ignore

		self.build_model((X_train.shape[1],))
		start_time = time.time()

		history = self.model.fit(
			X_train,
			y_train,
			validation_data=(X_val, y_val),
			epochs=self.params["epochs"],
			batch_size=self.params["batch_size"],
			verbose=0,
		)

		# history_dict = history.history
		# final_loss = history_dict["loss"][-1]
		# final_auc = history_dict["auc"][-1] if "auc" in history_dict else None

		self.training_time = time.time() - start_time
		self.y_prob = self.model.predict(X_val)
		self.y_pred = (self.y_prob > 0.5).astype(int)
		training_time = time.time() - start_time

		K.clear_session()
		gc.collect()
		
		return training_time

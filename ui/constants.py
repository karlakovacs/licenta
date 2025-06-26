DETALII_EDA = {
	"Setul de date": "Afișează setul de date în mod interactiv.\n\nPermite o primă verificare a consistenței datelor.\n\nUtil pentru a înțelege structura brută a fișierului încărcat.",
	"Analiza valorilor lipsă": "Evaluează câte valori lipsesc pe coloană, atât în număr absolut, cât și procentual.\n\nEste utilă pentru luarea deciziilor de curățare a datelor sau imputare.",
	"Distribuția tipurilor de variabile": "Arată câte variabile sunt de tip numeric, categorial, boolean, obiect (text) sau dată.\n\nAceastă informație este esențială pentru alegerea corectă a metodelor de preprocesare și analiză.",
	"Distribuția variabilei țintă": "Afișează distribuția clasei țintă (`target`), importantă pentru detectarea dezechilibrelor între clase.\n\nUn dezechilibru sever poate afecta performanța modelelor de clasificare.",
	"Statistici descriptive": "Oferă statistici relevante pentru fiecare variabilă, în funcție de tipul ei: medii, extreme, dispersie, modă, distribuție etc.\n\nAjută la înțelegerea comportamentului fiecărei variabile în mod individual.",
	"Matricea de corelație": "Prezintă corelațiile între variabile numerice. Coeficientul Pearson este folosit pentru a detecta relații liniare.\n\nPoate evidenția redundanțe sau relații utile pentru modelare.",
	"Variabilele puternic corelate cu ținta": "Identifică variabilele numerice care au o corelație puternică (pozitivă sau negativă) cu variabila țintă.\n\nAcestea pot fi predictori relevanți în modelele de clasificare.",
}

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

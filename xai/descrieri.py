DESCRIERI_XAI = {
	"bar": (
		"`Graficul SHAP Bar` prezintă importanța medie absolută a fiecărei caracteristici asupra predicției modelului, "
		"calculată pe întregul set de date. Caracteristicile sunt ordonate descrescător în funcție de influența lor. "
		"Este util pentru a înțelege care variabile contribuie cel mai mult la deciziile modelului."
	),
	"violin": (
		"`Graficul SHAP Violin` arată distribuția valorilor SHAP pentru fiecare caracteristică, reflectând atât influența, "
		"cât și variația acesteia între observații. Permite compararea efectelor caracteristicilor asupra predicției, "
		"inclusiv direcția (pozitivă sau negativă) și consistența impactului."
	),
	"waterfall": (
		"`Graficul SHAP Waterfall` explică predicția pentru o singură instanță, pornind de la valoarea de bază (baseline) și "
		"adăugând treptat contribuțiile fiecărei caracteristici. Este util pentru a înțelege de ce modelul a luat o "
		"anumită decizie pentru acel caz specific."
	),
	"lime": (
		"`Explicația LIME` arată contribuția locală a fiecărei caracteristici la predicția unei instanțe. Valorile "
		"pozitive și negative indică dacă o caracteristică a favorizat sau a contracarat predicția modelului. "
		"Caracteristicile sunt ordonate după influența lor asupra rezultatului."
	),
	"dice": (
		"`Explicațiile contrafactuale` oferă scenarii alternative în care predicția modelului s-ar fi schimbat. "
		"Se prezintă valorile caracteristicilor care trebuie modificate minim pentru a obține un rezultat diferit, "
		"oferind un ghid concret pentru acțiuni sau decizii."
	),
}

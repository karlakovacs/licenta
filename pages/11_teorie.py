import streamlit as st

from utils import nav_bar


st.set_page_config(layout="wide", page_title="Teorie", page_icon="📚")
nav_bar()

st.title("Modele de ML")

st.markdown(
	r"""
## Logistic Regression (LR)

Pentru o singură observație $x$, reprezentată ca un vector de caracteristici $[x_1, x_2, \dots, x_n]$, ieșirea clasificatorului $y$ poate fi $1$ (adică observația aparține clasei) sau $0$ (observația nu aparține clasei). Scopul este de a determina probabilitatea $P(y = 1 \mid x)$, adică probabilitatea ca observația să aparțină clasei pozitive.

Regresia logistică rezolvă această sarcină învățând, pe baza unui set de antrenament, un vector de ponderi $w_i$ și un termen de bias $b$. Fiecare pondere este un număr real asociat unei caracteristici de intrare $x_i$ și exprimă importanța acelei caracteristici în decizia de clasificare. O pondere pozitivă oferă dovezi în favoarea apartenenței la clasa pozitivă, iar una negativă – în favoarea clasei negative. Termenul de bias (sau interceptul) este un alt număr real care se adaugă la suma ponderată a intrărilor.

Rezultatul acestei combinații liniare este un număr real $z$, calculat astfel:
$$z = \sum_{i=1}^{n} w_i x_i + b$$

Funcția sigmoidă este apoi utilizată pentru a transforma acest scor $z$ într-o probabilitate:
$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

Funcția sigmoidă are proprietatea de a mapa orice valoare reală în intervalul $(0, 1)$, ceea ce o face potrivită pentru estimarea probabilităților. Astfel, pentru o observație $x$, se poate calcula probabilitatea $P(y = 1 \mid x)$. Clasificarea finală este realizată aplicând un prag: dacă $P(y = 1 \mid x) > 0.5$, se consideră că observația aparține clasei pozitive; în caz contrar, aparține clasei negative.

Sursa: [Speech and Language Processing. Daniel Jurafsky & James H. Martin. CHAPTER 5: Logistic Regression](https://web.stanford.edu/~jurafsky/slp3/5.pdf)
"""
)

st.markdown(
	r"""
## Linear Discriminant Analysis (LDA)

Analiza discriminantă liniară (LDA) utilizează funcții discriminante pentru a clasifica observațiile în clase, maximizând variația dintre clase și minimizând variația în interiorul claselor. Funcția discriminantă pentru clasa $k$ în LDA este derivată sub presupunerile că datele urmează o distribuție normală multivariată și că matricile de covarianță sunt egale între clase.

Funcția discriminantă LDA pentru clasa $k$ este:
$$\delta_k(x) = x^T \mathbf{\Sigma}^{-1} \mu_k - \frac{1}{2} \mu_k^T \mathbf{\Sigma}^{-1} \mu_k + \log(\pi_k)$$
unde $x$ = vectorul de caracteristici (de intrare), $\mu_k$ = vectorul mediu al clasei k, $\mathbf{\Sigma}$ = matricea de covarianță comună tuturor claselor, $\pi_k$ = probabilitatea a priori a clasei $k$, ce ia în considerare dezechilibrul între clase în stabilirea frontierei de decizie.

O observație $x$ este atribuită clasei $k$ care maximizează $\delta_k(x)$. În cazul a două clase, frontiera de decizie se reduce la un hiperplan liniar definit de egalitatea $\delta_1(x) = \delta_2(x)$.

[lol]:
- https://www.ibm.com/topics/linear-discriminant-analysis
- https://bookdown.org/tpinto_home/Regression-and-Classification/linear-discriminant-analysis.html
- https://www.engati.com/glossary/linear-discriminant-analysis
"""
)

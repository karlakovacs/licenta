import random

from plotly.colors import qualitative


def with_random_color(functie_plot):
	def wrapper(*args, **kwargs):
		culoare = random.choice(qualitative.Plotly)
		return functie_plot(*args, culoare=culoare, **kwargs)

	return wrapper

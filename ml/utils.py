import time

import numpy as np


def train_and_test(model, X_train, y_train, X_test, is_mlp: bool = False, epochs: int = 3, batch_size: int = 32) -> tuple[float, np.ndarray, np.ndarray]:
	timp_start = time.time()

	if is_mlp:
		model.fit(
			X_train,
			y_train,
			epochs=epochs,
			batch_size=batch_size,
			verbose=1,
		)
		proba = model.predict(X_test)
		y_prob = proba.flatten()
	else:
		model.fit(X_train, y_train)
		proba = model.predict_proba(X_test)
		y_prob = proba[:, 1]

	y_pred = (y_prob > 0.5).astype(int)
	timp_antrenare = time.time() - timp_start

	return timp_antrenare, y_pred, y_prob

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Utilizator(Base):
	__tablename__ = "utilizatori"

	id = Column(Integer, primary_key=True, autoincrement=True)
	google_id = Column(String, unique=True, nullable=False)
	email = Column(String, unique=True, nullable=False)
	created_at = Column(DateTime, default=datetime.now(timezone.utc))
	last_login = Column(DateTime, default=datetime.now(timezone.utc))

	preprocesari = relationship("Preprocesare", back_populates="utilizator")
	rapoarte = relationship("Raport", back_populates="utilizator")


class Preprocesare(Base):
	__tablename__ = "preprocesari"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_utilizator = Column(Integer, ForeignKey("utilizatori.id"), nullable=False)
	set_date = Column(Enum("MLG-ULB", "VESTA", name="tip_set_date"), nullable=False)
	optiune_selectie = Column(
		Enum("Testul Chi-Square", "Testul ANOVA", "Niciuna", name="tip_selectie"), nullable=False
	)
	nr_variabile = Column(Integer, nullable=True)
	optiune_dezechilibru = Column(
		Enum("Undersampling", "Oversampling", "ADASYN", "Niciuna", name="tip_dezechilibru"),
		nullable=False,
	)
	optiune_scalare = Column(
		Enum("StandardScaler", "MinMaxScaler", "RobustScaler", "Niciuna", name="tip_scalare"),
		nullable=False,
	)
	dimensiune_test = Column(Float, nullable=False)
	stratificat = Column(Boolean, nullable=False)
	created_at = Column(DateTime, default=datetime.now(timezone.utc))

	utilizator = relationship("Utilizator", back_populates="preprocesari")
	rulari = relationship("Rulare", back_populates="preprocesare")


class Rulare(Base):
	__tablename__ = "rulari"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_preprocesare = Column(Integer, ForeignKey("preprocesari.id"), nullable=False)
	model = Column(
		Enum(
			"AB",
			"CB",
			"DT",
			"GBC",
			"KNN",
			"LDA",
			"LGBM",
			"LR",
			"MLP",
			"QDA",
			"RF",
			"SVC",
			"XGB",
			name="tip_model",
		),
		nullable=False,
	)
	# id_metrici = Column(Integer, ForeignKey("metrici.id"), nullable=False)
	metrici = Column(JSON, nullable=False)
	timp_executie = Column(Float, nullable=False)
	hiperparametri = Column(JSON, nullable=True)
	created_at = Column(DateTime, default=datetime.now(timezone.utc))

	preprocesare = relationship("Preprocesare", back_populates="rulari")
	# metrici = relationship("Metrici", back_populates="rulari")
	grafice = relationship("Grafic", back_populates="rulare")
	rulari_rapoarte = relationship("RulareRaport", back_populates="rulare")


class Grafic(Base):
	__tablename__ = "grafice"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_rulare = Column(Integer, ForeignKey("rulari.id"), nullable=False)
	tip = Column(
		Enum(
			"Matrice de confuzie",
			"Curba ROC",
			"Curba PR",
			"SHAP Bar",
			"SHAP Waterfall",
			"SHAP Violin",
			"LIME",
			name="tip_grafic",
		),
		nullable=False,
	)
	url = Column(String, nullable=False)

	rulare = relationship("Rulare", back_populates="grafice")


class GraficComparativ(Base):
	__tablename__ = "grafice_comparative"

	id = Column(Integer, primary_key=True, autoincrement=True)
	url = Column(String, nullable=False)

	raport = relationship("Raport", back_populates="grafic_comparativ")


class Raport(Base):
	__tablename__ = "rapoarte"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_utilizator = Column(Integer, ForeignKey("utilizatori.id"), nullable=False)
	id_grafic_comparativ = Column(Integer, ForeignKey("grafice_comparative.id"), nullable=True)
	data_generare = Column(DateTime, default=datetime.now(timezone.utc))
	url = Column(String, nullable=False)

	utilizator = relationship("Utilizator", back_populates="rapoarte")
	grafic_comparativ = relationship("GraficComparativ", back_populates="raport")
	rulari_rapoarte = relationship("RulareRaport", back_populates="raport")


class RulareRaport(Base):
	__tablename__ = "rulari_rapoarte"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_rulare = Column(Integer, ForeignKey("rulari.id"), nullable=False)
	id_raport = Column(Integer, ForeignKey("rapoarte.id"), nullable=False)

	rulare = relationship("Rulare", back_populates="rulari_rapoarte")
	raport = relationship("Raport", back_populates="rulari_rapoarte")

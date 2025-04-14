from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Utilizator(Base):
	__tablename__ = "utilizatori"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_google = Column(String, unique=True, nullable=False)
	email = Column(String, unique=True, nullable=False)
	data_creare = Column(DateTime, default=datetime.now(timezone.utc))

	seturi_date = relationship("SetDate", back_populates="utilizator")
	preprocesari = relationship("Preprocesare", back_populates="utilizator")
	rapoarte = relationship("Raport", back_populates="utilizator")


class SetDate(Base):
	__tablename__ = "seturi_date"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_utilizator = Column(Integer, ForeignKey("utilizatori.id"), nullable=False)
	denumire = Column(String, nullable=False)
	sursa = Column(Enum("local", "kaggle", "predefinit", name="sursa_set_date"), nullable=False)
	url = Column(String, nullable=False)
	data_creare = Column(DateTime, default=datetime.now(timezone.utc))

	utilizator = relationship("Utilizator", back_populates="seturi_date")


class Preprocesare(Base):
	__tablename__ = "preprocesari"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_utilizator = Column(Integer, ForeignKey("utilizatori.id"), nullable=False)
	id_set_date = Column(Integer, ForeignKey("seturi_date.id"), nullable=False)
	optiune_selectie = Column(Enum("Testul Chi-Square", "Testul ANOVA", "Niciuna", name="tip_selectie"), nullable=False)
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
	data_creare = Column(DateTime, default=datetime.now(timezone.utc))

	utilizator = relationship("Utilizator", back_populates="preprocesari")
	rulari = relationship("Rulare", back_populates="preprocesare")


class Rulare(Base):
	__tablename__ = "rulari"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_preprocesare = Column(Integer, ForeignKey("preprocesari.id"), nullable=False)
	model = Column(
		Enum(
			"AB",
			"BRF",
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
	metrici = Column(JSON, nullable=False)
	timp_executie = Column(Float, nullable=False)
	hiperparametri = Column(JSON, nullable=True)
	data_creare = Column(DateTime, default=datetime.now(timezone.utc))

	preprocesare = relationship("Preprocesare", back_populates="rulari")


class Raport(Base):
	__tablename__ = "rapoarte"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_utilizator = Column(Integer, ForeignKey("utilizatori.id"), nullable=False)
	data_generare = Column(DateTime, default=datetime.now(timezone.utc))
	url = Column(String, nullable=False)

	utilizator = relationship("Utilizator", back_populates="rapoarte")

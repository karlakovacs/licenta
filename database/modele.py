from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Utilizator(Base):
	__tablename__ = "utilizatori"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_auth0 = Column(String, unique=True, nullable=False)
	data_creare = Column(DateTime, default=datetime.now())
	data_ultima_conectare = Column(DateTime, default=datetime.now())

	seturi_date = relationship("SetDateBrut", back_populates="utilizator", cascade="all, delete-orphan")


class SursaDate(Base):
	__tablename__ = "surse_date"

	id = Column(Integer, primary_key=True, autoincrement=True)
	denumire = Column(String, nullable=False)

	seturi_date = relationship("SetDateBrut", back_populates="sursa_date", cascade="all, delete-orphan")


class SetDateBrut(Base):
	__tablename__ = "seturi_date_brute"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_utilizator = Column(Integer, ForeignKey("utilizatori.id", ondelete="CASCADE"), nullable=True)
	id_sursa = Column(Integer, ForeignKey("surse_date.id", ondelete="CASCADE"), nullable=False)
	denumire = Column(String, nullable=False)
	tinta = Column(String, nullable=False)
	url = Column(String, nullable=False)
	data_creare = Column(DateTime, default=datetime.now())
	data_actualizare = Column(DateTime, default=datetime.now())

	utilizator = relationship("Utilizator", back_populates="seturi_date")
	sursa_date = relationship("SursaDate", back_populates="seturi_date")
	seturi_procesate = relationship("SetDateProcesat", back_populates="set_date_brut", cascade="all, delete-orphan")


class SetDateProcesat(Base):
	__tablename__ = "seturi_date_procesate"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_set_date = Column(Integer, ForeignKey("seturi_date_brute.id", ondelete="CASCADE"), nullable=False)
	denumire = Column(String, nullable=False)
	configuratie = Column(JSON)
	url = Column(String, nullable=False)
	data_procesare = Column(DateTime, default=datetime.now())

	set_date_brut = relationship("SetDateBrut", back_populates="seturi_procesate")
	modele = relationship("Model", back_populates="set_date_procesat", cascade="all, delete-orphan")
	rapoarte = relationship("Raport", back_populates="set_date_procesat", cascade="all, delete-orphan")


class Metrici(Base):
	__tablename__ = "metrici"

	id = Column(Integer, primary_key=True, autoincrement=True)
	prescurtare = Column(String, nullable=False)
	denumire = Column(String, nullable=False)

	metrici_model = relationship("ModeleMetrici", back_populates="metrica", cascade="all, delete-orphan")


class ModeleMetrici(Base):
	__tablename__ = "modele_metrici"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_model = Column(Integer, ForeignKey("modele.id", ondelete="CASCADE"), nullable=False)
	id_metrica = Column(Integer, ForeignKey("metrici.id", ondelete="CASCADE"), nullable=False)
	valoare = Column(Float, nullable=False)

	model = relationship("Model", back_populates="metrici")
	metrica = relationship("Metrici", back_populates="metrici_model")


class TipModel(Base):
	__tablename__ = "tipuri_modele"

	id = Column(Integer, primary_key=True, autoincrement=True)
	denumire = Column(String, nullable=False)

	modele = relationship("Model", back_populates="tip_model", cascade="all, delete-orphan")


class Model(Base):
	__tablename__ = "modele"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_set_date_procesat = Column(Integer, ForeignKey("seturi_date_procesate.id", ondelete="CASCADE"), nullable=False)
	id_tip_model = Column(Integer, ForeignKey("tipuri_modele.id", ondelete="SET NULL"), nullable=True)

	hiperparametri = Column(JSON, nullable=False)
	durata_antrenare = Column(Float, nullable=False)
	url = Column(String, nullable=False)
	data_antrenare = Column(DateTime, default=datetime.now())

	set_date_procesat = relationship("SetDateProcesat", back_populates="modele")
	tip_model = relationship("TipModel", back_populates="modele")
	metrici = relationship("ModeleMetrici", back_populates="model", cascade="all, delete-orphan")


class Raport(Base):
	__tablename__ = "rapoarte"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_set_date_procesat = Column(Integer, ForeignKey("seturi_date_procesate.id", ondelete="CASCADE"), nullable=False)
	url = Column(String, nullable=False)
	data_generare = Column(DateTime, default=datetime.now())

	set_date_procesat = relationship("SetDateProcesat", back_populates="rapoarte")

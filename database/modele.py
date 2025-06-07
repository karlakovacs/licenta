from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


# class Utilizator(Base):
# 	__tablename__ = "utilizatori"

# 	id = Column(Integer, primary_key=True, autoincrement=True)
# 	id_google = Column(String, unique=True, nullable=False)
# 	data_creare = Column(DateTime, default=datetime.now(timezone.utc))
# 	data_ultima_conectare = Column(DateTime, default=datetime.now(timezone.utc))

# 	seturi_date = relationship("SetDate", back_populates="utilizator")
# 	rapoarte = relationship("Raport", back_populates="utilizator")


class Utilizator(Base):
	__tablename__ = "utilizatori"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_google = Column(String, unique=True, nullable=True)
	id_supabase = Column(String, unique=True, nullable=True)
	email = Column(String, unique=True, nullable=False)
	nume = Column(String, nullable=True)
	data_creare = Column(DateTime, default=datetime.now(timezone.utc))
	data_ultima_conectare = Column(DateTime, default=datetime.now(timezone.utc))

	seturi_date = relationship("SetDate", back_populates="utilizator")
	rapoarte = relationship("Raport", back_populates="utilizator")


class SetDate(Base):
	__tablename__ = "seturi_date"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_utilizator = Column(Integer, ForeignKey("utilizatori.id"), nullable=False)
	denumire = Column(String, nullable=False)
	sursa = Column(Enum("Fișier local", "Link Kaggle", name="sursa_set_date"), nullable=False)
	url = Column(String, nullable=False)
	tinta = Column(String, nullable=False)
	data_creare = Column(DateTime, default=datetime.now(timezone.utc))
	data_actualizare = Column(DateTime, default=datetime.now(timezone.utc))

	utilizator = relationship("Utilizator", back_populates="seturi_date")


class Raport(Base):
	__tablename__ = "rapoarte"

	id = Column(Integer, primary_key=True, autoincrement=True)
	id_utilizator = Column(Integer, ForeignKey("utilizatori.id"), nullable=False)
	url = Column(String, nullable=False)
	data_generare = Column(DateTime, default=datetime.now(timezone.utc))

	utilizator = relationship("Utilizator", back_populates="rapoarte")

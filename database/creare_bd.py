from sqlalchemy.orm import sessionmaker

from database.config import engine
from database.modele import Base, Utilizator


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
db = Session()

utilizator = Utilizator(google_id="test", email="test@test.com")
db.add(utilizator)
db.commit()
db.close()

__author__ = 'Shtav'
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Shelter, Puppy, engine
import datetime

# Start the engine
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Query here

# filter by DoB
sixMonthsAgo = (datetime.date.today()-datetime.timedelta(6*365/12)).isoformat()
puppies = session.query(Puppy).filter(Puppy.dateOfBirth > sixMonthsAgo)

# order by weight
puppies = session.query(Puppy).group_by(Puppy.shelter_id)


for puppy in puppies:
    print(puppy.weight)


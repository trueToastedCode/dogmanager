from app import db, str_date
import datetime
from keys import *

MAX_NAME_LEN = 80


class Dog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_NAME_LEN), unique=False, nullable=False)

    def get_dict(self):
        return {
            KEY_ID: self.id,
            KEY_NAME: self.name
        }


class Feeding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(db.Integer, nullable=False)
    person_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)

    def get_dict(self):
        return {
            KEY_ID: self.id,
            KEY_DOG_ID: self.dog_id,
            KEY_PERSON_ID: self.person_id,
            KEY_DATE: str_date(self.date)
        }


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_NAME_LEN), nullable=False)

    def get_dict(self):
        return {
            KEY_ID: self.id,
            KEY_NAME: self.name
        }

    def feed(self, p_dog: Dog, p_date: datetime.datetime):
        feeding = Feeding(
            dog_id=p_dog.id,
            date=p_date,
            person_id=self.id,
        )
        db.session.add(feeding)
        db.session.commit()
        return feeding

    def walk(self, p_dog: Dog, p_date_start: datetime.datetime, p_date_end: datetime.datetime,
             p_pause_in_min: str):
        walk = Walk(
            dog_id=p_dog.id,
            person_id=self.id,
            date_start=p_date_start,
            date_end=p_date_end,
            pause_in_min=p_pause_in_min
        )
        db.session.add(walk)
        db.session.commit()
        return walk


class Walk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(db.Integer, nullable=False)
    person_id = db.Column(db.Integer, nullable=False)
    date_start = db.Column(db.Date, nullable=False, default=datetime.datetime.now)
    date_end = db.Column(db.Date, nullable=True)  # None -> Pending walk
    pause_in_min = db.Column(db.Integer, nullable=False)

    def get_dict(self):
        if self.date_end is None:
            date_end = None
        else:
            date_end = str_date(self.date_end)
        return {
            KEY_ID: self.id,
            KEY_DOG_ID: self.dog_id,
            KEY_PERSON_ID: self.person_id,
            KEY_DATE_START: str_date(self.date_start),
            KEY_DATE_END: date_end,
            KEY_PAUSE_IN_MIN: self.pause_in_min,
        }

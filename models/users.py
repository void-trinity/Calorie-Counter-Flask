from extensions import db
from math import floor


class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    gender = db.Column(db.String)
    age = db.Column(db.Integer)
    bmr = db.Column(db.Float)
    budget = db.Column(db.Integer)

    def __init__(self, name, weight, height, gender, age, username, password):
        self.name = name
        self.username = username
        self.password = password
        self.weight = weight
        self.height = height
        self.gender = gender
        self.age = age
        self.bmr = self.get_bmr()
        self.budget = floor(self.bmr * 1.2)

    def get_bmr(self):
        if self.gender == 'M':
            return 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        return 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'weight': self.weight,
            'height': self.height,
            'bmr': self.bmr,
            'age': self.age,
            'gender': self.gender,
            'budget': self.budget
        }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_username_password(cls, username, password):
        return cls.query.filter(cls.username.like(username), cls.password.like(password)).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

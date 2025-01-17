from extensions import db


class FoodModel(db.Model):
    __tablename__ = 'foods'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    serving_size = db.Column(db.String(100))
    calories = db.Column(db.Integer)

    def __init__(self, name, serving_size, calories):
        self.name = name
        self.serving_size = serving_size
        self.calories = calories

    @classmethod
    def find_by_name(cls, name):
        name = "%{}%".format(name)
        return cls.query.filter(cls.name.like(name)).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
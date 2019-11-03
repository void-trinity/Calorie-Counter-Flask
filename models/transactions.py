from extensions import db


class TransactionModel(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    food_id = db.Column(db.Integer)
    calorie_count = db.Column(db.Integer)

    def __init__(self, user_id, food_id, calorie_count=0):
        self.user_id = user_id
        self.food_id = food_id
        self.calorie_count = calorie_count

    @classmethod
    def find_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

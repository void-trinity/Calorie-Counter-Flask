from flask_restful import Resource, reqparse
from models.users import UserModel


class Users(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='This field cannot be blank', required=True)
        parser.add_argument('password', type=str, help='This field cannot be blank', required=True)

        data = parser.parse_args()

        username = data['username']
        password = data['password']

        user = UserModel.find_by_username_password(username, password)
        if user is not None:
            return user.json()
        return {'error': 'No user found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, type=str, help='This field cannot be blank')
        parser.add_argument('weight', required=True, type=float, help='This field cannot be blank')
        parser.add_argument('height', required=True, type=float, help='This field cannot be blank')
        parser.add_argument('gender', required=True, type=str, help='This field cannot be blank')
        parser.add_argument('age', required=True, type=int, help='This field cannot be blank')
        parser.add_argument('username', required=True, type=str, help='This field cannot be blank')
        parser.add_argument('password', required=True, type=str, help='This field cannot be blank')

        data = parser.parse_args()
        print(data)

        user = UserModel(
            name=data['name'],
            weight=data['weight'],
            height=data['height'],
            gender=data['gender'],
            age=data['age'],
            username=data['username'],
            password=data['password']
        )

        print(user.json())

        try:
            user.save_to_db()
        except Exception as e:
            print(e)
            return {'success': False, 'message': 'Server Error'}, 500

        return user.json(), 201

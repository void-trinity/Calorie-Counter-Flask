from flask import Flask
from flask_restful import Api
from routes.home import Home
from routes.users import Users
from routes.objectdetection import ObjectModel
from routes.images import Upload_Image, Get_Image, Test_Upload
from extensions import db

app = Flask(__name__, static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db.init_app(app)

api.add_resource(Home, '/')
api.add_resource(Users, '/user')
api.add_resource(ObjectModel, '/detectobject')
api.add_resource(Upload_Image, '/upload')
api.add_resource(Get_Image, '/image/<image>')
api.add_resource(Test_Upload, '/testupload')


if __name__ == "__main__":
    app.run()

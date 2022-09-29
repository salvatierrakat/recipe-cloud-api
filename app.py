from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_bcrypt import Bcrypt

import os

app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://fyszlckfhimhor:438d0acfc8bb5d9fdaced528a1558d03457ab8abce4edc250d4067c220893a00@ec2-3-219-19-205.compute-1.amazonaws.com:5432/d74kklupejjk1o" + \
    os.path.join(basedir, "app.sqlite")
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
CORS(app)


# recipe section

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)

    def __init__(self, recipe_name, instructions):
        self.recipe_name = recipe_name
        self.instructions = instructions


class RecipeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'recipe_name', 'instructions')


recipe_schema = RecipeSchema()
multiple_recipe_schema = RecipeSchema(many=True)


@app.route("/recipe/add", methods=["POST"])
def add_recipe():

    post_data = request.get_json()
    recipe_name = post_data.get("recipe_name")
    instructions = post_data.get("instructions")

    new_recipe = Recipe(recipe_name, instructions)
    db.session.add(new_recipe)
    db.session.commit()

    return jsonify("Recipe added!")


@app.route('/recipe', methods=["GET"])
def all_recipes():
    recipe_request = Recipe.query.all()
    recipe_results = multiple_recipe_schema.dump(
        recipe_request)
    return jsonify(recipe_results)


@app.route('/recipe/<id>', methods=["DELETE"])
def delete_recipe(id):
    recipe_to_delete = Recipe.query.get(id)
    db.session.delete(recipe_to_delete)
    db.session.commit()
    return jsonify('Recipe has been deleted')


# sign on section

class SignOn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


class SignOnSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password')


sign_on_schema = SignOnSchema()
multiple_signon_schema = SignOnSchema(many=True)


@app.route('/', methods=["GET"])
def homepage():
    return "Hello World"


@app.route('/users', methods=["GET"])
def all_users():
    signon_users = SignOn.query.all()
    results = multiple_signon_schema.dump(
        signon_users)
    return jsonify(results)


@app.route('/users', methods=["POST"])
def create_users():
    username = request.json['username']
    password = request.json['password']

    encrypted_password = bcrypt.generate_password_hash(
        password).decode('utf-8')
    new_user = SignOn(username, encrypted_password)

    db.session.add(new_user)
    db.session.commit()

    users = SignOn.query.get(new_user.id)
    return sign_on_schema.jsonify(users)


@app.route('/users/<id>', methods=["DELETE"])
def delete_user(id):
    user_to_delete = SignOn.query.get(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return jsonify('Username Deleted')


if __name__ == "__main__":
    app.run(debug=True)

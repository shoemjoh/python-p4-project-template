#!/usr/bin/env python3

# Standard library imports

# Remote library imports
from flask import request, session
from flask_restful import Resource

# Local imports
from config import app, db, api
# Add your model imports
from models import User, Review, Restaurant

# Views go here!
class Signup(Resource):
    def post(self):
        data = request.get_json()
        if 'username' not in data or 'password' not in data:
            return {"error": "Username and password required"}, 400
        user = User(
            username=data['username'],
            email=data.get('email',''),
        )
        user.password_hash = data['password']
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return user.to_dict(), 200

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter(User.username==data['username']).first()
        if user and user.check_password(data['password']):
            session['user_id']=user.id
            return user.to_dict(), 200
        return {"error": "Invalid username or password."}, 401

class ReviewCreate(Resource):
    def post(self):
        data = request.get_json()
        name = data['name']
        city = data['city']
        restaurant = Restaurant.query.filter(Restaurant.name==name, Restaurant.city==city).first()
        if not restaurant:
            restaurant = Restaurant(
                name=name,
                city=city
            )
            db.session.add(restaurant)
            db.session.commit()
        review = Review(
            content=data['content'],
            rating=data['rating'],
            user_id=data['user_id'],
            restaurant_id=restaurant.id
        )
        db.session.add(review)
        db.session.commit()
        return review.to_dict(), 201

class ReviewList(Resource):
    def get(self):
        city = request.args.get('city')
        if city:
            reviews = Review.query.join(Restaurant).filter(Restaurant.city == city).all()
        else:
            reviews = Review.query.all()
        return jsonify([review.to_dict() for review in reviews])

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.todict() for restaurant in restaurants], 200

class Reviews(Resource):
    def post(self):
        data = request.get_json()
        review = Review(
            content=data['content'],
            rating=data['rating'],
            user_id=data['user_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(review)
        db.session.commit()
        return review.to_dict(), 200
        

@app.route('/')
def index():
    return '<h1>Project Server</h1>'

api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Restaurants, '/restaurants')

api.add_resource(Reviews, '/reviews')


if __name__ == '__main__':
    app.run(port=5555, debug=True)


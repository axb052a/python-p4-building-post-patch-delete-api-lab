#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = Bakery.query.all()
    bakeries_serialized = [bakery.to_dict() for bakery in bakeries]

    response = make_response(
        jsonify(bakeries_serialized),
        200
    )
    return response

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()

    if bakery:
        bakery_serialized = bakery.to_dict()
        response = make_response(
            jsonify(bakery_serialized),
            200
        )
        return response
    else:
        return make_response(jsonify({'error': 'Bakery not found'}), 404)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]

    response = make_response(
        jsonify(baked_goods_by_price_serialized),
        200
    )
    return response

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()

    if most_expensive:
        most_expensive_serialized = most_expensive.to_dict()
        response = make_response(
            jsonify(most_expensive_serialized),
            200
        )
        return response
    else:
        return make_response(jsonify({'error': 'No baked goods found'}), 404)

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    try:
        data = request.form
        new_baked_good = BakedGood(
            name=data['name'],
            price=float(data['price']),
            description=data.get('description', '')
        )
        db.session.add(new_baked_good)
        db.session.commit()

        response = make_response(
            jsonify(new_baked_good.to_dict()),
            201  # Correct status code for successful creation
        )
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return make_response(jsonify({'error': 'Internal Server Error'}), 500)


@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    try:
        data = request.form
        bakery = Bakery.query.filter_by(id=id).first()

        if bakery:
            if 'name' in data:
                bakery.name = data['name']

            db.session.commit()

            response = make_response(
                jsonify(bakery.to_dict()),
                200
            )
            return response
        else:
            return make_response(jsonify({'error': 'Bakery not found'}), 404)
    except Exception as e:
        print(f"An error occurred: {e}")
        return make_response(jsonify({'error': 'Internal Server Error'}), 500)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    try:
        baked_good = BakedGood.query.filter_by(id=id).first()

        if baked_good:
            db.session.delete(baked_good)
            db.session.commit()

            response = make_response(
                jsonify({'message': 'Baked good deleted successfully'}),
                200
            )
            return response
        else:
            return make_response(jsonify({'error': 'Baked good not found'}), 404)
    except Exception as e:
        print(f"An error occurred: {e}")
        return make_response(jsonify({'error': 'Internal Server Error'}), 500)

if __name__ == '__main__':
    app.run(port=5555, debug=True)

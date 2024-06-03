from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        messages_serialized = [message.to_dict() for message in messages]
        return make_response(jsonify(messages_serialized), 200)

    if request.method == 'POST':
        data = request.form
        new_message = Message(
            body=data.get('body'),
            username=data.get('username'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_message)
        db.session.commit()
        return make_response(jsonify(new_message.to_dict()), 201)

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)
    
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    if request.method == 'GET':
        return make_response(jsonify(message.to_dict()), 200)
    
    if request.method == 'PATCH':
        data = request.form
        if 'body' in data:
            message.body = data.get('body')
            message.updated_at = datetime.utcnow()
            db.session.commit()
            return make_response(jsonify(message.to_dict()), 200)
        else:
            return make_response(jsonify({"error": "Invalid data"}), 400)
    
    if request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return make_response(jsonify({"message": "Message successfully deleted"}), 200)

if __name__ == '__main__':
    app.run(port=5555)

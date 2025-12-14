import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

INSTANCE_FOLDER_PATH = os.path.join(BASE_DIR, 'instance')
DB_PATH = os.path.join(INSTANCE_FOLDER_PATH, 'database.db')

if not os.path.exists(INSTANCE_FOLDER_PATH):
    os.makedirs(INSTANCE_FOLDER_PATH)
    print(f"Utworzono folder: {INSTANCE_FOLDER_PATH}")


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super_bardzo_tajny_klucz'

db = SQLAlchemy(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()


# Rejestracja 
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "Brak loginu lub hasła"}), 400


    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "Użytkownik już istnieje"}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Użytkownik utworzony pomyślnie"}), 200

# Logowanie 
@app.route('/token', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')


    print(f"--- DEBUG LOGOWANIA ---")
    print(f"Otrzymany login: '{username}'")
    print(f"Otrzymane hasło: '{password}'")
    
    user = User.query.filter_by(username=username).first()
    
    if user:
        print(f"Użytkownik '{username}' ZNALEZIONY w bazie.")
        haslo_ok = bcrypt.check_password_hash(user.password, password)
        print(f"Czy hasło pasuje?: {haslo_ok}")
    else:
        print(f"Użytkownik '{username}' NIE ISTNIEJE w bazie.")
    print("-----------------------")


    if not username or not password:
        return jsonify({"msg": "Brak danych logowania"}), 400

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    
    return jsonify({"msg": "Błędny login lub hasło"}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=8000)
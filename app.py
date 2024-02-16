from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    users = db.relationship('User', backref='company', lazy=True)

class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    
    user = db.relationship('User', backref='clients')

    
    company = db.relationship('Company', backref='clients')

    def __repr__(self):
        return f"Client(name={self.name}, email={self.email}, phone={self.phone})"

class ClientUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    deleted_at = db.Column(db.DateTime)
    active = db.Column(db.Boolean, nullable=False)




@app.route('/users', methods=['GET'])
def list_users():
    username = request.args.get('username')
    if username:
        users = User.query.filter_by(username=username).all()
    else:
        users = User.query.all()
    return jsonify([{'id': user.id, 'username': user.username} for user in users])


@app.route('/users/<int:user_id>', methods=['PUT'])
def replace_user(user_id):
    data = request.json
    user = User.query.get(user_id)
    if user:
        user.username = data.get('username')
        
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/clients', methods=['POST'])
def create_client():
    data = request.json
    company_name = data.get('company_name')
    if Client.query.filter_by(company_name=company_name).first():
        return jsonify({'error': 'Company already exists'}), 400
    client = Client(name=data.get('name'), email=data.get('email'), phone=data.get('phone'))
    
    client.user_id = data.get('user_id')
    client.company_id = data.get('company_id')
    db.session.add(client)
    db.session.commit()
    return jsonify({'message': 'Client created successfully'})


@app.route('/clients/<int:client_id>', methods=['PATCH'])
def change_client_fields(client_id):
    data = request.json
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    client.name = data.get('name', client.name)
    client.email = data.get('email', client.email)
    client.phone = data.get('phone', client.phone)
    db.session.commit()
    return jsonify({'message': 'Client fields updated successfully'})

if __name__ == '__main__':
    app.run(debug=True)
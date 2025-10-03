from flask import Flask
import app_secrets
from controller import order_bp, about_bp, home_bp, contact_bp
from models import db, Ingredient
from data import ingredients, drinks, desserts, customers
from Customer.auth import auth_bp


app = Flask(__name__)
app.secret_key = "super-secret-key-123"

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{app_secrets.username}:{app_secrets.password}@{app_secrets.db_ip}/pizza_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.register_blueprint(order_bp)
app.register_blueprint(about_bp)
app.register_blueprint(home_bp)
app.register_blueprint(contact_bp)

app.register_blueprint(auth_bp)

if __name__ == '__main__':
    with app.app_context():
        import sys
        if "initdb" in sys.argv:
            db.drop_all()
            db.create_all()
            # seed here...
            print("✅ Database initialized")
    app.run()
from flask import Flask, session
import app_secrets
from controller import order_bp, about_bp, home_bp, contact_bp
from models import db, Ingredient, Drink, Dessert, Order, Pizza, OrderDrink, OrderDessert, PizzaIngredient
from data import ingredients, drinks, desserts
from Customer.auth import auth_bp

app = Flask(__name__)
app.secret_key = "super-secret-key-123"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{app_secrets.username}:{app_secrets.password}@{app_secrets.db_ip}/pizza_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Register blueprints
app.register_blueprint(order_bp)
app.register_blueprint(about_bp)
app.register_blueprint(home_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(auth_bp)


with app.app_context():
    # Clear dependent tables first
    db.session.query(PizzaIngredient).delete()
    db.session.query(Pizza).delete()
    db.session.query(OrderDrink).delete()
    db.session.query(OrderDessert).delete()
    db.session.query(Order).delete()

    # Then your base tables
    db.session.query(Ingredient).delete()
    db.session.query(Drink).delete()
    db.session.query(Dessert).delete()

    # Re-seed base data
    db.session.add_all(ingredients + drinks + desserts)
    db.session.commit()

    app.run()

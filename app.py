from flask import Flask, session
import app_secrets
from controller import order_bp, about_bp, home_bp, contact_bp, reports_bp
from models import db, Ingredient, Drink, Dessert, Order, Pizza, OrderDrink, OrderDessert, PizzaIngredient
from data import ingredients, drinks, desserts, customers
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

app.register_blueprint(reports_bp)

@app.context_processor
def inject_customer():
    from flask import session
    from models import Customer

    customer = None
    customer_id = session.get("customer_id")
    if customer_id:
        customer = Customer.query.get(customer_id)
    return dict(customer=customer)

with app.app_context():
    # Only seed if there are no ingredients yet
    if not Ingredient.query.first():
        print("Seeding base data...")
        db.session.add_all(ingredients + drinks + desserts + customers)
        db.session.commit()
    else:
        print("Database already contains data, skipping seeding.")

app.run()
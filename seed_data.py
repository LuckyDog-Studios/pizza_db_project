import app_secrets
from models import *
from flask import Flask
from datetime import datetime, timedelta, timezone
import random

# ---- Import your app configuration (without circular import) ----
app = Flask(__name__)
app.secret_key = "super-secret-key-123"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{app_secrets.username}:{app_secrets.password}@{app_secrets.db_ip}/pizza_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# --- Helper Functions ---
def random_date(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def random_customer():
    first_names = ["John", "Jane", "Mike", "Sara", "Tom", "Anna", "Chris", "Emma"]
    last_names = ["Smith", "Doe", "Brown", "Johnson", "Lee", "Taylor"]
    birth_year = random.randint(1960, 2005)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    return Customer(
        FirstName=random.choice(first_names),
        LastName=random.choice(last_names),
        PasswordHash="hashedpassword",
        BirthDate=datetime(birth_year, birth_month, birth_day),
        PhoneNumber=f"06{random.randint(10000000,99999999)}",
        Email=f"user{random.randint(1000,9999)}@example.com",
        Street=f"Street {random.randint(1,50)}",
        HouseNumber=random.randint(1,200),
        City="CityName",
        PostalCode=f"{random.randint(1000,9999)}AB",
        TotalPizzasOrdered=random.randint(0,50)
    )

# --- Seed Database ---
with app.app_context():
    # 1. Create tables if they don’t exist
    db.create_all()

    # 2. Check if ingredients exist
    if not Ingredient.query.first():
        ingredients = [
            Ingredient(Name="Pepperoni", Price=1.5, IsVegetarian=False, IsVegan=False, CreateDate=datetime.now(timezone.utc)),
            Ingredient(Name="Mozzarella", Price=1.5, IsVegetarian=True, IsVegan=False, CreateDate=datetime.now(timezone.utc)),
            Ingredient(Name="Tomato Sauce", Price=0.0, IsVegetarian=True, IsVegan=True, CreateDate=datetime.now(timezone.utc)),
            # ... add the rest
        ]
        db.session.add_all(ingredients)
        db.session.commit()

    # 3. Seed drinks
    if not Drink.query.first():
        drinks = [
            Drink(Name="Coca Cola", Price=2.5, CreateDate=datetime.now(timezone.utc)),
            Drink(Name="Fanta", Price=2.5, CreateDate=datetime.now(timezone.utc)),
            Drink(Name="Iced Tea", Price=2.5, CreateDate=datetime.now(timezone.utc)),
        ]
        db.session.add_all(drinks)
        db.session.commit()

    # 4. Seed desserts
    if not Dessert.query.first():
        desserts = [
            Dessert(Name="Chocolate Cake", Price=5.5, CreateDate=datetime.now(timezone.utc)),
            Dessert(Name="Tiramisu", Price=5.8, CreateDate=datetime.now(timezone.utc)),
        ]
        db.session.add_all(desserts)
        db.session.commit()

    # 5. Seed customers
    if not Customer.query.first():
        customers = [random_customer() for _ in range(100)]
        db.session.add_all(customers)
        db.session.commit()

    # 6. Seed delivery persons
    if not DeliveryPerson.query.first():
        delivery_persons = [DeliveryPerson(Name=f"Delivery {i}", IsAvailable=True) for i in range(50)]
        db.session.add_all(delivery_persons)
        db.session.commit()

    # 7. Seed orders
    all_customers = Customer.query.all()
    all_delivery = DeliveryPerson.query.all()
    all_ingredients = Ingredient.query.all()
    all_drinks = Drink.query.all()
    all_desserts = Dessert.query.all()

    for _ in range(100):
        customer = random.choice(all_customers)
        delivery_person = random.choice(all_delivery)
        place_time = random_date(datetime(2025, 1, 1), datetime(2025, 10, 21))
        status = random.choice(["Paid", "Delivered", "Confirmed"])

        order = Order(
            customer=customer,
            DeliveryPersonId=delivery_person.DeliveryPersonId,
            PlaceDateTime=place_time,
            DeliveryDateTime=place_time + timedelta(hours=random.randint(1,3)),
            OrderStatus=status
        )
        db.session.add(order)
        db.session.flush()

        # Pizzas
        for _ in range(random.randint(1,3)):
            pizza = Pizza(OrderId=order.OrderId, Amount=random.randint(1,2), Finished=True)
            db.session.add(pizza)
            db.session.flush()
            for ing in random.sample(all_ingredients, random.randint(2,5)):
                db.session.add(PizzaIngredient(PizzaId=pizza.PizzaId, IngredientId=ing.IngredientId))

        # --- Add 0-2 drinks (without duplicates) ---
        drink_sample = random.sample(all_drinks, k=random.randint(0, min(2, len(all_drinks))))
        for drink in drink_sample:
            db.session.add(OrderDrink(
                OrderId=order.OrderId,
                DrinkId=drink.DrinkId,
                Amount=random.randint(1, 3)
            ))

        # --- Add 0-2 desserts (without duplicates) ---
        dessert_sample = random.sample(all_desserts, k=random.randint(0, min(2, len(all_desserts))))
        for dessert in dessert_sample:
            db.session.add(OrderDessert(
                OrderId=order.OrderId,
                DessertId=dessert.DessertId,
                Amount=random.randint(1, 2)
            ))

    db.session.commit()
    print("✅ Sample data inserted successfully!")

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = "customer"

    CustomerId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FirstName = db.Column(db.String(100), nullable=False)
    LastName = db.Column(db.String(100), nullable=False)
    PasswordHash = db.Column(db.String(200), nullable=False)
    BirthDate = db.Column(db.Date)
    PhoneNumber = db.Column(db.String(50))
    Email = db.Column(db.String(120), unique=True)
    Street = db.Column(db.String(200))
    HouseNumber = db.Column(db.Integer)
    City = db.Column(db.String(100))
    PostalCode = db.Column(db.String(20))
    TotalPizzasOrdered = db.Column(db.Integer, default=0)

    orders = db.relationship("Order", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer {self.CustomerId} {self.FirstName} {self.LastName}>"


class DeliveryPerson(db.Model):
    __tablename__ = "delivery_person"

    DeliveryPersonId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    IsAvailable = db.Column(db.Boolean, default=True)
    UnavailableUntil = db.Column(db.DateTime)

    orders = db.relationship("Order", back_populates="delivery_person")
    postal_assignments = db.relationship(
        "PostalAssignment", back_populates="delivery_person", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DeliveryPerson {self.DeliveryPersonId}>"


class Dessert(db.Model):
    __tablename__ = "dessert"

    DessertId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Price = db.Column(db.Numeric(10, 2), nullable=False)
    CreateDate = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    orders = db.relationship("OrderDessert", back_populates="dessert", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dessert {self.DessertId} {self.Name}>"


class DiscountCode(db.Model):
    __tablename__ = "discount_code"

    DiscountCodeId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Code = db.Column(db.String(50), unique=True, nullable=False)
    IsRedeemed = db.Column(db.Boolean, default=False)
    ExpiryDate = db.Column(db.Date)
    DiscountAmount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)  # flat discount in euros
    DiscountPercent = db.Column(db.Integer, default=0)  # e.g. 10 for 10%

    orders = db.relationship("Order", back_populates="discount_code")

    def __repr__(self):
        return f"<DiscountCode {self.Code} redeemed={self.IsRedeemed}>"


class Drink(db.Model):
    __tablename__ = "drink"

    DrinkId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Price = db.Column(db.Numeric(10, 2), nullable=False)
    CreateDate = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    orders = db.relationship("OrderDrink", back_populates="drink", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Drink {self.Name} €{self.Price}>"


class Ingredient(db.Model):
    __tablename__ = "ingredient"

    IngredientId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Price = db.Column(db.Numeric(10, 2), nullable=False)
    IsVegetarian = db.Column(db.Boolean, default=False)
    IsVegan = db.Column(db.Boolean, default=False)
    CreateDate = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    pizzas = db.relationship("PizzaIngredient", back_populates="ingredient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ingredient {self.Name} €{self.Price}>"


class OrderDessert(db.Model):
    __tablename__ = "order_dessert"

    OrderId = db.Column(db.Integer, db.ForeignKey("orders.OrderId"), primary_key=True)
    DessertId = db.Column(db.Integer, db.ForeignKey("dessert.DessertId"), primary_key=True)
    Amount = db.Column(db.Integer)

    order = db.relationship("Order", back_populates="desserts")
    dessert = db.relationship("Dessert", back_populates="orders")

    def __repr__(self):
        return f"<OrderDessert order={self.OrderId} dessert={self.DessertId} amount={self.Amount}>"


class OrderDrink(db.Model):
    __tablename__ = "order_drink"

    OrderId = db.Column(db.Integer, db.ForeignKey("orders.OrderId"), primary_key=True)
    DrinkId = db.Column(db.Integer, db.ForeignKey("drink.DrinkId"), primary_key=True)
    Amount = db.Column(db.Integer)

    order = db.relationship("Order", back_populates="drinks")
    drink = db.relationship("Drink", back_populates="orders")

    def __repr__(self):
        return f"<OrderDrink order={self.OrderId} drink={self.DrinkId} amount={self.Amount}>"


class Order(db.Model):
    __tablename__ = "orders"

    OrderId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CustomerId = db.Column(db.Integer, db.ForeignKey("customer.CustomerId"), nullable=False)
    PlaceDateTime = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    DeliveryDateTime = db.Column(db.DateTime)
    OrderStatus = db.Column(db.String(50))
    DiscountCodeId = db.Column(db.Integer, db.ForeignKey("discount_code.DiscountCodeId"))
    DeliveryPersonId = db.Column(db.Integer, db.ForeignKey("delivery_person.DeliveryPersonId"))

    customer = db.relationship("Customer", back_populates="orders")
    discount_code = db.relationship("DiscountCode", back_populates="orders")
    delivery_person = db.relationship("DeliveryPerson", back_populates="orders")

    drinks = db.relationship("OrderDrink", back_populates="order", cascade="all, delete-orphan")
    desserts = db.relationship("OrderDessert", back_populates="order", cascade="all, delete-orphan")
    pizzas = db.relationship("Pizza", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order {self.OrderId} Customer={self.CustomerId} Status={self.OrderStatus}>"


class Pizza(db.Model):
    __tablename__ = "pizza"

    PizzaId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderId = db.Column(db.Integer, db.ForeignKey("orders.OrderId"), nullable=False)
    Amount = db.Column(db.Integer)
    Finished = db.Column(db.Boolean, default=False)

    order = db.relationship("Order", back_populates="pizzas")
    ingredients = db.relationship("PizzaIngredient", back_populates="pizza", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Pizza {self.PizzaId} Order={self.OrderId} Amount={self.Amount} Finished={self.Finished}>"


class PizzaIngredient(db.Model):
    __tablename__ = "pizza_ingredient"

    PizzaId = db.Column(db.Integer, db.ForeignKey("pizza.PizzaId"), primary_key=True)
    IngredientId = db.Column(db.Integer, db.ForeignKey("ingredient.IngredientId"), primary_key=True)

    pizza = db.relationship("Pizza", back_populates="ingredients")
    ingredient = db.relationship("Ingredient", back_populates="pizzas")

    def __repr__(self):
        return f"<PizzaIngredient Pizza={self.PizzaId} Ingredient={self.IngredientId}>"


class PostalAssignment(db.Model):
    __tablename__ = "postal_assignments"

    PostalCode = db.Column(db.String(20), primary_key=True)
    DeliveryPersonId = db.Column(db.Integer, db.ForeignKey("delivery_person.DeliveryPersonId"), primary_key=True)

    delivery_person = db.relationship("DeliveryPerson", back_populates="postal_assignments")

    def __repr__(self):
        return f"<PostalAssignment PostalCode={self.PostalCode} DeliveryPerson={self.DeliveryPersonId}>"

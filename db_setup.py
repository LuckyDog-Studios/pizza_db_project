# db_setup.py
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    ForeignKey, DateTime, Date, Numeric, Table
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime
import secrets  # <-- create secrets.py with username, password, db_ip

Base = declarative_base()

# ===========================
# MODELS
# ===========================

class Customer(Base):
    __tablename__ = "customers"

    CustomerId = Column(Integer, primary_key=True)
    FirstName = Column(String(100), nullable=False)
    LastName = Column(String(100), nullable=False)
    BirthDate = Column(Date)
    PhoneNumber = Column(String(50))
    Email = Column(String(120), unique=True)
    Street = Column(String(200))
    HouseNumber = Column(Integer)
    City = Column(String(100))
    PostalCode = Column(String(20))
    TotalPizzasOrdered = Column(Integer, default=0)

    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    OrderId = Column(Integer, primary_key=True)
    CustomerId = Column(Integer, ForeignKey("customers.CustomerId"), nullable=False)
    PlaceDateTime = Column(DateTime, default=datetime.utcnow)
    DeliveryDateTime = Column(DateTime)
    OrderStatus = Column(String(50))

    DiscountCodeId = Column(Integer, ForeignKey("discount_codes.DiscountCodeId"))
    DeliveryPersonId = Column(Integer, ForeignKey("delivery_persons.DeliveryPersonId"))

    customer = relationship("Customer", back_populates="orders")
    pizzas = relationship("Pizza", back_populates="order", cascade="all, delete-orphan")
    drinks = relationship("OrderDrink", back_populates="order", cascade="all, delete-orphan")
    desserts = relationship("OrderDessert", back_populates="order", cascade="all, delete-orphan")


class Pizza(Base):
    __tablename__ = "pizzas"

    PizzaId = Column(Integer, primary_key=True)
    OrderId = Column(Integer, ForeignKey("orders.OrderId"), nullable=False)
    Amount = Column(Integer, default=1)
    Finished = Column(Boolean, default=False)

    order = relationship("Order", back_populates="pizzas")
    ingredients = relationship("PizzaIngredient", back_populates="pizza", cascade="all, delete-orphan")


class Ingredient(Base):
    __tablename__ = "ingredients"

    IngredientId = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)
    Price = Column(Numeric(10, 2), nullable=False)
    IsVegetarian = Column(Boolean, default=False)
    IsVegan = Column(Boolean, default=False)
    CreateDate = Column(DateTime, default=datetime.utcnow)

    pizzas = relationship("PizzaIngredient", back_populates="ingredient", cascade="all, delete-orphan")


class PizzaIngredient(Base):
    __tablename__ = "pizza_ingredients"

    PizzaId = Column(Integer, ForeignKey("pizzas.PizzaId"), primary_key=True)
    IngredientId = Column(Integer, ForeignKey("ingredients.IngredientId"), primary_key=True)

    pizza = relationship("Pizza", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="pizzas")


class Drink(Base):
    __tablename__ = "drinks"

    DrinkId = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)
    Price = Column(Numeric(10, 2), nullable=False)
    CreateDate = Column(DateTime, default=datetime.utcnow)


class Dessert(Base):
    __tablename__ = "desserts"

    DessertId = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)
    Price = Column(Numeric(10, 2), nullable=False)
    CreateDate = Column(DateTime, default=datetime.utcnow)


class OrderDrink(Base):
    __tablename__ = "order_drinks"

    OrderId = Column(Integer, ForeignKey("orders.OrderId"), primary_key=True)
    DrinkId = Column(Integer, ForeignKey("drinks.DrinkId"), primary_key=True)
    Amount = Column(Integer, default=1)

    order = relationship("Order", back_populates="drinks")
    drink = relationship("Drink")


class OrderDessert(Base):
    __tablename__ = "order_desserts"

    OrderId = Column(Integer, ForeignKey("orders.OrderId"), primary_key=True)
    DessertId = Column(Integer, ForeignKey("desserts.DessertId"), primary_key=True)
    Amount = Column(Integer, default=1)

    order = relationship("Order", back_populates="desserts")
    dessert = relationship("Dessert")


class DiscountCode(Base):
    __tablename__ = "discount_codes"

    DiscountCodeId = Column(Integer, primary_key=True)
    Code = Column(String(50), unique=True, nullable=False)
    IsRedeemed = Column(Boolean, default=False)
    ExpiryDate = Column(Date)


class DeliveryPerson(Base):
    __tablename__ = "delivery_persons"

    DeliveryPersonId = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)
    IsAvailable = Column(Boolean, default=True)
    UnavailableUntil = Column(DateTime)

    postal_assignments = relationship("PostalAssignment", back_populates="delivery_person", cascade="all, delete-orphan")


class PostalAssignment(Base):
    __tablename__ = "postal_assignments"

    PostalCode = Column(String(20), primary_key=True)
    DeliveryPersonId = Column(Integer, ForeignKey("delivery_persons.DeliveryPersonId"), primary_key=True)

    delivery_person = relationship("DeliveryPerson", back_populates="postal_assignments")


# ===========================
# DB CONNECTION + CREATE
# ===========================

DATABASE_URL = f"mysql+mysqlconnector://{secrets.username}:{secrets.password}@{secrets.db_ip}/pizza_db"  # change credentials
engine = create_engine(DATABASE_URL, echo=True)

# Create all tables
Base.metadata.create_all(engine)

# Optional: create a session
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

print("Database and tables created successfully!")

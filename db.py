# db_setup.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime

import secrets

Base = declarative_base()

# ----------------------
# Association Table: Pizza <-> Ingredient (Many-to-Many)
# ----------------------
pizza_ingredient_table = Table(
    'pizza_ingredient', Base.metadata,
    Column('pizza_id', Integer, ForeignKey('pizza.id'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredient.id'), primary_key=True)
)

# ----------------------
# Models
# ----------------------
class Pizza(Base):
    __tablename__ = 'pizza'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    vegetarian = Column(Boolean, default=False)
    vegan = Column(Boolean, default=False)
    ingredients = relationship('Ingredient', secondary=pizza_ingredient_table, back_populates='pizzas')

class Ingredient(Base):
    __tablename__ = 'ingredient'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    cost = Column(Float, nullable=False)
    type = Column(String(20))  # e.g., meat, veggie, dairy
    pizzas = relationship('Pizza', secondary=pizza_ingredient_table, back_populates='ingredients')

class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    orders = relationship('Order', back_populates='customer')

class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    order_time = Column(DateTime, default=datetime.utcnow)
    delivery_person_id = Column(Integer, ForeignKey('delivery_person.id'), nullable=True)
    discount_code_id = Column(Integer, ForeignKey('discount_code.id'), nullable=True)

    customer = relationship('Customer', back_populates='orders')
    delivery_person = relationship('DeliveryPerson', back_populates='orders')
    discount_code = relationship('DiscountCode', back_populates='orders')
    items = relationship('OrderItem', back_populates='order')

class OrderItem(Base):
    __tablename__ = 'order_item'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    pizza_id = Column(Integer, ForeignKey('pizza.id'))
    quantity = Column(Integer, default=1)

    order = relationship('Order', back_populates='items')
    pizza = relationship('Pizza')

class DeliveryPerson(Base):
    __tablename__ = 'delivery_person'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(20))
    orders = relationship('Order', back_populates='delivery_person')

class DiscountCode(Base):
    __tablename__ = 'discount_code'
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    percentage = Column(Float, nullable=False)
    orders = relationship('Order', back_populates='discount_code')


# ----------------------
# Database Setup
# ----------------------
DATABASE_URL = f"mysql+mysqlconnector://{secrets.username}:{secrets.password}@{secrets.db_ip}/pizza_db"  # <- change credentials
engine = create_engine(DATABASE_URL, echo=True)

# Create all tables
Base.metadata.create_all(engine)

# Optional: create a session
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

print("All tables created successfully!")

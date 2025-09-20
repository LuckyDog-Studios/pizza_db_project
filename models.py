from sqlalchemy import Column, Integer, String, Boolean, Float, Table, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

# Many-to-many table
pizza_ingredient_table = Table(
    'PizzaIngredient', Base.metadata,
    Column('pizza_id', Integer, ForeignKey('Pizza.id'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('Ingredient.id'), primary_key=True)
)

class Pizza(Base):
    __tablename__ = 'Pizza'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    vegetarian = Column(Boolean, nullable=False)
    vegan = Column(Boolean, nullable=False)
    ingredients = relationship('Ingredient', secondary=pizza_ingredient_table, back_populates='pizzas')

class Ingredient(Base):
    __tablename__ = 'Ingredient'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    cost = Column(Float, nullable=False)
    type = Column(String(20))  # 'meat', 'veggie', 'dairy', etc.
    pizzas = relationship('Pizza', secondary=pizza_ingredient_table, back_populates='ingredients')


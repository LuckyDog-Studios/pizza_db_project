from models import *
from sqlalchemy import Date

ingredients = [
    # Meats
    Ingredient(Name="Pepperoni", Price=1.50, IsVegetarian=False, IsVegan=False, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="Salami", Price=1.50, IsVegetarian=False, IsVegan=False, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="Ham", Price=1.50, IsVegetarian=False, IsVegan=False, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="Chicken", Price=1.80, IsVegetarian=False, IsVegan=False, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="Beef", Price=1.80, IsVegetarian=False, IsVegan=False, CreateDate=datetime.now(timezone.utc)),

    # Vegetables
    Ingredient(Name="Black Olive", Price=1.00, IsVegetarian=True, IsVegan=True, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="Mushrooms", Price=1.00, IsVegetarian=True, IsVegan=True, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="Onions", Price=0.80, IsVegetarian=True, IsVegan=True, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="Green Peppers", Price=1.00, IsVegetarian=True, IsVegan=True, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="Pineapple", Price=1.00, IsVegetarian=True, IsVegan=True, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="Basil", Price=0.80, IsVegetarian=True, IsVegan=True, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="Corn", Price=0.80, IsVegetarian=True, IsVegan=True, CreateDate=datetime.now(timezone.utc)),

    # Cheese + Base
    Ingredient(Name="Mozzarella", Price=1.50, IsVegetarian=True, IsVegan=False, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="Parmesan", Price=1.50, IsVegetarian=True, IsVegan=False, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="Tomato Sauce", Price=0.00, IsVegetarian=True, IsVegan=True, CreateDate=datetime.now(timezone.utc)),
    Ingredient(Name="BBQ Sauce", Price=0.00, IsVegetarian=True, IsVegan=True, CreateDate=datetime.now(timezone.utc)),
]

# DRINKS
drinks = [
    Drink(Name="Coca Cola", Price=2.50, CreateDate=datetime.now(timezone.utc)),
    Drink(Name="Fanta", Price=2.50, CreateDate=datetime.now(timezone.utc)),
    Drink(Name="Ice Tea", Price=2.50, CreateDate=datetime.now(timezone.utc)),
    Drink(Name="Sprite", Price=2.50, CreateDate=datetime.now(timezone.utc)),
]

# DESSERTS
desserts = [
    Dessert(Name="Chocolate Cake", Price=5.50, CreateDate=datetime.now(timezone.utc)),
    Dessert(Name="Tiramisu", Price=5.80, CreateDate=datetime.now(timezone.utc)),
    Dessert(Name="Crème Brulee", Price=6.00, CreateDate=datetime.now(timezone.utc)),
    Dessert(Name="Vanilla Ice Cream", Price=4.50, CreateDate=datetime.now(timezone.utc)),
]

#CUSTOM CUSTOMERS

customers = [
    Customer(CustomerId=1, FirstName="Noah", LastName="Janssen",BirthDate=None, PhoneNumber=None, Email="noahmjanssen@gmail.com"),
]
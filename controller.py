from flask import Blueprint, render_template, redirect, url_for, request, session, flash

from models import Ingredient, db, PizzaIngredient, Pizza, Order, Customer

order_bp = Blueprint('order', __name__)
home_bp = Blueprint('home', __name__)
contact_bp = Blueprint('contact', __name__)
about_bp = Blueprint('about', __name__)

#Orders page logic
@order_bp.route('/order', methods=['GET'])
def order():
    #  Use logged-in customer
    customer_id = session.get("customer_id")

    if not customer_id:
        flash("Please log in to view your orders.", "error")
        return redirect(url_for("auth.login"))

    customer = Customer.query.get(customer_id)

    # Get the customer's pending order
    order_obj = Order.query.filter_by(CustomerId=customer.CustomerId, OrderStatus="Pending").first()

    pizza_list = []
    total_order_price = 0
    if order_obj:
        for idx, p in enumerate(order_obj.pizzas, start=1):
            # List of ingredient names for this pizza
            ingredients = [pi.ingredient.Name for pi in p.ingredients]

            for ingredient in p.ingredients:
                print("Name: ",ingredient.ingredient.Name,"price:", ingredient.ingredient.Price)

            # Sum price of ingredients
            pizza_price = sum(float(pizza_ingredient.ingredient.Price) for pizza_ingredient in p.ingredients)
            total_order_price += pizza_price

            # Format the pizza text for the list item
            pizza_entry = f"Custom Pizza #{idx}: {', '.join(ingredients)} - €{pizza_price:.2f}"
            pizza_list.append(pizza_entry)

    return render_template(
        'order.html',
        active_page='order',
        order=pizza_list,
        total_price=f"{total_order_price:.2f}"
    )
@order_bp.route('/order/confirm', methods=['POST'])
def confirm_order():
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please log in to confirm your order.", "error")
        return redirect(url_for("auth.login"))

    order = Order.query.filter_by(CustomerId=customer_id, OrderStatus="Pending").first()
    if not order:
        flash("No pending order to confirm.", "error")
        return redirect(url_for("order.order"))

    order.OrderStatus = "Confirmed"
    db.session.commit()

    flash("Your order has been confirmed!", "success")
    return redirect(url_for("order.order"))


@order_bp.route('/order/add', methods=['POST'])
def add_to_order():
    data = request.form
    selected_ingredient_names = list(data.keys())

    if not selected_ingredient_names:
        flash("No ingredients selected.", "error")
        return redirect(url_for("order.order"))

    #Use logged-in customer
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please log in before adding to your order.", "error")
        return redirect(url_for("auth.login"))

    customer = Customer.query.get(customer_id)

    # Create a new order (or fetch an existing "pending" order)
    order = Order.query.filter_by(CustomerId=customer.CustomerId, OrderStatus="Pending").first()
    if not order:
        order = Order(CustomerId=customer.CustomerId, OrderStatus="Pending")
        db.session.add(order)
        db.session.commit()

    # Create a new pizza
    pizza = Pizza(OrderId=order.OrderId, Amount=1, Finished=False)
    db.session.add(pizza)
    db.session.commit()

    # Add ingredients to the pizza
    for ingredient_name in selected_ingredient_names:
        ingredient = Ingredient.query.filter_by(Name=ingredient_name.replace("_", " ").title()).first()
        if ingredient:
            db.session.add(PizzaIngredient(PizzaId=pizza.PizzaId, IngredientId=ingredient.IngredientId))
    db.session.commit()

    flash("Pizza added to your order!", "success")
    return redirect(url_for("order.order"))



#Home page logic
@home_bp.route('/home')
def home():
    return render_template('home.html', active_page='home')

#About page logic
@about_bp.route('/about')
def about():
    return render_template('about.html', active_page='about')

#Contact page logic
@contact_bp.route('/contact')
def contact():
    return render_template('contact.html', active_page='contact')


# reroute to home page
@home_bp.route('/')
def reroute_to_home_page():
    return redirect(url_for('home.home'))

from flask import Blueprint, render_template, redirect, url_for, request, session, flash

from models import Ingredient, db, PizzaIngredient, Pizza, Order, Customer, OrderDrink, Drink, OrderDessert, Dessert

order_bp = Blueprint('order', __name__)
home_bp = Blueprint('home', __name__)
contact_bp = Blueprint('contact', __name__)
about_bp = Blueprint('about', __name__)

#Orders page logic
@order_bp.route('/order', methods=['GET'])
def order():
    # Use logged-in customer
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please log in to view your orders.", "error")
        return redirect(url_for("auth.login"))

    customer = Customer.query.get(customer_id)

    # Get the customer's pending order
    order_obj = Order.query.filter_by(CustomerId=customer.CustomerId, OrderStatus="Pending").first()

    pizzas = []
    drinks = []
    desserts = []
    total_order_price = 0

    if order_obj:
        # --- PIZZAS ---
        for idx, p in enumerate(order_obj.pizzas, start=1):
            ingredients = [pi.ingredient.Name for pi in p.ingredients]
            pizza_price = sum(float(pi.ingredient.Price) for pi in p.ingredients)
            total_order_price += pizza_price

            pizzas.append({
                "id": p.PizzaId,
                "name": f"Custom Pizza #{idx}",
                "ingredients": ingredients,
                "price": f"{pizza_price:.2f}"
            })

        # --- DRINKS ---
        for od in order_obj.drinks:
            drink = od.drink
            amount = od.Amount or 1
            drink_total = float(drink.Price) * amount
            total_order_price += drink_total

            drinks.append({
                "id": drink.DrinkId,
                "name": drink.Name,
                "amount": amount,
                "price": f"{drink_total:.2f}"
            })

        # --- DESSERTS ---
        for od in order_obj.desserts:
            dessert = od.dessert
            amount = od.Amount or 1
            dessert_total = float(dessert.Price) * amount
            total_order_price += dessert_total

            desserts.append({
                "id": dessert.DessertId,
                "name": dessert.Name,
                "amount": amount,
                "price": f"{dessert_total:.2f}"
            })

    # Debug print
    print("ORDER ITEMS:", pizzas, drinks, desserts)

    return render_template(
        'order.html',
        active_page='order',
        pizzas=pizzas,
        drinks=drinks,
        desserts=desserts,
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
    form_id = request.form.get("form_id")
    data = request.form

    # --- PIZZA LOGIC ---
    if form_id == "add-order-form":
        selected_ingredient_names = list(data.keys())

        if not selected_ingredient_names:
            flash("No ingredients selected.", "error")
            return redirect(url_for("order.order"))

        customer_id = session.get("customer_id")
        if not customer_id:
            flash("Please log in before adding to your order.", "error")
            return redirect(url_for("auth.login"))

        customer = Customer.query.get(customer_id)
        order = Order.query.filter_by(CustomerId=customer.CustomerId, OrderStatus="Pending").first()
        if not order:
            order = Order(CustomerId=customer.CustomerId, OrderStatus="Pending")
            db.session.add(order)
            db.session.commit()

        pizza = Pizza(OrderId=order.OrderId, Amount=1, Finished=False)
        db.session.add(pizza)
        db.session.commit()

        for ingredient_name in selected_ingredient_names:
            ingredient = Ingredient.query.filter_by(Name=ingredient_name.replace("_", " ").title()).first()
            if ingredient:
                db.session.add(PizzaIngredient(PizzaId=pizza.PizzaId, IngredientId=ingredient.IngredientId))
        db.session.commit()

        flash("Pizza added to your order!", "success")
        return redirect(url_for("order.order"))

    # --- DRINK LOGIC ---
    elif form_id == "drink-add-order-form":
        drink_name = data.get("drink")

        if not drink_name:
            flash("No drink selected.", "error")
            return redirect(url_for("order.order"))

        # Ensure user logged in
        customer_id = session.get("customer_id")
        if not customer_id:
            flash("Please log in before adding to your order.", "error")
            return redirect(url_for("auth.login"))

        customer = Customer.query.get(customer_id)

        # Get or create a pending order
        order = Order.query.filter_by(CustomerId=customer.CustomerId, OrderStatus="Pending").first()
        if not order:
            order = Order(CustomerId=customer.CustomerId, OrderStatus="Pending")
            db.session.add(order)
            db.session.commit()

        # Find the drink in the database
        drink = Drink.query.filter_by(Name=drink_name).first()

        if not drink:
            flash(f"Drink '{drink_name}' not found in database.", "error")
            return redirect(url_for("order.order"))

        # Check if the drink is already in this order → just increase amount
        existing_order_drink = OrderDrink.query.filter_by(OrderId=order.OrderId, DrinkId=drink.DrinkId).first()

        if existing_order_drink:
            existing_order_drink.Amount += 1
        else:
            new_order_drink = OrderDrink(OrderId=order.OrderId, DrinkId=drink.DrinkId, Amount=1)
            db.session.add(new_order_drink)

        db.session.commit()

        flash(f"{drink_name} added to your order!", "success")
    # --- DESSERT LOGIC ---
    elif form_id == "dessert-add-order-form":
        dessert_name = data.get("dessert")
        if not dessert_name:
            flash("No dessert selected.", "error")
            return redirect(url_for("order.order"))

        # Ensure user logged in
        customer_id = session.get("customer_id")
        if not customer_id:
            flash("Please log in before adding to your order.", "error")
            return redirect(url_for("auth.login"))

        customer = Customer.query.get(customer_id)

        # Get or create a pending order
        order = Order.query.filter_by(CustomerId=customer.CustomerId, OrderStatus="Pending").first()
        if not order:
            order = Order(CustomerId=customer.CustomerId, OrderStatus="Pending")
            db.session.add(order)
            db.session.commit()

        # Find the dessert in the database
        dessert = Dessert.query.filter_by(Name=dessert_name).first()
        if not dessert:
            flash(f"Dessert '{dessert_name}' not found in database.", "error")
            return redirect(url_for("order.order"))

        # Check if the dessert is already in this order → just increase amount
        existing_order_dessert = OrderDessert.query.filter_by(OrderId=order.OrderId,
                                                              DessertId=dessert.DessertId).first()
        if existing_order_dessert:
            existing_order_dessert.Amount += 1
        else:
            new_order_dessert = OrderDessert(OrderId=order.OrderId, DessertId=dessert.DessertId, Amount=1)
            db.session.add(new_order_dessert)

        db.session.commit()
        flash(f"{dessert_name} added to your order!", "success")

    return redirect(url_for("order.order"))


@order_bp.route('/order/remove_item', methods=['POST'])
def remove_item():
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please log in first.", "error")
        return redirect(url_for("order.order"))

    order = Order.query.filter_by(CustomerId=customer_id, OrderStatus="Pending").first()
    if not order:
        flash("No pending order.", "error")
        return redirect(url_for("order.order"))

    # Remove pizza by ID
    pizza_id = request.form.get("pizza_id")
    if pizza_id:
        pizza = Pizza.query.get(int(pizza_id))
        if pizza:
            db.session.delete(pizza)
            db.session.commit()
            flash("Pizza removed from order.", "success")
        return redirect(url_for("order.order"))

    # Remove drink by ID
    drink_id = request.form.get("drink_id")
    if drink_id:
        order_drink = OrderDrink.query.get((order.OrderId, int(drink_id)))
        if order_drink:
            db.session.delete(order_drink)
            db.session.commit()
            flash("Drink removed from order.", "success")
        return redirect(url_for("order.order"))

    # Remove dessert by ID
    dessert_id = request.form.get("dessert_id")
    if dessert_id:
        order_dessert = OrderDessert.query.get((order.OrderId, int(dessert_id)))
        if order_dessert:
            db.session.delete(order_dessert)
            db.session.commit()
            flash("Dessert removed from order.", "success")
        return redirect(url_for("order.order"))

    flash("Item not found.", "error")
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

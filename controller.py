from flask import Blueprint, render_template, redirect, url_for, request, session, flash

from models import Ingredient, db, PizzaIngredient, Pizza, Order, Customer, DiscountCode
from datetime import date
from models import Ingredient, db, PizzaIngredient, Pizza, Order, Customer, OrderDrink, Drink, OrderDessert, Dessert

order_bp = Blueprint('order', __name__)
home_bp = Blueprint('home', __name__)
contact_bp = Blueprint('contact', __name__)
about_bp = Blueprint('about', __name__)

#Orders page logic
@order_bp.route('/order', methods=['GET'])
def order():
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please log in to view your orders.", "error")
        return redirect(url_for("auth.login"))

    customer = Customer.query.get(customer_id)

    # Check for any existing unpaid confirmed order
    confirmed_order = Order.query.filter_by(CustomerId=customer.CustomerId, OrderStatus="Confirmed").first()
    if confirmed_order:
        flash("⚠ You already have a confirmed unpaid order. Please go to 'My Orders' to pay or delete it.", "error")
        return redirect(url_for("order.order_history"))

    # Get or create a new pending order
    order_obj = (
        Order.query
        .filter_by(CustomerId=customer.CustomerId, OrderStatus="Pending")
        .first()
    )

    if not order_obj:
        order_obj = Order(CustomerId=customer.CustomerId, OrderStatus="Pending")
        db.session.add(order_obj)
        db.session.commit()

    pizzas, drinks, desserts = [], [], []
    total_order_price = 0

    # --- PIZZAS ---
    for idx, p in enumerate(order_obj.pizzas, start=1):
        ingredients = [pi.ingredient.Name for pi in p.ingredients]
        pizza_price = sum(float(pi.ingredient.Price) for pi in p.ingredients)
        total_order_price += pizza_price
        pizzas.append({
            "id": p.PizzaId,
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

    # Handle coupon input
    coupon_code = request.form.get("coupon", "").strip().upper()
    discount_applied = 0

    if coupon_code:
        discount = DiscountCode.query.filter_by(Code=coupon_code, IsRedeemed=False).first()
        if discount and (not discount.ExpiryDate or discount.ExpiryDate >= date.today()):
            discount_applied = discount.DiscountPercent
            order.DiscountCodeId = discount.DiscountCodeId
            discount.IsRedeemed = True

            db.session.add(order)
            db.session.add(discount)

            flash(f"Coupon '{coupon_code}' applied! You saved {discount_applied}%.", "success")
        else:
            flash("Invalid or expired coupon code.", "error")

    # Calculate total price
    total_price = 0
    for pizza in order.pizzas:
        pizza_price = sum(float(pi.ingredient.Price) for pi in pizza.ingredients)
        total_price += pizza_price

    if discount_applied > 0:
        total_price *= (1 - discount_applied / 100)

    order.OrderStatus = "Confirmed"
    db.session.commit()

    flash("Your order has been confirmed!", "success")
    return redirect(url_for("order.order"))







@order_bp.route('/order/add', methods=['POST'])
def add_to_order():
    form_id = request.form.get("form_id")
    customer_id = session.get("customer_id")

    if not customer_id:
        flash("Please log in before adding to your order.", "error")
        return redirect(url_for("auth.login"))

    # --- Block if there's a confirmed unpaid order ---
    unpaid_confirmed = Order.query.filter_by(CustomerId=customer_id, OrderStatus="Confirmed").first()
    if unpaid_confirmed:
        flash("⚠ You already have a confirmed unpaid order. Please go to 'My Orders' to pay or delete it.", "error")
        return redirect(url_for("order.order_history"))

    # --- Ensure a pending order exists ---
    customer = Customer.query.get(customer_id)
    order = Order.query.filter_by(CustomerId=customer.CustomerId, OrderStatus="Pending").first()
    if not order:
        order = Order(CustomerId=customer.CustomerId, OrderStatus="Pending")
        db.session.add(order)
        db.session.commit()

    # --- PIZZA LOGIC ---
    if form_id == "add-order-form":
        # Only collect checked boxes, ignore form_id/csrf_token
        selected_ingredient_names = [
            key for key in request.form.keys()
            if key not in ("form_id", "csrf_token")
        ]

        if not selected_ingredient_names:
            flash("⚠ Please select at least one ingredient.", "error")
            return redirect(url_for("order.order"))

        # Create the pizza
        pizza = Pizza(OrderId=order.OrderId, Amount=1, Finished=False)
        db.session.add(pizza)
        db.session.commit()

        # Link each selected ingredient
        for name in selected_ingredient_names:
            formatted_name = name.replace("_", " ").title()
            ingredient = Ingredient.query.filter_by(Name=formatted_name).first()
            if ingredient:
                db.session.add(PizzaIngredient(PizzaId=pizza.PizzaId, IngredientId=ingredient.IngredientId))
        db.session.commit()

        flash("🍕 Pizza added to your order!", "success")

    # --- DRINK LOGIC ---
    elif form_id == "drink-add-order-form":
        drink_name = request.form.get("drink")
        if not drink_name:
            flash("⚠ No drink selected.", "error")
            return redirect(url_for("order.order"))

        drink = Drink.query.filter_by(Name=drink_name).first()
        if not drink:
            flash(f"Drink '{drink_name}' not found in database.", "error")
            return redirect(url_for("order.order"))

        existing = OrderDrink.query.filter_by(OrderId=order.OrderId, DrinkId=drink.DrinkId).first()
        if existing:
            existing.Amount += 1
        else:
            db.session.add(OrderDrink(OrderId=order.OrderId, DrinkId=drink.DrinkId, Amount=1))
        db.session.commit()
        flash(f"🥤 {drink_name} added to your order!", "success")

    # --- DESSERT LOGIC ---
    elif form_id == "dessert-add-order-form":
        dessert_name = request.form.get("dessert")
        if not dessert_name:
            flash("⚠ No dessert selected.", "error")
            return redirect(url_for("order.order"))

        dessert = Dessert.query.filter_by(Name=dessert_name).first()
        if not dessert:
            flash(f"Dessert '{dessert_name}' not found in database.", "error")
            return redirect(url_for("order.order"))

        existing = OrderDessert.query.filter_by(OrderId=order.OrderId, DessertId=dessert.DessertId).first()
        if existing:
            existing.Amount += 1
        else:
            db.session.add(OrderDessert(OrderId=order.OrderId, DessertId=dessert.DessertId, Amount=1))
        db.session.commit()
        flash(f"🍰 {dessert_name} added to your order!", "success")

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
        order_drink = OrderDrink.query.filter_by(OrderId=order.OrderId, DrinkId=int(drink_id)).first()
        if order_drink:
            if order_drink.Amount > 1:
                order_drink.Amount -= 1
                db.session.commit()
                flash("One drink removed from order.", "success")
            else:
                db.session.delete(order_drink)
                db.session.commit()
                flash("Drink removed from order.", "success")
        return redirect(url_for("order.order"))

    # Remove dessert by ID
    dessert_id = request.form.get("dessert_id")
    if dessert_id:
        order_dessert = OrderDessert.query.filter_by(OrderId=order.OrderId, DessertId=int(dessert_id)).first()
        if order_dessert:
            if order_dessert.Amount > 1:
                order_dessert.Amount -= 1
                db.session.commit()
                flash("One dessert removed from order.", "success")
            else:
                db.session.delete(order_dessert)
                db.session.commit()
                flash("Dessert removed from order.", "success")
        return redirect(url_for("order.order"))

    flash("Item not found.", "error")
    return redirect(url_for("order.order"))








@order_bp.route('/order/checkout', methods=['GET', 'POST'])
def checkout():
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please log in to continue.", "error")
        return redirect(url_for("auth.login"))

    # --- Block checkout if a confirmed unpaid order exists ---
    confirmed_unpaid = Order.query.filter_by(CustomerId=customer_id, OrderStatus="Confirmed").first()
    if confirmed_unpaid:
        flash("️ Order cannot be accepted because you already have a confirmed unpaid order. Please checkout 'My Orders' before creating a new one.", "error")
        return redirect(url_for("order.order"))

    # --- Get the current pending order ---
    order = Order.query.filter_by(CustomerId=customer_id, OrderStatus="Pending").first()
    if not order:
        flash("⚠ Can't go to checkout without ordering anything.", "error")
        return redirect(url_for("order.order"))

    # --- Prevent empty order checkout ---
    if not order.pizzas and not order.drinks and not order.desserts:
        flash("⚠ Can't go to checkout without ordering anything.", "error")
        return redirect(url_for("order.order"))

    coupon_code = ""
    discount_message = None
    error_message = None
    customer = Customer.query.get(customer_id)

    # HANDLE POST
    if request.method == "POST":
        action = request.form.get("action")
        coupon_code = request.form.get("coupon", "").strip().upper()

        # Read delivery info
        street = request.form.get("street", "").strip()
        house_number = request.form.get("house_number", "").strip()
        city = request.form.get("city", "").strip()
        postal_code = request.form.get("postal_code", "").strip()
        phone = request.form.get("phone", "").strip()

        # --- CONFIRM ORDER ---
        if action == "confirm_order":
            # Validate all fields before continuing
            if not all([street, house_number, city, postal_code, phone]):
                flash("⚠ Please fill in all delivery fields before continuing to payment.", "error")
                return redirect(url_for("order.checkout"))

            # Update customer info
            customer.Street = street
            customer.HouseNumber = int(house_number) if house_number.isdigit() else None
            customer.City = city
            customer.PostalCode = postal_code
            customer.PhoneNumber = phone
            db.session.commit()

            # Mark coupon as used (if exists)
            if order.DiscountCodeId:
                discount = DiscountCode.query.filter_by(
                    DiscountCodeId=order.DiscountCodeId,
                    CustomerId=customer_id
                ).first()
                if discount and not discount.IsRedeemed:
                    discount.IsRedeemed = True
                    db.session.add(discount)

            order.OrderStatus = "Confirmed"
            db.session.commit()
            flash(" Your order has been confirmed! Redirecting to payment...", "success")
            return redirect(url_for("order.pay"))

        # --- APPLY COUPON ---
        elif action == "apply_coupon":
            if coupon_code:
                discount = DiscountCode.query.filter_by(
                    Code=coupon_code,
                    CustomerId=customer_id
                ).first()
                if not discount:
                    error_message = "Invalid coupon code or not linked to your account."
                elif discount.IsRedeemed:
                    error_message = "This coupon has already been used."
                elif discount.ExpiryDate and discount.ExpiryDate < date.today():
                    error_message = "This coupon has expired."
                else:
                    order.DiscountCodeId = discount.DiscountCodeId
                    db.session.add(order)
                    db.session.commit()
                    discount_message = (
                        f"Coupon '{coupon_code}' is valid! "
                        f"{discount.DiscountPercent}% discount will be applied at checkout."
                    )
            else:
                error_message = "Please enter a coupon code first."

        # --- REMOVE COUPON ---
        elif action == "remove_coupon":
            if order.DiscountCodeId:
                order.DiscountCodeId = None
                db.session.commit()
                discount_message = "Coupon has been removed."
            else:
                error_message = "No coupon to remove."

    # --- CALCULATE TOTAL ---
    order_items = []
    total_price = 0

    # PIZZAS
    for idx, p in enumerate(order.pizzas, start=1):
        ingredients = [pi.ingredient.Name for pi in p.ingredients]
        pizza_price = sum(float(pi.ingredient.Price) for pi in p.ingredients)
        total_price += pizza_price
        order_items.append(f"Custom Pizza #{idx}: {', '.join(ingredients)} - €{pizza_price:.2f}")

    # DRINKS
    for od in order.drinks:
        drink = od.drink
        amount = od.Amount or 1
        drink_total = float(drink.Price) * amount
        total_price += drink_total
        order_items.append(f"{drink.Name} x{amount} - €{drink_total:.2f}")

    # DESSERTS
    for od in order.desserts:
        dessert = od.dessert
        amount = od.Amount or 1
        dessert_total = float(dessert.Price) * amount
        total_price += dessert_total
        order_items.append(f"{dessert.Name} x{amount} - €{dessert_total:.2f}")

    # DISCOUNT
    if order.DiscountCodeId:
        discount = DiscountCode.query.filter_by(
            DiscountCodeId=order.DiscountCodeId,
            CustomerId=customer_id
        ).first()
        if discount:
            total_price *= (1 - discount.DiscountPercent / 100)

    # RENDER PAGE
    return render_template(
        "checkout.html",
        order=order_items,
        total_price=f"{total_price:.2f}",
        customer=customer,
        order_obj=order,
        coupon_code=coupon_code,
        discount_message=discount_message,
        error_message=error_message
    )






@order_bp.route('/order/pay', methods=['GET', 'POST'])
def pay():
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please log in to continue.", "error")
        return redirect(url_for("auth.login"))

    # Try to get a specific order ID (for paying from history)
    order_id = request.args.get("order_id", type=int)

    if order_id:
        order = Order.query.filter_by(OrderId=order_id, CustomerId=customer_id).first()
    else:
        order = Order.query.filter(
            Order.CustomerId == customer_id,
            Order.OrderStatus.in_(["Pending", "Confirmed"])
        ).first()

    if not order:
        flash("No order found to pay for.", "error")
        return redirect(url_for("order.order"))

    customer = Customer.query.get(customer_id)

    # Handle payment confirmation
    if request.method == "POST":
        # Redeem coupon if it exists
        if order.DiscountCodeId:
            discount = DiscountCode.query.filter_by(
                DiscountCodeId=order.DiscountCodeId,
                CustomerId=customer_id
            ).first()
            if discount and not discount.IsRedeemed:
                discount.IsRedeemed = True
                db.session.add(discount)

        # Update order status to Paid
        order.OrderStatus = "Paid"
        db.session.add(order)
        db.session.commit()

        flash("Payment successful! Thank you for your order ✧｡٩(ˊᗜˋ )و✧*", "success")
        return redirect(url_for("home.home"))

    # Calculate total price (Pizzas + Drinks + Desserts)
    order_items = []
    total_price = 0

    # --- PIZZAS ---
    for idx, p in enumerate(order.pizzas, start=1):
        ingredients = [pi.ingredient.Name for pi in p.ingredients]
        pizza_price = sum(float(pi.ingredient.Price) for pi in p.ingredients)
        total_price += pizza_price
        order_items.append(f"Custom Pizza #{idx}: {', '.join(ingredients)} - €{pizza_price:.2f}")

    # --- DRINKS ---
    for od in order.drinks:
        drink = od.drink
        amount = od.Amount or 1
        drink_total = float(drink.Price) * amount
        total_price += drink_total
        order_items.append(f"{drink.Name} x{amount} - €{drink_total:.2f}")

    # --- DESSERTS ---
    for od in order.desserts:
        dessert = od.dessert
        amount = od.Amount or 1
        dessert_total = float(dessert.Price) * amount
        total_price += dessert_total
        order_items.append(f"{dessert.Name} x{amount} - €{dessert_total:.2f}")

    # --- APPLY DISCOUNT ---
    if order.DiscountCodeId:
        discount = DiscountCode.query.filter_by(
            DiscountCodeId=order.DiscountCodeId,
            CustomerId=customer_id
        ).first()
        if discount:
            total_price *= (1 - discount.DiscountPercent / 100)

    #  Render payment page
    return render_template(
        "pay.html",
        customer=customer,
        order=order_items,
        total_price=f"{total_price:.2f}"
    )






@order_bp.route('/order/delete', methods=['POST'])
def delete_order():
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))

    order_id = request.form.get("order_id", type=int)
    if not order_id:
        flash("Invalid order.", "error")
        return redirect(url_for("order.order_history"))

    order = Order.query.filter_by(OrderId=order_id, CustomerId=customer_id).first()
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("order.order_history"))

    # Only allow deletion if not paid
    if order.OrderStatus == "Paid":
        flash("You can’t delete an order that has already been paid.", "error")
        return redirect(url_for("order.order_history"))

    db.session.delete(order)
    db.session.commit()

    flash("Order deleted successfully.", "success")
    return redirect(url_for("order.order_history"))







@order_bp.route('/coupons')
def coupons():
    from datetime import date, timedelta
    customer_id = session.get("customer_id")

    if not customer_id:
        flash("Please log in to view your coupons.", "error")
        return redirect(url_for("auth.login"))

    customer = Customer.query.get(customer_id)

    # Birthday coupon (only once per year)
    if customer.BirthDate:
        today = date.today()
        if (customer.BirthDate.month, customer.BirthDate.day) == (today.month, today.day):
            existing_bday = DiscountCode.query.filter_by(
                CustomerId=customer_id, Code=f"BIRTHDAY-{customer_id}-{today.year}"
            ).first()
            if not existing_bday:
                birthday_coupon = DiscountCode(
                    Code=f"BIRTHDAY-{customer_id}-{today.year}",
                    DiscountPercent=15,
                    ExpiryDate=today + timedelta(days=3),
                    IsRedeemed=False,
                    CustomerId=customer_id
                )
                db.session.add(birthday_coupon)
                db.session.commit()
                flash("🎂 Happy Birthday! You received a 15% discount coupon!", "success")

    # Welcome coupon (unique per customer)
    existing_welcome = DiscountCode.query.filter_by(
        CustomerId=customer_id, Code=f"BAMSIES-{customer_id}"
    ).first()

    if not existing_welcome:
        new_coupon = DiscountCode(
            Code=f"BAMSIES-{customer_id}",
            DiscountPercent=5,
            ExpiryDate=date.today() + timedelta(days=365),
            IsRedeemed=False,
            CustomerId=customer_id
        )
        db.session.add(new_coupon)
        db.session.commit()
        flash("🎉 Welcome! You received a 5% discount coupon.", "success")

    # Count *only this customer's* pizzas
    total_pizzas = (
        db.session.query(Pizza)
        .join(Order, Pizza.OrderId == Order.OrderId)
        .filter(Order.CustomerId == customer_id)
        .count()
    )

    #  Loyalty every 10 pizzas
    loyalty_count = total_pizzas // 10
    existing_loyalties = DiscountCode.query.filter(
        DiscountCode.CustomerId == customer_id,
        DiscountCode.Code.like(f"LOYALTY-{customer_id}-%")
    ).count()

    if loyalty_count > existing_loyalties:
        for i in range(existing_loyalties + 1, loyalty_count + 1):
            new_loyalty = DiscountCode(
                Code=f"LOYALTY-{customer_id}-{i}",
                DiscountPercent=10,
                ExpiryDate=date.today() + timedelta(days=365),
                IsRedeemed=False,
                CustomerId=customer_id
            )
            db.session.add(new_loyalty)
        db.session.commit()
        flash("🍕 Congrats! You earned a 10% loyalty coupon for your pizza orders!", "success")

    #  Fetch personal coupons
    coupons = DiscountCode.query.filter(
        DiscountCode.CustomerId == customer_id
    ).order_by(DiscountCode.ExpiryDate.asc()).all()

    #  Add short descriptions dynamically
    for c in coupons:
        if c.Code.startswith("BAMSIES"):
            c.Description = "Welcome gift for joining Bam’s Pizza!"
        elif c.Code.startswith("LOYALTY"):
            c.Description = "Thanks for being a loyal pizza lover! You earn one every 10 pizzas ❤"
        elif c.Code.startswith("BIRTHDAY"):
            c.Description = "Happy Birthday! Celebrate with a sweet 15% off (੭ˊᵕˋ)੭🎂"
        else:
            c.Description = "Special offer coupon "

    return render_template('coupons.html', active_page='coupons', coupons=coupons, date=date)






@order_bp.route('/order/history')
def order_history():
    from datetime import timedelta
    customer_id = session.get("customer_id")

    if not customer_id:
        flash("Please log in to view your order history.", "error")
        return redirect(url_for("auth.login"))

    # Fetch all customer orders (excluding Pending)
    orders = (
        Order.query
        .filter_by(CustomerId=customer_id)
        .filter(Order.OrderStatus != "Pending")
        .all()
    )

    # Compute total price for each order
    for o in orders:
        total_price = 0
        for pizza in o.pizzas:
            total_price += sum(float(pi.ingredient.Price) for pi in pizza.ingredients)
        for od in o.drinks:
            if od.drink:
                total_price += float(od.drink.Price) * (od.Amount or 1)
        for od in o.desserts:
            if od.dessert:
                total_price += float(od.dessert.Price) * (od.Amount or 1)
        if o.DiscountCodeId:
            discount = DiscountCode.query.get(o.DiscountCodeId)
            if discount:
                total_price *= (1 - discount.DiscountPercent / 100)
        o.total_price = total_price


    orders.sort(
        key=lambda o: (
            0 if o.OrderStatus == "Confirmed" else 1,   # Confirmed first
            o.PlaceDateTime.timestamp() if o.PlaceDateTime else 0  # newest first (descending below)
        ),
        reverse=True  # <--- FLIP ORDER
    )

    return render_template(
        'order_history.html',
        active_page='order_history',
        orders=orders,
        timedelta=timedelta
    )





    #Home page logic
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

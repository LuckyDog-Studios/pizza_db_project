from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from sqlalchemy import func

from models import ( db, Ingredient, PizzaIngredient, Pizza, Order, Customer, OrderDrink, Drink, OrderDessert, Dessert, DeliveryPerson, PostalAssignment, DiscountCode)
from datetime import date
from datetime import datetime, timedelta, timezone

#  Helper: Automatically refresh delivery availability
def update_delivery_availability():
    """Auto-refresh availability of couriers when cooldown expires."""
    now = datetime.now(timezone.utc)
    busy_drivers = DeliveryPerson.query.filter(
        DeliveryPerson.IsAvailable == False,
        DeliveryPerson.UnavailableUntil <= now
    ).all()

    for driver in busy_drivers:
        driver.IsAvailable = True
        driver.UnavailableUntil = None

    if busy_drivers:
        db.session.commit()


def assign_delivery_person(postal_code):
    """Assign a delivery person for a postal code.
    If all couriers for that area are busy, create a new one.
    Each courier becomes available again after 30 minutes."""
    now = datetime.now(timezone.utc)

    # Find existing postal assignments for this area
    assignments = PostalAssignment.query.filter_by(PostalCode=postal_code).all()
    driver_ids = [a.DeliveryPersonId for a in assignments]
    drivers = DeliveryPerson.query.filter(
        DeliveryPerson.DeliveryPersonId.in_(driver_ids)
    ).all() if driver_ids else []

    # Check for available drivers
    available_driver = next((d for d in drivers if d.IsAvailable), None)

    # If no available driver → create new one and assign
    if not available_driver:
        new_driver = DeliveryPerson(
            Name=f"Driver {len(drivers) + 1} ({postal_code})",
            IsAvailable=False,
            UnavailableUntil=now + timedelta(minutes=30)
        )
        db.session.add(new_driver)
        db.session.flush()  # get the ID before commit

        assignment = PostalAssignment(
            PostalCode=postal_code,
            DeliveryPersonId=new_driver.DeliveryPersonId
        )
        db.session.add(assignment)
        db.session.commit()
        return new_driver
    else:
        # Mark chosen driver unavailable temporarily
        available_driver.IsAvailable = False
        available_driver.UnavailableUntil = now + timedelta(minutes=30)
        db.session.commit()
        return available_driver


order_bp = Blueprint('order', __name__)
home_bp = Blueprint('home', __name__)
contact_bp = Blueprint('contact', __name__)
about_bp = Blueprint('about', __name__)

reports_bp = Blueprint('reports', __name__)

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
        flash("You already have a confirmed unpaid order. Please go to 'My Orders' to pay or delete it.", "error")
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
        flash("You already have a confirmed unpaid order. Please go to 'My Orders' to pay or delete it.", "error")
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
            flash("Please select at least one ingredient.", "error")
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
            flash("No drink selected.", "error")
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
            flash("No dessert selected.", "error")
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
        flash("Can't go to checkout without ordering anything.", "error")
        return redirect(url_for("order.order"))

    # --- Prevent empty order checkout ---
    if not order.pizzas and not order.drinks and not order.desserts:
        flash("Can't go to checkout without ordering anything.", "error")
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
                flash("Please fill in all delivery fields before continuing to payment.", "error")
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
            total_price *= (1 - float(discount.DiscountPercent) / 100)

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

        # --- PAYMENT LOGIC ---
        order.OrderStatus = "Paid"
        db.session.add(order)
        db.session.commit()

        # --- DELIVERY ASSIGNMENT (NEW CLEAN VERSION) ---
        delivery_person = assign_delivery_person(customer.PostalCode)
        order.DeliveryPersonId = delivery_person.DeliveryPersonId
        order.DeliveryDateTime = datetime.now(timezone.utc) + timedelta(minutes=30)

        db.session.add(order)
        db.session.commit()

        flash(f"🚴 {delivery_person.Name} assigned! Estimated delivery in 30 minutes.", "success")
        flash("💳 Payment successful! Thank you for your order ✧｡٩(ˊᗜˋ )و✧*", "success")
        return redirect(url_for("home.home"))

    # --- CALCULATE TOTAL PRICE (Pizzas + Drinks + Desserts) ---
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
            total_price *= (1 - float(discount.DiscountPercent) / 100)

    # --- RENDER PAYMENT PAGE ---
    return render_template(
        "pay.html",
        customer=customer,
        order=order_items,
        total_price=f"{total_price:.2f}"
    )






@order_bp.route('/order/track/<int:order_id>')
def track_delivery(order_id):
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please log in to track your delivery.", "error")
        return redirect(url_for("auth.login"))

    order = Order.query.filter_by(OrderId=order_id, CustomerId=customer_id).first()
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("order.order_history"))

    if not order.delivery_person or not order.DeliveryDateTime:
        flash("Delivery not started yet.", "info")
        return redirect(url_for("order.order_history"))

    # Compute remaining seconds
    now = datetime.now(timezone.utc)
    eta = order.DeliveryDateTime
    remaining = max(0, int((eta - now).total_seconds()))

    return render_template(
        "track_delivery.html",
        order=order,
        delivery_person=order.delivery_person,
        remaining=remaining
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



@order_bp.route("/update_order_status/<int:order_id>", methods=["POST"])
def update_order_status(order_id):
    """AJAX endpoint to mark order as delivered when countdown reaches zero."""
    order = Order.query.get(order_id)
    if not order:
        return {"error": "Order not found"}, 404

    if order.OrderStatus == "Paid":
        order.OrderStatus = "Delivered"
        db.session.commit()

    return {"message": "Order marked as delivered"}, 200







@order_bp.route('/order/history')
def order_history():
    from datetime import timedelta, datetime, timezone
    update_delivery_availability()

    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please log in to view your order history.", "error")
        return redirect(url_for("auth.login"))

    # Fetch all orders (excluding Pending)
    orders = (
        Order.query
        .filter_by(CustomerId=customer_id)
        .filter(Order.OrderStatus != "Pending")
        .all()
    )

    now = datetime.now(timezone.utc)
    for o in orders:
        # --- Compute total price ---
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
                total_price *= (1 - float(discount.DiscountPercent) / 100)
        o.total_price = total_price

        # --- Countdown for Paid orders ---
        o.remaining_seconds = None
        if o.OrderStatus == "Paid" and o.DeliveryDateTime:
            if o.DeliveryDateTime.tzinfo is None:
                o.DeliveryDateTime = o.DeliveryDateTime.replace(tzinfo=timezone.utc)
            remaining = int((o.DeliveryDateTime - now).total_seconds())
            if remaining > 0:
                o.remaining_seconds = remaining
            else:
                o.OrderStatus = "Delivered"
                o.remaining_seconds = 0
                db.session.commit()

    # ⚡ Sort oldest → newest (we’ll reverse in template)
    orders.sort(key=lambda o: o.PlaceDateTime.timestamp() if o.PlaceDateTime else 0)

    # --- JSON for countdown timers ---
    orders_json = [
        {
            "OrderId": o.OrderId,
            "Status": o.OrderStatus,
            "remaining_seconds": o.remaining_seconds or 0
        }
        for o in orders
    ]

    return render_template(
        "order_history.html",
        active_page="order_history",
        orders=orders,
        timedelta=timedelta,
        orders_json=orders_json
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

@reports_bp.route('/report')
def reports():
    # --- Top-selling pizzas ---
    top_pizzas = (
        db.session.query(
            Ingredient.Name,
            func.sum(Pizza.Amount).label("total_sold")
        )
        .join(PizzaIngredient, PizzaIngredient.IngredientId == Ingredient.IngredientId)
        .join(Pizza, Pizza.PizzaId == PizzaIngredient.PizzaId)
        .group_by(Ingredient.Name)
        .order_by(func.sum(Pizza.Amount).desc())
        .limit(10)
        .all()
    )

    # --- Undelivered orders ---
    undelivered_orders = (
        Order.query.filter(Order.OrderStatus != "Delivered")
        .order_by(Order.PlaceDateTime.desc())
        .all()
    )

    # --- Monthly earnings by age and postal code ---
    earnings_by_age_postal = {}
    orders = Order.query.join(Customer).all()
    for order in orders:
        # Compute age in Python
        birthdate = order.customer.BirthDate
        if birthdate:
            today = datetime.now().date()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        else:
            age = None

        postal = order.customer.PostalCode or "Unknown"

        # Total price of order
        total_price = 0
        for pizza in order.pizzas:
            pizza_total = sum(ing.ingredient.Price for ing in pizza.ingredients) * pizza.Amount
            total_price += pizza_total
        for drink in order.drinks:
            total_price += drink.Amount * drink.drink.Price
        for dessert in order.desserts:
            total_price += dessert.Amount * dessert.dessert.Price

        # Monthly key
        month_key = order.PlaceDateTime.strftime("%Y-%m")

        # Organize in dict: earnings_by_age_postal[month][postal][age] = total
        earnings_by_age_postal.setdefault(month_key, {})
        earnings_by_age_postal[month_key].setdefault(postal, {})
        earnings_by_age_postal[month_key][postal].setdefault(age, 0)
        earnings_by_age_postal[month_key][postal][age] += total_price

    return render_template(
        "reports.html",
        top_pizzas=top_pizzas,
        undelivered_orders=undelivered_orders,
        earnings_by_age_postal=earnings_by_age_postal
    )

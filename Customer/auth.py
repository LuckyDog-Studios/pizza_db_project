from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from Customer import customer_service as cs

auth_bp = Blueprint("auth", __name__)




# Register
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")

        # check if email already exists
        existing_user = cs.find_by_email(email)
        if existing_user:
            flash("Email already registered. Please log in.", "error")
            return render_template("register.html")

        # create customer
        hashed_pw = generate_password_hash(password)
        cs.create_customer(first_name, last_name, email, hashed_pw)

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")




# Login
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        customer = cs.find_by_email(email)

        if not customer or not check_password_hash(customer.PasswordHash, password):
            flash("Invalid email or password (╥╯⌒╰╥๑)", "error")
            return render_template("login.html")

        # login successful → store in session
        session["customer_id"] = customer.CustomerId
        session["customer_name"] = customer.FirstName

        flash(f"(〜^∇^)〜 Welcome back, {customer.FirstName}! ~( ˘▾˘~)", "success")
        return redirect(url_for("home.home"))

    return render_template("login.html")





# Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home.home"))




# Account
@auth_bp.route("/account", methods=["GET", "POST"])
def account():
    if not session.get("customer_id"):
        flash("Please log in to access your account.", "error")
        return redirect(url_for("auth.login"))

    customer = cs.find_by_id(session["customer_id"])

    if request.method == "POST":
        cs.update_customer(customer, request.form)
        flash("Your account details have been updated.", "success")
        return redirect(url_for("auth.account"))

    return render_template("account.html", customer=customer)

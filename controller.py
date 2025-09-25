from flask import Blueprint, render_template, redirect, url_for

order_bp = Blueprint('order', __name__)
home_bp = Blueprint('home', __name__)
contact_bp = Blueprint('contact', __name__)
about_bp = Blueprint('about', __name__)

#Orders page logic
@order_bp.route('/order')
def order():
    return render_template('order.html', active_page='order')

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

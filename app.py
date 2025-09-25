from flask import Flask, render_template
from controller import order_bp, about_bp, home_bp, contact_bp

app = Flask(__name__)
app.register_blueprint(order_bp)
app.register_blueprint(about_bp)
app.register_blueprint(home_bp)
app.register_blueprint(contact_bp)

if __name__ == '__main__':
    app.run()

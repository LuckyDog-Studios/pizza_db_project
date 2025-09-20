from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/about')
def about():
    return "<h1>Hello World!</h1>"

@app.route('/contact')
def contact():
    return "<h1>Hello World!</h1>"

if __name__ == '__main__':
    app.run()

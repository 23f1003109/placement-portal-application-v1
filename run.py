from flask import render_template, redirect, url_for
from app import create_app

app = create_app()

@app.errorhandler(404)
def bad_request(error):
    return render_template('errors/404.html'), 404

@app.route('/')
def index():
    return redirect(url_for("auth.login"))

if __name__ == '__main__':
    app.run(debug=True)
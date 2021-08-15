from flask import Blueprint,redirect,url_for,render_template


views = Blueprint('views', __name__)

@views.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@views.app_errorhandler(500)
def internal_erorr(e):
    return render_template('500.html'), 500

@views.route('/')
def home():
    return redirect(url_for("auth.login"))

from flask import Blueprint

company_bp = Blueprint('company_bp', __name__)

from . import routes

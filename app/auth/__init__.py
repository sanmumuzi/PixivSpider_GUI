from flask import Blueprint, redirect

auth = Blueprint('auth', __name__, url_prefix='/auth')

from . import views

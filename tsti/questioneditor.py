import functools
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from tsti.auth import login_required,allowed_file,getExtension
from tsti.db import get_db

bp = Blueprint('questioneditor', __name__,url_prefix='/editor')

def editoraccess_control(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user['editorer'] == 1:
            flash("????")
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/')
@login_required
def main_page():
    print(g.user['editorer'])
    return render_template("questioneditor/ed_main.html")

@bp.route('/request/<int:id>') # id is prime number id of a permission
def permission_request(id):
    print(g.user['editorer'])
    flash("Damn. "+str(id))
    return redirect(url_for("questioneditor.main_page"))
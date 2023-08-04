import functools, re, sys

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
import hashlib

from db import get_db #type:ignore

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=("GET", "POST"))
def register():
    """
        Register new user in the database
        Needs to enter a username and password
        Store username and password hash
    """

    db = get_db()

    if request.method == "POST":

        # Fetching form data
        username = request.form["username"]
        password = hashlib.sha256(bytes(request.form["password"], 'utf-8')).hexdigest() # Hash the input, which we check against the hash stored in the database
        email = request.form["email"]

        r = re.compile(".*@.*") # Using regex to check email format
        error = None
        if not username:    # Most of these don't get run because the fields are required in html anyways, but they remain nevertheless
            error = 'Username is required.'
        elif not email:
            error='Email is required'
        elif r.match(email) is None:    # Regex checking. This one actually gets run
            error = 'Unrecognised Email Format'
        elif not password:
            error = 'Password is required.'

        if error is None:
            # Check if username is already taken
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM tblusers WHERE username = %s",
                    (username)
                    )

                if cursor.fetchone() is not None:
                    error = "Username already taken"

                # Check if email is already registered
                cursor.execute(
                    "SELECT * FROM tblusers WHERE email = %s",
                    (email)
                    )
                if cursor.fetchone() is not None:
                    error = "Email is already registered "

        if error is None:
            try:
                cursor = db.cursor()
                # Create new user in tblusers
                sql = "INSERT INTO `tblusers` (`username`, `password`, `email`) VALUES (%s,%s,%s)"
                cursor.execute(
                    sql,
                    (username, password, email)
                    )
                db.commit()
                cursor.execute("SELECT * FROM tblusers WHERE username = %s", (username))
                user = cursor.fetchone()
                session.clear()
                session['user_id'] = user[0]
            except db.IntegrityError as e:
                # According to flask docs this exception will catch when a username is taken. Doesn't work here because I don't use the username as the primary key.
                print(e)
            else:
                return redirect(url_for('dashboard'))
        flash(error)
            


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(bytes(request.form["password"], 'utf-8')).hexdigest()
        db = get_db()
        error = None
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM tblusers WHERE username = %s', (username)
        )
        user = cursor.fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif user[2] != password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return jsonify({'error': "", 'redirect': url_for('dashboard')})
        else:
            return jsonify({'error': error, 'redirect': ""})

@bp.route('/sign_out', methods=('GET', 'POST'))
def sign_out():
    g.user = None
    session.clear()
    return redirect(url_for('dashboard'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        cursor = get_db().cursor()
        cursor.execute(
            'SELECT * FROM tblusers WHERE id = %s', (user_id,)
        )
        g.user = cursor.fetchone()
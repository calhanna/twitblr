import functools, re, sys

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
import hashlib

from db import get_db #type:ignore
from emailer import send_email as send_message #type:ignore
import app #type:ignore

CONFIRM_MESSAGE = """\
    <style>
        h1, h3{
            margin-left: auto;
            margin-right: auto;
        }

        p {
            margin-top: 50px
        }
    </style>

    <body style="text-align: center">
        <h1> Confirm your email </h1> <br>
        <h3>Hi, %s. To complete your account creation process, please click this link to confirm your email: </h3> <br>
        <h3><a href = "%s" >Confirm</a></h3> <br>
        <p> If this wasn't you, please contact us at our main site to resolve </p>
    </body>
"""

PASSWORD_CHANGE = """\
    <style>
        h1, h3{
            margin-left: auto;
            margin-right: auto;
        }

        p {
            margin-top: 50px
        }
    </style>

    <body style="text-align: center">
        <h1> Change your password </h1> <br>
        <h3>Hi, %s. We have recieved a request to change your password. Please click the link below to do so. </h3> <br>
        <h3><a href = "%s" >Change Password</a></h3> <br>
        <p> If this wasn't you, sign out on all devices and click the link to change your password. </p>
    </body>
"""


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
                send_message(email, "Confirm your email", CONFIRM_MESSAGE % (username, url_for('confirm_email', _external=True)))
                return jsonify({'error': 'none'})
            except db.IntegrityError as e:
                # According to flask docs this exception will catch when a username is taken. Doesn't work here because I don't use the username as the primary key.
                return jsonify({'error': e})
        else:
            return jsonify({'error': error})

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

@bp.route('/change_password/<email>', methods=["GET", "POST"])
def change_password(email):
    """ Does 3 things:
    1. Sends the change password email
    2. Displays the change password page when the email link is clicked
    3. Changes the user's password
    """

    db = get_db()
    if request.method == "POST" and email == "none":
        # Send password request email
        send_message(g.user[3], "Change your password", PASSWORD_CHANGE % (g.user[1], url_for('auth.change_password', _external=True, email=g.user[3])))

        with db.cursor() as cursor:
            # Record request
            cursor.execute("INSERT INTO tblactions (user_id, type) VALUES (%s, 'ChangePassword')", (g.user[0]))
            db.commit()

        return jsonify({})
    elif request.method == "POST":
        if email != g.user[3]:
            # signed in as wrong user, go away
            return redirect(url_for('dashboard'))
        
        with db.cursor() as cursor:
            # Changes the password and expires the record
            cursor.execute("UPDATE tblusers SET password=%s WHERE email=%s", (hashlib.sha256(bytes(request.form["password"], 'utf-8')).hexdigest(), email))
            cursor.execute("DELETE FROM tblactions WHERE user_id = %s AND type='ChangePassword'", (g.user[0]))
            db.commit()

        return redirect(url_for('dashboard'))
    else:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM tblactions INNER JOIN tblusers ON tblactions.user_id = tblusers.id WHERE email = %s and type='ChangePassword'", (g.user[3]))
            if cursor.fetchall():
                # Only display page if there is an unexpired request.
                return render_template("/auth/change_password.html")
            else:
                return redirect(url_for('dashboard'))

@bp.route('/confirm_email', methods=["POST"])
def confirm_email():
    send_message(g.user[3], "Confirm your email", CONFIRM_MESSAGE % (g.user[1], url_for('confirm_email', _external=True)))
    app.send_notification(g.user, "Confirmation email sent! ")
    return jsonify({})
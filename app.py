"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.

Notes to self:
- HTML/css needs work, doesnt look nice on mobile
- Prioritory is login/register rn
"""

from concurrent.futures import process
from flask import (
    Flask, 
    render_template, 
    request,
    redirect,
    url_for,
    g,
    flash,
    session,
    jsonify
    )

import re, os, markupsafe, datetime, random

import auth #type: ignore
from db import get_db #type: ignore

from PIL import Image

# A blacklist of html tags that users aren't allowed to put in their posts.
# There are ways around this - they can use encoding, etc, but this is strangely resistant to a lot of common xss attacks
HTML_BLACKLIST = {
    "SCRIPT",
    "ALERT",
    "FONT-SIZE",
    "DIV",
    "!IMPORTANT",
    "DISPLAY",
    "ONCLICK",
    "ON",
    "JAVASCRIPT"
}

# App initialisation
app = Flask(__name__)
app.config.from_mapping(SECRET_KEY='dev', UPLOAD_FOLDER="./static/userUploads/") # We need a secret key to access the session, and an upload folder to put user profile pictures
print(app.config["UPLOAD_FOLDER"])

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

# Blueprint for authentication functions
app.register_blueprint(auth.bp)

@app.route('/')
def index():
    """
    Startup
    Renders either welcome page or dashboard
    """

    return redirect(url_for('dashboard'))

def check_likes(cursor, post):
    """ 
        Likes/Dislikes are stored in a table called 'actions'
        We only want to count each user once, and we don't want them to be able to like and dislike at the same time
        Therefore, the only action we care about is the last one performed by each user.
    """

    # Execute SQL to fetch actions
    sql = "SELECT * FROM TBLactions WHERE post_id = %s"
    cursor.execute(sql, (post[0]))

    # Convert tuple to array (possibly a no longer necessary artifact of an older implementation, but hey it works)
    actions = list(cursor.fetchall())
    actions.reverse()   # Most recent actions first

    # Create a dict to sort each action into it's user
    user_actions = {}
    for action in actions:
        if action[2] in user_actions:
            user_actions[action[2]].append(action[3])
        else:
            user_actions[action[2]] = [action[3]]
    return user_actions

def fetch_post(post, cursor):
    """ Fetches all the additional information about a post and formats it into a new list """

    # I meant to do this with a table link thing but I can't remember what they were called and therefore I can't google it
    user_id = post[1]

    # Fetch the username using the user_id
    # We can either run an SQL check for every post or we can do it in python. I'm doing the SQL check because I think it's easier
    cursor.execute(
        "SELECT * FROM TBLusers WHERE ID = %s",
        (user_id)
        )
    user = cursor.fetchone()
    post[1] = user[1]   # Override the user_id number with the name of the user
    post.append(user[4])

    # Fetch likes/dislikes
    user_actions = check_likes(cursor, post)

    # Figure out what the current user did last. Could do this better with code that has been added after, but I don't care enough to do so
    # The purpose of this is so we can colour the buttons they've already pressed.
    last_action = None
    if g.user is not None:
        last_action = 'none'
        cursor.execute("SELECT * FROM TBLactions WHERE post_id = %s AND user_id = %s", (post[0], g.user[0]))
        results = list(cursor.fetchall())
        if results:
            last_action = results[-1] 

    # Tally up the likes/dislikes, only considering the last action of each user
    likes, dislikes = 0, 0
    for user in user_actions:
        if user_actions[user]:
            a = user_actions[user][0]   # I'm sorry for the single character variable but it only exists in this scope ok?
            if a == "Like":
                likes += 1
            else:
                dislikes += 1

    # Escape blacklisted html
    # Use regex to search for HTML tags, i.e <h1>, <img>, <script>
    for tag in re.findall(r"<.*>", post[4]):
        # Check against the HTML blacklist. Blacklist isn't just tags, includes style entries.
        for bad_tag in HTML_BLACKLIST:
            if bad_tag in tag.upper():
                # Replace the offending tag with an escaped version
                post[4] = post[4].replace(tag, markupsafe.escape(tag))

    post.extend([likes, dislikes, last_action])
    return post

def fetch_replies(post, cursor, checked):
    """ Recursive function to fetch the replies to a post and the replies to each reply"""
    if post not in checked:
        checked.append(post)
        cursor.execute(
            "SELECT * FROM TBLpost WHERE reply_id = %s",
            (post[0])
        )
        replies = list(cursor.fetchall())
        replies = [list(reply) for reply in replies]
        processed_replies = []
        for reply in replies:
            processed_replies.append(fetch_post(reply, cursor))

        for reply in processed_replies:
            processed_replies.extend(fetch_replies(reply, cursor, checked))

        return processed_replies
    return []

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    """ Fetches posts from database and displays on a feed """
    db = get_db()
    session['url'] = url_for("dashboard")

    print(g.user)

    with db.cursor() as cursor:

        if g.user is not None:
            # Fetch all posts excluding those made by the current user.
            cursor.execute(
                "SELECT * FROM TBLpost WHERE user_id != %s AND reply_id = 0",
                (g.user[0])
                )
        else:
            cursor.execute("SELECT * FROM TBLpost WHERE reply_id = 0")
        
        posts = cursor.fetchall()

        posts = [list(post) for post in posts]  # We want to edit the post and tuples can't be edited
        posts.reverse() # Chronological ordering, newest first

        for post in posts:
            
            post = fetch_post(post, cursor)

            # Fetch replies
            checked = []
            replies = fetch_replies(post, cursor, checked)

            post.append(replies)

    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM TBLusers"
        )
        users = cursor.fetchall()
        username_list = [user[1] for user in users]

    return render_template('/blog/dash.html', posts=posts, username_list = username_list)

@app.route('/add_like', methods=['POST'])
def add_likes():
    """ Function for adding likes to posts by creating entry in TBLactions. Slight misnomer, this function also handles dislikes"""

    if request.method == 'POST':
        if g.user is None:
            return jsonify({
                'success': False
            })

        db = get_db()
        post_id = request.form['post_id']
        action = request.form['like']
        
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM TBLactions WHERE user_id = %s AND post_id = %s", (g.user[0], post_id))
            results = cursor.fetchall()
            if len(results) == 0:
                # Create entry
                sql = "INSERT INTO TBLactions (post_id, user_id, type) VALUES (%s, %s, '" + action + "')"
            else:
                # Update entry
                sql = "UPDATE TBLactions SET `type`='"+ action +"' WHERE post_id = %s and user_id = %s" 

            cursor.execute(
                sql,
                (post_id, g.user[0])
                )
            db.commit()

            cursor.execute('SELECT * FROM TBLactions WHERE post_id = %s AND type = "Like"', (post_id))
            like_count = len(cursor.fetchall())
            cursor.execute("SELECT * FROM TBLactions WHERE post_id = %s AND type = 'Dislike'", (post_id))
            dislike_count = len(cursor.fetchall())

        return jsonify(
            {
                'success': True,
                'like_count': like_count,
                'dislike_count': dislike_count
            }
        )

@app.route("/create_post/<reply_id>", methods=["GET", "POST"])
def create_post(reply_id):
    if request.method == "POST":
        content = request.form["postContent"]
        db = get_db()

        error = None

        if not content:
            error = "Post body required"
        elif len(content) > 255:
            error = "%s/255 character limit" % len(content)
        else:
            cursor = db.cursor()
            now = datetime.datetime.now()
            cursor.execute(
                " INSERT INTO TBLpost (user_id, date, time, content, reply_id) VALUES (%s, %s, %s, %s, %s)",
                (g.user[0], now.date(), now.time(), content, reply_id)
                )
            db.commit()

            #return jsonify({'posts': })

        flash(error)
    return render_template('/blog/createPost.html')

@app.route("/delete_post/<post_id>", methods=["GET", "POST"])
def delete_post(post_id):
    db = get_db()

    with db.cursor() as cursor:
        cursor.execute(
            "DELETE FROM TBLpost WHERE post_id = %s",
            (post_id)
        )
        db.commit()

    return redirect(session['url'])

@app.route("/profile", methods = ["GET", "POST"])
def profile():
    db = get_db()

    session['url'] = url_for("profile")

    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM TBLpost WHERE user_id = %s",
        (g.user[0])
    )
    posts = cursor.fetchall()
    posts = [list(post) for post in posts]  # We want to edit the post and tuples can't be edited
    posts.reverse() # Chronological ordering, newest first
    for post in posts:
        post = fetch_post(post, cursor)

        # Fetch replies
        checked = []
        replies = fetch_replies(post, cursor, checked)

        post.append(replies)

    if request.method=="POST":
        # Upload user profile_picture
        if 'pfp' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pfp']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            upload_folder = app.config['UPLOAD_FOLDER'].replace("./static/", "./")
            n = "%s.%s" % (g.user[0], file.filename.split('.')[-1])

            print

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], n))
            cursor.execute(
                "UPDATE TBLusers SET `profile_picture` = %s WHERE ID = %s",
                (os.path.join(upload_folder, n), g.user[0])
                )
            db.commit()
    return render_template('/blog/profile.html', posts=posts)

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    g.user = None
    return redirect(url_for('auth.login'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ["png", "jpg", "jpeg", "jfif", "webp"]

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)

"""
Insta485 index (main) view.

URLs include:
/user/<user_url_slug>/, /users/<user_url_slug>/followers/,
/users/<user_url_slug>/following/
"""

import os
import flask
import insta485
import insta485.model


@insta485.app.route('/users/<user_url_slug>/', methods=['GET'])
def show_user(user_url_slug):
    """Display user route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    logname = flask.session.get('username')
    user = connection.execute(
        "SELECT username, fullname, filename FROM users WHERE username = ?",
        (user_url_slug,)
    ).fetchone()
    if user is None:
        flask.abort(404)
    logname_follows_username = connection.execute(
        "SELECT 1 FROM following WHERE username1 = ? AND username2 = ?",
        (logname, user_url_slug)
    ).fetchone() is not None
    posts = connection.execute(
        "SELECT postid, filename FROM posts WHERE owner = ?",
        (user_url_slug,)
    ).fetchall()
    total_posts = len(posts)
    followers = connection.execute(
        "SELECT COUNT(*) AS count FROM following WHERE username2 = ?",
        (user_url_slug,)
    ).fetchone()['count']
    following = connection.execute(
        "SELECT COUNT(*) AS count FROM following WHERE username1 = ?",
        (user_url_slug,)
    ).fetchone()['count']
    context = {
        'username': user['username'],
        'fullname': user['fullname'],
        'logname': logname,
        'lognameFollowsUsername': logname_follows_username,
        'totalPosts': total_posts,
        'followers': followers,
        'following': following,
        'posts': posts
    }
    return flask.render_template("users.html", **context)


@insta485.app.route('/users/<user_url_slug>/followers/', methods=['GET'])
def show_followers(user_url_slug):
    """Display user followers."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    user = connection.execute(
        "SELECT username, fullname, filename FROM users WHERE username = ?",
        (user_url_slug,)
    ).fetchone()
    if user is None:
        flask.abort(404)
    logname = flask.session['username']
    followers = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username IN ( "
        "SELECT username1 "
        "FROM following "
        "WHERE username2 = ? ) ",
        (user_url_slug,)
    ).fetchall()
    complete_followers = []
    for follower in followers:
        logname_follows = connection.execute(
            "SELECT 1 FROM following WHERE username1 = ? AND username2 = ?",
            (logname, follower['username'])
        ).fetchone() is not None
        complete_follower = {
            "username": follower['username'],
            "profilePic": follower['filename'],
            "lognameFollows": logname_follows
        }
        complete_followers.append(complete_follower)
    context = {
        'username': user,
        'logname': logname,
        'followers': complete_followers
    }
    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<user_url_slug>/following/', methods=['GET'])
def show_following(user_url_slug):
    """Display user following."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    user = connection.execute(
        "SELECT username, fullname, filename FROM users WHERE username = ?",
        (user_url_slug,)
    ).fetchone()
    if user is None:
        flask.abort(404)
    logname = flask.session['username']
    followings = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username IN ( "
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ? ) ",
        (user_url_slug,)
    ).fetchall()
    logname_followings = connection.execute(
        "SELECT username2 FROM following WHERE username1 = ?",
        (logname,)
    ).fetchall()
    logname_followings_set = {f['username2'] for f in logname_followings}
    complete_followings = []
    for following in followings:
        complete_following = {
            "username": following['username'],
            "profilePic": following['filename'],
            "lognameFollows": following['username'] in logname_followings_set
        }
        complete_followings.append(complete_following)
    context = {
        'username': user,
        'logname': logname,
        'followings': complete_followings
    }
    print("Followings:", complete_followings)
    return flask.render_template("following.html", **context)


@insta485.app.route('/following/', methods=['POST'])
def handle_follows():
    """Docstring."""
    operation = flask.request.form["operation"]
    username = flask.request.form["username"]
    logname = flask.session['username']
    connection = insta485.model.get_db()
    if operation == "follow":
        user_followed = connection.execute(
            "SELECT 1 FROM following WHERE username1 = ? AND username2 =?",
            (logname, username)
        ).fetchone()
        if user_followed:
            flask.abort(409)
        connection.execute(
            "INSERT INTO following(username1, username2) VALUES (?, ?)",
            (logname, username)
        )
        connection.commit()
    if operation == "unfollow":
        user_followed = connection.execute(
            "SELECT 1 FROM following WHERE username1 = ? AND username2 =?",
            (logname, username)
        ).fetchone()
        if not user_followed:
            flask.abort(409)
        connection.execute(
            "DELETE FROM following WHERE username1 = ? AND username2 = ?",
            (logname, username)
        )
        connection.commit()
    target = flask.request.args.get("target", "/")
    return flask.redirect(target)


@insta485.app.route('/likes/', methods=["POST"])
def handle_likes():
    """Docstring."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    operation = flask.request.form["operation"]
    postid = flask.request.form["postid"]
    logname = flask.session['username']
    connection = insta485.model.get_db()
    if operation == "like":
        already_liked = connection.execute(
            "SELECT 1 FROM likes WHERE owner = ? AND postid = ?",
            (logname, postid)
        ).fetchone()
        if already_liked:
            flask.abort(409)
        connection.execute(
            "INSERT INTO likes(owner, postid) VALUES (?, ?)",
            (logname, postid)
        )
        connection.commit()
    elif operation == "unlike":
        not_liked = connection.execute(
            "SELECT 1 FROM likes WHERE owner = ? AND postid = ?",
            (logname, postid)
        ).fetchone()
        if not not_liked:
            flask.abort(409)
        connection.execute(
            "DELETE FROM likes WHERE owner = ? AND postid = ?",
            (logname, postid)
        )
        connection.commit()
    target = flask.request.args.get("target", "/")
    return flask.redirect(target)


@insta485.app.route("/comments/", methods=["POST"])
def handle_comments():
    """Docstring."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    operation = flask.request.form["operation"]
    logname = flask.session['username']
    if operation == 'create':
        text = flask.request.form['text']
        postid = flask.request.form['postid']
        if not text:
            flask.abort(400)
        connection.execute(
            "INSERT INTO comments(owner, postid, text) VALUES (?, ?, ?)",
            (logname, postid, text)
        )
        connection.commit()
    elif operation == 'delete':
        print("Test")
        commentid = flask.request.form['commentid']
        comment_owned = connection.execute(
            "SELECT 1 FROM comments WHERE owner = ? AND commentid = ?",
            (logname, commentid)
        ).fetchone()
        print(comment_owned)
        if not comment_owned:
            flask.abort(403)
        connection.execute(
            "DELETE FROM comments WHERE owner = ? AND commentid = ?",
            (logname, commentid)
        )
        connection.commit()
    target = flask.request.args.get("target", "/")
    return flask.redirect(target)


@insta485.app.route("/uploads/<filename>", methods=['GET'])
def upload_file(filename):
    """Serve file."""
    if 'username' not in flask.session:
        flask.abort(403)
    upload_folder = insta485.app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)
    if not os.path.isfile(file_path):
        flask.abort(404)
    return flask.send_from_directory(upload_folder, filename)

"""Insta485 account urls view.

URLs include:
/
"""
import pathlib
import hashlib
import uuid
import flask
import insta485


@insta485.app.route('/accounts/login/', methods=['GET'])
def login():
    """Login view."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("login.html")


@insta485.app.route('/accounts/create/', methods=['GET'])
def create():
    """Create account view."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('edit'))
    return flask.render_template("create.html")


@insta485.app.route('/accounts/delete/', methods=['GET'])
def delete():
    """Delete account view."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template("delete.html", **context)


@insta485.app.route('/accounts/edit/', methods=['GET'])
def edit():
    """Edit account view."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    logname = flask.session['username']
    user = connection.execute(
        "SELECT username, fullname, email, filename "
        "FROM users "
        "WHERE username = ? ",
        (logname,)
    ).fetchone()

    context = {
        "logname": logname,
        "user": user
    }
    return flask.render_template("edit.html", **context)


@insta485.app.route('/accounts/password/', methods=['GET'])
def password():
    """Change password view."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template("password.html", **context)


@insta485.app.route('/accounts/auth/', methods=['GET'])
def auth():
    """Authorize user."""
    if 'username' in flask.session:
        return '', 200
    flask.abort(403)


@insta485.app.route('/accounts/logout/', methods=['POST'])
def handle_logout():
    """Handle logout."""
    flask.session.clear()
    return flask.redirect(flask.url_for('login'))


@insta485.app.route('/accounts/', methods=['POST'])
def handle_account():
    """Handle account operations."""
    operation = flask.request.form['operation']
    if operation == 'login':
        username = flask.request.form['username']
        password1 = flask.request.form['password']
        if not username or not password1:
            flask.abort(400)
        return accounts_login(username, password1)
    if operation == 'create':
        username = flask.request.form['username']
        password1 = flask.request.form['password']
        fullname = flask.request.form['fullname']
        email = flask.request.form['email']
        profile_pic = flask.request.files['file']
        if (not username or not password1 or
                not fullname or not email or not profile_pic):
            flask.abort(400)
        return accounts_create(username, password1,
                               fullname, email, profile_pic)
    if operation == 'delete':
        return accounts_delete()
    if operation == 'edit_account':
        fullname = flask.request.form['fullname']
        email = flask.request.form['email']
        profile_pic = flask.request.files['file']
        if not fullname or not email:
            flask.abort(400)
        return accounts_edit(fullname, email, profile_pic)
    if operation == 'update_password':
        old_password = flask.request.form['password']
        new_password1 = flask.request.form['new_password1']
        new_password2 = flask.request.form['new_password2']
        if not old_password or not new_password1 or not new_password2:
            flask.abort(400)
        return accounts_update_password(old_password,
                                        new_password1, new_password2)
    flask.abort(400)


def accounts_login(username, password1):
    """Handle user login."""
    connection = insta485.model.get_db()
    user_exists = connection.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    if not user_exists:
        flask.abort(403)
    user_password = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    ).fetchone()['password']
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    salt = user_password.split('$')[1]
    password_salted = salt + password1
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    if f"{algorithm}${salt}${password_hash}" != user_password:
        flask.abort(403)
    flask.session['username'] = username
    target = flask.request.args.get("target")
    return flask.redirect(target or flask.url_for('show_index'))


def accounts_create(username, password1, fullname, email, profile_pic):
    """Create a new user account."""
    connection = insta485.model.get_db()
    user_exists = connection.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    if user_exists:
        flask.abort(409)
    filename = profile_pic.filename
    uuid_basename = (
                     f"{uuid.uuid4().hex}"
                     f"{pathlib.Path(filename).suffix.lower()}")
    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
    profile_pic.save(path)
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new('sha512')
    password_salted = salt + password1
    hash_obj.update(password_salted.encode('utf-8'))
    password_string = "$".join(['sha512', salt, hash_obj.hexdigest()])
    connection.execute(
        "INSERT INTO users(username, password, fullname, email, filename) "
        "VALUES (?, ?, ?, ?, ?)",
        (username, password_string, fullname, email, uuid_basename,)
    )
    connection.commit()
    flask.session['username'] = username
    return flask.redirect(
        flask.request.args.get("target")
        or flask.url_for('show_index'))


def accounts_delete():
    """Delete user account."""
    if 'username' not in flask.session:
        flask.abort(403)
    username = flask.session['username']
    connection = insta485.model.get_db()
    connection.execute("PRAGMA foreign_keys = ON;")
    # Clear user posts
    post_filenames = connection.execute(
        "SELECT filename FROM posts WHERE owner = ?",
        (username,)
    ).fetchall()
    for post in post_filenames:
        post_path = (pathlib.Path(insta485.app.config["UPLOAD_FOLDER"]) /
                     post['filename'])
        post_path.unlink(missing_ok=True)
    # Clear user
    filename = connection.execute(
        "SELECT filename FROM users WHERE username = ?",
        (username,)
    ).fetchone()['filename']
    path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"]) / filename
    path.unlink()
    connection.execute(
        "DELETE FROM users WHERE username = ?",
        (username,)
    )
    connection.commit()
    flask.session.clear()
    target = flask.request.args.get("target")
    return flask.redirect(target or flask.url_for('show_index'))


def accounts_edit(fullname, email, profile_pic):
    """Edit user account."""
    if 'username' not in flask.session:
        flask.abort(403)
    connection = insta485.model.get_db()
    username = flask.session['username']
    if profile_pic:
        old_filename = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (username,)
        ).fetchone()['filename']
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(profile_pic.filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        upload_folder = pathlib.Path(insta485.app.config['UPLOAD_FOLDER'])
        new_filepath = upload_folder / uuid_basename
        profile_pic.save(new_filepath)
        old_filepath = upload_folder / old_filename
        old_filepath.unlink()
        connection.execute(
            "UPDATE users SET fullname = ?, "
            "email = ?, filename = ? WHERE username = ?",
            (fullname, email, uuid_basename, username)
        )
    else:
        connection.execute(
            "UPDATE users SET fullname = ?, email = ? WHERE username = ?",
            (fullname, email, username)
        )
    connection.commit()
    target = flask.request.args.get("target")
    return flask.redirect(target or flask.url_for('show_index'))


def accounts_update_password(old_password, new_password1, new_password2):
    """Update user password."""
    if 'username' not in flask.session:
        flask.abort(403)
    connection = insta485.model.get_db()
    username = flask.session['username']
    user_info = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    password_hash = user_info['password']
    salt = password_hash.split('$')[1]
    # Check the old password
    hashed_old = hashlib.sha512(
        (salt + old_password).encode('utf-8')
        ).hexdigest()
    if password_hash != f"sha512${salt}${hashed_old}":
        flask.abort(403)
    if new_password1 != new_password2:
        flask.abort(401)
    # Update password logic
    new_salt = uuid.uuid4().hex
    new_hash_obj = hashlib.new('sha512')
    new_password_salted = new_salt + new_password1
    new_hash_obj.update(new_password_salted.encode('utf-8'))
    new_password_hash = new_hash_obj.hexdigest()
    new_password_string = "$".join(['sha512', new_salt, new_password_hash])
    connection.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (new_password_string, username)
    )
    connection.commit()
    target = flask.request.args.get("target")
    return flask.redirect(target or flask.url_for('show_index'))

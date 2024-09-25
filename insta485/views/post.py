"""
Insta485 post view.

URLs include:
/posts/<postid_url_slug>/
"""
import pathlib  # standard import first
import uuid  # standard import second
import flask  # third-party imports next
import arrow
import insta485  # first-party import last


@insta485.app.route('/posts/<postid_url_slug>/', methods=['GET'])
def show_post(postid_url_slug):
    """Display post route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    connection = insta485.model.get_db()
    logname = flask.session['username']

    post = connection.execute(
        "SELECT filename, owner, postid, created "
        "FROM posts "
        "WHERE postid = ? ",
        (postid_url_slug,)
    ).fetchone()

    if post is None:
        flask.abort(404)

    idx = post['postid']
    comments = connection.execute(
        "SELECT commentid, owner, postid, text, created "
        "FROM comments "
        "WHERE postid = ? "
        "ORDER by commentid ASC",
        (idx,)
    ).fetchall()
    likes_dup = connection.execute(
        "SELECT COUNT(*) AS like_count "
        "FROM likes "
        "WHERE postid = ?",
        (idx,)
    ).fetchone()['like_count']

    liked_by_user = connection.execute(
        "SELECT 1 FROM likes WHERE postid = ? AND owner = ? ",
        (idx, logname)
    ).fetchone() is not None

    time = arrow.get(post['created']).humanize()

    profile_pic = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ?",
        (post['owner'],)
    ).fetchone()['filename']

    context = {
        "logname": logname,
        "likes": likes_dup,
        "time": time,
        "postid": idx,
        "comments": comments,
        "post_file": post['filename'],
        "username": post['owner'],
        "liked_by_user": liked_by_user,
        "profile_pic": profile_pic
    }

    return flask.render_template("post.html", **context)


@insta485.app.route('/posts/', methods=['POST'])
def handle_post():
    """Handle post create/delete."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    operation = flask.request.form["operation"]
    logname = flask.session['username']
    connection = insta485.model.get_db()

    if operation == 'create':
        postfile = flask.request.files["file"]
        if not postfile:
            flask.abort(400)

        filename1 = postfile.filename
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename1).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
        postfile.save(path)

        connection.execute(
            "INSERT INTO posts (filename, owner) VALUES (?, ?)",
            (uuid_basename, logname)
        )
        connection.commit()

    if operation == 'delete':
        postid = flask.request.form['postid']

        post = connection.execute(
            "SELECT filename, owner "
            "FROM posts "
            "WHERE postid = ?",
            (postid,)
        ).fetchone()

        if post['owner'] != logname:
            flask.abort(403)

        filename2 = post['filename']
        path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"]) / filename2
        path.unlink()

        connection.execute("DELETE FROM comments WHERE postid = ?", (postid,))
        connection.execute("DELETE FROM posts WHERE postid = ?", (postid,))
        connection.commit()

    target = flask.request.args.get("target")
    if not target:
        return flask.redirect(
            flask.url_for('show_user', user_url_slug=logname)
        )
    return flask.redirect(target)

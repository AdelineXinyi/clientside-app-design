"""
Insta485 index (main) view.

URLs include:
/
"""
import arrow  # third-party import should be first
import flask
import insta485


@insta485.app.route('/')
def show_index():
    """Display / route."""
    connection = insta485.model.get_db()
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    logname = flask.session['username']
    # Fetch logged-in user's followed users
    user_following = connection.execute(
        "SELECT username, fullname, filename "
        "FROM users "
        "WHERE username = ? "
        "OR username IN ( "
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ? )",
        (logname, logname)
    ).fetchall()
    # Create dictionary with username as key and filename as value
    user_filenames = {
        user['username']: user['filename'] for user in user_following
    }
    posts = connection.execute(
        f"SELECT filename, owner, postid, created "
        f"FROM posts "
        f"WHERE owner IN ({','.join('?' * len(user_filenames))}) "
        f"ORDER BY postid DESC",
        tuple(user_filenames)
    ).fetchall()
    complete_posts = []
    for post in posts:
        post_id = post['postid']
        # Fetch comments
        comments_dup = connection.execute(
            "SELECT commentid, owner, postid, text, created "
            "FROM comments "
            "WHERE postid = ? "
            "ORDER by commentid ASC",
            (post_id,)
        ).fetchall()
        # Fetch likes
        likes = connection.execute(
            "SELECT COUNT(*) AS like_count "
            "FROM likes "
            "WHERE postid = ?",
            (post_id,)
        ).fetchone()['like_count']
        # Check if post is liked by the logged-in user
        liked_by_user = connection.execute(
            "SELECT 1 FROM likes WHERE postid = ? AND owner = ?",
            (post_id, logname)
        ).fetchone() is not None

        # Get human-readable time and user profile picture
        time = arrow.get(post['created']).humanize()
        profile_pic = user_filenames.get(post['owner'], None)

        # Create post dictionary
        post_data = {
            "postid": post['postid'],
            "owner": post['owner'],
            "post_file": post['filename'],
            "time": time,
            "comments": comments_dup,
            "likes": likes,
            "liked_by_user": liked_by_user,
            "profile_pic": profile_pic
        }
        complete_posts.append(post_data)

    # Render template with posts
    context = {
        "logname": logname,
        "posts": complete_posts
    }
    return flask.render_template("index.html", **context)

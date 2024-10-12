"""REST API for posts."""
import flask
import insta485
import insta485.model


@insta485.app.route('/api/v1/', methods=['GET'])
def get_service():
    """Return a list of services available."""
    services = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**services)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=['GET'])
def get_post(postid_url_slug):
    """Docstring."""
    username = flask.session.get('username')
    if not username:
        auth = flask.request.authorization
        if insta485.model.hash_pass() is False:
            return insta485.model.helper_auth()
        username = auth['username']
    connection = insta485.model.get_db()
    post = connection.execute(
        "SELECT owner, filename, "
        "created FROM posts "
        "WHERE postid = ?",
        (postid_url_slug,)).fetchone()
    if post is None:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404
    comments = connection.execute(
        """
        SELECT commentid, owner, text
        FROM comments
        WHERE postid = ?
        ORDER BY commentid ASC
        """,
        (postid_url_slug,)
    ).fetchall()

    # Fetch likes count
    likes_count = connection.execute(
        "SELECT COUNT(*) AS numLikes FROM likes WHERE postid = ?",
        (postid_url_slug,)
    ).fetchone()['numLikes']

    # Check if the logged-in user likes this post and get likeid if exists
    user_like = connection.execute(
        "SELECT likeid FROM likes WHERE postid = ? AND owner = ?",
        (postid_url_slug, username)
    ).fetchone()

    logname_likes = user_like is not None
    likeid_url = f"/api/v1/likes/{user_like['likeid']}/" \
        if logname_likes else None

    # Prepare comments list
    comments_list = []
    for comment in comments:
        comments_list.append({
            "commentid": comment['commentid'],
            "lognameOwnsThis": comment['owner'] == username,
            "owner": comment['owner'],
            "ownerShowUrl": f"/users/{comment['owner']}/",
            "text": comment['text'],
            "url": f"/api/v1/comments/{comment['commentid']}/"
        })
    owner_info = connection.execute(
        "SELECT filename FROM users WHERE username = ?",
        (post['owner'],)
    ).fetchone()

    owner_img_filename = owner_info['filename'] \
        if owner_info else 'default.jpg'

    # Prepare the response context
    context = {
        "comments": comments_list,
        "comments_url": f"/api/v1/comments/?postid={postid_url_slug}",
        "created": post['created'],  # Raw timestamp
        "imgUrl": f"/uploads/{post['filename']}",
        "likes": {
            "lognameLikesThis": logname_likes,
            "numLikes": likes_count,
            "url": likeid_url
        },
        "owner": post['owner'],
        "ownerImgUrl": f"/uploads/{owner_img_filename}",
        "ownerShowUrl": f"/users/{post['owner']}/",
        "postShowUrl": f"/posts/{postid_url_slug}/",
        "postid": postid_url_slug,
        "url": f"/api/v1/posts/{postid_url_slug}/"
    }

    return flask.jsonify(**context), 200


@insta485.app.route('/api/v1/posts/', methods=['GET'])
def get_posts():
    """Docstring."""
    username = flask.session.get('username')
    connection = insta485.model.get_db()
    if not username:
        auth = flask.request.authorization
        if insta485.model.hash_pass() is False:
            return insta485.model.helper_auth()
        username = auth['username']
    followed_users = connection.execute(
        "SELECT username2 FROM following WHERE username1 = ?",
        (username,)).fetchall()
    followed_usernames = [row['username2'] for row in followed_users]
    followed_usernames.append(username)

    postid_lte = flask.request.args.get('postid_lte', type=int)
    size = flask.request.args.get('size', default=10, type=int)
    page = flask.request.args.get('page', default=0, type=int)
    if size <= 0:
        return flask.jsonify(
            {"message": "size must be a positive integer",
             "status_code": 400}), 400
    if page < 0:
        return flask.jsonify(
            {"message": "page must be a non-negative integer",
             "status_code": 400}), 400
    if postid_lte is None:
        recent_post = connection.execute(
            f"SELECT postid FROM posts "
            f"WHERE owner IN ({', '.join(['?'] * len(followed_usernames))}) "
            f"ORDER BY postid DESC LIMIT 1", followed_usernames
        ).fetchone()
        postid_lte = recent_post['postid'] if recent_post else 0
    query = f"""
        SELECT postid, filename, owner, created
        FROM posts
        WHERE owner IN ({', '.join(['?'] * len(followed_usernames))})
    """
    query += " AND postid <= ?"
    query += " ORDER BY postid DESC LIMIT ? OFFSET ?"  # Changed this line
    params = followed_usernames
    params.append(postid_lte)
    params += [size, page * size]
    posts = connection.execute(query, params).fetchall()

    results = [{
        "postid": post['postid'],
        "url": f"/api/v1/posts/{post['postid']}/"
    } for post in posts]

    # Check if there's a next page
    next_url = ""
    if len(posts) == size:
        next_url = flask.url_for('get_posts', size=size,
                                 page=page + 1, postid_lte=postid_lte)

    current_url = flask.request.path
    if flask.request.query_string:
        current_url += f"?{flask.request.query_string.decode()}"
    return flask.jsonify({
        "next": next_url,
        "results": results,
        "url": current_url
    }), 200

"""REST API for posts."""
import flask
import insta485
import arrow

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

@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/',methods=['GET'])
def get_post(postid_url_slug):
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    if not username or not password:
        return flask.jsonify({"error": "Unauthorized"}), 403
    connection = insta485.model.get_db()
    post = connection.execute(
        "SELECT owner, filename, created FROM posts WHERE postid = ?",
        (postid_url_slug,)
    ).fetchone()

    # Return 404 if post not found
    if post is None:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404

    # Fetch comments
    comments_query = """
        SELECT commentid, owner, text 
        FROM comments 
        WHERE postid = ?
        ORDER BY commentid ASC
    """
    comments = connection.execute(comments_query, (postid_url_slug,)).fetchall()

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
    likeid_url = f"/api/v1/likes/{user_like['likeid']}/" if logname_likes else None

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

    owner_img_filename = owner_info['filename'] if owner_info else 'default.jpg'

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
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    if not username or not password:
        return flask.jsonify({"error": "Unauthorized"}), 403
    connection = insta485.model.get_db()
    followed_users = connection.execute(
        "SELECT username2 FROM following WHERE username1 = ?",
        (username,)
    ).fetchall()
    followed_usernames = [row['username2'] for row in followed_users]
    followed_usernames.append(username) 
    query = f"""
        SELECT postid, filename, owner, created 
        FROM posts 
        WHERE owner IN ({','.join(['?'] * len(followed_usernames))})
        ORDER BY postid DESC 
        LIMIT 10
    """
    posts = connection.execute(query, followed_usernames).fetchall()
    results = []
    for post in posts:
        results.append({
            "postid": post['postid'],
            "url": f"/api/v1/posts/{post['postid']}/"
        })

    # Check if there's a next page
    next_url = ""
    if len(posts) == 10:
        next_url = flask.url_for('get_posts', username=username, _external=True)  # Assuming pagination

    return flask.jsonify({
        "next": next_url,
        "results": results,
        "url": flask.request.path
    }), 200


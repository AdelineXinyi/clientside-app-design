import flask
import insta485
import sys


@insta485.app.route('/api/v1/likes/<int:postid_url_slug>', methods=['POST'])
def add_like(postid_url_slug):
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
  
    if not username or not password:
        return flask.jsonify({"error": "Unauthorized"}), 403
    connection = insta485.model.get_db()
    post = connection.execute(
        "SELECT owner, created FROM posts WHERE postid = ?",
        (postid_url_slug,)
    ).fetchone()

    # Return 404 if post not found
    if post is None:
        print(f"Post with postid {postid_url_slug} not found.")
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404

    existing_like = connection.execute(
        "SELECT likeid FROM likes WHERE postid = ? AND owner = ?",
        (postid_url_slug, username)
    ).fetchone()
    if existing_like:
        return flask.jsonify({
            "likeid": existing_like['likeid'],
            "url": f"/api/v1/likes/{existing_like['likeid']}/"
        }), 200

    # Insert new like into the database
    result = connection.execute(
        "INSERT INTO likes (postid, owner) VALUES (?, ?)",
        (postid_url_slug, username)
    )
    connection.commit()
    
    # Get the new like ID
    new_like_id = result.lastrowid
    
    return flask.jsonify({
        "likeid": new_like_id,
        "url": f"/api/v1/likes/{new_like_id}/"
    }), 201
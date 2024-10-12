"""Docstring."""
import sqlite3
import flask
import insta485
import insta485.model


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def add_comment():
    """Add a comment."""
    username1 = flask.session.get('username')
    connection = insta485.model.get_db()
    if not username1:
        auth = flask.request.authorization
        if insta485.model.hash_pass() is False:
            insta485.model.helper_auth()
        username1 = auth['username']

    postid = flask.request.args.get('postid')
    text = flask.request.json.get('text')

    if not postid or not text:
        return flask.jsonify({"error": "postid and text are required"}), 404

    try:
        # Insert the comment into the database
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO comments (postid, text, owner) VALUES (?, ?, ?)',
            (postid, text, username1)
        )
        comment_id = cursor.lastrowid  # Retrieve last inserted comment ID
        connection.commit()  # Commit the transaction

        return flask.jsonify({
            "commentid": comment_id,
            "lognameOwnsThis": True,
            "owner": username1,
            "ownerShowUrl": f"/users/{username1}/",
            "text": text,
            "url": f"/api/v1/comments/{comment_id}/"
        }), 201

    except sqlite3.Error as e:
        print("Database error occurred:", e)  # Log the error for debugging
        return flask.jsonify(
            {"error": "An error occurred while adding the comment."}
        ), 500


@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    """Delete a comment."""
    username1 = flask.session.get('username')
    connection = insta485.model.get_db()

    if not username1:
        auth = flask.request.authorization
        if insta485.model.hash_pass() is False:
            insta485.model.helper_auth()
        username1 = auth['username']

    comment = connection.execute(
        'SELECT * FROM comments WHERE commentid = ?', (commentid,)
    ).fetchone()

    if not comment:
        return flask.jsonify({"error": "valid commentid is required"}), 404

    if comment['owner'] != username1:
        return flask.jsonify({"error": "comments not owned"}), 403

    connection.execute(
        'DELETE FROM comments WHERE commentid = ?', (commentid,))
    connection.commit()

    return '', 204

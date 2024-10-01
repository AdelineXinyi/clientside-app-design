import flask
import insta485
import insta485.model


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def add_comment():
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    postid = flask.request.args.get('postid')
    text = flask.request.json.get('text')

    if not postid:
        return flask.jsonify({"error": "postid and text are required"}), 404

    connection = insta485.model.get_db()
    cursor = connection.cursor()

    # Insert the comment into the database
    cursor.execute('INSERT INTO comments (postid, text, owner) VALUES (?, ?, ?)',
                   (postid, text, username))  
    comment_id = cursor.lastrowid
    connection.commit()

    return flask.jsonify({
        "commentid": comment_id,
        "lognameOwnsThis": True,
        "owner": username,
        "ownerShowUrl": f"/users/{username}/",
        "text": text,
        "url": f"/api/v1/comments/{comment_id}/"
    }), 201

@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    connection = insta485.model.get_db()
    comment = connection.execute('SELECT * FROM comments WHERE commentid = ?',
                                (commentid,)).fetchone()
    if not comment:
        return flask.jsonify({"error": "valid commentid is required"}), 404
    if comment['owner'] != username:  
       return flask.jsonify({"error": "comments not owned"}), 403
    connection.execute('DELETE FROM comments WHERE commentid = ?', (commentid,))
    connection.commit()

    return '', 204 
"""Docstring."""
import flask
import insta485
import insta485.model


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def add_like():
    """Docstring."""
    username2 = flask.session.get('username')
    connection = insta485.model.get_db()
    if not username2:
        auth = flask.request.authorization
        if insta485.model.hash_pass() is False:
            insta485.model.helper_auth()
        username2 = auth['username']
    pid = flask.request.args.get("postid")
    post = connection.execute(
        "SELECT owner, filename, created FROM posts WHERE postid = ?",
        (pid,)
    ).fetchone()
    if post is None:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404
    existing_like = connection.execute(
        "SELECT likeid FROM likes WHERE postid = ? AND owner = ?",
        (pid, username2)
    ).fetchone()
    if existing_like:
        return flask.jsonify({
            "likeid": existing_like['likeid'],
            "url": f"/api/v1/likes/{existing_like['likeid']}/"
        }), 200
    # action
    result = connection.execute(
        "INSERT INTO likes (postid, owner) VALUES (?, ?)",
        (pid, username2)
    )
    connection.commit()
    new_like_id = result.lastrowid
    return flask.jsonify({
        "likeid": new_like_id,
        "url": f"/api/v1/likes/{new_like_id}/"
    }), 201


@insta485.app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
def delete_like(likeid):
    """Docstring."""
    username3 = flask.session.get('username')
    connection = insta485.model.get_db()
    if not username3:
        auth1 = flask.request.authorization
        if insta485.model.hash_pass() is not True:
            insta485.model.helper_auth()
        username3 = auth1['username']
    like = connection.execute(
        "SELECT owner FROM likes WHERE likeid = ?",
        (likeid,)).fetchone()
    if like is None:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404
    if like['owner'] != username3:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403
    # action
    connection.execute(
        "DELETE FROM likes WHERE likeid = ?",
        (likeid,)
    )
    connection.commit()
    return '', 204

import flask
import insta485
import insta485.model


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def add_like():
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    if not username or not password:
        return flask.jsonify({"error": "Unauthorized"}), 403
    connection = insta485.model.get_db()
    #test exist
    pid=flask.request.args.get("postid")
    post = connection.execute(
        "SELECT owner, filename, created FROM posts WHERE postid = ?",
        (pid,)
    ).fetchone()
    if post is None:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404
    existing_like = connection.execute(
        "SELECT likeid FROM likes WHERE postid = ? AND owner = ?",
        (pid, username)
    ).fetchone()
    if existing_like:
        return flask.jsonify({
            "likeid": existing_like['likeid'],
            "url": f"/api/v1/likes/{existing_like['likeid']}/"
        }), 200
    #action
    result = connection.execute(
        "INSERT INTO likes (postid, owner) VALUES (?, ?)",
        (pid, username)
    )
    connection.commit()
    new_like_id = result.lastrowid
    return flask.jsonify({
        "likeid": new_like_id,
        "url": f"/api/v1/likes/{new_like_id}/"
    }), 201

@insta485.app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
def delete_like(likeid):
    print("hello")
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    if not username or not password:
        return flask.jsonify({"error": "Unauthorized"}), 403
    connection = insta485.model.get_db()
    #test exist
    like = connection.execute(
        "SELECT owner FROM likes WHERE likeid = ?",
        (likeid,)
    ).fetchone()
    if like is None:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404
    if like['owner'] != username:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403
    #action
    connection.execute(
        "DELETE FROM likes WHERE likeid = ?",
        (likeid,)
    )
    connection.commit() 
    return '', 204

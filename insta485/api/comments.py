import flask
import insta485
import insta485.model
import hashlib


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def add_comment():
    username = flask.session.get('username')
    connection = insta485.model.get_db()
    if not username:
        auth = flask.request.authorization
        if  insta485.model.hash_pass()==False:
            return flask.jsonify({
            "message": "Authentication required",
            "status_code": 403
        }), 403
        username = auth['username']
    postid = flask.request.args.get('postid')
    text = flask.request.json.get('text')

    if not postid:
        return flask.jsonify({"error": "postid and text are required"}), 404

    try:
        # Insert the comment into the database
        cursor = connection.cursor()  # Get the cursor before executing the insert
        cursor.execute('INSERT INTO comments (postid, text, owner) VALUES (?, ?, ?)', (postid, text, username))
        
        comment_id = cursor.lastrowid  # Retrieve last inserted comment ID
        connection.commit()  # Commit the transaction

        return flask.jsonify({
            "commentid": comment_id,
            "lognameOwnsThis": True,
            "owner": username,
            "ownerShowUrl": f"/users/{username}/",
            "text": text,
            "url": f"/api/v1/comments/{comment_id}/"
        }), 201
    except Exception as e:
        print("An error occurred:", e)  # Log the error for debugging
        return flask.jsonify({"error": "An error occurred while adding the comment."}), 500  # Internal server error
    

@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    username = flask.session.get('username')
    connection = insta485.model.get_db()
    if not username:
        auth = flask.request.authorization
        if  insta485.model.hash_pass()==False:
            return flask.jsonify({
            "message": "Authentication required",
            "status_code": 403
        }), 403
        username = auth['username']
    comment = connection.execute('SELECT * FROM comments WHERE commentid = ?',
                                (commentid,)).fetchone()
    if not comment:
        return flask.jsonify({"error": "valid commentid is required"}), 404
    if comment['owner'] != username:  
       return flask.jsonify({"error": "comments not owned"}), 403
    connection.execute('DELETE FROM comments WHERE commentid = ?', (commentid,))
    connection.commit()

    return '', 204 

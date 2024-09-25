"""
Insta485 index explore view.

URLs include:
/
"""
import flask
import insta485


@insta485.app.route('/explore/')
def explore():
    """Display explore route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    logname = flask.session['username']
    users = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username != ? "
        "AND username NOT IN ( "
        "SELECT username2 FROM following "
        "WHERE username1 = ?)",
        (logname, logname)
    ).fetchall()
    context = {
        "logname": logname,
        "users": users
    }
    return flask.render_template("explore.html", **context)

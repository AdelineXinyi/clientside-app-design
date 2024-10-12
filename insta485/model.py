"""Insta485 model (database) API."""
import sqlite3
import hashlib
import flask
import insta485


def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    """Open a new database connection.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    if 'sqlite_db' not in flask.g:
        db_filename = insta485.app.config['DATABASE_FILENAME']
        flask.g.sqlite_db = sqlite3.connect(str(db_filename))
        flask.g.sqlite_db.row_factory = dict_factory

        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")

    return flask.g.sqlite_db


def hash_pass():
    """Docstring."""
    auth = flask.request.authorization
    if not auth or 'username' not in auth or 'password' not in auth:
        return False
    username = auth['username']
    password = auth['password']
    connection = insta485.model.get_db()
    user_password = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)).fetchone()['password']
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    salt = user_password.split('$')[1]
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    if f"{algorithm}${salt}${password_hash}" != user_password:
        return False
    return True


def helper_auth():
    """Docstring."""
    return flask.jsonify({
        "message": "Authentication required",
        "status_code": 403
    }), 403


@insta485.app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    assert error or not error  # Needed to avoid superfluous style error
    sqlite_db = flask.g.pop('sqlite_db', None)
    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()

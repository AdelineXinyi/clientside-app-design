"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.post import show_post, handle_post
from insta485.views.explore import explore
from insta485.views.user import (show_user, show_followers,
                                 show_following, handle_likes, handle_comments,
                                 upload_file, handle_follows)
from insta485.views.account import (login, create, edit, delete, auth,
                                    password, handle_logout, handle_account)

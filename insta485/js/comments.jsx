import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

export default function Comments({ postid, initialComments }) {
  const [comments, setComments] = useState(initialComments);
  const [newCommentText, setNewCommentText] = useState("");

  useEffect(() => {
    setComments(initialComments);
  }, [initialComments]);

  const handleDelete = (commentid) => {
    const deleteCommentUrl = `/api/v1/comments/${commentid}`;
    fetch(deleteCommentUrl, { credentials: "same-origin", method: "DELETE" })
      .then((response) => {
        if (!response.ok) throw new Error(response.statusText);
        setComments((prevComments) =>
          prevComments.filter((comment) => comment.commentid !== commentid),
        );
      })
      .catch((error) => console.error("Error deleting comment:", error));
  };

  const handleSubmit = (event) => {
    if (event.key === "Enter" && newCommentText.trim()) {
      event.preventDefault(); // Prevent default behavior for Enter key
      const makeCommentUrl = `/api/v1/comments/?postid=${postid}`;
      fetch(makeCommentUrl, {
        credentials: "same-origin",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: newCommentText }),
      })
        .then((response) => {
          if (!response.ok) throw new Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          setComments((prevComments) => [
            ...prevComments,
            {
              commentid: data.commentid,
              lognameOwnsThis: data.lognameOwnsThis,
              owner: data.owner,
              text: data.text,
              ownerShowUrl: data.ownerShowUrl,
              url: data.url,
            },
          ]);
          setNewCommentText("");
        })
        .catch((error) => console.error("Error adding comment:", error));
    }
  };

  return (
    <div>
      <section>
        {comments.map((comment) => (
          <form
            key={comment.commentid}
            data-testid="comment-text"
            onSubmit={(e) => e.preventDefault()}
          >
            <div>
              <p>
                <a href={comment.ownerShowUrl}>{comment.owner}</a>:{" "}
                {comment.text}
              </p>
              {comment.lognameOwnsThis && (
                <button
                  type="button"
                  data-testid="delete-comment-button"
                  onClick={() => handleDelete(comment.commentid)}
                >
                  Delete Comment
                </button>
              )}
            </div>
          </form>
        ))}
      </section>
      {/* Form for adding new comments */}
      <form data-testid="comment-form">
        <input
          type="text"
          required
          value={newCommentText}
          onChange={(e) => setNewCommentText(e.target.value)}
          onKeyDown={handleSubmit} // Ensure the function is called on keydown
        />
      </form>
    </div>
  );
}

Comments.propTypes = {
  postid: PropTypes.number.isRequired,
  initialComments: PropTypes.arrayOf(
    PropTypes.shape({
      commentid: PropTypes.number.isRequired,
      lognameOwnsThis: PropTypes.bool.isRequired,
      owner: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      ownerShowUrl: PropTypes.string.isRequired,
      url: PropTypes.string.isRequired,
    }),
  ).isRequired,
};

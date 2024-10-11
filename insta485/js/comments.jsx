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
    fetch(deleteCommentUrl, { credentials: 'same-origin', method: 'DELETE' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        setComments((prevComments) => prevComments.filter(comment => comment.commentid !== commentid));
      })
      .catch((error) => console.log(error));
  };

  const handleSubmit = (event) => {
    if (event.key === 'Enter' && newCommentText.trim()) {
      event.preventDefault();
      const makeCommentUrl = `api/v1/comments/?postid=${postid}`;
      fetch(makeCommentUrl, {
        credentials: 'same-origin',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: newCommentText }),
      })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
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
            url: data.url
          },
        ]);
        setNewCommentText("");
      })
      .catch((error) => console.log(error));
    }
  };

  return (
    <div>
      <section>
        {comments.map((comment) => (
          <div key={comment.commentid}>
            <p>
              <a href={comment.ownerShowUrl}>{comment.owner}</a>: {comment.text}
            </p>
            {comment.lognameOwnsThis && (
              <button onClick={() => handleDelete(comment.commentid)}>Delete Comment</button>
            )}
          </div>
        ))}
      </section>
      <input
        type="text"
        required
        placeholder="Add a comment"
        value={newCommentText}
        onChange={(e) => setNewCommentText(e.target.value)}
        onKeyDown={handleSubmit}
      />
    </div>
  );
}

Comments.propTypes = {
  postid: PropTypes.string.isRequired,
  initialComments: PropTypes.arrayOf(PropTypes.shape({
    commentid: PropTypes.number.isRequired,
    lognameOwnsThis: PropTypes.bool.isRequired,
    owner: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
    ownerShowUrl: PropTypes.string.isRequired,
    url: PropTypes.string.isRequired,
  })).isRequired,
};

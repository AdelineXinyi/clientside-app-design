import React from "react";
import PropTypes from "prop-types";

export default function Likes({ numLikes, isLiked, postURL, toggle }) {
  const handleDoubleClick = () => {
    if (!isLiked) {
      return toggle();
    }
    return undefined;
  };

  return (
    <div>
      <img
        src={postURL}
        alt="Post"
        onDoubleClick={handleDoubleClick}
        style={{ cursor: "pointer" }}
      />
      <button type="button" data-testid="like-unlike-button" onClick={toggle}>
        {isLiked ? "Unlike" : "Like"}
      </button>
      <p>
        {numLikes} {numLikes === 1 ? "like" : "likes"}
      </p>
    </div>
  );
}

Likes.propTypes = {
  numLikes: PropTypes.number.isRequired,
  postURL: PropTypes.string.isRequired,
  toggle: PropTypes.func.isRequired,
  isLiked: PropTypes.bool.isRequired,
};

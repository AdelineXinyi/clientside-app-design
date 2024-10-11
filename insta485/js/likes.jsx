import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

export default function Likes({ postid, initialLikes }) {
  const [likes, setLikes] = useState(initialLikes);

  useEffect(() => {
    setLikes(initialLikes);
  }, [initialLikes]);

  const handleLike = () => {
    const makeLikeUrl = `/api/v1/likes/?postid=${postid}`;
    fetch(makeLikeUrl, { credentials: 'same-origin', method: 'POST' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
          setLikes((prevLikes) => ({
            ...prevLikes,
            numLikes: prevLikes.numLikes + 1,
            lognameLikesThis: true,
            url: data.url,
          }));
      })
      .catch((error) => console.log(error));
  };

  const handleUnlike = () => {
    const deleteLikeUrl = likes.url;
    fetch(deleteLikeUrl, { credentials: 'same-origin', method: 'DELETE' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
      })
      .then(() => {
          setLikes((prevLikes) => ({
            ...prevLikes,
            numLikes: prevLikes.numLikes - 1,
            lognameLikesThis: false,
            url: null,
          }));
      })
      .catch((error) => console.log(error));
  };

  const handleDoubleClick = () => {
    if (!likes.lognameLikesThis) {
      handleLike();
    }
  };

  return (
    <div onDoubleClick={handleDoubleClick}>
      <button 
        data-testid="like-unlike-button"
        onClick={likes.lognameLikesThis ? handleUnlike : handleLike}>
        {likes.lognameLikesThis ? 'Unlike' : 'Like'}
      </button>
      <p>{likes.numLikes} {likes.numLikes === 1 ? 'Like' : 'Likes'}</p>
    </div>
  );
}

Likes.propTypes = {
  postid: PropTypes.number.isRequired,
  initialLikes: PropTypes.shape({
    numLikes: PropTypes.number.isRequired,
    lognameLikesThis: PropTypes.bool.isRequired,
    url: PropTypes.string,
  }).isRequired,
};
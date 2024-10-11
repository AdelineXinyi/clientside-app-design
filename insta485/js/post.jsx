import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import Likes from "./likes";
import Comments from "./comments";

dayjs.extend(relativeTime);
dayjs.extend(utc);

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("")
  const [comments, setComments] = useState([])
  const [likes, setLikes] = useState({})
  const [comments_url, setCommentsUrl] = useState("")
  const [created, setCreated] = useState("")
  const [ownerShowUrl, setOwnerShowUrl] = useState("")
  const [postShowUrl, setPostShowUrl] = useState("")
  const [postid, setPostid] = useState(0)

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setOwnerImgUrl(data.ownerImgUrl)
          setComments(data.comments)
          setLikes(data.likes)
          setCommentsUrl(data.comments_url)
          setCreated(data.created)
          setOwnerShowUrl(data.ownerShowUrl)
          setPostShowUrl(data.postShowUrl)
          setPostid(data.postid)
        }
      })
      .catch((error) => console.log(error));

    const formattedCreatedTime = created
      ? dayjs.utc(created).local().fromNow()
      : "";

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  // Render post image and post owner
  return (
    <div className="post">
      <img src={imgUrl} alt="post_image" />
      <p>{owner}</p>
            <p>
                <a href={postShowUrl}>{formattedCreatedTime()}</a>
                <a href={ownerShowUrl}>{owner}</a>
                <a href={ownerShowUrl}>
                    <img src={ownerImgUrl} alt={`${owner}s profile image`} className="profile-pic"/>
                </a>
            </p>
            <img src={postShowUrl} alt={`Post ${postid}`} className="post-pic"></img>
            <Likes postid={postid} initialLikes={likes} />
            <Comments postid={postid} initialComments={comments} />
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

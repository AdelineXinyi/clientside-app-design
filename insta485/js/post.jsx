import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import InfiniteScroll from "react-infinite-scroll-component";
import Likes from "./likes";
import Comments from "./comments";

dayjs.extend(relativeTime);
dayjs.extend(utc);

export default function Post({ url }) {
  const [postData, setPostData] = useState({
    posts: [],
  });
  const [nextUrl, setNextUrl] = useState(url); // Initialize nextUrl with the provided URL
  const [hasMore, setHasMore] = useState(true); // To control when to stop infinite scroll

  // Fetch posts function
  const fetchPosts = async () => {
    if (!nextUrl) return; // If there's no next URL, stop the function
    try {
      const response = await fetch(nextUrl, { credentials: "same-origin" });
      if (!response.ok) throw new Error(response.statusText);
      const data = await response.json();

      // Array to hold detailed post data
      const detailedPostsPromises = data.results.map(async (result) => {
        const postResponse = await fetch(result.url, { credentials: "same-origin" });
        if (!postResponse.ok) throw new Error(postResponse.statusText);
        const postDetail = await postResponse.json(); // Fetch each post's details
        return {
          imgUrl: postDetail.imgUrl,
          owner: postDetail.owner,
          ownerImgUrl: postDetail.ownerImgUrl,
          comments: postDetail.comments,
          likes: postDetail.likes,
          created: postDetail.created,
          ownerShowUrl: postDetail.ownerShowUrl,
          postShowUrl: postDetail.postShowUrl,
          postId: postDetail.postid,
        };
      });

      // Resolve all the promises to get detailed post data
      const detailedPosts = await Promise.all(detailedPostsPromises);

      // Append new detailed posts to the postData
      setPostData((prevPostData) => {
        const existingPostIds = new Set(prevPostData.posts.map(post => post.postId));
        const newPosts = detailedPosts.filter(post => !existingPostIds.has(post.postId));

        return {
          posts: [...prevPostData.posts, ...newPosts], // Append only unique new posts
        };
      });

      // Update nextUrl state for pagination
      if (data.next) {
        setNextUrl(data.next);
      } else {
        setHasMore(false); // If there's no next URL, stop infinite scroll
      }
    } catch (error) {
      console.error("Error fetching posts:", error);
    }
  };

  // Fetch posts when the component mounts (initial load)
  useEffect(() => {
    fetchPosts(); // Call fetchPosts once when the component mounts
  }, []); // Empty dependency array ensures this runs only once

  // Resetting scroll position when component mounts
  useEffect(() => {
    window.scrollTo(0, 0); // Scroll to top of the page
  }, []);

  return (
    <div className="post">
      <InfiniteScroll
        dataLength={postData.posts.length} // Length of currently loaded posts
        next={fetchPosts} // Function to load more when scrolling
        hasMore={hasMore} // Whether there's more to load
        loader={<h4>Loading more posts...</h4>} // Loading indicator
        endMessage={<p>No more posts to display.</p>} // End message when no more posts
      >
        {[...postData.posts].map((post) => (
          <div key={post.postId} className="additional-posts">
            <a href={post.ownerShowUrl}>
              <img
                src={post.ownerImgUrl}
                alt={`${post.owner}'s profile`}
                className="profile-pic"
              />
            </a>
            <a href={post.ownerShowUrl}>{post.owner}</a>
            <p>
              <a href={post.postShowUrl}>
                {dayjs.utc(post.created).local().fromNow()}
              </a>
            </p>
            <Likes postid={post.postId} initialLikes={post.likes} postURL={post.imgUrl} />
            <Comments postid={post.postId} initialComments={post.comments} />
          </div>
        ))}
      </InfiniteScroll>
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

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
  const [loading, setLoading] = useState(true);
  const [postData, setPostData] = useState({
    posts: [],
  });
  const [nextUrl, setNextUrl] = useState(url); // Initialize nextUrl with the provided URL

  // Fetch posts
  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true); // Set loading to true at the start
        const response = await fetch(nextUrl, { credentials: "same-origin" });
        if (!response.ok) throw new Error(response.statusText);
        const data = await response.json();

        // Array to hold detailed post data
        const detailedPostsPromises = data.results.map(async (result) => {
          const postResponse = await fetch(result.url, { credentials: "same-origin" });
          if (!postResponse.ok) throw new Error(postResponse.statusText);
          const postData = await postResponse.json(); // Fetch each post's details
          return {
            imgUrl: postData.imgUrl,
            owner: postData.owner,
            ownerImgUrl: postData.ownerImgUrl,
            comments: postData.comments,
            likes: postData.likes,
            created: postData.created,
            ownerShowUrl: postData.ownerShowUrl,
            postShowUrl: postData.postShowUrl,
            postId: postData.postid,
          };
        });

        // Resolve all the promises to get detailed post data
        const detailedPosts = await Promise.all(detailedPostsPromises);

        // Append new detailed posts to the postData
        setPostData((prevPostData) => ({
          posts: [...prevPostData.posts, ...detailedPosts], // Append new detailed posts
        }));

        // Update nextUrl state
        setNextUrl(data.next); // Set nextUrl for pagination
        setLoading(false); // Set loading to false after fetching
      } catch (error) {
        console.error("Error fetching posts:", error);
        setLoading(false); // Ensure loading is set to false on error
      }
    };

    // Only fetch posts if nextUrl is defined
    if (nextUrl) {
      fetchPosts();
    }
  }, [nextUrl]); // Dependency on nextUrl

  // Resetting scroll position when component mounts
  useEffect(() => {
    window.scrollTo(0, 0); // Scroll to top of the page
  }, []);

  return (
    <div className="post">
      {loading ? (
        <p>Loading...</p> // Show loading message until data arrives
      ) : (
        <InfiniteScroll
          dataLength={postData.posts.length} // Length of currently loaded posts
          next={nextUrl} // Function to load more
          hasMore={!!nextUrl} // Whether there's more to load
          loader={<h4>Loading more posts...</h4>} // Loading indicator
          endMessage={<p>No more posts to display.</p>} // End message
        >
          {postData.posts.map((post) => (
            <div key={post.postId} className="additional-posts">
              <img src={post.imgUrl} alt="post_image" />
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
              <img src={post.postShowUrl} alt={`Post ${post.postId}`} className="post-pic" />
              <Likes postid={post.postId} initialLikes={post.likes} />
              <Comments postid={post.postId} initialComments={post.comments} />
            </div>
          ))}
        </InfiniteScroll>
      )}
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

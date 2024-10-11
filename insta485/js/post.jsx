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
    imgUrl: "",
    owner: "",
    ownerImgUrl: "",
    comments: [],
    likes: {
      numLikes: 0,
      lognameLikesThis: false,
      url: ""
    },
    created: "",
    ownerShowUrl: "",
    postShowUrl: "",
    postId: 1,
  });
  const [pagenation, setPagenation] = useState({
    next: "",
    results: [],
    url: ""
  })

  // Fetch posts
  // 1. fetch api/v1/posts/
  // 2. 10 posts are put in the results (with urls and post ids ())
  //      - if less, next will be empty
  //      - if more, next will have the next page
  // 3. fetch api/v1/posts/<post_id> for each post id (full url)
  // 4. 
  useEffect(() => {
    let ignoreStaleRequest = false;

    const fetchPostData = async () => {
      try {
        const response = await fetch(url, { credentials: "same-origin" });
        if (!response.ok) throw new Error(response.statusText);
        const data = await response.json();

        if (!ignoreStaleRequest) {
          setPostData((prevPostData) => ({
            posts: [
              {
                imgUrl: data.imgUrl,
                owner: data.owner,
                ownerImgUrl: data.ownerImgUrl,
                comments: data.comments,
                likes: data.likes,
                created: data.created,
                ownerShowUrl: data.ownerShowUrl,
                postShowUrl: data.postShowUrl,
                postId: data.postid,
              },
              ...prevPostData.posts, // Keep existing posts (if any)
            ],
            nextUrl: data.nextUrl,
            hasMore: !!data.nextUrl,
          }));
          setLoading(false); // Data has been loaded
        }
      } catch (error) {
        console.error("Error fetching post data:", error);
      }
    };

    fetchPostData();

    return () => {
      ignoreStaleRequest = true;
    };
  }, [url]);

  const loadMorePosts = async () => {
    if (!postData.nextUrl) return; // No more posts to load
  
    try {
      const response = await fetch(postData.nextUrl, { credentials: "same-origin" });
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
        nextUrl: data.nextUrl,
        hasMore: !!data.nextUrl, // Check if there's more to load
      }));
    } catch (error) {
      console.error("Error fetching more posts:", error);
    }
  };
  

  return (
    <div className="post">
      {loading ? (
        <p>Loading...</p> // Show loading message until data arrives
      ) : (
        <InfiniteScroll
          dataLength={postData.posts.length} // Length of currently loaded posts
          next={loadMorePosts} // Function to load more
          hasMore={postData.hasMore} // Whether there's more to load
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

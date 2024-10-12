import React, { useState, useEffect, useCallback } from "react";
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
  const [nextUrl, setNextUrl] = useState(url);
  const [hasMore, setHasMore] = useState(true);

  const fetchPosts = useCallback(async () => {
    if (!nextUrl) return;

    try {
      const response = await fetch(nextUrl, { credentials: "same-origin" });
      if (!response.ok) throw new Error(response.statusText);
      const data = await response.json();

      const detailedPostsPromises = data.results.map(async (result) => {
        const postResponse = await fetch(result.url, {
          credentials: "same-origin",
        });
        if (!postResponse.ok) throw new Error(postResponse.statusText);
        const postDetail = await postResponse.json();

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

      const detailedPosts = await Promise.all(detailedPostsPromises);

      setPostData((prevPostData) => {
        const existingPostIds = new Set(
          prevPostData.posts.map((post) => post.postId),
        );
        const newPosts = detailedPosts.filter(
          (post) => !existingPostIds.has(post.postId),
        );

        return {
          posts: [...prevPostData.posts, ...newPosts],
        };
      });

      if (data.next) {
        setNextUrl(data.next);
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error("Error fetching posts:", error);
    }
  }, [nextUrl]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="post">
      <InfiniteScroll
        dataLength={postData.posts.length}
        next={fetchPosts}
        hasMore={hasMore}
        loader={<h4>Loading more posts...</h4>}
        endMessage={<p>No more posts to display.</p>}
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
            <Likes
              postid={post.postId}
              initialLikes={post.likes}
              postURL={post.imgUrl}
            />
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

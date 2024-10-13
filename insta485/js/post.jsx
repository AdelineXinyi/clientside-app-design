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
  const [nextUrl, setNextUrl] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStale = false;
    setLoading(true);
    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin", method: "GET" })
      .then((response) => {
        if (!response.ok) {
          throw Error(response.statusText);
        }
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStale) {
          const detailedPostsPromises = data.results.map((result) =>
            fetch(result.url, { credentials: "same-origin" })
              .then((postResponse) => {
                if (!postResponse.ok) {
                  throw Error(postResponse.statusText);
                }
                return postResponse.json();
              })
              .then((postDetail) => ({
                imgUrl: postDetail.imgUrl,
                owner: postDetail.owner,
                ownerImgUrl: postDetail.ownerImgUrl,
                comments: postDetail.comments,
                likes: postDetail.likes,
                created: postDetail.created,
                ownerShowUrl: postDetail.ownerShowUrl,
                postShowUrl: postDetail.postShowUrl,
                postId: postDetail.postid,
                isActive: postDetail.likes.lognameLikesThis,
              })),
          );

          // Wait for all post details to be fetched
          Promise.all(detailedPostsPromises).then((detailedPosts) => {
            setPostData({ posts: detailedPosts });
            if (data.next) {
              setNextUrl(data.next);
            } else {
              setHasMore(false);
            }
          });
        }
      })
      .catch((error) => {
        console.error("Error fetching initial posts:", error);
      })
      .finally(() => {
        setLoading(false);
      });

    // Cleanup
    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render,
      // should avoid updating state.
      ignoreStale = true;
    };
  }, [url]);

  const fetchPosts = () => {
    if (!nextUrl) return;
    setLoading(true);
    fetch(url, { credentials: "same-origin", method: "GET" })
      .then((response) => {
        if (!response.ok) {
          throw Error(response.statusText);
        }
        return response.json();
      })
      .then((data) => {
        const detailedPostsPromises = data.results.map((result) =>
          fetch(result.url, { credentials: "same-origin" })
            .then((postResponse) => {
              if (!postResponse.ok) {
                throw Error(postResponse.statusText);
              }
              return postResponse.json();
            })
            .then((postDetail) => ({
              imgUrl: postDetail.imgUrl,
              owner: postDetail.owner,
              ownerImgUrl: postDetail.ownerImgUrl,
              comments: postDetail.comments,
              likes: postDetail.likes,
              created: postDetail.created,
              ownerShowUrl: postDetail.ownerShowUrl,
              postShowUrl: postDetail.postShowUrl,
              postId: postDetail.postid,
              isActive: postDetail.likes.lognameLikesThis,
            })),
        );
        // Wait for all post details to be fetched
        Promise.all(detailedPostsPromises).then((detailedPosts) => {
          setPostData({ posts: detailedPosts });
          if (data.next) {
            setNextUrl(data.next);
          } else {
            setHasMore(false);
          }
        });
      })
      .catch((error) => {
        console.error("Error fetching initial posts:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const isLiked = async (postId) => {
    postData.posts.map((post) => {
      if (post.postId === postId) {
        if (!post.likes.lognameLikesThis) {
          // If not liked, like post
          const makeLikeUrl = `/api/v1/likes/?postid=${postId}`;
          fetch(makeLikeUrl, { credentials: "same-origin", method: "POST" })
            .then((response) => {
              if (!response.ok) throw new Error(response.statusText);
              return response.json();
            })
            .then((data) => {
              setPostData((prevData) => {
                const newPosts = prevData.posts.map((p) => {
                  if (p.postId === postId) {
                    return {
                      ...p,
                      likes: {
                        ...p.likes,
                        numLikes: p.likes.numLikes + 1,
                        lognameLikesThis: true,
                        url: data.url,
                      },
                      isActive: true,
                    };
                  }
                  return p;
                });
                return { ...prevData, posts: newPosts };
              });
            })
            .catch((error) => console.error("Error liking post:", error));
        } else {
          // If liked, unlike post
          const deleteLikeUrl = post.likes.url;
          fetch(deleteLikeUrl, { credentials: "same-origin", method: "DELETE" })
            .then((response) => {
              if (!response.ok) throw new Error(response.statusText);
              // Only update state after successful deletion
              setPostData((prevData) => {
                const newPosts = prevData.posts.map((p) => {
                  if (p.postId === postId) {
                    return {
                      ...p,
                      likes: {
                        ...p.likes,
                        numLikes: p.likes.numLikes - 1,
                        lognameLikesThis: false,
                        url: null,
                      },
                      isActive: false,
                    };
                  }
                  return p;
                });
                return { ...prevData, posts: newPosts };
              });
            })
            .catch((error) => console.error("Error unliking post:", error));
        }
      }
      return post;
    });
  };

  return (
    <div className="post">
      <InfiniteScroll
        dataLength={postData.posts.length}
        next={fetchPosts}
        hasMore={hasMore}
        loader={<h4>Loading more posts...</h4>}
        endMessage={<p>No more posts to display.</p>}
      >
        {postData.posts.map((post) => (
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
            {!loading && (
              <>
                <Likes
                  toggle={() => isLiked(post.postId)}
                  numLikes={post.likes.numLikes}
                  postURL={post.imgUrl}
                  isLiked={post.isActive}
                />
                <Comments
                  postid={post.postId}
                  initialComments={post.comments}
                />
              </>
            )}
          </div>
        ))}
      </InfiniteScroll>
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

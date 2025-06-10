import React, { useEffect, useRef } from "react";

function TwitterFeed({ username }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!window.twttr) return;

    // Xóa nội dung cũ nếu có (khi reload hoặc re-render)
    containerRef.current.innerHTML = "";

    window.twttr.widgets.createTimeline(
      {
        sourceType: "profile",
        screenName: username
      },
      containerRef.current,
      {
        height: 500
      }
    );
  }, [username]);

  return (
    <div style={{ margin: 10 }}>
      <h2>Twitter: @{username}</h2>
      <div ref={containerRef}></div>
    </div>
  );
}

export default TwitterFeed;

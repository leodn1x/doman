import React, { useEffect, useRef } from "react";

function TwitterTimeline({ username }) {
  const containerRef = useRef(null);

  useEffect(() => {
    // Load Twitter embed script
    const script = document.createElement("script");
    script.src = "https://platform.twitter.com/widgets.js";
    script.async = true;
    containerRef.current.appendChild(script);
  }, []);

  return (
    <div>
      <h2>@{username} Tweets</h2>
      <div ref={containerRef}>
        <a
          className="twitter-timeline"
          data-theme="light"
          data-chrome="nofooter noheader"
          data-height="500"
          href={`https://twitter.com/${username}`}
        >
          Tweets by @{username}
        </a>
      </div>
    </div>
  );
}

export default TwitterTimeline;

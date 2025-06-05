import React, { useEffect, useState } from "react";
import "./App.css";

function NewsList({ title, apiUrl }) {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchNews() {
      try {
        const res = await fetch(apiUrl);
        if (!res.ok) throw new Error("Failed to fetch");

        const data = await res.json();
        setNews(data.news);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    }

    fetchNews();
    const interval = setInterval(fetchNews, 30000); // reload mỗi 60s
    return () => clearInterval(interval);
  }, [apiUrl]);

  if (loading) return <p>Loading {title} news...</p>;
  if (error) return <p>Error loading {title} news: {error}</p>;
  if (news.length === 0) return <p>No {title} news found.</p>;

  return (
    <div style={{ padding: 10 }}>
      <h2>{title} Latest News</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {news.map((article, idx) => (
          <li key={idx} style={{ marginBottom: 15 }}>
            <a
              href={article.link}
              target="_blank"
              rel="noopener noreferrer"
              className="news-link"
            >
              {article.title}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

function App() {
  const boxStyle = {
    flex: 1,
    margin: 10,
    overflowY: "auto",
    border: "1px solid #ccc",
    padding: 10,
    height: 400,
    resize: "vertical"
  };

  return (
    <div style={{ fontFamily: "Arial", padding: 20 }}>
      {/* Row 1 */}
      <div style={{ display: "flex" }}>
        <div style={boxStyle}>
          <NewsList title="CNN" apiUrl="http://localhost:5000/api/cnn-news" />
        </div>
        <div style={boxStyle}>
          <NewsList title="CNBC" apiUrl="http://localhost:5000/api/news" />
        </div>
        <div style={boxStyle}>
          <NewsList title="Foxbusiness" apiUrl="http://localhost:5000/api/foxbusiness-news" />
        </div>
      </div>

      {/* Row 2 */}
      <div style={{ display: "flex" }}>
        <div style={boxStyle}>
          <NewsList title="CBS News" apiUrl="http://localhost:5000/api/cbs-news" />
        </div>
        <div style={boxStyle}>
          <NewsList title="Yahoo News" apiUrl="http://localhost:5000/api/yahoo-news" />
        </div>
      </div>
      
    </div>
  );
}

export default App;

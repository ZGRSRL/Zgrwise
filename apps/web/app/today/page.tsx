import React from 'react';

export default function TodayPage() {
  return (
    <div>
      <h1>Bugün - Okunmamış Makaleler</h1>
      <div>
        <h2>Henüz Makale Yok</h2>
        <p>RSS feed'leri ekleyip makalelerin gelmesini bekleyin.</p>
        <div>
          <h3>RSS Feed Eklemek İçin:</h3>
          <code>
            curl -X POST http://localhost:8000/api/rss/feeds -H "X-API-Key: devkey" -H "Content-Type: application/json" -d '{"url": "https://hnrss.org/frontpage", "title": "Hacker News", "weight": 80}'
          </code>
        </div>
      </div>
    </div>
  );
}
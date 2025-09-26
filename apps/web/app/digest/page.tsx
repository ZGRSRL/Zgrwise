import React from 'react';

export default function DigestPage() {
  return (
    <div>
      <h1>Günlük Özet</h1>
      <div>
        <h2>Günlük Özet Hazırlanıyor</h2>
        <p>Sistem her gün saat 08:00'de otomatik olarak günlük özet oluşturur.</p>
        <div>
          <h3>Özet İçeriği:</h3>
          <ul>
            <li>Yüksek öncelikli makaleler</li>
            <li>AI ile oluşturulmuş özetler</li>
            <li>Etiketler ve kategoriler</li>
            <li>Markdown formatında export</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
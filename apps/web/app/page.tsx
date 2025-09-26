export default function HomePage() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', textAlign: 'center', marginBottom: '2rem' }}>
          ZgrWise - RSS "Gündem Kaçırmama" Sistemi
        </h1>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', maxWidth: '1000px', margin: '0 auto' }}>
          <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>📰 Bugün</h2>
            <p style={{ color: '#6b7280', marginBottom: '1rem' }}>Okunmamış makaleleri görüntüle</p>
            <a 
              href="/today" 
              style={{ 
                display: 'inline-block', 
                backgroundColor: '#2563eb', 
                color: 'white', 
                padding: '0.5rem 1rem', 
                borderRadius: '0.25rem', 
                textDecoration: 'none',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#1d4ed8'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#2563eb'}
            >
              Görüntüle
            </a>
          </div>
          
          <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>📊 Günlük Özet</h2>
            <p style={{ color: '#6b7280', marginBottom: '1rem' }}>Günlük digest ve istatistikler</p>
            <a 
              href="/digest" 
              style={{ 
                display: 'inline-block', 
                backgroundColor: '#16a34a', 
                color: 'white', 
                padding: '0.5rem 1rem', 
                borderRadius: '0.25rem', 
                textDecoration: 'none',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#15803d'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#16a34a'}
            >
              Görüntüle
            </a>
          </div>
          
          <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>⚙️ Ayarlar</h2>
            <p style={{ color: '#6b7280', marginBottom: '1rem' }}>RSS feed'leri ve sistem ayarları</p>
            <a 
              href="/settings" 
              style={{ 
                display: 'inline-block', 
                backgroundColor: '#6b7280', 
                color: 'white', 
                padding: '0.5rem 1rem', 
                borderRadius: '0.25rem', 
                textDecoration: 'none',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#4b5563'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#6b7280'}
            >
              Ayarlar
            </a>
          </div>
        </div>
        
        <div style={{ marginTop: '3rem', textAlign: 'center' }}>
          <h3 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem' }}>Sistem Durumu</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ backgroundColor: '#dcfce7', padding: '1rem', borderRadius: '0.5rem' }}>
              <div style={{ color: '#166534', fontWeight: '600' }}>API</div>
              <div style={{ color: '#16a34a' }}>Çalışıyor</div>
            </div>
            <div style={{ backgroundColor: '#dcfce7', padding: '1rem', borderRadius: '0.5rem' }}>
              <div style={{ color: '#166534', fontWeight: '600' }}>Database</div>
              <div style={{ color: '#16a34a' }}>Bağlı</div>
            </div>
            <div style={{ backgroundColor: '#dcfce7', padding: '1rem', borderRadius: '0.5rem' }}>
              <div style={{ color: '#166534', fontWeight: '600' }}>Redis</div>
              <div style={{ color: '#16a34a' }}>Aktif</div>
            </div>
            <div style={{ backgroundColor: '#fef3c7', padding: '1rem', borderRadius: '0.5rem' }}>
              <div style={{ color: '#92400e', fontWeight: '600' }}>Worker</div>
              <div style={{ color: '#d97706' }}>Hazırlanıyor</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
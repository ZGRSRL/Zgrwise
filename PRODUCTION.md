# ZgrWise Production Deployment Guide

Bu doküman ZgrWise sistemini production ortamında deploy etmek için gerekli adımları içerir.

## 🚀 Hızlı Başlangıç

### 1. Ön Gereksinimler

- Docker ve Docker Compose
- En az 4GB RAM
- 20GB disk alanı
- Domain adı (opsiyonel)
- SSL sertifikası (Let's Encrypt önerilir)

### 2. Hızlı Deploy

```bash
# 1. Repository'yi klonlayın
git clone <your-repo-url>
cd ZgrWise

# 2. Environment dosyasını oluşturun
cp env.example .env
# .env dosyasını düzenleyin

# 3. Production'a deploy edin
make deploy
```

## 📋 Detaylı Kurulum

### 1. Environment Yapılandırması

`.env` dosyasını production değerleriyle güncelleyin:

```bash
# Kritik güvenlik ayarları
API_KEY=your-super-secure-api-key-here
SECRET_KEY=your-super-secure-secret-key-here
POSTGRES_PASSWORD=your-super-secure-db-password

# AI servisi
GEMINI_API_KEY=your-actual-gemini-api-key

# Production ayarları
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ALLOW_ORIGINS=https://yourdomain.com

# Domain ayarları
NEXT_PUBLIC_API_URL=https://yourdomain.com
```

### 2. SSL Sertifikası Kurulumu

#### Let's Encrypt ile (Önerilen)

```bash
# Certbot kurulumu
sudo apt update
sudo apt install certbot

# Sertifika oluşturma
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Sertifikaları kopyalama
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*.pem
```

#### Manuel SSL Sertifikası

```bash
# SSL dizinini oluşturun
mkdir -p ssl

# Sertifikalarınızı ssl/ dizinine kopyalayın
# cert.pem -> SSL sertifikası
# key.pem -> Private key
```

### 3. NGINX Yapılandırması

`nginx/conf.d/zgrwise.conf` dosyasında domain adınızı güncelleyin:

```nginx
server_name yourdomain.com www.yourdomain.com;
```

HTTPS'i etkinleştirmek için HTTP'den HTTPS'e yönlendirme bölümünün yorumlarını kaldırın.

### 4. Database Optimizasyonu

```bash
# Database optimizasyonlarını çalıştırın
make db-optimize

# Database istatistiklerini kontrol edin
make db-stats
```

## 🔧 Production Komutları

### Temel Komutlar

```bash
# Production ortamını başlat
make prod-up

# Production ortamını durdur
make prod-down

# Production loglarını görüntüle
make prod-logs

# Health check
make prod-health

# Database migration
make prod-migrate
```

### Monitoring

```bash
# Monitoring stack'ini başlat
make monitoring-up

# Prometheus: http://yourdomain.com:9091
# Grafana: http://yourdomain.com:3001 (admin/admin)
```

### Backup ve Restore

```bash
# Database backup oluştur
make backup

# Mevcut backup'ları listele
make backup-list

# Backup'tan restore et
make restore BACKUP_FILE=backups/zgrwise_backup_20241201_120000.sql.gz
```

## 📊 Monitoring ve Logging

### Prometheus Metrics

- **API Metrics**: `http://yourdomain.com/metrics`
- **Request Rate**: `rate(http_requests_total[5m])`
- **Response Time**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- **Error Rate**: `rate(http_requests_total{status_code=~"5.."}[5m])`

### Grafana Dashboards

1. **ZgrWise Overview**: Genel sistem durumu
2. **Database Performance**: PostgreSQL metrikleri
3. **Application Metrics**: API ve worker metrikleri

### Log Management

```bash
# JSON formatında structured logging
# Log dosyaları: ./logs/ dizininde

# API logları
make api-logs

# Worker logları
make worker-logs

# NGINX logları
tail -f logs/nginx/access.log
tail -f logs/nginx/error.log
```

## 🔒 Güvenlik

### Güvenlik Kontrolleri

```bash
# Security scan
make security-scan

# Code linting
make lint

# Code formatting
make format
```

### Güvenlik Önerileri

1. **API Keys**: Güçlü, rastgele API anahtarları kullanın
2. **Database**: Güçlü şifreler ve sınırlı erişim
3. **CORS**: Sadece gerekli domain'leri izin verin
4. **HTTPS**: Her zaman HTTPS kullanın
5. **Firewall**: Sadece gerekli portları açın (80, 443)
6. **Updates**: Düzenli olarak güncelleme yapın

## 🚨 Troubleshooting

### Yaygın Sorunlar

#### 1. Servisler Başlamıyor

```bash
# Logları kontrol edin
make prod-logs

# Health check yapın
make prod-health

# Servisleri yeniden başlatın
make prod-down && make prod-up
```

#### 2. Database Bağlantı Hatası

```bash
# Database shell'e bağlanın
make db-shell

# Connection pool ayarlarını kontrol edin
# .env dosyasında DB_POOL_SIZE ve DB_MAX_OVERFLOW
```

#### 3. SSL Sertifika Hatası

```bash
# Sertifika dosyalarını kontrol edin
ls -la ssl/

# Sertifika geçerliliğini kontrol edin
openssl x509 -in ssl/cert.pem -text -noout
```

#### 4. Performance Sorunları

```bash
# Database optimizasyonlarını çalıştırın
make db-optimize

# Resource kullanımını kontrol edin
docker stats

# Monitoring dashboard'larını kontrol edin
```

### Log Analizi

```bash
# Error loglarını filtrele
grep "ERROR" logs/api.log

# Slow query'leri bul
grep "slow" logs/api.log

# Memory usage
grep "memory" logs/worker.log
```

## 📈 Performance Tuning

### Database Optimizasyonu

1. **Indexes**: Otomatik olarak oluşturulur
2. **Connection Pooling**: Yapılandırılabilir
3. **Query Optimization**: EXPLAIN ANALYZE kullanın
4. **Vacuum**: Otomatik olarak çalışır

### Application Optimizasyonu

1. **Caching**: Redis cache kullanımı
2. **Rate Limiting**: NGINX ile sınırlandırma
3. **Compression**: Gzip compression aktif
4. **CDN**: Static asset'ler için

### Resource Monitoring

```bash
# Container resource kullanımı
docker stats

# Disk kullanımı
df -h

# Memory kullanımı
free -h

# CPU kullanımı
top
```

## 🔄 Maintenance

### Günlük Bakım

```bash
# Health check
make prod-health

# Log rotation (otomatik)
# Backup kontrolü
make backup-list
```

### Haftalık Bakım

```bash
# Database optimizasyonu
make db-optimize

# Security scan
make security-scan

# Log cleanup
find logs/ -name "*.log" -mtime +7 -delete
```

### Aylık Bakım

```bash
# Full backup
make backup

# System updates
docker compose -f docker-compose.prod.yml pull
make prod-build
make prod-up

# Performance review
make db-stats
```

## 📞 Destek

### Log Toplama

```bash
# Tüm logları topla
mkdir -p support-logs
docker compose -f docker-compose.prod.yml logs > support-logs/all-logs.txt
docker compose -f docker-compose.prod.yml exec db pg_dump -U zgr zgrwise > support-logs/database-dump.sql
```

### Health Check Raporu

```bash
# Sistem durumu raporu
curl -s http://localhost/health/detailed > support-logs/health-report.json
```

## 🎯 Production Checklist

- [ ] Environment variables yapılandırıldı
- [ ] SSL sertifikası kuruldu
- [ ] Domain yapılandırması tamamlandı
- [ ] Database optimizasyonları çalıştırıldı
- [ ] Monitoring stack kuruldu
- [ ] Backup stratejisi yapılandırıldı
- [ ] Security scan tamamlandı
- [ ] Performance test yapıldı
- [ ] Documentation güncellendi
- [ ] Team training tamamlandı

---

**Not**: Bu doküman sürekli güncellenmektedir. En güncel versiyon için GitHub repository'sini kontrol edin.

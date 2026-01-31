# 🚀 Otonom WhatsApp Gönderici (SaaS)

Bu proje, WhatsApp Web üzerinden çalışan, gelişmiş bir toplu mesajlaşma ve kampanya yönetimi sistemidir. 

![Dashboard](https://via.placeholder.com/800x400?text=WhatsApp+Sender+Dashboard)

## 🌟 Özellikler

*   **⚡ Otomatik Bağlantı**: QR Kod ile hızlı eşleşme, tarayıcıyı arka planda yönetme.
*   **👥 Grup Senkronizasyonu**: WhatsApp gruplarını ve kişilerini tek tıkla veritabanına çeker.
*   **📅 Kampanya Yönetimi**: 
    *   Grupları seçerek hedef kitle belirleme.
    *   Özelleştirilebilir mesaj içerikleri.
    *   Zamanlanmış gönderim (Gecikme süresi ayarı).
*   **📊 Canlı Raporlama**: Gönderim durumlarını (Başarılı/Hatalı) anlık izleme.
*   **🛡️ Admin Paneli**: Kullanıcı yönetimi ve üyelik planları (Free/Basic/Pro).

## 🛠️ Kurulum

### Gereksinimler
*   Node.js (v16+)
*   Python (v3.9+)
*   Google Chrome

### 1. Backend (Sunucu)
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 2. Frontend (Arayüz)
```bash
cd frontend
npm install
npm run dev
```

## 🚀 Tek Tıkla Çalıştırma (Windows)
Proje dizinindeki `baslat_tek_tik.bat` dosyasını çalıştırarak tüm sistemi ve internet tünelini tek seferde açabilirsiniz.

## 🔒 Güvenlik Notu
`localtunnel` kullanırken ilk girişte sizden IP adresi (şifre) istenir. Başlatma scripti bu IP'yi ekrana basar.

## 📄 Lisans
MIT License

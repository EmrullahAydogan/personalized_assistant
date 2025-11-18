# 🤖 Kişisel Yapay Zeka Asistanı

Gelişmiş özellikler ve çoklu platform desteği ile tam donanımlı bir kişisel AI asistanı projesi.

## ✨ Özellikler

### 🧠 AI Entegrasyonu
- **Çoklu AI Sağlayıcı Desteği:**
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic Claude
  - Google Gemini
  - Ollama (Yerel modeller)
- Esnek AI sağlayıcı seçimi
- Sohbet geçmişi yönetimi

### 🎤 Ses Özellikleri
- Konuşma tanıma (Speech-to-Text)
- Metin okuma (Text-to-Speech)
- Ses kaydetme desteği
- Türkçe ve İngilizce dil desteği

### 📝 Görev Yönetimi
- Görev oluşturma, güncelleme, silme
- Öncelik seviyeleri (Düşük, Orta, Yüksek, Acil)
- Hatırlatıcılar
- Tekrarlayan görevler (Cron benzeri)
- Durum takibi (Yapılacak, Devam Eden, Tamamlandı)

### 📅 Takvim Entegrasyonu
- Etkinlik oluşturma ve yönetimi
- Tekrarlayan etkinlikler (iCalendar formatı)
- Hatırlatıcılar
- Gelecek etkinlikleri görüntüleme

### 📄 Belge Analizi
- Desteklenen formatlar: PDF, DOCX/DOC, TXT, Görsel dosyalar (OCR ile)
- AI destekli belge analizi
- Otomatik özet oluşturma

### 🔍 Web Arama
- Google arama entegrasyonu
- AI destekli sonuç özetleme

## 🚀 Hızlı Başlangıç

### Backend Kurulumu

1. **Virtual environment oluşturun:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac veya venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

2. **Ortam değişkenlerini ayarlayın:**
```bash
cp .env.example .env
# .env dosyasını düzenleyin ve API anahtarlarınızı ekleyin
```

3. **PostgreSQL veritabanı oluşturun:**
```bash
createdb personalized_assistant
```

4. **Uygulamayı başlatın:**
```bash
cd app
python main.py
```

API: `http://localhost:8000`
Dokümantasyon: `http://localhost:8000/docs`

## 📡 API Örnekleri

### Sohbet
```bash
curl -X POST "http://localhost:8000/api/v1/chat/" -H "Content-Type: application/json" -d '{"message": "Merhaba!", "ai_provider": "gemini"}'
```

### Görev Oluştur
```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" -H "Content-Type: application/json" -d '{"title": "Toplantı", "priority": "high"}'
```

## 🛠️ Teknolojiler

**Backend:** FastAPI, SQLAlchemy, PostgreSQL
**AI:** OpenAI, Anthropic Claude, Google Gemini, Ollama
**Ses:** SpeechRecognition, gTTS
**Belge:** PyPDF2, python-docx, Pytesseract

## 🔮 Gelecek Özellikler

- React Native mobil uygulama
- Electron/Tauri desktop uygulama
- JWT kimlik doğrulama
- WebSocket sohbet
- Email/SMS bildirimleri

---
**Not:** Proje aktif geliştirme aşamasındadır
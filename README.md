# Bog'cha Boshqaruv Tizimi

Bu loyiha bog'cha oshxonasi uchun to'liq boshqaruv tizimi bo'lib, mahsulotlar, ovqatlar va porsiyalarni boshqarish imkoniyatini beradi.

## Xususiyatlar

### 🍽️ Asosiy Funksiyalar
- **Mahsulotlar boshqaruvi**: Ombordagi mahsulotlarni qo'shish, tahrirlash va kuzatish
- **Ovqatlar boshqaruvi**: Retseptlar va ingredientlarni boshqarish
- **Ovqat berish tizimi**: Porsiyalar berish va ingredientlarni avtomatik ayirish
- **Porsiya hisoblash**: Mavjud mahsulotlar asosida mumkin bo'lgan porsiyalarni hisoblash
- **Hisobotlar**: Oylik hisobotlar va iste'mol tahlili
- **Ogohlantirishlar**: Kam qolgan mahsulotlar haqida xabar berish

### 👥 Foydalanuvchi Rollari
- **Admin**: To'liq kirish huquqi, barcha sozlamalar
- **Menejer**: Ombor yangilash, tahlillar ko'rish
- **Oshpaz**: Faqat ovqat berish imkoniyati

### 📊 Hisobotlar va Tahlil
- Oylik samaradorlik hisobotlari
- Mahsulot iste'moli grafiklari
- Shubhali faoliyat aniqlash (15% dan ortiq farq)
- Real-vaqt statistikalar

## Texnologiyalar

### Backend
- **FastAPI**: Modern, tez Python web framework
- **SQLAlchemy**: ORM va ma'lumotlar bazasi boshqaruvi
- **PostgreSQL**: Asosiy ma'lumotlar bazasi
- **JWT**: Xavfsiz autentifikatsiya
- **Pydantic**: Ma'lumotlar validatsiyasi

### Frontend
- **HTML5/CSS3**: Zamonaviy web interfeys
- **Vanilla JavaScript**: Dinamik funksiyalar
- **Chart.js**: Grafiklar va vizualizatsiya
- **Font Awesome**: Ikonkalar

## O'rnatish

### 1. Talablarni o'rnatish

\`\`\`bash
pip install -r requirements.txt
\`\`\`


### 5. Serverni ishga tushirish

\`\`\`bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

## Foydalanish

### Boshlang'ich kirish ma'lumotlari

- **Admin**: `admin` / `admin123`
- **Menejer**: `manager1` / `manager123`
- **Oshpaz**: `cook1` / `cook123`

### Asosiy ishlar ketma-ketligi

1. **Mahsulotlarni qo'shish**: Ombordagi mahsulotlarni ro'yxatga olish
2. **Ovqatlar yaratish**: Retseptlar va ingredientlarni belgilash
3. **Ovqat berish**: Porsiyalar berish va ingredientlarni ayirish
4. **Hisobotlarni ko'rish**: Samaradorlik va iste'molni tahlil qilish

## API Hujjatlari

Server ishga tushgandan so'ng, API hujjatlarini ko'rish uchun:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Fayl Strukturasi

\`\`\`
├── app/
│   ├── main.py              # Asosiy FastAPI ilovasi
│   ├── database.py          # Ma'lumotlar bazasi konfiguratsiyasi
│   ├── models.py            # SQLAlchemy modellari
│   ├── schemas.py           # Pydantic sxemalari
│   ├── auth.py              # Autentifikatsiya
│   └── routers/             # API router'lari
│       ├── auth.py
│       ├── products.py
│       ├── meals.py
│       ├── servings.py
│       ├── reports.py
│       └── users.py
├── static/
│   ├── index.html           # Asosiy HTML sahifa
│   ├── css/
│   │   └── style.css        # CSS stillari
│   └── js/
│       └── app.js           # JavaScript funksiyalari
├── scripts/
│   ├── 01_create_database.sql
│   └── 02_seed_data.sql
├── requirements.txt
└── README.md
\`\`\`

## Xavfsizlik

- JWT token asosida autentifikatsiya
- Rol asosida kirish nazorati
- Ma'lumotlar validatsiyasi
- SQL injection himoyasi
- CORS sozlamalari

## Kelajakdagi Rivojlantirish

- [ ] Real-vaqt WebSocket yangilanishlar
- [ ] Celery bilan fon vazifalari
- [ ] Email xabarnomalar
- [ ] Mobile responsive dizayn
- [ ] Eksport/Import funksiyalari
- [ ] Backup va restore
- [ ] Audit log tizimi

## Yordam

Savollar yoki muammolar bo'lsa, GitHub Issues orqali murojaat qiling.

## Litsenziya

MIT License

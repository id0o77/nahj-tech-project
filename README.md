# Mohamed 2 - Flask Project

## تشغيل المشروع

```bash
python -m pip install -r requirements.txt
python app.py
```

افتح:

```text
http://127.0.0.1:5000
```

## دخول لوحة التحكم

```text
username: admin
password: admin123
```

## المميزات

- تصميم جديد بألوان مختلفة.
- لوقو الشركة مضاف في الهيدر وصفحة الدخول.
- دعم عربي / English مع تبديل الاتجاه RTL و LTR.
- لوحة إدارة للخدمات: إضافة، تعديل، حذف، عرض.
- قاعدة بيانات SQLite.
- حفظ رسائل التواصل في قاعدة البيانات وعرضها في لوحة التحكم.
- حماية CSRF، تشفير كلمة المرور، حماية الجلسات، وتحديد محاولات الدخول والتواصل.


## النشر على Render

Build Command:
```bash
pip install -r requirements.txt
```

Start Command:
```bash
python app.py
```

تم ضبط التطبيق ليعمل على `0.0.0.0` ويستخدم متغير البيئة `PORT` الخاص بمنصة Render.

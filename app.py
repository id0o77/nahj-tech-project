import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os, sqlite3, secrets, re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'najh_tech.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=6)
)

LOGIN_ATTEMPTS = {}
CONTACT_ATTEMPTS = {}

TRANSLATIONS = {
    'ar': {
        'brand':'Najh Tech','home':'الرئيسية','services':'الخدمات','about':'من نحن','contact':'تواصل معنا','login':'دخول','logout':'خروج','dashboard':'لوحة التحكم',
        'hero_badge':'حلول رقمية آمنة','hero_title':'طريق النجاح يبدأ بتجربة رقمية قوية','hero_desc':'نصمم ونطور مواقع وتطبيقات احترافية بسرعة عالية وحماية مناسبة وقاعدة بيانات لإدارة خدماتك ورسائل عملائك.',
        'discover':'اكتشف خدماتنا','start_now':'ابدأ الآن','our_services':'خدماتنا','services_desc':'الخدمات تظهر هنا مباشرة من لوحة الإدارة وقاعدة البيانات.','details':'التفاصيل',
        'values_title':'من نحن','values_desc':'نحوّل الأفكار إلى منتجات رقمية واضحة وآمنة وقابلة للتوسع.','cta_title':'جاهز تبدأ مشروعك؟','cta_desc':'راسلنا الآن وسنساعدك في تحويل فكرتك إلى موقع أو تطبيق عملي.',
        'contact_title':'تواصل معنا','contact_desc':'ارسل لنا تفاصيل مشروعك وسنرد عليك في أقرب وقت.','full_name':'الاسم الكامل','company':'الشركة (اختياري)','email':'البريد الإلكتروني','message':'الرسالة','send':'إرسال الرسالة',
        'admin_area':'إدارة الموقع','add_service':'إضافة خدمة','edit':'تعديل','delete':'حذف','service_name':'اسم الخدمة','description':'الوصف','price':'السعر','status':'الحالة','icon':'الأيقونة','save':'حفظ','messages':'رسائل العملاء','current_user':'المستخدم الحالي',
        'username':'اسم المستخدم','password':'كلمة المرور','login_title':'تسجيل الدخول','default_account':'الحساب الافتراضي: admin / admin123','footer':'نحوّل الأفكار إلى مواقع وتطبيقات آمنة وجذابة.'
    },
    'en': {
        'brand':'Najh Tech','home':'Home','services':'Services','about':'About','contact':'Contact','login':'Login','logout':'Logout','dashboard':'Dashboard',
        'hero_badge':'Secure Digital Solutions','hero_title':'Your success starts with a powerful digital experience','hero_desc':'We design and build professional websites and apps with strong performance, practical security, and database-powered management.',
        'discover':'Explore Services','start_now':'Start Now','our_services':'Our Services','services_desc':'Services are managed directly from the admin dashboard and database.','details':'Details',
        'values_title':'About Us','values_desc':'We turn ideas into clear, secure, and scalable digital products.','cta_title':'Ready to start your project?','cta_desc':'Contact us and we will help turn your idea into a working website or app.',
        'contact_title':'Contact Us','contact_desc':'Send your project details and we will get back to you soon.','full_name':'Full Name','company':'Company (optional)','email':'Email Address','message':'Message','send':'Send Message',
        'admin_area':'Website Management','add_service':'Add Service','edit':'Edit','delete':'Delete','service_name':'Service Name','description':'Description','price':'Price','status':'Status','icon':'Icon','save':'Save','messages':'Customer Messages','current_user':'Current User',
        'username':'Username','password':'Password','login_title':'Login','default_account':'Default account: admin / admin123','footer':'We turn ideas into secure and attractive websites and applications.'
    }
}

DEFAULT_SERVICES = [
    ('UI/UX Design','تصميم واجهات وتجارب استخدام جميلة وسهلة ترفع ثقة العميل وتزيد التفاعل.','حسب المشروع','active','🎨'),
    ('Web Development','بناء مواقع ويب سريعة وآمنة ومتجاوبة باستخدام أفضل الممارسات الحديثة.','حسب المشروع','active','</>'),
    ('Mobile Applications','تطوير تطبيقات جوال أصلية أو متعددة المنصات بأداء وتجربة ممتازة.','حسب المشروع','active','▯'),
    ('Digital Strategy','توجيه استراتيجي يساعد مشروعك على النمو والظهور بشكل أقوى في السوق الرقمي.','حسب المشروع','active','◎'),
]

VALUES = [
    ('ابتكار','نتجاوز الحدود ونتبنى الأفكار الجديدة لتقديم حلول متطورة.','💡'),
    ('الشفافية','تواصل واضح وصادق في كل مشروع وشراكة.','👁'),
    ('جودة','معايير عالية في البرمجة والتصميم والتسليم في كل مشروع.','🛡'),
    ('حماية','بياناتك وأصولك الرقمية محمية بأفضل الممارسات والعناية.','🔒'),
]

def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M')

def current_lang():
    code = session.get('lang', 'ar')
    return code if code in TRANSLATIONS else 'ar'

@app.context_processor
def inject_language():
    code = current_lang()
    return {'lang': code, 'dir': 'rtl' if code == 'ar' else 'ltr', 't': TRANSLATIONS[code]}

def db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_=None):
    conn = g.pop('db', None)
    if conn:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT "admin", created_at TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT NOT NULL, price TEXT, status TEXT NOT NULL DEFAULT "active", icon TEXT, created_at TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, company TEXT, email TEXT NOT NULL, message TEXT NOT NULL, ip TEXT, created_at TEXT NOT NULL)')
    if conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0:
        conn.execute('INSERT INTO users (username,password_hash,role,created_at) VALUES (?,?,?,?)', ('admin', generate_password_hash('admin123'), 'admin', now()))
    if conn.execute('SELECT COUNT(*) FROM services').fetchone()[0] == 0:
        conn.executemany('INSERT INTO services (name,description,price,status,icon,created_at) VALUES (?,?,?,?,?,?)', [(n,d,p,s,i,now()) for n,d,p,s,i in DEFAULT_SERVICES])
    conn.commit(); conn.close()

def client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0].strip()

def rate_limited(bucket, key, limit, seconds):
    t = datetime.now()
    bucket[key] = [x for x in bucket.get(key, []) if (t-x).total_seconds() < seconds]
    if len(bucket[key]) >= limit:
        return True
    bucket[key].append(t)
    return False

def csrf_token():
    token = session.get('_csrf') or secrets.token_urlsafe(32)
    session['_csrf'] = token
    return token
app.jinja_env.globals['csrf_token'] = csrf_token

def validate_csrf():
    if request.method == 'POST' and request.form.get('_csrf') != session.get('_csrf'):
        abort(400)

@app.before_request
def before_request():
    validate_csrf()

@app.after_request
def security_headers(resp):
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    resp.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    resp.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; font-src https://fonts.gstatic.com; script-src 'self'; img-src 'self' data:"
    return resp

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            flash('سجل الدخول أولاً', 'error')
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper

def valid_email(email):
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email or ''))

@app.route('/set-lang/<code>')
def set_lang(code):
    if code in TRANSLATIONS:
        session['lang'] = code
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    services = db().execute("SELECT * FROM services WHERE status='active' ORDER BY id").fetchall()
    return render_template('index.html', services=services, values=VALUES)

@app.route('/services')
def services():
    services = db().execute("SELECT * FROM services WHERE status='active' ORDER BY id").fetchall()
    return render_template('services.html', services=services)

@app.route('/service/<int:service_id>')
def service_detail(service_id):
    service = db().execute('SELECT * FROM services WHERE id=?', (service_id,)).fetchone()
    if not service:
        return render_template('404.html'), 404
    return render_template('service_detail.html', service=service)

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        if rate_limited(CONTACT_ATTEMPTS, client_ip(), 5, 600):
            flash('تم تجاوز عدد المحاولات. حاول لاحقاً.', 'error')
            return redirect(url_for('contact'))
        name = request.form.get('name','').strip()[:80]
        company = request.form.get('company','').strip()[:80]
        email = request.form.get('email','').strip()[:120]
        message = request.form.get('message','').strip()[:2000]
        if not name or not valid_email(email) or len(message) < 10:
            flash('تأكد من الاسم والبريد والرسالة.', 'error')
            return redirect(url_for('contact'))
        db().execute('INSERT INTO messages (name,company,email,message,ip,created_at) VALUES (?,?,?,?,?,?)', (name,company,email,message,client_ip(),now()))
        db().commit()
        flash('تم إرسال رسالتك بنجاح، سنتواصل معك قريباً.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if rate_limited(LOGIN_ATTEMPTS, client_ip(), 6, 900):
            flash('محاولات كثيرة. حاول بعد 15 دقيقة.', 'error')
            return redirect(url_for('login'))
        username = request.form.get('username','').strip()
        user = db().execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if user and check_password_hash(user['password_hash'], request.form.get('password','')):
            session.clear(); session.permanent = True
            session['user_id'] = user['id']; session['user'] = user['username']; csrf_token()
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('dashboard'))
        flash('بيانات الدخول غير صحيحة', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    services = db().execute('SELECT * FROM services ORDER BY id').fetchall()
    messages = db().execute('SELECT * FROM messages ORDER BY id DESC').fetchall()
    return render_template('dashboard.html', services=services, messages=messages)

@app.route('/add-service', methods=['GET','POST'])
@login_required
def add_service():
    if request.method == 'POST':
        name = request.form.get('name','').strip()[:80]
        desc = request.form.get('description','').strip()[:400]
        if not name or not desc:
            flash('اسم الخدمة والوصف مطلوبان.', 'error')
            return redirect(url_for('add_service'))
        db().execute('INSERT INTO services (name,description,price,status,icon,created_at) VALUES (?,?,?,?,?,?)', (name,desc,request.form.get('price','').strip()[:80],request.form.get('status','active'),request.form.get('icon','✦').strip()[:20],now()))
        db().commit()
        flash('تمت إضافة الخدمة', 'success')
        return redirect(url_for('dashboard'))
    return render_template('service_form.html', service=None, form_title=TRANSLATIONS[current_lang()]['add_service'])

@app.route('/edit-service/<int:service_id>', methods=['GET','POST'])
@login_required
def edit_service(service_id):
    service = db().execute('SELECT * FROM services WHERE id=?', (service_id,)).fetchone()
    if not service:
        return render_template('404.html'), 404
    if request.method == 'POST':
        name = request.form.get('name','').strip()[:80]
        desc = request.form.get('description','').strip()[:400]
        if not name or not desc:
            flash('اسم الخدمة والوصف مطلوبان.', 'error')
            return redirect(url_for('edit_service', service_id=service_id))
        db().execute('UPDATE services SET name=?, description=?, price=?, status=?, icon=? WHERE id=?', (name, desc, request.form.get('price','').strip()[:80], request.form.get('status','active'), request.form.get('icon','✦').strip()[:20], service_id))
        db().commit()
        flash('تم تعديل الخدمة بنجاح', 'success')
        return redirect(url_for('dashboard'))
    return render_template('service_form.html', service=service, form_title=TRANSLATIONS[current_lang()]['edit'])

@app.route('/delete-service/<int:service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    db().execute('DELETE FROM services WHERE id=?', (service_id,))
    db().commit()
    flash('تم حذف الخدمة', 'success')
    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def nf(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def se(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

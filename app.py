
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///veritabani.db'
db = SQLAlchemy(app)

class Kategori(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(80), unique=True, nullable=False)
    hesaplar = db.relationship('Hesap', backref='kategori', lazy=True)

class Hesap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    veri = db.Column(db.String(200), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori.id'), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return redirect('/admin')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        sifre = request.form.get('sifre')
        if sifre == 'admin123':
            session['admin'] = True
            return redirect('/panel')
        else:
            return "Hatalı şifre"
    return render_template('admin_login.html')

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if not session.get('admin'):
        return redirect('/admin')

    kategoriler = Kategori.query.all()

    if request.method == 'POST':
        if 'kategori_adi' in request.form:
            yeni_ad = request.form.get('kategori_adi')
            if not Kategori.query.filter_by(ad=yeni_ad).first():
                db.session.add(Kategori(ad=yeni_ad))
                db.session.commit()
        elif 'hesap_veri' in request.form and 'kategori_id' in request.form:
            veri = request.form.get('hesap_veri')
            kategori_id = int(request.form.get('kategori_id'))
            db.session.add(Hesap(veri=veri, kategori_id=kategori_id))
            db.session.commit()
        return redirect('/panel')

    return render_template('panel.html', kategoriler=kategoriler)

@app.route('/api/<kategori_adi>')
def kategori_api(kategori_adi):
    kategori = Kategori.query.filter_by(ad=kategori_adi).first()
    if not kategori or not kategori.hesaplar:
        return jsonify({'hata': 'Hesap bulunamadı'})
    hesap = kategori.hesaplar[0]
    db.session.delete(hesap)
    db.session.commit()
    return jsonify({'hesap': hesap.veri})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

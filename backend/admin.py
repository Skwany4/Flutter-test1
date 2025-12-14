from app import app, db, User, bcrypt

with app.app_context():
    # Sprawdź czy user już jest
    if not User.query.filter_by(username='admin').first():
        hashed_pw = bcrypt.generate_password_hash('admin').decode('utf-8')
        user = User(username='admin', password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        print("Użytkownik 'admin' z hasłem 'admin' został dodany!")
    else:
        print("Użytkownik 'admin' już istnieje.")
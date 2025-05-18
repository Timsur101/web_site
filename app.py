from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'anton'  
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  
        password="password!",  
        database="web_site"
    )
    return conn

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = 'SELECT * FROM recipes WHERE id_user = %s'
    params = [session['user_id']]
    if search_query:
        query += ' AND title LIKE %s'
        params.append(f'%{search_query}%')
    cursor.execute(query, params)
    recipes = cursor.fetchall()
    cursor.execute('SELECT id_recipe FROM favorites WHERE id_user = %s', (session['user_id'],))
    favorite_ids = {row['id_recipe'] for row in cursor.fetchall()}
    for recipe in recipes:
        recipe['is_favorite'] = recipe['id_recipe'] in favorite_ids
    cursor.close()
    conn.close()
    return render_template('main.html', recipes=recipes, search_query=search_query)

@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = '''
            SELECT r.* FROM recipes r
            JOIN favorites f ON r.id_recipe = f.id_recipe
            WHERE f.id_user = %s
        '''
        params = [session['user_id']]
        if search_query:
            query += ' AND r.title LIKE %s'
            params.append(f'%{search_query}%')
        cursor.execute(query, params)
        favorites = cursor.fetchall()
    except mysql.connector.Error as e:
        favorites = []
    finally:
        cursor.close()
        conn.close()
    return render_template('favorite.html', favorites=favorites, search_query=search_query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id_user, username, email, role FROM users WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['user_id'] = user['id_user']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']
            return redirect(url_for('index'))
        return render_template('login.html', error="Неверная почта или пароль")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = email.split('@')[0]
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)', 
                          (username, email, password, 'visitor'))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            cursor.close()
            conn.close()
            return render_template('register.html', error="Эта почта уже зарегистрирована")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST' and session['role'] in ['visitor', 'admin']:
        title = request.form['title']
        description = request.form['description']
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = f'uploads/{filename}'
        else:
            image_path = None
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO recipes (id_user, description, title, image_path) VALUES (%s, %s, %s, %s)',
                       (session['user_id'], description, title, image_path))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET username = %s, email = %s, password = %s WHERE id_user = %s',
                          (username, email, password, session['user_id']))
            conn.commit()
            session['username'] = username
            session['email'] = email
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        except mysql.connector.Error as err:
            cursor.close()
            conn.close()
            return render_template('profile.html', error="Ошибка обновления данных")
    return render_template('profile.html', username=session.get('username'), email=session.get('email'))

@app.route('/toggle_favorite/<int:recipe_id>')
def toggle_favorite(recipe_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM favorites WHERE id_user = %s AND id_recipe = %s',
                  (session['user_id'], recipe_id))
    exists = cursor.fetchone()
    if exists:
        cursor.execute('DELETE FROM favorites WHERE id_user = %s AND id_recipe = %s',
                      (session['user_id'], recipe_id))
    else:
        cursor.execute('INSERT INTO favorites (id_user, id_recipe) VALUES (%s, %s)',
                      (session['user_id'], recipe_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete', methods=['GET', 'POST'])
def delete_recipe():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        recipe_id = request.form.get('recipe_id')
        if recipe_id:
            cursor.execute('DELETE FROM recipes WHERE id_recipe = %s', (recipe_id,))
            conn.commit()
        return redirect(url_for('index'))
    cursor.execute('SELECT * FROM recipes')
    recipes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('delete.html', recipes=recipes)

if __name__ == '__main__':
    app.run(debug=True)
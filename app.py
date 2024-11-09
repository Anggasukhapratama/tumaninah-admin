from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pythonlogin'
app.secret_key = 'udinduin'  # Tambahkan ini untuk mendukung sesi

# Inisialisasi MySQL
mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        # Cek akun di database
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, username, password FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account:
            stored_password_hash = account[2]  # Pastikan ini adalah hash password
            if check_password_hash(stored_password_hash, password):
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[1]
                return redirect(url_for('dashboard'))
            else:
                msg = 'Incorrect password!'
        else:
            msg = 'Username not found!'
    
    return render_template('login.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        # Cek apakah username sudah ada
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account:
            msg = 'Username already exists!'
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO accounts (username, password) VALUES (%s, %s)', (username, hashed_password))
            mysql.connection.commit()
            msg = 'You have successfully registered! You can now log in.'
    
    return render_template('register.html', msg=msg)

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        # Ambil jumlah pengguna dari database
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM accounts')  # Hitung jumlah user di tabel accounts
        total_users = cursor.fetchone()[0]
        cursor.close()

        # Kirim jumlah pengguna ke template
        return render_template('dashboard.html', username=session['username'], total_users=total_users)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Menampilkan Daftar Pengguna
@app.route('/users')
def users():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM accounts')  # Menggunakan tabel accounts
    user_data = cursor.fetchall()
    cursor.close()
    return render_template('user/users.html', users=user_data)

# Menambahkan Pengguna Baru
@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO accounts (username, password) VALUES (%s, %s)', (username, password))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('users'))
    return render_template('user/add_user.html')

# Mengedit Pengguna
@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM accounts WHERE id = %s', (id,))
    user = cursor.fetchone()  # Menggunakan tabel accounts
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = generate_password_hash(request.form['password'])
        cursor.execute('UPDATE accounts SET username = %s, password = %s WHERE id = %s', (new_username, new_password, id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('users'))
    cursor.close()
    return render_template('edit_user.html', user=user)

# Menghapus Pengguna
@app.route('/users/delete/<int:id>')
def delete_user(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM accounts WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('users'))

if __name__ == '__main__':
    app.run(debug=True)

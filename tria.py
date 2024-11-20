import sqlite3
import subprocess
import secrets
from flask import Flask, request, session, redirect, render_template, jsonify
from web3 import Web3

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Use a more secure secret key

# Connect to SQLite
def get_db_connection():
    conn = sqlite3.connect('ethereum_wallet.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create the database table if it doesn't exist
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            address TEXT NOT NULL UNIQUE,
            private_key TEXT NOT NULL
        )''')
    conn.commit()
    conn.close()

# Register route with wallet generation
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Generate Ethereum wallet
        web3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/2a195169b77c4532a9660754f9d15905'))
        account = web3.eth.account.create()  # Generate new Ethereum account
        address = account.address
        private_key = account.key.hex()

        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute('INSERT INTO users (username, password, address, private_key) VALUES (?, ?, ?, ?)',
                        (username, password, address, private_key))
            conn.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return 'Username already exists!'
        finally:
            conn.close()
    
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                            (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['address'] = user['address']
            session['private_key'] = user['private_key']

            # Retrieve Ethereum balance using let.mjs
            address = user['address']
            try:
                result = subprocess.run(
                    ['node', 'let.mjs', 'check', 'eth', address],
                    capture_output=True,
                    text=True
                )
                balance_eth = result.stdout.strip()  # Get the balance from the output
                session['balance'] = balance_eth  # Store balance in session for display in the index route
                return redirect('/')
            except Exception as e:
                return f'Error retrieving balance: {str(e)}', 500
            
        else:
            return 'Invalid credentials!'

    return render_template('login.html')

# Index route for balance checking and sending Ethereum
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' in session:
        if request.method == 'POST':
            to_address = request.form.get('to_address')
            amount = request.form.get('amount')

            if to_address and amount:
                try:
                    # Call the Node.js script to send Ethereum
                    result = subprocess.run(
                        ['node', 'let.mjs', 'send', 'eth', session['address'], session['private_key'], to_address, amount],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    output = result.stdout.strip()  # Get the output from the script

                    # Check if the output indicates success
                    if "Transaction successful with hash" in output:
                        transaction_hash = output.split("Transaction successful with hash: ")[1].strip()  # Extract transaction hash
                        return render_template('ex.html', transaction_hash=transaction_hash, success_message="Transaction successful!", balance=session['balance'], address=session['address'])
                    else:
                        return render_template('ex.html', error="Transaction failed: " + output, success_message=None, balance=session['balance'], address=session['address'])

                except subprocess.CalledProcessError as e:
                    error_message = e.stderr.strip() or "Error sending Ethereum."
                    return render_template('ex.html', error=error_message, success_message=None, balance=session['balance'], address=session['address'])

            return render_template('ex.html', error='Invalid input provided.', success_message=None, balance=session['balance'], address=session['address'])

        # Display balance and send form
        return render_template('ex.html', balance=session['balance'], address=session['address'])

    return redirect('/login')

@app.route('/get_address', methods=['GET'])
def get_address():
    if 'user_id' in session:
        address = session['address']  # Get the address from the session
        return jsonify({'address': address})
    return jsonify({'error': 'User not logged in'}), 401

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear the session data
    return redirect('/login')  # Redirect to the login page

if __name__ == '__main__':
    init_db()  # Initialize database on startup
    app.run(debug=True)

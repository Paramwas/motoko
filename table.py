from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        address = request.form.get('address')
        if address:
            try:
                # Call the Node.js script and capture the output
                result = subprocess.run(
                    ['node', 'wallet.mjs', 'eth', address],  # Ensure to include 'eth' as a network
                    capture_output=True,
                    text=True,
                    check=True
                )
                balance = result.stdout.strip()  # Get the balance from the output
                return render_template('dex.html', balance=balance, address=address)
            except subprocess.CalledProcessError as e:
                # Handle errors from the wallet.mjs execution
                error_message = e.stderr.strip() or "Error fetching balance."
                return render_template('dex.html', error=error_message)

        return render_template('dex.html', error='Invalid address provided.')
    return render_template('dex.html')

if __name__ == '__main__':
    app.run(debug=True)

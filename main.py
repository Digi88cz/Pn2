from flask import Flask, request, redirect, render_template_string, url_for
from cryptography.fernet import Fernet
import uuid

app = Flask(__name__)

# Klíč pro šifrování
key = Fernet.generate_key()
cipher = Fernet(key)

# Skladování poznámek
notes = {}

@app.route('/')
def home():
    return '''
        <h1>Jednorázové šifrované poznámky</h1>
        <form action="/create" method="post">
            <textarea name="note" rows="5" cols="40" placeholder="Napište vaši poznámku zde..."></textarea><br><br>
            <button type="submit">Vytvořit poznámku</button>
        </form>
    '''

@app.route('/create', methods=['POST'])
def create_note():
    note = request.form['note']
    # Šifrování poznámky
    encrypted_note = cipher.encrypt(note.encode())
    note_id = str(uuid.uuid4())
    notes[note_id] = encrypted_note

    # Odkaz na poznámku
    link = url_for('view_note', note_id=note_id, _external=True)
    return f'''
        <h1>Poznámka vytvořena!</h1>
        <input type="text" id="note-link" value="{link}" readonly style="width:100%;"><br><br>
        <button onclick="copyLink()">Kopírovat odkaz</button><br><br>
        <a href="/">Vytvořit další poznámku</a>
        <script>
            function copyLink() {{
                const link = document.getElementById("note-link");
                link.select();
                document.execCommand("copy");
                alert("Odkaz byl zkopírován do schránky!");
            }}
        </script>
    '''

@app.route('/note/<note_id>')
def view_note(note_id):
    encrypted_note = notes.pop(note_id, None)
    if not encrypted_note:
        return "Tato poznámka již neexistuje nebo byla přečtena."

    # Dešifrování poznámky
    note = cipher.decrypt(encrypted_note).decode()
    return f'''
        <h1>Vaše poznámka</h1>
        <p>{note}</p>
        <a href="/">Vytvořit novou poznámku</a>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

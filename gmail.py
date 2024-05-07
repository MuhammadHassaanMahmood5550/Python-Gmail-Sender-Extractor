import imaplib
import email
import sqlite3

username = 'johnbient@gmail.com'
password = '###########'

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(username, password)
mail.select('inbox')

result, data = mail.search(None, '(FROM "johnobrient@gmail.com")')
if result == 'OK':
    email_ids = data[0].split()
else:
    print("Error searching for emails.")

conn = sqlite3.connect('emails.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS emails
                (id INTEGER PRIMARY KEY, subject TEXT, sender TEXT, body TEXT)''')

# get and save
for email_id in email_ids:
    try:
        result, data = mail.fetch(email_id, '(RFC822)')
        if result == 'OK':
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            subject = msg['subject']
            sender = msg['from']
            body = ''
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body += part.get_payload(decode=True).decode('utf-8')
            cursor.execute('INSERT INTO emails (subject, sender, body) VALUES (?, ?, ?)', (subject, sender, body))
        else:
            print(f"Error fetching email {email_id}")
    except Exception as e:
        print(f"Error processing email {email_id}: {str(e)}")

# =-------- close connections (relea resourses as not needed)
conn.commit()
conn.close()
mail.close()
mail.logout()

print("Emails saved successfully.")

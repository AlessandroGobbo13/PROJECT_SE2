import streamlit as st
import sqlite3
import time
import smtplib 
from email.mime.text import MIMEText
from random import randrange


def user_list():
    dict_mail_pass = {}
    db = sqlite3.connect('user.db')
    cursor = db.cursor()
    cursor.execute("SELECT Mail, Password, User_Type FROM USER")
    rows = cursor.fetchall()
    
    for row in rows:
        dict_mail_pass[row[0]] = {'password': row[1], 'user_type': row[2]}
    
    return dict_mail_pass

def add_user(Mail, Username, User_type, Password):
    sql_insert = '''INSERT INTO USER(Mail, Name_Surname, User_Type, Password) 
                    VALUES (?, ?, ?, ?)'''
    
    db = sqlite3.connect('user.db')
    cursor = db.cursor()
    
    try:
        cursor.execute(sql_insert, (Mail, Username, User_type, Password))
        db.commit()
    except sqlite3.Error as e:
        st.error(f"Errore nel database: {e}")
        return False
    finally:
        db.close()
    return True

def authentication():
    """
    Gestisce il processo di autenticazione (login, registrazione, recupero password)
    Returns:
        tuple: (bool, str, str) - (autenticato, email utente, tipo utente)
    """
    # Inizializzazione stati
    if 'user_state' not in st.session_state:
        st.session_state.user_state = {
            'username': '',
            'user_type': '',
            'logged_in': False
        }
    
    if 'users_list' not in st.session_state:
        st.session_state.users_list = user_list()

    if 'widget_key' not in st.session_state:
        st.session_state.widget_key = 0

    st.title('User Login Page')

    # Selectbox con key dinamica
    option = st.selectbox(
        'Choose the action',
        ("Login", "Sign Up", "Forgot Password"),
        key=f"select_{st.session_state.widget_key}"
    )

    if option == 'Login':
        container = st.container(border=True)
        email = container.text_input('E-Mail')
        password = container.text_input('Password', type='password')
        submit = st.button('Login')

        if submit:
            if email in st.session_state.users_list and \
               password == st.session_state.users_list[email]['password']:
                st.success('Login successful!')
                return True, email, st.session_state.users_list[email]['user_type']
            else:
                st.error('Invalid email or password')

    elif option == 'Sign Up':
        container = st.container(border=True)
        col1, col2 = container.columns(2)
        
        with container:
            mail = col1.text_input('Inserisci e-mail')
            username = col1.text_input('Inserisci nome e cognome')
            password = col2.text_input('Inserisci password', type='password')
            user_type = col2.selectbox('User Type',('Viewer', 'Sales'))
            submit = st.button('Sign Up')

        if submit:
            if mail and username and password:
                if mail not in st.session_state.users_list:
                    if add_user(mail, username, user_type, password):
                        st.success("Registrazione completata! Verrai indirizzato al login.")
                        st.session_state.users_list = user_list()
                        time.sleep(4)
                        st.session_state.widget_key += 1  # Incrementa la key

                        st.rerun()
                else:
                    st.error("Email già registrata")
            else:
                st.warning("Compila tutti i campi")

    else:  # Forgot Password
        container = st.container(border=True)
        email_recovery = container.text_input('Inserisci la tua email')
        submit = st.button('Recupera Password')
        
        if submit:
            if email_recovery in st.session_state.users_list:
                st.success("Prosegui con procedimento di verifica")
                
                #campi della mail e invio messaggio
                email_send = 'alessandrogobbo19@gmail.com'
                subject = 'Codice di verifica ALESSANDRO GOBBO'
                password_app = 'mtea hxhm cbph tquw'
                verify_number = randrange(0, 999)  # Codice a 6 cifre
                
                # Salva il codice di verifica nella session state
                if 'verify_number' not in st.session_state:
                    st.session_state.verify_number = verify_number

                message = f"""
                Il tuo codice di verifica è: {verify_number}
                
                Inserisci questo codice per completare il processo di recupero password.
                """
                
                try:
                    msg = MIMEText(message)
                    msg['From'] = email_send
                    msg['To'] = email_recovery
                    msg['Subject'] = subject

                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(email_send, password_app)
                    server.sendmail(email_send, email_recovery, msg.as_string())
                    server.quit()
                    st.success("Email inviata con successo!")
                except Exception as e:
                    st.error(f"Errore invio della mail : {e}")

                # Input per il codice di verifica
                number = st.text_input('Inserisci il codice di verifica')
                submit = st.button('Conferma')
                
                if submit:
                    if number == f'{st.session_state.verify_number}':
                        st.write('prova')
                    
                
                st.write('Test')
                
                
            else:
                st.error("Email non trovata")

    return False, '', ''

# Esempio di utilizzo in main.py
if __name__ == "__main__":
    is_authenticated, user_email, user_type = authentication()
    
    if is_authenticated:
        st.write(f"Benvenuto {user_email}")
        st.write(f"Il tuo tipo utente è: {user_type}")
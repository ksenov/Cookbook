import sqlite3


def login(login, passw, signal, signal2):

    con = sqlite3.connect('handler/users')
    cur = con.cursor()

    # Проверка пользователя
    cur.execute(f'SELECT * FROM users WHERE name="{login}";')
    value = cur.fetchall()
    
    if value != [] and value[0][2] == passw:
        signal.emit('Успешная авторизация!')
        signal2.emit(f"{login}")
    else:
        signal.emit('Проверьте правильность ввода данных!')

    cur.close()
    con.close()



def register(login, passw, signal):
    con = sqlite3.connect('handler/users')
    cur = con.cursor()

    cur.execute(f'SELECT * FROM users WHERE name="{login}";')
    value = cur.fetchall()

    if value != []:
        signal.emit('Такой ник уже используется!')

    elif value == []:
        cur.execute(f"INSERT INTO users (name, password) VALUES ('{login}', '{passw}')")
        signal.emit('Вы успешно зарегистрированы!')
        con.commit()


    cur.close()
    con.close()
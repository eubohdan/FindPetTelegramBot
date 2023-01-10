import sqlite3 as sq


def start_db():
    with sq.connect('animals.db') as con:
        cur = con.cursor()
        print('[INFO] SQLite database was connected.')
        cur.execute('CREATE TABLE IF NOT EXISTS pets(img TEXT, name TEXT, type TEXT, sex TEXT, age TEXT, sterilized TEXT, place TEXT, needs_temp_keeping TEXT, description TEXT, curator TEXT, published_by_id TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS "orgs" ("org_id" INTEGER, "org_name" TEXT, "description" TEXT, "volunteer_help" TEXT, "material_help" TEXT, "financial_help" TEXT, "admin_id" TEXT, "site" TEXT, "telegram" TEXT, "vk" TEXT, "instagram" TEXT, "logo" TEXT, PRIMARY KEY("org_id" AUTOINCREMENT))')


def get_org_names() -> list[tuple]:
    '''Возвращает список всех названий организаций'''
    with sq.connect('animals.db') as con:
        cur = con.cursor()
        res = [i for i in cur.execute("SELECT org_id, org_name from orgs").fetchall()]
        return res


def get_org_social(row_id: str) -> dict:
    '''Возвращает словарь, где ключ - название ресурса, значение - ссылка'''
    with sq.connect('animals.db') as con:
        cur = con.cursor()
        links = cur.execute(f'''SELECT site, telegram, vk, instagram from orgs WHERE org_id = {row_id}''').fetchone()
        res = dict()
        rus_buttons = ['Сайт', 'Telegram', 'ВКонтакте', 'Instagram']
        for i in range(len(links)):
            if links[i]:
                res[rus_buttons[i]] = links[i]
        return res


def get_org_info(data_type: str, row_id: str) -> str:
    '''Получает информацию из столбца data_type и строки с номером организации row_id'''
    with sq.connect('animals.db') as con:
        cur = con.cursor()
        res = cur.execute(f'''SELECT {data_type} from orgs WHERE org_id = {row_id}''').fetchone()[0]
        return res


def set_org_info(data_type: str, row_id: str, value: str):
    '''Изменяет информацию из столбца data_type и строки с номером организации row_id на значение value'''
    with sq.connect('animals.db') as con:
        cur = con.cursor()
        cur.execute(f'''UPDATE orgs SET {data_type} = '{value}' WHERE org_id = {row_id}''')


"""------------------------------------------------------------------------------------------"""



# def add_pet(state):
#     with state.proxy() as data:
#         with sq.connect('animals.db') as con:
#             cur = con.cursor()
#             cur.execute('INSERT INTO pets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(data.values()))




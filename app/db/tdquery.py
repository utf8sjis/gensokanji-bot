import json

import config
from db.connect import PostgreConnect


# DBへの接続
def connect_db():
    return PostgreConnect(
        url=config.DATABASE_URL,
        host='localhost',
        port=5432,
        dbname='bot_db',
        scheme='public',
        user=config.LOCAL_DB_USER,
        password=config.LOCAL_DB_PASS
    )


# テーブルの初期化
def init_table():
    db = connect_db()
    if not db.exists('tweeted_data'):
        # テーブルが存在しなかったら

        # テーブルを作成
        sql = '''
            CREATE TABLE tweeted_data
            (
                name text NOT NULL,
                data text,
                CONSTRAINT pk_name PRIMARY KEY (name)
            );
        '''
        db.execute(sql)

        # レコードを初期化
        sql = '''
            INSERT INTO tweeted_data
                (name, data)
            VALUES
                ('main', %s);
        '''
        db.execute(sql, [json.dumps({
            'last_update': '',
            'total': 0,
            'tweeted': 0,
            'tweeted_id_list': [],
        })])


# データの取得
def get_data():
    db = connect_db()
    sql = '''
        SELECT
            data
        FROM
            tweeted_data
        WHERE
            name = 'main';
    '''
    json_s = db.execute_query(sql)[0][0]
    return json.loads(json_s)


# データの更新
def update_data(data):
    db = connect_db()
    sql = '''
        UPDATE tweeted_data
        SET
            data = %s
        WHERE
            name = 'main';
    '''
    db.execute(sql, [json.dumps(data)])

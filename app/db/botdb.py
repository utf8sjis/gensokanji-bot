import json

from db import PostgreConnect


class BotDBQuery():

    def __init__(self, url, local_user, local_pass):
        self.url = url
        self.local_user = local_user
        self.local_pass = local_pass

    def _connect(self):
        # 接続
        return PostgreConnect(
            url=self.url,
            host='localhost',
            port=5432,
            dbname='bot_db',
            scheme='public',
            user=self.local_user,
            password=self.local_pass
        )

    def init_table(self):
        # テーブルの初期化
        db = self._connect()

        if not db.exists('tweeted_data'):
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

    def get_data(self):
        # データの取得
        db = self._connect()

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

    def update_data(self, data):
        # データの更新
        db = self._connect()

        sql = '''
            UPDATE tweeted_data
            SET
                data = %s
            WHERE
                name = 'main';
        '''
        db.execute(sql, [json.dumps(data)])

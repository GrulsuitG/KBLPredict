from sqlalchemy import create_engine
import json
from urllib.parse import quote

class HYGPDB:
    def read_DB_info(self):
        with open('config.json', 'r') as f:
            config = json.load(f)['DB']

        return config

    def set_page_DB(self):
        config = self.read_DB_info()

        self.engine = create_engine(("mysql+pymysql://" +
                                     config['user'] + ":%s@" +
                                     config['host'] + ":3306" + "/" +
                                     config['db'] + "?charset=utf8") % quote(config['password']),
                                    encoding='utf-8'
                                    )
        self.conn = self.engine.connect()
        print("Connect!")
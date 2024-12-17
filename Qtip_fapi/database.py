from databases import Database
from sqlalchemy import create_engine, MetaData

DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/qtip_schema"


database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
metadata = MetaData()

import os, sys; sys.path.insert(0, '/app')
from app.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
try:
    r = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema')")).fetchall()
    print('Tables:', [x[0] for x in r])
    r2 = db.execute(text('SELECT id, username, role FROM iam.usuarios LIMIT 5')).fetchall()
    print('Users:', r2)
except Exception as e:
    print('Error:', e)
finally:
    db.close()

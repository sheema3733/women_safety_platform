from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from app.database.base import Base

engine = None
_session_factory = sessionmaker(autoflush=False, autocommit=False)
db_session = scoped_session(_session_factory)

def init_db(app):
    global engine
    database_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
    
    # SQLite foreign keys support & thread safety settings
    connect_args = {}
    if database_uri.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(
        database_uri,
        connect_args=connect_args,
        echo=False,
        future=True
    )

    if database_uri.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    _session_factory.configure(bind=engine)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return engine, db_session

def create_all_tables():
    if engine:
        Base.metadata.create_all(bind=engine)

def drop_all_tables():
    if engine:
        Base.metadata.drop_all(bind=engine)

"""
database.py

"""

from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Apunta a app/data/ donde están los demás archivos de datos
_DB_PATH = Path(__file__).resolve().parent / "loncoexpress.db"
_DB_URL  = f"sqlite:///{_DB_PATH}"

# ── Engine ────────────────────────────────────────────────────────────────────
# check_same_thread=False es necesario en PyQt6 porque la UI puede consultar
# desde el hilo principal mientras callbacks usan hilos secundarios.
engine = create_engine(
    _DB_URL,
    connect_args={"check_same_thread": False},
    echo=False,          # Cambiar a True para ver el SQL generado en consola (debug)
)

# Activa las claves foráneas en cada conexión nueva (SQLite las ignora por defecto)
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _):
    dbapi_conn.execute("PRAGMA foreign_keys = ON")


# ── Sesión ────────────────────────────────────────────────────────────────────
_SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_session():
    """
    Context manager que entrega una sesión lista para usar.
    Hace commit automático al salir sin errores;
    rollback automático si ocurre cualquier excepción.

    """
    session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ── Base declarativa ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Clase base de la que heredan todos los modelos ORM."""
    pass


# ── Inicialización ────────────────────────────────────────────────────────────
def init_db() -> None:
    """
    Crea todas las tablas en el archivo .db si aún no existen.
    Llamar una sola vez al arrancar la aplicación (en main.py).
    No destruye datos existentes.
    """
    # Importar los modelos para que SQLAlchemy los registre en Base.metadata
    import app.data.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
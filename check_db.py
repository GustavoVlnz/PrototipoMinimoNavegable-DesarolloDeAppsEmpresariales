from sqlalchemy import text
from app.data.database import _SessionFactory

db = _SessionFactory()
print("--- solicitudes ---")
rows = db.execute(text("SELECT id, estado_solicitud FROM solicitudes_transporte")).fetchall()
for r in rows:
    print(r)

print("--- asignaciones ---")
rows = db.execute(text("SELECT id, estado_asignacion FROM asignaciones_transporte")).fetchall()
for r in rows:
    print(r)
db.close()
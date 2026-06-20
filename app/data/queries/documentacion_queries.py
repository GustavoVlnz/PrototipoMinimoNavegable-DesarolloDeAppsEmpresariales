#app/data/queries/documentacion_queries.py

from datetime import datetime

from app.data.models import DocumentacionVehiculo, Vehiculo


# ─── Helper ORM → dict ────────────────────────────────────────────────────────

def _documento_a_dict(doc: DocumentacionVehiculo) -> dict:
    """Convierte un ORM DocumentacionVehiculo a diccionario."""
    vehiculo = doc.vehiculo
    return {
        "id": doc.id,
        "documento_id": doc.id,
        "vehiculo": vehiculo.patente if vehiculo else "—",
        "vehiculo_id": doc.vehiculo_id,
        "doc_tipo": doc.tipo_documento.replace("_", " "),
        "tipo_documento": doc.tipo_documento,
        "vencimiento": doc.fecha_vencimiento or "—",
        "estado": doc.estado_documental.replace("_", " "),
        "estado_raw": doc.estado_documental,
        "dias_restantes": 0,  # Se calcula en lógica
    }


# ─── Consultas de lectura ─────────────────────────────────────────────────────

def obtener_todos_documentos(session) -> list[dict]:
    documentos = session.query(DocumentacionVehiculo).all()
    return [_documento_a_dict(d) for d in documentos]


def obtener_documentos_por_vehiculo(session, vehiculo_id: int) -> list[dict]:
    documentos = (
        session.query(DocumentacionVehiculo)
        .filter(DocumentacionVehiculo.vehiculo_id == vehiculo_id)
        .all()
    )
    return [_documento_a_dict(d) for d in documentos]


def obtener_documentos_por_estado(session, estado: str) -> list[dict]:
    estado_bd = estado.replace(" ", "_")

    documentos = (
        session.query(DocumentacionVehiculo)
        .filter(DocumentacionVehiculo.estado_documental == estado_bd)
        .all()
    )

    return [_documento_a_dict(d) for d in documentos]


def obtener_documento_por_id(session, documento_id: int) -> dict | None:
    documento = (
        session.query(DocumentacionVehiculo)
        .filter(DocumentacionVehiculo.id == documento_id)
        .first()
    )

    return _documento_a_dict(documento) if documento else None


# ─── Operaciones de actualización ─────────────────────────────────────────────

def actualizar_fecha_vencimiento(
    session,
    documento_id: int,
    nueva_fecha: str
) -> bool:

    try:
        documento = (
            session.query(DocumentacionVehiculo)
            .filter(DocumentacionVehiculo.id == documento_id)
            .first()
        )

        if not documento:
            return False

        documento.fecha_vencimiento = nueva_fecha
        session.commit()
        return True

    except Exception as e:
        print(f"Error al actualizar fecha de vencimiento: {e}")
        return False


def actualizar_estado_documento(
    session,
    documento_id: int,
    nuevo_estado: str
) -> bool:

    estado_bd = nuevo_estado.replace(" ", "_")

    try:
        documento = (
            session.query(DocumentacionVehiculo)
            .filter(DocumentacionVehiculo.id == documento_id)
            .first()
        )

        if not documento:
            return False

        documento.estado_documental = estado_bd
        session.commit()
        return True

    except Exception as e:
        print(f"Error al actualizar estado del documento: {e}")
        return False


def crear_documento(
    session,
    vehiculo_id: int,
    tipo_documento: str,
    fecha_vencimiento: str
) -> bool:

    try:
        nuevo_doc = DocumentacionVehiculo(
            vehiculo_id=vehiculo_id,
            tipo_documento=tipo_documento,
            fecha_vencimiento=fecha_vencimiento,
            estado_documental="Vigente",
        )

        session.add(nuevo_doc)
        session.commit()
        return True

    except Exception as e:
        print(f"Error al crear documento: {e}")
        return False

#app/data/queries/documentacion_queries.py

from app.data.models import DocumentacionVehiculo, Vehiculo
from app.logic import transition_service
from app.logic.transition_service import TransitionError


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
        "dias_restantes": 0,  # Se calcula en documentacion_logic
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


def obtener_documento_orm_por_id(session, documento_id: int) -> DocumentacionVehiculo | None:
    """
    Igual que obtener_documento_por_id(), pero retorna el objeto ORM en
    vez de un dict. Se usa donde se necesita pasarlo directamente a
    transition_service.
    """
    return (
        session.query(DocumentacionVehiculo)
        .filter(DocumentacionVehiculo.id == documento_id)
        .first()
    )


# ─── Operaciones de actualización ─────────────────────────────────────────────

def marcar_vencido(session, documento_id: int) -> tuple[bool, str | None]:
    """
    Marca un documento como Vencido y sincroniza el estado del vehículo
    asociado (lo bloquea, salvo que esté En_Ruta -- ver
    transition_service.sincronizar_disponibilidad_vehiculo).
    """
    doc = session.query(DocumentacionVehiculo).filter(
        DocumentacionVehiculo.id == documento_id
    ).first()
    if not doc:
        return False, "El documento no existe."

    try:
        transition_service.marcar_documento_vencido(session, doc)
    except TransitionError as e:
        return False, str(e)

    return True, None


def renovar(session, documento_id: int, nueva_fecha: str) -> tuple[bool, str | None]:
    """
    Renueva un documento (pasa a Vigente con nueva fecha de
    vencimiento) y sincroniza el estado del vehículo asociado
    """
    doc = session.query(DocumentacionVehiculo).filter(
        DocumentacionVehiculo.id == documento_id
    ).first()
    if not doc:
        return False, "El documento no existe."

    try:
        transition_service.renovar_documento(session, doc, nueva_fecha)
    except TransitionError as e:
        return False, str(e)

    return True, None


def crear_documento(
    session,
    vehiculo_id: int,
    tipo_documento: str,
    fecha_vencimiento: str,
) -> bool:
    #Crea un nuevo documento de vehículo en estado Vigente. 
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
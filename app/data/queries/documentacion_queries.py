#app/logic/documentaciones_queries.py

from datetime import datetime

from app.data.database import get_session
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

def obtener_todos_documentos() -> list[dict]:
    """Retorna todos los documentos de vehículos de la base de datos."""
    with get_session() as session:
        documentos = session.query(DocumentacionVehiculo).all()
        resultado = [_documento_a_dict(d) for d in documentos]
    return resultado


def obtener_documentos_por_vehiculo(vehiculo_id: int) -> list[dict]:
    """Retorna documentos de un vehículo específico."""
    with get_session() as session:
        documentos = (
            session.query(DocumentacionVehiculo)
            .filter(DocumentacionVehiculo.vehiculo_id == vehiculo_id)
            .all()
        )
        resultado = [_documento_a_dict(d) for d in documentos]
    return resultado


def obtener_documentos_por_estado(estado: str) -> list[dict]:
    """Retorna documentos filtrados por estado de vigencia."""
    # Convertir estado display a estado BD (ej: "Por Vencer" → "Por_Vencer")
    estado_bd = estado.replace(" ", "_")
    
    with get_session() as session:
        documentos = (
            session.query(DocumentacionVehiculo)
            .filter(DocumentacionVehiculo.estado_documental == estado_bd)
            .all()
        )
        resultado = [_documento_a_dict(d) for d in documentos]
    return resultado


def obtener_documento_por_id(documento_id: int) -> dict | None:
    """Retorna un documento específico por su ID."""
    with get_session() as session:
        documento = (
            session.query(DocumentacionVehiculo)
            .filter(DocumentacionVehiculo.id == documento_id)
            .first()
        )
        if documento:
            return _documento_a_dict(documento)
    return None


# ─── Operaciones de actualización ─────────────────────────────────────────────

def actualizar_fecha_vencimiento(documento_id: int, nueva_fecha: str) -> bool:
    """
    Actualiza la fecha de vencimiento de un documento.
    
    Args:
        documento_id: ID del documento
        nueva_fecha: Formato "YYYY-MM-DD"
    
    Returns:
        True si fue exitoso, False en caso contrario.
    """
    try:
        with get_session() as session:
            documento = (
                session.query(DocumentacionVehiculo)
                .filter(DocumentacionVehiculo.id == documento_id)
                .first()
            )
            if not documento:
                return False
            documento.fecha_vencimiento = nueva_fecha
            # commit automático al salir del context manager
        return True
    except Exception as e:
        print(f"Error al actualizar fecha de vencimiento: {e}")
        return False


def actualizar_estado_documento(documento_id: int, nuevo_estado: str) -> bool:
    """
    Actualiza el estado de vigencia de un documento.
    
    Args:
        documento_id: ID del documento
        nuevo_estado: Uno de: "Vigente", "Vencido", "Por_Vencer"
    
    Returns:
        True si fue exitoso.
    """
    estado_bd = nuevo_estado.replace(" ", "_")
    
    try:
        with get_session() as session:
            documento = (
                session.query(DocumentacionVehiculo)
                .filter(DocumentacionVehiculo.id == documento_id)
                .first()
            )
            if not documento:
                return False
            documento.estado_documental = estado_bd
        return True
    except Exception as e:
        print(f"Error al actualizar estado del documento: {e}")
        return False


def crear_documento(vehiculo_id: int, tipo_documento: str, fecha_vencimiento: str) -> bool:
    """
    Crea un nuevo documento de vehículo.
    
    Args:
        vehiculo_id: ID del vehículo
        tipo_documento: Uno de los tipos válidos del enum
        fecha_vencimiento: Formato "YYYY-MM-DD"
    
    Returns:
        True si fue exitoso.
    """
    try:
        with get_session() as session:
            nuevo_doc = DocumentacionVehiculo(
                vehiculo_id=vehiculo_id,
                tipo_documento=tipo_documento,
                fecha_vencimiento=fecha_vencimiento,
                estado_documental="Vigente",
            )
            session.add(nuevo_doc)
        return True
    except Exception as e:
        print(f"Error al crear documento: {e}")
        return False

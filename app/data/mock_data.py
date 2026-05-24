"""
Datos de prueba para el prototipo de LoncoExpress.

"""

from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# VEHÍCULOS
# ─────────────────────────────────────────────
VEHICULOS = [
    {
        "id": "V001",
        "patente": "BKRT-42",
        "tipo": "Camioneta",
        "modelo": "Toyota Hilux",
        "capacidad_kg": 1200,
        "estado": "Bloqueado",
        "ubicacion": "Temuco",
        "ultima_mantencion": "2024-11-10",
        "seguro_vence": "2026-08-15",
        "permiso_vence": "2026-09-01",
        "revision_tecnica": "2026-06-30",
        "observacion": "Mantención preventiva vencida (>6 meses)",
        "kilometraje": 87430,
    },
    {
        "id": "V002",
        "patente": "GKRS-91",
        "tipo": "Furgón",
        "modelo": "Peugeot Boxer",
        "capacidad_kg": 1500,
        "estado": "Disponible",
        "ubicacion": "Temuco",
        "ultima_mantencion": "2026-03-22",
        "seguro_vence": "2026-05-23",
        "permiso_vence": "2026-05-23",
        "revision_tecnica": "2026-11-10",
        "observacion": "Permiso de circulación vence en 3 días",
        "kilometraje": 55210,
    },
    {
        "id": "V003",
        "patente": "FLRT-15",
        "tipo": "Camión liviano",
        "modelo": "Mercedes Sprinter",
        "capacidad_kg": 2500,
        "estado": "En Ruta",
        "ubicacion": "Ruta 5 Sur km 112",
        "ultima_mantencion": "2026-04-01",
        "seguro_vence": "2026-12-01",
        "permiso_vence": "2026-10-15",
        "revision_tecnica": "2026-09-20",
        "observacion": "",
        "kilometraje": 120400,
    },
    {
        "id": "V004",
        "patente": "KPNW-88",
        "tipo": "Camioneta",
        "modelo": "Ford Ranger",
        "capacidad_kg": 1000,
        "estado": "En Mantención",
        "ubicacion": "Taller Santiago",
        "ultima_mantencion": "2026-05-18",
        "seguro_vence": "2026-07-30",
        "permiso_vence": "2026-08-10",
        "revision_tecnica": "2026-12-05",
        "observacion": "Reparación sistema de frenos",
        "kilometraje": 63000,
    },
    {
        "id": "V005",
        "patente": "MRTS-34",
        "tipo": "Furgón",
        "modelo": "Renault Master",
        "capacidad_kg": 1800,
        "estado": "Disponible",
        "ubicacion": "Los Ángeles",
        "ultima_mantencion": "2026-02-14",
        "seguro_vence": "2026-11-20",
        "permiso_vence": "2026-10-08",
        "revision_tecnica": "2026-08-25",
        "observacion": "",
        "kilometraje": 41200,
    },
    {
        "id": "V006",
        "patente": "QNBK-67",
        "tipo": "Camioneta",
        "modelo": "Nissan NP300",
        "capacidad_kg": 900,
        "estado": "Reservado",
        "ubicacion": "Concepción",
        "ultima_mantencion": "2026-04-28",
        "seguro_vence": "2026-09-15",
        "permiso_vence": "2026-07-22",
        "revision_tecnica": "2026-06-18",
        "observacion": "",
        "kilometraje": 29800,
    },
    {
        "id": "V007",
        "patente": "STTJ-21",
        "tipo": "Camión liviano",
        "modelo": "VW Delivery",
        "capacidad_kg": 3000,
        "estado": "Fuera de Servicio",
        "ubicacion": "Santiago Bodega Norte",
        "ultima_mantencion": "2026-01-05",
        "seguro_vence": "2026-06-30",
        "permiso_vence": "2026-05-31",
        "revision_tecnica": "2026-03-10",
        "observacion": "Falla eléctrica grave — esperando repuestos",
        "kilometraje": 198300,
    },
]

# ─────────────────────────────────────────────
# CONDUCTORES
# ─────────────────────────────────────────────
CONDUCTORES = [
    {
        "id": "C001",
        "nombre": "Carlos Moya",
        "rut": "14.233.421-K",
        "estado": "En espera",
        "habilitado": True,
        "licencia": "Clase B+D",
        "licencia_vence": "2027-03-15",
        "sucursal": "Temuco",
        "asignacion_activa": "AS-004",
        "telefono": "+56 9 8821 4432",
    },
    {
        "id": "C002",
        "nombre": "Marco Díaz",
        "rut": "12.875.330-5",
        "estado": "Asignado",
        "habilitado": True,
        "licencia": "Clase B+D",
        "licencia_vence": "2026-11-20",
        "sucursal": "Temuco",
        "asignacion_activa": "AS-003",
        "telefono": "+56 9 7714 9981",
    },
    {
        "id": "C003",
        "nombre": "Rodrigo Pérez",
        "rut": "16.102.887-2",
        "estado": "Disponible",
        "habilitado": True,
        "licencia": "Clase B",
        "licencia_vence": "2028-06-01",
        "sucursal": "Santiago",
        "asignacion_activa": None,
        "telefono": "+56 9 6631 2208",
    },
    {
        "id": "C004",
        "nombre": "Andrea Fuentes",
        "rut": "18.440.215-9",
        "estado": "Disponible",
        "habilitado": True,
        "licencia": "Clase B+D",
        "licencia_vence": "2027-08-30",
        "sucursal": "Concepción",
        "asignacion_activa": None,
        "telefono": "+56 9 9903 5547",
    },
    {
        "id": "C005",
        "nombre": "Luis Soto",
        "rut": "10.998.441-1",
        "estado": "En descanso",
        "habilitado": True,
        "licencia": "Clase B+D+E",
        "licencia_vence": "2026-09-10",
        "sucursal": "Los Ángeles",
        "asignacion_activa": None,
        "telefono": "+56 9 5521 7763",
    },
    {
        "id": "C006",
        "nombre": "Pablo Morales",
        "rut": "19.321.004-7",
        "estado": "No habilitado",
        "habilitado": False,
        "licencia": "Clase B",
        "licencia_vence": "2026-04-01",  # vencida
        "sucursal": "Temuco",
        "asignacion_activa": None,
        "telefono": "+56 9 4418 0099",
    },
]

# ─────────────────────────────────────────────
# SOLICITUDES
# ─────────────────────────────────────────────
SOLICITUDES = [
    {
        "id": "SOL-001",
        "origen": "Temuco",
        "destino": "Concepción",
        "carga_kg": 800,
        "prioridad": "Alta",
        "estado": "Completada con incidencia",
        "creada": "2026-05-20 07:45",
        "solicitante": "Javier Riquelme",
        "sucursal_origen": "Temuco",
    },
    {
        "id": "SOL-002",
        "origen": "Temuco",
        "destino": "Santiago",
        "carga_kg": 1200,
        "prioridad": "Media",
        "estado": "Pendiente de Reasignación",
        "creada": "2026-05-20 09:00",
        "solicitante": "Javier Riquelme",
        "sucursal_origen": "Temuco",
    },
    {
        "id": "SOL-003",
        "origen": "Los Ángeles",
        "destino": "Concepción",
        "carga_kg": 600,
        "prioridad": "Baja",
        "estado": "Confirmada",
        "creada": "2026-05-20 08:30",
        "solicitante": "Patricia Vidal",
        "sucursal_origen": "Los Ángeles",
    },
    {
        "id": "SOL-004",
        "origen": "Santiago",
        "destino": "Valparaíso",
        "carga_kg": 2200,
        "prioridad": "Alta",
        "estado": "En evaluación",
        "creada": "2026-05-20 10:15",
        "solicitante": "Hernán Castro",
        "sucursal_origen": "Santiago",
    },
    {
        "id": "SOL-005",
        "origen": "Concepción",
        "destino": "Chillán",
        "carga_kg": 300,
        "prioridad": "Baja",
        "estado": "Creada",
        "creada": "2026-05-20 11:00",
        "solicitante": "Daniela Ortiz",
        "sucursal_origen": "Concepción",
    },
    {
        "id": "SOL-006",
        "origen": "Temuco",
        "destino": "Osorno",
        "carga_kg": 950,
        "prioridad": "Alta",
        "estado": "Reprogramada",
        "creada": "2026-05-19 16:00",
        "solicitante": "Javier Riquelme",
        "sucursal_origen": "Temuco",
    },
]

# ─────────────────────────────────────────────
# ASIGNACIONES
# ─────────────────────────────────────────────
ASIGNACIONES = [
    {
        "id": "AS-001",
        "solicitud_id": "SOL-001",
        "vehiculo_patente": "BKRT-42",
        "conductor": "Carlos Moya",
        "origen": "Temuco",
        "destino": "Concepción",
        "estado": "Completada con incidencia",
        "inicio": "2026-05-20 08:28",
        "fin": "2026-05-20 15:20",
        "prioridad": "Alta",
    },
    {
        "id": "AS-002",
        "solicitud_id": "SOL-001",
        "vehiculo_patente": "MRTS-34",
        "conductor": "Andrea Fuentes",
        "origen": "Los Ángeles",
        "destino": "Concepción",
        "estado": "Completada",
        "inicio": "2026-05-20 11:30",
        "fin": "2026-05-20 15:20",
        "prioridad": "Alta",
    },
    {
        "id": "AS-003",
        "solicitud_id": "SOL-003",
        "vehiculo_patente": "GKRS-91",
        "conductor": "Marco Díaz",
        "origen": "Temuco",
        "destino": "Concepción",
        "estado": "En ejecución",
        "inicio": "2026-05-20 08:58",
        "fin": None,
        "prioridad": "Alta",
    },
    {
        "id": "AS-004",
        "solicitud_id": "SOL-004",
        "vehiculo_patente": "QNBK-67",
        "conductor": "Carlos Moya",
        "origen": "Santiago",
        "destino": "Valparaíso",
        "estado": "Confirmada",
        "inicio": None,
        "fin": None,
        "prioridad": "Alta",
    },
]

# ─────────────────────────────────────────────
# INCIDENTES
# ─────────────────────────────────────────────
INCIDENTES = [
    {
        "id": "INC-001",
        "asignacion_id": "AS-001",
        "vehiculo_patente": "BKRT-42",
        "conductor": "Carlos Moya",
        "tipo": "Falla crítica",
        "descripcion": "Falla en sistema de frenos detectada en km 112 Ruta 5 Sur",
        "gravedad": "Crítica",
        "estado": "En gestión",
        "hora_reporte": "2026-05-20 10:33",
        "supervisor": "Felipe Rivas",
        "resolucion": "Asistencia mecánica enviada. Carga reasignada.",
    },
    {
        "id": "INC-002",
        "asignacion_id": "AS-003",
        "vehiculo_patente": "GKRS-91",
        "conductor": "Marco Díaz",
        "tipo": "Demora",
        "descripcion": "Retraso por tráfico en acceso a Concepción",
        "gravedad": "Menor",
        "estado": "Registrado",
        "hora_reporte": "2026-05-20 12:45",
        "supervisor": "Felipe Rivas",
        "resolucion": "",
    },
]

# ─────────────────────────────────────────────
# MANTENIMIENTO
# ─────────────────────────────────────────────
MANTENIMIENTO = [
    {
        "id": "MNT-001",
        "vehiculo_patente": "BKRT-42",
        "tipo": "Preventiva",
        "descripcion": "Mantención preventiva vencida — más de 6 meses sin revisión",
        "estado": "Pendiente",
        "generado": "2026-05-20 08:05",
        "tecnico": "Sin asignar",
        "prioridad": "Alta",
    },
    {
        "id": "MNT-002",
        "vehiculo_patente": "KPNW-88",
        "tipo": "Correctiva",
        "descripcion": "Reparación sistema de frenos — falla crítica en ruta",
        "estado": "En revisión",
        "generado": "2026-05-20 10:45",
        "tecnico": "Jorge Fernández",
        "prioridad": "Alta",
    },
    {
        "id": "MNT-003",
        "vehiculo_patente": "STTJ-21",
        "tipo": "Correctiva",
        "descripcion": "Falla eléctrica — revisión completa del sistema",
        "estado": "En espera de repuestos",
        "generado": "2026-05-15 09:00",
        "tecnico": "Jorge Fernández",
        "prioridad": "Media",
    },
    {
        "id": "MNT-004",
        "vehiculo_patente": "MRTS-34",
        "tipo": "Preventiva",
        "descripcion": "Revisión preventiva programada — 40.000 km",
        "estado": "Programada",
        "generado": "2026-05-22 08:00",
        "tecnico": "Sin asignar",
        "prioridad": "Baja",
    },
]

# ─────────────────────────────────────────────
# DOCUMENTACIÓN (alertas)
# ─────────────────────────────────────────────
DOCUMENTACION = [
    {
        "vehiculo": "GKRS-91",
        "doc_tipo": "Permiso Circulación",
        "vencimiento": "2026-05-23",
        "dias_restantes": 3,
        "estado": "Por vencer",
    },
    {
        "vehiculo": "GKRS-91",
        "doc_tipo": "Seguro Obligatorio",
        "vencimiento": "2026-05-23",
        "dias_restantes": 3,
        "estado": "Por vencer",
    },
    {
        "vehiculo": "STTJ-21",
        "doc_tipo": "Permiso Circulación",
        "vencimiento": "2026-05-31",
        "dias_restantes": 11,
        "estado": "Por vencer",
    },
    {
        "vehiculo": "STTJ-21",
        "doc_tipo": "Revisión Técnica",
        "vencimiento": "2026-03-10",
        "dias_restantes": -71,
        "estado": "Vencida",
    },
    {
        "vehiculo": "Pablo Morales (conductor)",
        "doc_tipo": "Licencia de Conducir",
        "vencimiento": "2026-04-01",
        "dias_restantes": -49,
        "estado": "Vencida",
    },
    {
        "vehiculo": "BKRT-42",
        "doc_tipo": "Seguro Obligatorio",
        "vencimiento": "2026-08-15",
        "dias_restantes": 87,
        "estado": "Vigente",
    },
]

# ─────────────────────────────────────────────
# KPIs DASHBOARD
# ─────────────────────────────────────────────
def get_kpis():
    disponibles = sum(1 for v in VEHICULOS if v["estado"] == "Disponible")
    en_ruta = sum(1 for v in VEHICULOS if v["estado"] == "En Ruta")
    bloqueados = sum(1 for v in VEHICULOS if v["estado"] in ("Bloqueado", "Fuera de Servicio"))
    en_mantencion = sum(1 for v in VEHICULOS if v["estado"] == "En Mantención")
    alertas = sum(1 for d in DOCUMENTACION if d["estado"] in ("Por vencer", "Vencida"))
    incidentes_activos = sum(1 for i in INCIDENTES if i["estado"] in ("Registrado", "En gestión"))
    return {
        "disponibles": disponibles,
        "en_ruta": en_ruta,
        "bloqueados": bloqueados,
        "en_mantencion": en_mantencion,
        "alertas_doc": alertas,
        "incidentes_activos": incidentes_activos,
        "total_vehiculos": len(VEHICULOS),
        "conductores_disponibles": sum(1 for c in CONDUCTORES if c["estado"] == "Disponible"),
    }

# ─────────────────────────────────────────────
# ALERTAS PARA DASHBOARD
# ─────────────────────────────────────────────
ALERTAS = [
    {"tipo": "critica", "mensaje": "BKRT-42 bloqueado — mantención preventiva vencida (+6 meses)"},
    {"tipo": "critica", "mensaje": "INC-001 activo — falla crítica de frenos en BKRT-42"},
    {"tipo": "advertencia", "mensaje": "GKRS-91 — permiso de circulación vence en 3 días (23/05)"},
    {"tipo": "advertencia", "mensaje": "STTJ-21 — revisión técnica vencida hace 71 días"},
    {"tipo": "info", "mensaje": "SOL-002 pendiente de reasignación tras incidente en ruta"},
]

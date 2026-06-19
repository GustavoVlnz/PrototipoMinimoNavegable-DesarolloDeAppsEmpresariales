"""
seed.py
-------
Puebla loncoexpress.db con datos de prueba listos para demostrar la aplicación.

Uso (desde la raíz del proyecto):
    python -m app.data.seed
"""
import os
from datetime import datetime

from app.data.database import DB_PATH, init_db, get_session
from app.data.models import (
    Sucursal, Usuario, Vehiculo, Conductor,
    DocumentacionVehiculo, Solicitud, Asignacion,
    Incidente, Mantenimiento,
)


# ─────────────────────────────────────────────────────────────────────────────
def _seed_sucursales(db) -> dict:
    """Retorna dict nombre → objeto Sucursal."""
    datos = [
        ("Temuco",      "Av. Caupolicán 100, Temuco"),
        ("Santiago",    "Av. Américo Vespucio 500, Santiago"),
        ("Concepción",  "Av. Los Carrera 300, Concepción"),
        ("Los Ángeles", "Calle Colo-Colo 200, Los Ángeles"),
        ("Valparaíso",  "Av. Argentina 180, Valparaíso"),
        ("Chillán",     "Av. O'Higgins 450, Chillán"),
        ("Osorno",      "Av. Matta 320, Osorno"),
    ]
    sucursales = {}
    for nombre, direccion in datos:
        s = Sucursal(nombre=nombre, direccion=direccion)
        db.add(s)
        sucursales[nombre] = s
    db.flush()
    return sucursales


# ─────────────────────────────────────────────────────────────────────────────
def _seed_usuarios(db, sucursales: dict) -> dict:
    """Retorna dict nombre → objeto Usuario."""
    datos = [
        # (nombre,           rut,             rol,                        sucursal)
        ("Javier Riquelme",  "15.221.334-6",  "Encargado_Sucursal",       "Temuco"),
        ("Patricia Vidal",   "13.440.882-3",  "Encargado_Sucursal",       "Los Ángeles"),
        ("Hernán Castro",    "11.998.005-K",  "Encargado_Sucursal",       "Santiago"),
        ("Daniela Ortiz",    "17.330.441-8",  "Encargado_Sucursal",       "Concepción"),
        ("Felipe Rivas",     "12.110.773-2",  "Supervisor_Operacional",   "Temuco"),
        ("Jorge Fernández",  "14.882.119-5",  "Tecnico_Mantencion",       "Santiago"),
        ("Carlos Moya",      "14.233.421-K",  "Encargado_Flota",          "Temuco"),
        ("Marco Díaz",       "12.875.330-5",  "Encargado_Flota",          "Temuco"),
        ("Rodrigo Pérez",    "16.102.887-2",  "Encargado_Flota",          "Santiago"),
        ("Andrea Fuentes",   "18.440.215-9",  "Encargado_Flota",          "Concepción"),
        ("Luis Soto",        "10.998.441-1",  "Encargado_Flota",          "Los Ángeles"),
        ("Pablo Morales",    "19.321.004-7",  "Encargado_Flota",          "Temuco"),
    ]
    usuarios = {}
    for nombre, rut, rol, suc in datos:
        u = Usuario(
            nombre=nombre,
            rut=rut,
            rol=rol,
            activo=True,
            sucursal_id=sucursales[suc].id,
        )
        db.add(u)
        usuarios[nombre] = u
    db.flush()
    return usuarios


# ─────────────────────────────────────────────────────────────────────────────
def _seed_conductores(db, usuarios: dict) -> dict:
    """Retorna dict nombre → objeto Conductor."""
    datos = [
        # (nombre_usuario,   licencia,     licencia_vence, habilitado, estado)
        ("Carlos Moya",   "Clase B+D",  "2027-03-15", True,  "Disponible"),
        ("Marco Díaz",    "Clase B+D",  "2026-11-20", True,  "Asignado"),
        ("Rodrigo Pérez", "Clase B",    "2028-06-01", True,  "Disponible"),
        ("Andrea Fuentes","Clase B+D",  "2027-08-30", True,  "Disponible"),
        ("Luis Soto",     "Clase B+D+E","2026-09-10", True,  "En_Descanso"),
        ("Pablo Morales", "Clase B",    "2026-04-01", False, "No_Habilitado"),
    ]
    conductores = {}
    for nombre, lic, vence, hab, estado in datos:
        c = Conductor(
            usuario_id=usuarios[nombre].id,
            tipo_licencia=lic,
            licencia_vence=vence,
            habilitado=hab,
            estado_disponibilidad=estado,
        )
        db.add(c)
        conductores[nombre] = c
    db.flush()
    return conductores


# ─────────────────────────────────────────────────────────────────────────────
def _seed_vehiculos(db, sucursales: dict) -> dict:
    """Retorna dict patente → objeto Vehiculo."""
    datos = [
        {
            "patente": "BKRT-42", "tipo": "Camioneta",     "marca_modelo": "Toyota Hilux",
            "capacidad_kg": 1200, "estado_operacional": "Bloqueado",
            "sucursal": "Temuco", "kilometraje": 87430,
            "ultima_mantencion": "2024-11-10",
            "seguro_vence": "2026-08-15", "permiso_vence": "2026-09-01", "revision_tecnica": "2026-06-30",
            "observacion": "Mantención preventiva vencida (>6 meses)",
        },
        {
            "patente": "GKRS-91", "tipo": "Furgon",         "marca_modelo": "Peugeot Boxer",
            "capacidad_kg": 1500, "estado_operacional": "Disponible",
            "sucursal": "Temuco", "kilometraje": 55210,
            "ultima_mantencion": "2026-03-22",
            "seguro_vence": "2026-05-23", "permiso_vence": "2026-05-23", "revision_tecnica": "2026-11-10",
            "observacion": "Permiso de circulación vence en 3 días",
        },
        {
            "patente": "FLRT-15", "tipo": "Camion_Liviano", "marca_modelo": "Mercedes Sprinter",
            "capacidad_kg": 2500, "estado_operacional": "En_Ruta",
            "sucursal": "Temuco", "kilometraje": 120400,
            "ultima_mantencion": "2026-04-01",
            "seguro_vence": "2026-12-01", "permiso_vence": "2026-10-15", "revision_tecnica": "2026-09-20",
            "observacion": "",
        },
        {
            "patente": "KPNW-88", "tipo": "Camioneta",      "marca_modelo": "Ford Ranger",
            "capacidad_kg": 1000, "estado_operacional": "En_Mantencion",
            "sucursal": "Santiago", "kilometraje": 63000,
            "ultima_mantencion": "2026-05-18",
            "seguro_vence": "2026-07-30", "permiso_vence": "2026-08-10", "revision_tecnica": "2026-12-05",
            "observacion": "Reparación sistema de frenos",
        },
        {
            "patente": "MRTS-34", "tipo": "Furgon",          "marca_modelo": "Renault Master",
            "capacidad_kg": 1800, "estado_operacional": "Disponible",
            "sucursal": "Los Ángeles", "kilometraje": 41200,
            "ultima_mantencion": "2026-02-14",
            "seguro_vence": "2026-11-20", "permiso_vence": "2026-10-08", "revision_tecnica": "2026-08-25",
            "observacion": "",
        },
        {
            "patente": "QNBK-67", "tipo": "Camioneta",       "marca_modelo": "Nissan NP300",
            "capacidad_kg": 900,  "estado_operacional": "Reservado",
            "sucursal": "Concepción", "kilometraje": 29800,
            "ultima_mantencion": "2026-04-28",
            "seguro_vence": "2026-09-15", "permiso_vence": "2026-07-22", "revision_tecnica": "2026-06-18",
            "observacion": "",
        },
        {
            "patente": "STTJ-21", "tipo": "Camion_Liviano",  "marca_modelo": "VW Delivery",
            "capacidad_kg": 3000, "estado_operacional": "Fuera_de_Servicio",
            "sucursal": "Santiago", "kilometraje": 198300,
            "ultima_mantencion": "2026-01-05",
            "seguro_vence": "2026-06-30", "permiso_vence": "2026-05-31", "revision_tecnica": "2026-03-10",
            "observacion": "Falla eléctrica grave — esperando repuestos",
        },
    ]
    vehiculos = {}
    for d in datos:
        v = Vehiculo(
            patente=d["patente"],
            tipo=d["tipo"],
            marca_modelo=d["marca_modelo"],
            capacidad_kg=d["capacidad_kg"],
            estado_operacional=d["estado_operacional"],
            sucursal_actual_id=sucursales[d["sucursal"]].id,
            kilometraje=d["kilometraje"],
            ultima_mantencion=d["ultima_mantencion"],
            seguro_vence=d["seguro_vence"],
            permiso_vence=d["permiso_vence"],
            revision_tecnica=d["revision_tecnica"],
            observacion=d.get("observacion", ""),
        )
        db.add(v)
        vehiculos[d["patente"]] = v
    db.flush()
    return vehiculos


# ─────────────────────────────────────────────────────────────────────────────
def _seed_documentacion(db, vehiculos: dict):
    docs = [
        ("GKRS-91", "Permiso_Circulacion", "2026-05-23", "Por_Vencer"),
        ("GKRS-91", "Seguro_Obligatorio",  "2026-05-23", "Por_Vencer"),
        ("STTJ-21", "Permiso_Circulacion", "2026-05-31", "Por_Vencer"),
        ("STTJ-21", "Revision_Tecnica",    "2026-03-10", "Vencido"),
        ("BKRT-42", "Seguro_Obligatorio",  "2026-08-15", "Vigente"),
        ("KPNW-88", "Seguro_Obligatorio",  "2026-07-30", "Vigente"),
        ("MRTS-34", "Revision_Tecnica",    "2026-08-25", "Vigente"),
        ("QNBK-67", "Permiso_Circulacion", "2026-07-22", "Vigente"),
    ]
    for patente, tipo, vence, estado in docs:
        db.add(DocumentacionVehiculo(
            vehiculo_id=vehiculos[patente].id,
            tipo_documento=tipo,
            fecha_vencimiento=vence,
            estado_documental=estado,
        ))
    db.flush()


# ─────────────────────────────────────────────────────────────────────────────
def _seed_solicitudes(db, sucursales: dict, usuarios: dict) -> dict:
    datos = [
        # (origen,        destino,       kg,   prio,   estado,                    creada,               solicitante)
        ("Temuco",      "Concepción",   800,  "Alta",  "Aprobada",               "2026-05-20 07:45",  "Javier Riquelme"),
        ("Temuco",      "Santiago",     1200, "Media", "Pendiente_Reasignacion", "2026-05-20 09:00",  "Javier Riquelme"),
        ("Los Ángeles", "Concepción",   600,  "Baja",  "Aprobada",               "2026-05-20 08:30",  "Patricia Vidal"),
        ("Santiago",    "Valparaíso",   2200, "Alta",  "En_Evaluacion",          "2026-05-20 10:15",  "Hernán Castro"),
        ("Concepción",  "Chillán",      300,  "Baja",  "Creada",                 "2026-05-20 11:00",  "Daniela Ortiz"),
        ("Temuco",      "Osorno",       950,  "Alta",  "Reprogramada",           "2026-05-19 16:00",  "Javier Riquelme"),
    ]
    solicitudes = {}
    for origen, destino, kg, prio, estado, fecha_str, solicitante in datos:
        s = Solicitud(
            sucursal_origen_id=sucursales[origen].id,
            sucursal_destino_id=sucursales[destino].id,
            carga_kg=kg,
            prioridad=prio,
            estado_solicitud=estado,
            creado_por=usuarios[solicitante].id,
            fecha_creacion=datetime.strptime(fecha_str, "%Y-%m-%d %H:%M"),
        )
        db.add(s)
        solicitudes[f"{origen}-{destino}"] = s
    db.flush()
    return solicitudes


# ─────────────────────────────────────────────────────────────────────────────
def _seed_asignaciones(db, solicitudes: dict, vehiculos: dict, conductores: dict, usuarios: dict) -> dict:
    sol = list(solicitudes.values())
    asignaciones = {}

    datos = [
        # (solicitud_idx, patente,    conductor,        estado,                     fecha_asig,         asignador)
        (0, "BKRT-42", "Carlos Moya",   "Completada_Con_Incidencia", "2026-05-20 08:28", "Felipe Rivas"),
        (0, "MRTS-34", "Andrea Fuentes","Completada",                 "2026-05-20 11:30", "Felipe Rivas"),
        (2, "GKRS-91", "Marco Díaz",    "En_Ejecucion",               "2026-05-20 08:58", "Felipe Rivas"),
        (3, "QNBK-67", "Carlos Moya",   "Confirmada",                 None,               "Felipe Rivas"),
    ]
    for i, (sol_idx, patente, conductor, estado, fecha_str, asignador) in enumerate(datos):
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M") if fecha_str else None
        a = Asignacion(
            solicitud_id=sol[sol_idx].id,
            vehiculo_id=vehiculos[patente].id,
            conductor_id=conductores[conductor].id,
            estado_asignacion=estado,
            fecha_asignacion=fecha,
            asignado_por=usuarios[asignador].id,
        )
        db.add(a)
        asignaciones[f"AS-{i+1:03d}"] = a
    db.flush()
    return asignaciones


# ─────────────────────────────────────────────────────────────────────────────
def _seed_incidentes(db, asignaciones: dict, usuarios: dict):
    datos = [
        {
            "asignacion": "AS-001",
            "gravedad": "Falla_Critica",
            "descripcion": "Falla en sistema de frenos detectada en km 112 Ruta 5 Sur",
            "km": 112,
            "requiere_asistencia": True,
            "estado": "En_Gestion",
            "gestionado_por": "Felipe Rivas",
            "fecha": "2026-05-20 10:33",
        },
        {
            "asignacion": "AS-003",
            "gravedad": "Incidente_Menor",
            "descripcion": "Retraso por tráfico en acceso a Concepción",
            "km": None,
            "requiere_asistencia": False,
            "estado": "Registrado",
            "gestionado_por": "Felipe Rivas",
            "fecha": "2026-05-20 12:45",
        },
    ]
    incidentes = []
    for d in datos:
        inc = Incidente(
            asignacion_id=asignaciones[d["asignacion"]].id,
            fecha_hora_reporte=datetime.strptime(d["fecha"], "%Y-%m-%d %H:%M"),
            clasificacion_gravedad=d["gravedad"],
            descripcion_falla=d["descripcion"],
            kilometro_ruta=d["km"],
            requiere_asistencia=d["requiere_asistencia"],
            estado_incidente=d["estado"],
            gestionado_por=usuarios[d["gestionado_por"]].id,
        )
        db.add(inc)
        incidentes.append(inc)
    db.flush()
    return incidentes


# ─────────────────────────────────────────────────────────────────────────────
def _seed_mantenimientos(db, vehiculos: dict, incidentes: list, usuarios: dict):
    datos = [
        {
            "patente": "BKRT-42", "tipo": "Preventiva",
            "descripcion": "Mantención preventiva vencida — más de 6 meses sin revisión",
            "estado": "Pendiente", "prioridad": "Alta",
            "fecha": "2026-05-20 08:05", "incidente": None, "tecnico": None,
        },
        {
            "patente": "KPNW-88", "tipo": "Correctiva",
            "descripcion": "Reparación sistema de frenos — falla crítica en ruta",
            "estado": "En_Revision", "prioridad": "Alta",
            "fecha": "2026-05-20 10:45", "incidente": 0, "tecnico": "Jorge Fernández",
        },
        {
            "patente": "STTJ-21", "tipo": "Correctiva",
            "descripcion": "Falla eléctrica — revisión completa del sistema",
            "estado": "En_Espera_Repuestos", "prioridad": "Media",
            "fecha": "2026-05-15 09:00", "incidente": None, "tecnico": "Jorge Fernández",
        },
        {
            "patente": "MRTS-34", "tipo": "Preventiva",
            "descripcion": "Revisión preventiva programada — 40.000 km",
            "estado": "Programada", "prioridad": "Baja",
            "fecha": "2026-05-22 08:00", "incidente": None, "tecnico": None,
        },
    ]
    for d in datos:
        tecnico_id = usuarios[d["tecnico"]].id if d["tecnico"] else None
        inc_id = incidentes[d["incidente"]].id if d["incidente"] is not None else None
        db.add(Mantenimiento(
            vehiculo_id=vehiculos[d["patente"]].id,
            incidente_id=inc_id,
            tipo_mantencion=d["tipo"],
            descripcion=d["descripcion"],
            estado=d["estado"],
            prioridad=d["prioridad"],
            fecha_ingreso=datetime.strptime(d["fecha"], "%Y-%m-%d %H:%M"),
            validado_por_tecnico=tecnico_id,
        ))
    db.flush()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
def run_seed():
    print("Inicializando base de datos LoncoExpress")

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Base de datos anterior eliminada.")

    init_db()

    with get_session() as db:

        print("   Creando sucursales")
        sucursales = _seed_sucursales(db)

        print("   Creando usuarios")
        usuarios = _seed_usuarios(db, sucursales)

        print("   Creando conductores")
        conductores = _seed_conductores(db, usuarios)

        print("   Creando vehículos")
        vehiculos = _seed_vehiculos(db, sucursales)

        print("   Creando documentación de vehículos...")
        _seed_documentacion(db, vehiculos)

        print("   Creando solicitudes")
        solicitudes = _seed_solicitudes(db, sucursales, usuarios)

        print("   Creando asignaciones")
        asignaciones = _seed_asignaciones(db, solicitudes, vehiculos, conductores, usuarios)

        print("   Creando incidentes")
        incidentes = _seed_incidentes(db, asignaciones, usuarios)

        print("   Creando mantenimientos")
        _seed_mantenimientos(db, vehiculos, incidentes, usuarios)

    print("\n  Seed completado. loncoexpress.db lista para usar.")
    print(f"   Sucursales : {len(sucursales)}")
    print(f"   Usuarios   : {len(usuarios)}")
    print(f"   Conductores: {len(conductores)}")
    print(f"   Vehículos  : {len(vehiculos)}")
    print(f"   Solicitudes: {len(solicitudes)}")
    print(f"   Asignaciones: {len(asignaciones)}")


if __name__ == "__main__":
    run_seed()
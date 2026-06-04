"""
models.py
Define todas las tablas de LoncoExpress como clases ORM de SQLAlchemy.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey,
    Integer, String, Text,
)
from sqlalchemy.orm import relationship

from app.data.database import Base


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SUCURSALES
# ═══════════════════════════════════════════════════════════════════════════════
class Sucursal(Base):
    __tablename__ = "sucursales"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    nombre    = Column(String(100), nullable=False, unique=True)   # "Temuco", "Santiago"…
    direccion = Column(String(255), nullable=True)

    # Relaciones inversas (útiles para reportes)
    solicitudes_origen  = relationship("Solicitud", foreign_keys="Solicitud.sucursal_origen_id",  back_populates="sucursal_origen")
    solicitudes_destino = relationship("Solicitud", foreign_keys="Solicitud.sucursal_destino_id", back_populates="sucursal_destino")
    vehiculos           = relationship("Vehiculo", back_populates="sucursal_actual")
    usuarios            = relationship("Usuario",  back_populates="sucursal")

    def __repr__(self):
        return f"<Sucursal {self.nombre}>"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. USUARIOS
# ═══════════════════════════════════════════════════════════════════════════════
class Usuario(Base):
    __tablename__ = "usuarios"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    nombre      = Column(String(150), nullable=False)
    rut         = Column(String(20),  nullable=False, unique=True)
    rol         = Column(
        Enum(
            "Encargado_Sucursal",
            "Encargado_Flota",
            "Supervisor_Operacional",
            "Personal_Administrativo",
            "Tecnico_Mantencion",
            "Administrador",
            name="rol_usuario",
        ),
        nullable=False,
    )
    activo      = Column(Boolean, default=True, nullable=False)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)

    # Relaciones
    sucursal  = relationship("Sucursal", back_populates="usuarios")
    conductor = relationship("Conductor", back_populates="usuario", uselist=False)

    def __repr__(self):
        return f"<Usuario {self.nombre} ({self.rol})>"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. VEHÍCULOS
# ═══════════════════════════════════════════════════════════════════════════════
class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    patente             = Column(String(10),  nullable=False, unique=True)
    tipo                = Column(
        Enum("Camioneta", "Furgon", "Camion_Liviano", name="tipo_vehiculo"),
        nullable=False,
    )
    marca_modelo        = Column(String(100), nullable=True)
    capacidad_kg        = Column(Integer,     nullable=False)
    estado_operacional  = Column(
        Enum(
            "Disponible", "Reservado", "En_Ruta",
            "En_Mantencion", "Fuera_de_Servicio", "Bloqueado",
            name="estado_vehiculo",
        ),
        nullable=False,
        default="Disponible",
    )
    sucursal_actual_id  = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    kilometraje         = Column(Integer, default=0)
    observacion         = Column(Text, nullable=True)
    ultima_mantencion   = Column(String(20), nullable=True)   # "YYYY-MM-DD"

    # Documentos de vigencia
    seguro_vence        = Column(String(20), nullable=True)
    permiso_vence       = Column(String(20), nullable=True)
    revision_tecnica    = Column(String(20), nullable=True)

    # Relaciones
    sucursal_actual = relationship("Sucursal", back_populates="vehiculos")
    documentos      = relationship("DocumentacionVehiculo", back_populates="vehiculo", cascade="all, delete-orphan")
    mantenimientos  = relationship("Mantenimiento",         back_populates="vehiculo")
    asignaciones    = relationship("Asignacion",            back_populates="vehiculo")

    def __repr__(self):
        return f"<Vehiculo {self.patente} [{self.estado_operacional}]>"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CONDUCTORES
# ═══════════════════════════════════════════════════════════════════════════════
class Conductor(Base):
    __tablename__ = "conductores"

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id            = Column(Integer, ForeignKey("usuarios.id"), nullable=False, unique=True)
    tipo_licencia         = Column(String(30), nullable=False)    # "Clase B", "Clase B+D"…
    licencia_vence        = Column(String(20), nullable=True)     # "YYYY-MM-DD"
    habilitado            = Column(Boolean, default=True)
    estado_disponibilidad = Column(
        Enum(
            "Disponible", "Asignado",
            "No_Habilitado", "En_Descanso",
            name="estado_conductor",
        ),
        nullable=False,
        default="Disponible",
    )

    # Relaciones
    usuario      = relationship("Usuario",    back_populates="conductor")
    asignaciones = relationship("Asignacion", back_populates="conductor")

    def __repr__(self):
        return f"<Conductor id={self.id} [{self.estado_disponibilidad}]>"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. DOCUMENTACIÓN DE VEHÍCULOS
# ═══════════════════════════════════════════════════════════════════════════════
class DocumentacionVehiculo(Base):
    __tablename__ = "documentacion_vehiculos"

    id                 = Column(Integer, primary_key=True, autoincrement=True)
    vehiculo_id        = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    tipo_documento     = Column(
        Enum(
            "Permiso_Circulacion", "Seguro_Obligatorio", "Revision_Tecnica",
            name="tipo_documento",
        ),
        nullable=False,
    )
    fecha_vencimiento  = Column(String(20), nullable=False)   # "YYYY-MM-DD"
    estado_documental  = Column(
        Enum("Vigente", "Vencido", "Por_Vencer", name="estado_documental"),
        nullable=False,
        default="Vigente",
    )

    # Relación
    vehiculo = relationship("Vehiculo", back_populates="documentos")

    def __repr__(self):
        return f"<Documento {self.tipo_documento} veh={self.vehiculo_id}>"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. SOLICITUDES DE TRANSPORTE
# ═══════════════════════════════════════════════════════════════════════════════
class Solicitud(Base):
    __tablename__ = "solicitudes_transporte"

    id                        = Column(Integer, primary_key=True, autoincrement=True)
    sucursal_origen_id        = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    sucursal_destino_id       = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    carga_kg                  = Column(Integer, nullable=False)
    prioridad                 = Column(
        Enum("Alta", "Media", "Baja", name="prioridad_solicitud"),
        nullable=False,
    )
    fecha_salida_requerida    = Column(DateTime, nullable=True)
    fecha_llegada_comprometida= Column(DateTime, nullable=True)
    estado_solicitud          = Column(
        Enum(
            "Creada", "En_Evaluacion", "Aprobada", "Rechazada",
            "Pendiente_Reasignacion", "Cancelada", "Reprogramada",
            name="estado_solicitud",
        ),
        nullable=False,
        default="Creada",
    )
    creado_por                = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_creacion            = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    sucursal_origen  = relationship("Sucursal",  foreign_keys=[sucursal_origen_id],  back_populates="solicitudes_origen")
    sucursal_destino = relationship("Sucursal",  foreign_keys=[sucursal_destino_id], back_populates="solicitudes_destino")
    solicitante      = relationship("Usuario",   foreign_keys=[creado_por])
    asignaciones     = relationship("Asignacion", back_populates="solicitud")

    def folio(self) -> str:
        """Retorna el folio legible: SOL-001, SOL-042, etc."""
        return f"SOL-{self.id:03d}"

    def __repr__(self):
        return f"<Solicitud {self.folio()} [{self.estado_solicitud}]>"


# ═══════════════════════════════════════════════════════════════════════════════
# 7. ASIGNACIONES DE TRANSPORTE
# ═══════════════════════════════════════════════════════════════════════════════
class Asignacion(Base):
    __tablename__ = "asignaciones_transporte"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    solicitud_id     = Column(Integer, ForeignKey("solicitudes_transporte.id"), nullable=False)
    vehiculo_id      = Column(Integer, ForeignKey("vehiculos.id"),  nullable=False)
    conductor_id     = Column(Integer, ForeignKey("conductores.id"), nullable=False)
    estado_asignacion= Column(
        Enum(
            "Solicitada", "Pendiente", "Confirmada", "En_Ejecucion",
            "Con_Incidencia", "Completada", "Completada_Con_Incidencia",
            "Fallida", "Fallida_Parcial", "Cerrada",
            name="estado_asignacion",
        ),
        nullable=False,
        default="Solicitada",
    )
    fecha_asignacion = Column(DateTime, nullable=True)
    asignado_por     = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # Relaciones
    solicitud  = relationship("Solicitud",  back_populates="asignaciones")
    vehiculo   = relationship("Vehiculo",   back_populates="asignaciones")
    conductor  = relationship("Conductor",  back_populates="asignaciones")
    asignador  = relationship("Usuario",    foreign_keys=[asignado_por])
    incidentes = relationship("Incidente",  back_populates="asignacion")
    checkout   = relationship("CheckoutOperativo", back_populates="asignacion", uselist=False)
    trazabilidad = relationship("TrazabilidadRuta", back_populates="asignacion", uselist=False)

    def folio(self) -> str:
        return f"AS-{self.id:03d}"

    def __repr__(self):
        return f"<Asignacion {self.folio()} [{self.estado_asignacion}]>"


# ═══════════════════════════════════════════════════════════════════════════════
# 8. CHECKOUT OPERATIVO
# ═══════════════════════════════════════════════════════════════════════════════
class CheckoutOperativo(Base):
    __tablename__ = "checkouts_operativos"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    asignacion_id        = Column(Integer, ForeignKey("asignaciones_transporte.id"), nullable=False, unique=True)
    fecha_checkout       = Column(DateTime, default=datetime.utcnow)
    anomalias_detectadas = Column(Boolean, default=False)
    detalle_anomalias    = Column(Text, nullable=True)
    carga_verificada     = Column(Boolean, default=False)
    estado_salida        = Column(
        Enum(
            "Aprobado", "Aprobado_Con_Observacion", "Rechazado_Bloqueado",
            name="estado_checkout",
        ),
        nullable=False,
    )

    # Relación
    asignacion = relationship("Asignacion", back_populates="checkout")

    def __repr__(self):
        return f"<Checkout asig={self.asignacion_id} [{self.estado_salida}]>"


# ═══════════════════════════════════════════════════════════════════════════════
# 9. TRAZABILIDAD DE RUTAS
# ═══════════════════════════════════════════════════════════════════════════════
class TrazabilidadRuta(Base):
    __tablename__ = "trazabilidad_rutas"

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    asignacion_id           = Column(Integer, ForeignKey("asignaciones_transporte.id"), nullable=False, unique=True)
    fecha_hora_partida      = Column(DateTime, nullable=True)
    fecha_hora_arribo_real  = Column(DateTime, nullable=True)
    incumplimiento_plazo    = Column(Boolean, default=False)
    recepcion_conforme      = Column(Boolean, nullable=True)
    observaciones_receptor  = Column(Text, nullable=True)

    # Relación
    asignacion = relationship("Asignacion", back_populates="trazabilidad")

    def __repr__(self):
        return f"<Trazabilidad asig={self.asignacion_id}>"


# ═══════════════════════════════════════════════════════════════════════════════
# 10. INCIDENTES
# ═══════════════════════════════════════════════════════════════════════════════
class Incidente(Base):
    __tablename__ = "incidentes"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    asignacion_id        = Column(Integer, ForeignKey("asignaciones_transporte.id"), nullable=False)
    fecha_hora_reporte   = Column(DateTime, default=datetime.utcnow)
    clasificacion_gravedad = Column(
        Enum(
            "Incidente_Menor", "Falla_Operativa", "Falla_Critica",
            name="gravedad_incidente",
        ),
        nullable=False,
    )
    descripcion_falla    = Column(Text, nullable=False)
    kilometro_ruta       = Column(Integer, nullable=True)
    requiere_asistencia  = Column(Boolean, default=False)
    estado_incidente     = Column(
        Enum(
            "Registrado", "En_Analisis", "En_Gestion", "Resuelto", "Cerrado",
            name="estado_incidente",
        ),
        nullable=False,
        default="Registrado",
    )
    gestionado_por       = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # Relaciones
    asignacion = relationship("Asignacion", back_populates="incidentes")
    supervisor = relationship("Usuario",    foreign_keys=[gestionado_por])
    mantenimiento = relationship("Mantenimiento", back_populates="incidente", uselist=False)

    def folio(self) -> str:
        return f"INC-{self.id:03d}"

    def __repr__(self):
        return f"<Incidente {self.folio()} [{self.estado_incidente}]>"


# ═══════════════════════════════════════════════════════════════════════════════
# 11. MANTENIMIENTOS
# ═══════════════════════════════════════════════════════════════════════════════
class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    vehiculo_id          = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    incidente_id         = Column(Integer, ForeignKey("incidentes.id"), nullable=True)
    tipo_mantencion      = Column(
        Enum("Preventiva", "Correctiva", name="tipo_mantencion"),
        nullable=False,
    )
    descripcion          = Column(Text, nullable=True)
    estado               = Column(
        Enum(
            "Pendiente", "En_Revision", "En_Espera_Repuestos",
            "Programada", "Completada",
            name="estado_mantenimiento",
        ),
        nullable=False,
        default="Pendiente",
    )
    fecha_ingreso        = Column(DateTime, default=datetime.utcnow)
    fecha_egreso_real    = Column(DateTime, nullable=True)
    diagnostico_tecnico  = Column(Text, nullable=True)
    prioridad            = Column(
        Enum("Alta", "Media", "Baja", name="prioridad_mnt"),
        nullable=False,
        default="Media",
    )
    validado_por_tecnico = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    validado_por_flota   = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # Relaciones
    vehiculo          = relationship("Vehiculo",   back_populates="mantenimientos")
    incidente         = relationship("Incidente",  back_populates="mantenimiento")
    tecnico_validador = relationship("Usuario",    foreign_keys=[validado_por_tecnico])
    flota_validador   = relationship("Usuario",    foreign_keys=[validado_por_flota])

    def folio(self) -> str:
        return f"MNT-{self.id:03d}"

    def __repr__(self):
        return f"<Mantenimiento {self.folio()} [{self.estado}]>"


# ═══════════════════════════════════════════════════════════════════════════════
# 12. BITÁCORA DE CONTINGENCIA MANUAL
# ═══════════════════════════════════════════════════════════════════════════════
class BitacoraContingencia(Base):
    __tablename__ = "bitacora_contingencia_manual"

    id                              = Column(Integer, primary_key=True, autoincrement=True)
    tipo_registro_afectado          = Column(
        Enum("Solicitud", "Incidente", "Asignacion", name="tipo_contingencia"),
        nullable=False,
    )
    descripcion_operacion           = Column(Text, nullable=False)
    fecha_hora_suceso_real          = Column(DateTime, nullable=False)
    fecha_hora_sincronizacion       = Column(DateTime, nullable=True)
    responsable_sincronizacion_id   = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # Relación
    responsable = relationship("Usuario", foreign_keys=[responsable_sincronizacion_id])

    def __repr__(self):
        return f"<Contingencia {self.tipo_registro_afectado} {self.fecha_hora_suceso_real}>"
# PrototipoMinimoNavegable-DesarolloDeAppsEmpresariales

lista de funcionalidades que debe tener:
1. Dashboard General

KPIs en tiempo real: vehículos disponibles, en ruta, bloqueados, en mantención
Solicitudes activas del día
Alertas de documentación próxima a vencer
Resumen de incidentes abiertos

2. Solicitudes de Transporte

Crear solicitud (carga kg, destino, prioridad, hora salida)
Listar solicitudes con estados: Creada / En evaluación / Pendiente / Confirmada / Cancelada / Reprogramada
Reprogramar o cancelar solicitud
Historial de solicitudes

3. Gestión de Vehículos

Listado de flota con estado visual: Disponible / Reservado / En Ruta / Bloqueado / Fuera de Servicio / En Mantención
Ficha de vehículo (patente, capacidad, estado técnico, documentación)
Bloquear / desbloquear vehículo
Alertas de mantención vencida

4. Gestión de Conductores

Listado con estados: Disponible / Asignado / No habilitado / En descanso
Ficha de conductor (nombre, habilitación, asignación activa)

5. Asignaciones

Crear asignación (vehículo + conductor + solicitud)
Validación automática de aptitud técnica y documental
Estados: Confirmada / En ejecución / Completada / Completada con incidencia / Fallida / Cancelada
Reasignación por conflicto de prioridad (alta > media, y por hora de creación si empatan)
Check-out del conductor

6. Incidentes en Ruta

Reportar incidente desde ruta (nivel: menor / falla operativa / falla crítica)
Escalar a Supervisor Operacional
Gestionar reasignación de carga
Cerrar incidente (requiere aprobación técnica + administrativa)

7. Mantenimiento

Órdenes de mantención generadas automáticamente al bloquear vehículo
Validación del Técnico para liberar vehículo a "Disponible"
Historial de mantenciones por vehículo

8. Documentación / Alertas

Control de permiso de circulación, seguro y revisión técnica
Alertas de vencimiento próximo (ej: vence en 3 días)
Bloqueo automático si documentación vence

9. Reportes

Registro de incumplimientos de plazo
Trazabilidad: quién usó cada vehículo, cuándo y en qué estado lo devolvió
Historial de asignaciones cerradas

10. Contingencia (Protocolo manual)

Registro manual de solicitudes e incidencias cuando el sistema cae
Sincronización posterior al restablecer el sistema
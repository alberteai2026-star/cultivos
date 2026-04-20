# Plan de Implementación para Producción (MySQL)

## 1) Objetivo

Este documento define el plan de ejecución para llevar el sistema integral de cultivos a producción con una arquitectura modular y base de datos **MySQL 8.0**.

Incluye:
- Cronograma por fases y sprints.
- Alcance por módulo y submódulo.
- Modelo de datos base en MySQL.
- Estrategia de pruebas, despliegue y operación.

---

## 2) Decisiones técnicas base

- **Base de datos:** MySQL 8.0 (InnoDB, UTF8MB4).
- **Arquitectura:** API-first, multi-finca (tenant lógico por `finca_id`).
- **Seguridad:** JWT + RBAC por finca + auditoría de eventos.
- **Despliegue:** CI/CD con ambientes `dev`, `staging`, `prod`.
- **Trazabilidad:** logs de auditoría en todas las operaciones críticas.

---

## 3) Cronograma maestro (18 meses / 36 sprints)

Cada sprint tiene 2 semanas.

### Fase 0 — Fundación (S1-S4)
- Arquitectura, CI/CD, seguridad base, esquema troncal MySQL.
- Módulos: M1 (base), setup M2.

### Fase 1 — MVP Campo (S5-S10)
- M1 Auth completo, M2 Fincas, M3 Lotes, M5 Labores, M14 Inventario, M12 RRHH base.
- Resultado: operación mínima real de finca.

### Fase 2 — Núcleo Agronómico (S11-S18)
- M4 Cultivos, M9 Clima, M10 Riego, M13 Maquinaria, M8 Monitoreo, M6 Insumos.

### Fase 3 — Producción, calidad y cumplimiento (S19-S24)
- M7 Cosechas, M15 Calidad, M17 Cuaderno Fitosanitario, M18 Finanzas.

### Fase 4 — Comercial y analítica (S25-S30)
- M19 Facturación, M20 Logística, M21 Marketplace, M22 Reportes, M23 IA.

### Fase 5 — Gobierno y UX central (S31-S34)
- M24 Auditoría, M25 Ajustes, M26 Dashboard.

### Fase 6 — Avanzados y cierre corporativo (S35-S36 + hardening)
- M27 SIG, M28 IoT, M29 GPS, M30 Tracking empleados, M31 Vigilancia, M32 NIIF.

> Nota: Los módulos 27-32 pueden requerir 2-4 sprints adicionales de hardening.

---

## 3.1 Checklist de avance (control de implementación)

> Marcar con `[x]` cuando esté implementado y validado en `staging`.
> Última actualización manual de este checklist: **2026-04-20**.

### Resumen rápido de avance (2026-04-20)

- Fases completas: **0/7**
- Módulos completos: **21/32** (pendientes M22-M32)
- Sprints completos: **3/36** (S23, S24, S25)
- Submódulos completos: **15/111**

### Brecha principal pendiente

1. **Analítica y gobierno:** M22, M23, M24, M25, M26.
2. **Capacidades avanzadas:** M27, M28, M29, M30, M31, M32.
3. **Cierre formal de calidad:** checklist DoD operativo global sin marcar.

### Estado por fase

- [ ] Fase 0 — Fundación (S1-S4)
- [ ] Fase 1 — MVP Campo (S5-S10)
- [ ] Fase 2 — Núcleo Agronómico (S11-S18)
- [ ] Fase 3 — Producción, calidad y cumplimiento (S19-S24)
- [ ] Fase 4 — Comercial y analítica (S25-S30)
- [ ] Fase 5 — Gobierno y UX central (S31-S34)
- [ ] Fase 6 — Avanzados y cierre corporativo (S35-S36 + hardening)

### Estado por módulo (M1-M32)

- [x] M1 — Autenticación y usuarios
- [x] M2 — Fincas
- [x] M3 — Lotes
- [x] M4 — Cultivos
- [x] M5 — Labores
- [x] M6 — Insumos
- [x] M7 — Cosechas
- [x] M8 — Monitoreo de cultivos
- [x] M9 — Clima y meteorología
- [x] M10 — Gestión de riego
- [x] M11 — Rotación de cultivos
- [x] M12 — Recurso humano
- [x] M13 — Maquinaria
- [x] M14 — Inventario
- [x] M15 — Calidad
- [x] M16 — Semillero/Vivero
- [x] M17 — Cuaderno fitosanitario
- [x] M18 — Finanzas
- [x] M19 — Facturación
- [x] M20 — Logística
- [x] M21 — Marketplace
- [ ] M22 — Reportes y analítica
- [ ] M23 — IA insights
- [ ] M24 — Auditoría
- [ ] M25 — Ajustes
- [ ] M26 — Dashboard
- [ ] M27 — Cartografía SIG
- [ ] M28 — IoT
- [ ] M29 — Seguimiento vehicular/GPS
- [ ] M30 — Seguimiento de empleados en campo
- [ ] M31 — Vigilancia y seguridad perimetral
- [ ] M32 — Contabilidad agrícola NIIF

### Criterio de check por módulo (Definition of Done operativo)

- [ ] Código implementado y mergeado en rama principal.
- [ ] Migraciones MySQL aplicadas y validadas.
- [ ] Pruebas unitarias e integración aprobadas.
- [ ] Pruebas E2E/UAT aprobadas por negocio.
- [ ] RBAC por finca y auditoría verificados.
- [ ] Observabilidad activa (logs, métricas, alertas).
- [ ] Manual técnico/operativo actualizado.

---

## 4) Alcance funcional por módulo (resumen de producción)

- **M1-M3:** Identidad, fincas y lotes (base operativa).
- **M4-M11:** Núcleo agronómico (cultivos, labores, monitoreo, clima, riego, rotación).
- **M12-M16:** Recursos (RRHH, maquinaria, inventario, calidad, vivero).
- **M17:** Cumplimiento fitosanitario.
- **M18-M21:** Finanzas y comercial.
- **M22-M26:** Analítica, auditoría, configuración y dashboard.
- **M27-M32:** GIS/IoT/GPS/seguridad perimetral/NIIF.

---

## 5) Diseño de datos MySQL (troncal)

## 5.1 Convenciones

- PK: `BIGINT UNSIGNED AUTO_INCREMENT`
- FK: `*_id`
- Fechas: `DATETIME` UTC
- Soft delete: `deleted_at DATETIME NULL`
- Auditoría mínima por tabla crítica: `created_at`, `updated_at`, `created_by`, `updated_by`

## 5.2 Tablas base (mínimas)

### Identidad y seguridad
- `users`
- `roles`
- `permissions`
- `role_permissions`
- `user_farm_roles`
- `sessions`
- `security_events`

### Organización
- `farms`
- `plots`
- `plot_polygons` (WKT/GeoJSON como texto + índices auxiliares)
- `plot_history_events`

### Producción
- `crop_species`
- `crop_varieties`
- `crop_cycles`
- `crop_stage_logs`
- `tasks`
- `task_assignments`
- `task_executions`
- `task_evidence`
- `inputs`
- `input_applications`
- `harvests`
- `harvest_batches`

### Clima y riego
- `weather_observations`
- `weather_alerts`
- `irrigation_plans`
- `irrigation_events`

### Recursos
- `workers`
- `timesheets`
- `machines`
- `machine_usage_logs`
- `maintenance_orders`
- `warehouses`
- `stock_movements`
- `stock_lots`

### Cumplimiento y calidad
- `quality_tests`
- `certifications`
- `phytosanitary_records`
- `residue_analyses`

### Finanzas y comercial
- `cost_entries`
- `cashflow_movements`
- `invoices`
- `invoice_lines`
- `payments`
- `shipments`
- `market_listings`

### Analítica y gobierno
- `report_templates`
- `insight_runs`
- `insight_recommendations`
- `audit_logs`
- `system_settings`
- `dashboard_widgets`

### Avanzados
- `map_layers`
- `iot_devices`
- `iot_readings`
- `iot_rules`
- `vehicle_positions`
- `employee_tracking_events`
- `camera_events`
- `accounting_entries`

---

## 6) Reglas clave de implementación

1. Todas las tablas operativas llevan `finca_id`.
2. Ningún endpoint omite validación RBAC por finca.
3. Toda acción crítica genera evento en `audit_logs`.
4. Operaciones de inventario/costos usan transacciones MySQL.
5. Reportes críticos se materializan para evitar consultas lentas en producción.

---

## 7) API mínima por módulo (patrón)

- `GET /{modulo}` listado con filtros.
- `GET /{modulo}/{id}` detalle.
- `POST /{modulo}` crear.
- `PATCH /{modulo}/{id}` editar.
- `DELETE /{modulo}/{id}` eliminación lógica.
- `GET /{modulo}/export` exportación.

Además, endpoints de negocio específicos (ej.: `POST /tasks/{id}/start`, `POST /tasks/{id}/finish`).

---

## 8) Estrategia de pruebas

## 8.1 Capas
- Unitarias: servicios, validaciones, reglas.
- Integración: API + MySQL real en entorno aislado.
- E2E: flujos de campo y escritorio.
- UAT: validación con usuarios de finca.

## 8.2 Flujos E2E críticos
1. Login → finca activa → crear lote.
2. Crear cultivo → programar labor → ejecutar labor → consumir inventario.
3. Registrar monitoreo → generar alerta fitosanitaria.
4. Cosecha → factura → despacho → impacto financiero.
5. Exportar cuaderno fitosanitario legal.

---

## 9) Despliegue y operación

## 9.1 Pre-producción
- Pruebas de carga API.
- Migraciones validadas en staging.
- Backup/restore probado.

## 9.2 Producción
- Deploy blue/green o rolling.
- Ventana de despliegue nocturna.
- Monitoreo de errores y latencia.
- Plan de rollback definido.

## 9.3 Post-producción (primeros 30 días)
- Mesa de soporte priorizada.
- Seguimiento diario de KPIs operativos.
- Correcciones rápidas por incidentes críticos.

---

## 10) KPIs de salida por fase

- Adopción usuarios activos semanales.
- % labores ejecutadas a tiempo.
- Precisión inventario (teórico vs físico).
- Tiempo de cierre de registro fitosanitario.
- Rentabilidad por lote/ciclo disponible y confiable.
- Incidentes críticos por semana.

---

## 11) Riesgos y mitigación

- **Riesgo:** alcance creciente sin control.  
  **Mitigación:** comité de cambios quincenal.

- **Riesgo:** baja calidad de datos en campo.  
  **Mitigación:** validaciones fuertes + capacitación + UX guiada.

- **Riesgo:** dependencia tardía de módulos avanzados.  
  **Mitigación:** spikes técnicos tempranos para GIS/IoT.

---

## 12) Lista de arranque inmediato (primeros 15 días)

1. Aprobar este plan y alcance del MVP.
2. Crear proyecto Jira con épicas M1-M32.
3. Montar pipelines CI/CD y ambientes.
4. Implementar esquema MySQL troncal + migraciones iniciales.
5. Desarrollar M1 y M2 en paralelo.
6. Preparar pruebas UAT del sprint 2.

---

## 13) Criterio de “listo para producción”

Un módulo se considera listo cuando cumple:
- funcionalidades acordadas,
- pruebas unitarias/integración/E2E aprobadas,
- RBAC y auditoría verificados,
- observabilidad activa,
- documentación técnica y operativa publicada.

---

## 14) Cronograma detallado por sprint (S1-S36)

> Cada sprint = 2 semanas.  
> Cierre de sprint obligatorio: demo + QA + checklist DoD parcial.

### Bloque A — Fundación y MVP (S1-S10)

- [ ] **S1:** Arquitectura base, repositorios, convenciones, CI inicial.
- [ ] **S2:** Seguridad base, JWT, estructura RBAC.
- [ ] **S3:** Invitaciones, sesiones, recuperación contraseña.
- [ ] **S4:** M2 Fincas completo + selector de finca activa.
- [ ] **S5:** M3 Lotes (CRUD + estados + validaciones).
- [ ] **S6:** M3 Polígonos y georreferenciación básica.
- [ ] **S7:** M5 Labores (catálogo y programación).
- [ ] **S8:** M5 Ejecución real, evidencias y alertas.
- [ ] **S9:** M14 Inventario (movimientos + kardex + integración con labores).
- [ ] **S10:** M12 RRHH base + UAT MVP.

### Bloque B — Núcleo agronómico (S11-S18)

- [ ] **S11:** M4 Catálogo cultivos + registro de siembra.
- [ ] **S12:** M4 Fenología BBCH + alertas de desvío.
- [ ] **S13:** M9 Clima (API + histórico + alertas).
- [ ] **S14:** M10 Planificación de riego.
- [ ] **S15:** M10 Ejecución/costos + eficiencia hídrica.
- [ ] **S16:** M13 Maquinaria + mantenimiento + M11 rotación base.
- [ ] **S17:** M8 Monitoreo (visitas, incidencias, umbrales).
- [ ] **S18:** M6 Insumos (aplicaciones, ICA, carencias y bloqueos).

### Bloque C — Producción, calidad y cumplimiento (S19-S24)

- [ ] **S19:** M7 Cosechas (registro y rendimiento).
- [ ] **S20:** M7 Trazabilidad QR + cierre ciclo operativo.
- [ ] **S21:** M15 Calidad (ensayos, certificaciones, alertas vigencia).
- [ ] **S22:** M17 Cuaderno fitosanitario legal y exportable.
- [x] **S23:** M18 Costeo por lote/ciclo + desvíos presupuestales.
- [x] **S24:** M18 Flujo de caja y rentabilidad consolidada.

### Bloque D — Comercial y analítica (S25-S30)

- [x] **S25:** M19 Facturación base.
- [ ] **S26:** M19 DIAN + cartera.
- [ ] **S27:** M20 Logística + remisiones PDF.
- [ ] **S28:** M21 Marketplace + integración precios.
- [ ] **S29:** M22 Reportes (PDF/Excel + firma agrónomo).
- [ ] **S30:** M23 IA (recomendaciones y alertas predictivas).

### Bloque E — Gobierno y UX central (S31-S34)

- [ ] **S31:** M24 Auditoría forense completa.
- [ ] **S32:** M25 Ajustes + notificaciones + integraciones externas.
- [ ] **S33:** M26 Dashboard central con alertas consolidadas.
- [ ] **S34:** Hardening de seguridad, rendimiento y regresión integral.

### Bloque F — Avanzados y cierre (S35-S36)

- [ ] **S35:** M27 SIG + M29 GPS + M30 tracking empleados.
- [ ] **S36:** M28 IoT + M31 vigilancia + M32 NIIF + cierre de salida.

---

## 15) Checklist por submódulo (detalle implementable)

> Marcar cada submódulo cuando cumpla DoD técnico y funcional.

### M1 — Autenticación y usuarios
- [ ] M1.S1 Registro/Login
- [ ] M1.S2 Recuperación de contraseña
- [ ] M1.S3 Roles por finca
- [ ] M1.S4 Invitaciones
- [ ] M1.S5 Sesiones y seguridad

### M2 — Fincas
- [ ] M2.S1 CRUD finca
- [ ] M2.S2 Selector finca activa
- [ ] M2.S3 Dashboard finca

### M3 — Lotes
- [ ] M3.S1 Registro y ficha técnica
- [ ] M3.S2 Estados de lote
- [ ] M3.S3 Polígono y georreferenciación
- [ ] M3.S4 Historial de lote

### M4 — Cultivos
- [ ] M4.S1 Catálogo especie/variedad
- [ ] M4.S2 Siembra/trasplante
- [ ] M4.S3 Fenología BBCH
- [ ] M4.S4 Proyección de cosecha
- [ ] M4.S5 Alertas de desviación

### M5 — Labores
- [ ] M5.S1 Tipos de labor
- [ ] M5.S2 Programación
- [ ] M5.S3 Ejecución
- [ ] M5.S4 Costeo real
- [ ] M5.S5 Calendario y alertas

### M6 — Insumos
- [ ] M6.S1 Catálogo de insumos
- [ ] M6.S2 Aplicaciones por lote/cultivo
- [ ] M6.S3 ICA y carencias
- [ ] M6.S4 Bloqueo de cosecha por carencia

### M7 — Cosechas
- [ ] M7.S1 Registro de cosecha
- [ ] M7.S2 Rendimiento por lote
- [ ] M7.S3 Trazabilidad QR

### M8 — Monitoreo
- [ ] M8.S1 Visitas de campo
- [ ] M8.S2 Incidencias fitosanitarias
- [ ] M8.S3 Trampas y capturas
- [ ] M8.S4 Umbral y alertas técnicas

### M9 — Clima
- [ ] M9.S1 Integración API climática
- [ ] M9.S2 Histórico y exportación
- [ ] M9.S3 DGA
- [ ] M9.S4 Alertas climáticas

### M10 — Riego
- [ ] M10.S1 Programación
- [ ] M10.S2 Ejecución
- [ ] M10.S3 Balance hídrico
- [ ] M10.S4 Alertas déficit/exceso

### M11 — Rotación
- [ ] M11.S1 Historial de rotación
- [ ] M11.S2 Reglas agronómicas
- [ ] M11.S3 Alertas monocultivo

### M12 — RRHH
- [ ] M12.S1 Maestro de trabajadores
- [ ] M12.S2 Jornadas y asistencia
- [ ] M12.S3 Liquidación base

### M13 — Maquinaria
- [ ] M13.S1 Registro de equipos
- [ ] M13.S2 Uso por labor
- [ ] M13.S3 Mantenimiento
- [ ] M13.S4 Alertas de mantenimiento

### M14 — Inventario
- [ ] M14.S1 Bodegas/Subbodegas
- [ ] M14.S2 Entradas/Salidas/Transferencias
- [ ] M14.S3 Vencimientos y mínimos
- [ ] M14.S4 Kardex y valorización

### M15 — Calidad
- [x] M15.S1 Análisis y clasificación
- [x] M15.S2 Certificaciones
- [ ] M15.S3 Alertas de vigencia

### M16 — Semillero/Vivero
- [x] M16.S1 Germinación
- [x] M16.S2 Seguimiento plántulas
- [x] M16.S3 Trasplante y trazabilidad

### M17 — Cuaderno fitosanitario
- [x] M17.S1 Registro legal completo
- [ ] M17.S2 Export oficial PDF
- [ ] M17.S3 QR trazabilidad

### M18 — Finanzas
- [x] M18.S1 Costos automáticos
- [x] M18.S2 Flujo de caja
- [x] M18.S3 Rentabilidad por lote
- [ ] M18.S4 Alertas de desviación

### M19 — Facturación
- [x] M19.S1 Clientes y documentos
- [ ] M19.S2 DIAN
- [ ] M19.S3 Cartera

### M20 — Logística
- [x] M20.S1 Despachos
- [x] M20.S2 Seguimiento
- [ ] M20.S3 Remisiones/devoluciones

### M21 — Marketplace
- [x] M21.S1 Publicaciones
- [x] M21.S2 Compradores/ofertas
- [ ] M21.S3 Cierre comercial

### M22 — Reportes
- [ ] M22.S1 Productivos/financieros
- [ ] M22.S2 Export PDF/Excel
- [ ] M22.S3 Firma agrónomo

### M23 — IA
- [ ] M23.S1 Recomendaciones agronómicas
- [ ] M23.S2 Predicción de rendimiento
- [ ] M23.S3 Alertas predictivas

### M24 — Auditoría
- [ ] M24.S1 Log de acciones
- [ ] M24.S2 Filtros forenses
- [ ] M24.S3 Export y firma digital

### M25 — Ajustes
- [ ] M25.S1 Parametrización
- [ ] M25.S2 Alertas por usuario/canal
- [ ] M25.S3 Integraciones API (DIAN/SIPSA/ICA/ERP)

### M26 — Dashboard
- [ ] M26.S1 KPIs generales
- [ ] M26.S2 Alertas consolidadas
- [ ] M26.S3 Estado de lotes

### M27 — Cartografía SIG
- [ ] M27.S1 Capas satélite/OSM/NDVI
- [ ] M27.S2 Polígonos editables
- [ ] M27.S3 Exportación de mapas

### M28 — IoT
- [x] M28.S1 Registro de sensores
- [ ] M28.S2 Lecturas en tiempo real
- [ ] M28.S3 Reglas de automatización
- [ ] M28.S4 Control de electroválvulas

> Nota técnica (2026-04-20): existe base IoT para alta de dispositivos, lecturas persistidas,
> consulta de últimas lecturas (polling) y stream WebSocket básico. Falta robustecer tiempo
> real (broadcast/event bus), reglas de automatización y control de actuadores.

### M29 — Seguimiento vehicular
- [ ] M29.S1 GPS en tiempo real
- [ ] M29.S2 Historial de rutas
- [ ] M29.S3 Geocercas y alertas

### M30 — Seguimiento empleados
- [ ] M30.S1 Check-in/Check-out georreferenciado
- [ ] M30.S2 Offline y sincronización
- [ ] M30.S3 Evidencias fotográficas

### M31 — Vigilancia
- [ ] M31.S1 Cámaras IP
- [ ] M31.S2 Video en vivo y grabación
- [ ] M31.S3 Alertas de intrusión

### M32 — NIIF
- [ ] M32.S1 Modelo NIC 41/NIIF 13
- [ ] M32.S2 Activos biológicos
- [ ] M32.S3 Estados financieros agrícolas

# Sprint Backlog — cierre del MVP

Plan de la iteración de estabilización. La Carta Gantt orienta las fases y las evaluaciones informadas por el equipo tuvieron un desplazamiento de una semana. La fecha de entrega debe confirmarse con el docente antes de asumirla como compromiso definitivo.

**Objetivo:** validar el recorrido integrado y preparar una demostración reproducible. Capacidad de Benjamín: referencia de aproximadamente 5 horas semanales declaradas; no ocho horas diarias. Las estimaciones son planificación, no horas realmente trabajadas.

| Tarea | PB | Responsable propuesto | Estimación | Dependencia | Resultado / estado |
|---|---|---|---:|---|---|
| ST-01 Revisar mapa y ficha en pantalla estrecha | 04,15 | Benjamín | 1 h | App integrada | Pendiente de dispositivos físicos |
| ST-02 Recorrido completo en dos cuentas | 05–11 | Benjamín | 1 h | Datos de prueba | Automatizado; aceptación manual del equipo pendiente |
| ST-03 Verificar arranque Docker y persistencia | 14 | Benjamín | 1 h | Docker activo | Terminado el 04-11-2026: API saludable, web HTTP 200 y datos persistentes |
| ST-04 Restauración aislada de respaldo | 17 | Benjamín | 1 h | Respaldo SQLite/media | Pendiente |
| ST-05 Corregir principal bloqueo observado | 15,18 | Benjamín | 1 h | Resultados ST-01/02 | Reserva, sin trabajo ficticio asignado |
| ST-06 Revisar visión, alcance y RNF | 13 | Felipe | 1 h | Documentación actual | Propuesto |
| ST-07 Registrar casos y capturas de aceptación | 15,16 | Daniel | 1 h | Coordinación de pruebas | Propuesto |
| ST-08 Preparar guion de demo y revisar manual | 14 | Felipe + Daniel | 1 h conjunta | Manual y entorno | Propuesto |

**Marco de trabajo:** Scrum adaptado al contexto académico, con una iteración de estabilización y revisión semanal. Trello se utiliza como tablero Kanban para visualizar pendiente, en curso, en revisión y terminado; GitHub conserva las versiones y evidencias. La coordinación declarada considera revisión los miércoles en clases y seguimiento por WhatsApp cada dos días. No existe un burndown fiable porque el equipo no ha registrado horas y estados diariamente.

**Reglas:** máximo una tarea de programación activa; un fallo bloqueante desplaza mejoras visuales secundarias. Al cerrar, registrar fecha, commit, quién probó, resultado y pendientes; no marcar todo terminado solo porque el código existe.

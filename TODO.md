# TODO - Mejoras ETL HealthAnalytics IPS (blackboxai)

- [ ] Implementar utilidades aditivas:
  - [ ] CorrectorLinguisticoClinico (4.1 ETL_CONTEXT.md)
  - [ ] ParserNumericoEspanol (4.2 ETL_CONTEXT.md)
- [ ] Persistencia de auditoría ETL:
  - [ ] Agregar modelo AuditoriaTransaccionalETL (4.3)
  - [ ] Crear migración correspondiente
- [ ] Integrar utilidades en pipeline ETL de forma aditiva:
  - [ ] Usar CorrectorLinguisticoClinico para normalizar diagnóstico_preliminar
  - [ ] Usar ParserNumericoEspanol para limpiar/parsear edad
  - [ ] Asegurar que IMC usa fórmula inalterable (verificar/ajustar si aplica)
- [ ] Ejecutar verificación mínima:
  - [ ] `python backend/manage.py makemigrations && python backend/manage.py migrate`
  - [ ] (si aplica) ejecutar `python backend/manage.py run_etl` para validar carga


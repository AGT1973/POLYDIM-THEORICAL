-- ============================================================
-- POLYDIM Anti-Amnesia: VIEWs Seguras para Bootstrap (Regla 0)
-- Ejecutar sobre POLYDIM_VECDB.sqlite si se pierde la BD
-- Fecha: 2026-10-04
-- ============================================================

-- 1. Resumen por categoría (~16 filas, <1 KB)
CREATE VIEW IF NOT EXISTS v_bootstrap_summary AS
SELECT
    category,
    COUNT(*) AS n,
    MAX(updated_at) AS last_updated
FROM permanent_vault
GROUP BY category
ORDER BY last_updated DESC;

-- 2. Detalle truncado (values <=200 chars, api_keys redactadas, blobs etiquetados)
CREATE VIEW IF NOT EXISTS v_bootstrap AS
SELECT
    id,
    category,
    key_name,
    CASE
        WHEN category = 'api_key' THEN '[REDACTED-' || length(value) || 'ch]'
        WHEN category = 'vault_full_backup' THEN '[BLOB-' || length(value) || 'B-NO-LEER]'
        WHEN length(value) > 200 THEN substr(value, 1, 200) || '...[TRUNC]'
        ELSE value
    END AS value_safe,
    length(value) AS value_bytes,
    updated_at
FROM permanent_vault
ORDER BY updated_at DESC;

-- 3. Conteo de teoremas (1 fila)
CREATE VIEW IF NOT EXISTS v_bootstrap_theorems AS
SELECT
    COUNT(*) AS total_theorems,
    MAX(id) AS last_id,
    MIN(id) AS first_id
FROM polydim_theorems;

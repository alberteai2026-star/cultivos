-- 002_plots.sql
-- Módulo 3 (Lotes): tabla base de lotes.

CREATE TABLE IF NOT EXISTS plots (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  code VARCHAR(50) NOT NULL,
  name VARCHAR(150) NOT NULL,
  area_ha DECIMAL(12,2) NULL,
  soil_type VARCHAR(80) NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'libre',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_plot_code_by_farm (farm_id, code),
  KEY idx_plots_farm_id (farm_id),
  CONSTRAINT fk_plots_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

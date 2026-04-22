-- 006_harvests.sql
-- Módulo 7 (Cosechas): registro base de cosechas.

CREATE TABLE IF NOT EXISTS harvests (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NOT NULL,
  crop_cycle_id BIGINT UNSIGNED NULL,
  harvested_at DATETIME NOT NULL,
  quantity DECIMAL(12,3) NOT NULL,
  unit VARCHAR(20) NOT NULL DEFAULT 'kg',
  quality_grade VARCHAR(30) NULL,
  destination VARCHAR(80) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_harvests_farm_id (farm_id),
  KEY idx_harvests_plot_id (plot_id),
  KEY idx_harvests_crop_cycle_id (crop_cycle_id),
  CONSTRAINT fk_harvests_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_harvests_plot FOREIGN KEY (plot_id) REFERENCES plots(id),
  CONSTRAINT fk_harvests_crop_cycle FOREIGN KEY (crop_cycle_id) REFERENCES crop_cycles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

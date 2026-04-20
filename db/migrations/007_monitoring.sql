-- 007_monitoring.sql
-- Módulo 8 (Monitoreo): visitas de monitoreo agronómico.

CREATE TABLE IF NOT EXISTS monitoring_visits (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NOT NULL,
  crop_cycle_id BIGINT UNSIGNED NULL,
  observed_at DATETIME NOT NULL,
  bbch_stage VARCHAR(20) NULL,
  issue_type VARCHAR(80) NULL,
  severity VARCHAR(20) NULL,
  notes VARCHAR(500) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_monitoring_farm_id (farm_id),
  KEY idx_monitoring_plot_id (plot_id),
  KEY idx_monitoring_cycle_id (crop_cycle_id),
  CONSTRAINT fk_monitoring_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_monitoring_plot FOREIGN KEY (plot_id) REFERENCES plots(id),
  CONSTRAINT fk_monitoring_cycle FOREIGN KEY (crop_cycle_id) REFERENCES crop_cycles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

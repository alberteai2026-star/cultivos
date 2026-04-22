CREATE TABLE IF NOT EXISTS irrigation_events (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NOT NULL,
  scheduled_at DATETIME NOT NULL,
  applied_mm DECIMAL(8,2) NULL,
  cost DECIMAL(12,2) NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'programado',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_irrigation_farm_id (farm_id),
  KEY idx_irrigation_plot_id (plot_id),
  CONSTRAINT fk_irrigation_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_irrigation_plot FOREIGN KEY (plot_id) REFERENCES plots(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS rotation_plans (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NOT NULL,
  next_species VARCHAR(120) NOT NULL,
  recommendation VARCHAR(500) NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'propuesto',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_rotation_farm_id (farm_id),
  KEY idx_rotation_plot_id (plot_id),
  CONSTRAINT fk_rotation_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_rotation_plot FOREIGN KEY (plot_id) REFERENCES plots(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

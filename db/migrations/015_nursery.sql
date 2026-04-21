CREATE TABLE IF NOT EXISTS nursery_batches (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NULL,
  species VARCHAR(120) NOT NULL,
  variety VARCHAR(120) NULL,
  sowing_date DATETIME NOT NULL,
  tray_count INT NOT NULL DEFAULT 0,
  status VARCHAR(30) NOT NULL DEFAULT 'activo',
  notes VARCHAR(250) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_nursery_batches_farm_id (farm_id),
  KEY idx_nursery_batches_plot_id (plot_id),
  CONSTRAINT fk_nursery_batches_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_nursery_batches_plot FOREIGN KEY (plot_id) REFERENCES plots(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

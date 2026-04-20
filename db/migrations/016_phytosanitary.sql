CREATE TABLE IF NOT EXISTS phytosanitary_records (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NOT NULL,
  crop_cycle_id BIGINT UNSIGNED NULL,
  detected_issue VARCHAR(150) NOT NULL,
  severity VARCHAR(30) NOT NULL DEFAULT 'media',
  action_taken TEXT NOT NULL,
  observed_at DATETIME NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_phytosanitary_records_farm_id (farm_id),
  KEY idx_phytosanitary_records_plot_id (plot_id),
  KEY idx_phytosanitary_records_crop_cycle_id (crop_cycle_id),
  CONSTRAINT fk_phytosanitary_records_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_phytosanitary_records_plot FOREIGN KEY (plot_id) REFERENCES plots(id),
  CONSTRAINT fk_phytosanitary_records_crop_cycle FOREIGN KEY (crop_cycle_id) REFERENCES crop_cycles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

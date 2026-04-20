CREATE TABLE IF NOT EXISTS finance_entries (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NULL,
  crop_cycle_id BIGINT UNSIGNED NULL,
  entry_type VARCHAR(20) NOT NULL,
  category VARCHAR(80) NOT NULL,
  amount DECIMAL(14,2) NOT NULL,
  description TEXT NULL,
  happened_at DATETIME NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_finance_entries_farm_id (farm_id),
  KEY idx_finance_entries_plot_id (plot_id),
  KEY idx_finance_entries_crop_cycle_id (crop_cycle_id),
  KEY idx_finance_entries_type (entry_type),
  CONSTRAINT fk_finance_entries_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_finance_entries_plot FOREIGN KEY (plot_id) REFERENCES plots(id),
  CONSTRAINT fk_finance_entries_crop_cycle FOREIGN KEY (crop_cycle_id) REFERENCES crop_cycles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

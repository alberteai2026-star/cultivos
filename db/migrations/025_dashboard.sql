CREATE TABLE IF NOT EXISTS dashboard_snapshots (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  active_cycles INT NOT NULL DEFAULT 0,
  pending_tasks INT NOT NULL DEFAULT 0,
  inventory_low_items INT NOT NULL DEFAULT 0,
  income_total DECIMAL(14,2) NOT NULL DEFAULT 0,
  cost_total DECIMAL(14,2) NOT NULL DEFAULT 0,
  captured_at DATETIME NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_dashboard_snapshots_farm_id (farm_id),
  KEY idx_dashboard_snapshots_captured_at (captured_at),
  CONSTRAINT fk_dashboard_snapshots_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

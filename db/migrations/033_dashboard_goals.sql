CREATE TABLE IF NOT EXISTS dashboard_goals (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  kpi_key VARCHAR(50) NOT NULL,
  target_value DECIMAL(14,2) NOT NULL,
  period_label VARCHAR(30) NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'activa',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_dashboard_goals_farm_id (farm_id),
  KEY idx_dashboard_goals_kpi_key (kpi_key),
  KEY idx_dashboard_goals_status (status),
  CONSTRAINT fk_dashboard_goals_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

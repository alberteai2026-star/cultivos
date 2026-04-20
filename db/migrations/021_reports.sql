CREATE TABLE IF NOT EXISTS report_exports (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  report_type VARCHAR(60) NOT NULL,
  format VARCHAR(20) NOT NULL DEFAULT 'pdf',
  period_label VARCHAR(80) NULL,
  file_url TEXT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'generado',
  generated_at DATETIME NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_report_exports_farm_id (farm_id),
  KEY idx_report_exports_type (report_type),
  CONSTRAINT fk_report_exports_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

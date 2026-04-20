CREATE TABLE IF NOT EXISTS audit_exports (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT UNSIGNED NOT NULL,
  farm_id BIGINT UNSIGNED NULL,
  format VARCHAR(20) NOT NULL DEFAULT 'csv',
  filters_json TEXT NULL,
  file_url TEXT NULL,
  signature VARCHAR(160) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_audit_exports_user_id (user_id),
  KEY idx_audit_exports_farm_id (farm_id),
  CONSTRAINT fk_audit_exports_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_audit_exports_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

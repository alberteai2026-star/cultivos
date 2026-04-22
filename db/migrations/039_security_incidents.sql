CREATE TABLE IF NOT EXISTS security_incidents (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  alert_type VARCHAR(50) NOT NULL,
  severity VARCHAR(20) NOT NULL DEFAULT 'media',
  status VARCHAR(20) NOT NULL DEFAULT 'abierta',
  description TEXT NULL,
  detected_at DATETIME NOT NULL,
  resolved_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_security_incidents_farm_id (farm_id),
  KEY idx_security_incidents_status (status),
  KEY idx_security_incidents_severity (severity),
  CONSTRAINT fk_security_incidents_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

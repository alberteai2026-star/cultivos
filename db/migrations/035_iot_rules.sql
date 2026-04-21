CREATE TABLE IF NOT EXISTS iot_rules (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  device_id BIGINT UNSIGNED NULL,
  metric VARCHAR(60) NOT NULL,
  operator VARCHAR(5) NOT NULL,
  threshold_value DECIMAL(14,4) NOT NULL,
  severity VARCHAR(20) NOT NULL DEFAULT 'medium',
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_iot_rules_farm_id (farm_id),
  KEY idx_iot_rules_device_id (device_id),
  KEY idx_iot_rules_metric (metric),
  CONSTRAINT fk_iot_rules_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_iot_rules_device FOREIGN KEY (device_id) REFERENCES iot_devices(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

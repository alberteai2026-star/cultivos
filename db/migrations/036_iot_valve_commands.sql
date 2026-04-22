CREATE TABLE IF NOT EXISTS iot_valve_commands (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  device_id BIGINT UNSIGNED NOT NULL,
  action VARCHAR(20) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'queued',
  source VARCHAR(20) NOT NULL DEFAULT 'manual',
  requested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  executed_at DATETIME NULL,
  KEY idx_iot_valve_commands_farm_id (farm_id),
  KEY idx_iot_valve_commands_device_id (device_id),
  KEY idx_iot_valve_commands_status (status),
  CONSTRAINT fk_iot_valve_commands_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_iot_valve_commands_device FOREIGN KEY (device_id) REFERENCES iot_devices(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

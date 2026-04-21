CREATE TABLE IF NOT EXISTS iot_devices (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NULL,
  name VARCHAR(120) NOT NULL,
  device_type VARCHAR(60) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_iot_devices_farm_id (farm_id),
  KEY idx_iot_devices_plot_id (plot_id),
  CONSTRAINT fk_iot_devices_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_iot_devices_plot FOREIGN KEY (plot_id) REFERENCES plots(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS iot_readings (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  device_id BIGINT UNSIGNED NOT NULL,
  metric VARCHAR(60) NOT NULL,
  value DECIMAL(14,4) NOT NULL,
  unit VARCHAR(20) NULL,
  recorded_at DATETIME NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_iot_readings_device_id (device_id),
  KEY idx_iot_readings_recorded_at (recorded_at),
  CONSTRAINT fk_iot_readings_device FOREIGN KEY (device_id) REFERENCES iot_devices(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

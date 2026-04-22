CREATE TABLE IF NOT EXISTS farm_settings (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  category VARCHAR(60) NOT NULL,
  setting_key VARCHAR(80) NOT NULL,
  setting_value TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_farm_settings (farm_id, category, setting_key),
  KEY idx_farm_settings_farm_id (farm_id),
  CONSTRAINT fk_farm_settings_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS setting_templates (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  crop_type VARCHAR(60) NOT NULL,
  category VARCHAR(60) NOT NULL,
  setting_key VARCHAR(80) NOT NULL,
  default_value TEXT NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_setting_templates_crop_type (crop_type),
  KEY idx_setting_templates_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

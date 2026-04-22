CREATE TABLE IF NOT EXISTS farm_setting_history (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  setting_id BIGINT UNSIGNED NOT NULL,
  changed_by_user_id BIGINT UNSIGNED NULL,
  previous_value TEXT NULL,
  new_value TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_farm_setting_history_setting_id (setting_id),
  KEY idx_farm_setting_history_user_id (changed_by_user_id),
  CONSTRAINT fk_farm_setting_history_setting FOREIGN KEY (setting_id) REFERENCES farm_settings(id),
  CONSTRAINT fk_farm_setting_history_user FOREIGN KEY (changed_by_user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

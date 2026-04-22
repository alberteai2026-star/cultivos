CREATE TABLE IF NOT EXISTS report_templates (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  template_name VARCHAR(120) NOT NULL,
  report_type VARCHAR(60) NOT NULL,
  format VARCHAR(20) NOT NULL DEFAULT 'pdf',
  filters_json TEXT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_report_templates_farm (farm_id),
  INDEX idx_report_templates_type (report_type),
  CONSTRAINT fk_report_templates_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
);

CREATE TABLE IF NOT EXISTS quality_tests (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NULL,
  harvest_id BIGINT UNSIGNED NULL,
  test_type VARCHAR(80) NOT NULL,
  result_value VARCHAR(120) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'ok',
  tested_at DATETIME NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_quality_tests_farm_id (farm_id),
  KEY idx_quality_tests_plot_id (plot_id),
  KEY idx_quality_tests_harvest_id (harvest_id),
  CONSTRAINT fk_quality_tests_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_quality_tests_plot FOREIGN KEY (plot_id) REFERENCES plots(id),
  CONSTRAINT fk_quality_tests_harvest FOREIGN KEY (harvest_id) REFERENCES harvests(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS certifications (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  name VARCHAR(120) NOT NULL,
  issuer VARCHAR(120) NULL,
  valid_until DATETIME NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'vigente',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_certifications_farm_id (farm_id),
  CONSTRAINT fk_certifications_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

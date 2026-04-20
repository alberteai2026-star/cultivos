-- 005_inputs.sql
-- Módulo 6 (Insumos): catálogo y aplicaciones.

CREATE TABLE IF NOT EXISTS input_products (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(180) NOT NULL UNIQUE,
  category VARCHAR(80) NOT NULL,
  ica_register VARCHAR(80) NULL,
  withholding_days INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS input_applications (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NOT NULL,
  task_id BIGINT UNSIGNED NULL,
  input_product_id BIGINT UNSIGNED NOT NULL,
  applied_at DATETIME NOT NULL,
  quantity DECIMAL(12,3) NOT NULL,
  unit VARCHAR(20) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_input_app_farm_id (farm_id),
  KEY idx_input_app_plot_id (plot_id),
  KEY idx_input_app_task_id (task_id),
  KEY idx_input_app_product_id (input_product_id),
  CONSTRAINT fk_input_app_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_input_app_plot FOREIGN KEY (plot_id) REFERENCES plots(id),
  CONSTRAINT fk_input_app_task FOREIGN KEY (task_id) REFERENCES tasks(id),
  CONSTRAINT fk_input_app_product FOREIGN KEY (input_product_id) REFERENCES input_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

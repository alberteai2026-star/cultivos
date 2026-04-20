CREATE TABLE IF NOT EXISTS customers (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  full_name VARCHAR(150) NOT NULL,
  document_id VARCHAR(50) NULL,
  email VARCHAR(120) NULL,
  phone VARCHAR(50) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_customers_farm_id (farm_id),
  CONSTRAINT fk_customers_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS invoices (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  customer_id BIGINT UNSIGNED NOT NULL,
  invoice_number VARCHAR(60) NOT NULL,
  issue_date DATETIME NOT NULL,
  due_date DATETIME NULL,
  total_amount DECIMAL(14,2) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'pendiente',
  notes TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_invoices_farm_id (farm_id),
  KEY idx_invoices_customer_id (customer_id),
  KEY idx_invoices_issue_date (issue_date),
  CONSTRAINT fk_invoices_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_invoices_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

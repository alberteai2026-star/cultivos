CREATE TABLE IF NOT EXISTS inventory_items (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  name VARCHAR(180) NOT NULL,
  unit VARCHAR(20) NOT NULL,
  min_stock DECIMAL(12,3) NULL,
  current_stock DECIMAL(12,3) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_inventory_items_farm_id (farm_id),
  CONSTRAINT fk_inventory_items_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS inventory_movements (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  item_id BIGINT UNSIGNED NOT NULL,
  movement_type VARCHAR(20) NOT NULL,
  quantity DECIMAL(12,3) NOT NULL,
  reason VARCHAR(120) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_inventory_movements_farm_id (farm_id),
  KEY idx_inventory_movements_item_id (item_id),
  CONSTRAINT fk_inventory_movements_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_inventory_movements_item FOREIGN KEY (item_id) REFERENCES inventory_items(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

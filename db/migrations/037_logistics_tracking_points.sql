CREATE TABLE IF NOT EXISTS logistics_tracking_points (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  shipment_id BIGINT UNSIGNED NOT NULL,
  latitude DECIMAL(10,7) NOT NULL,
  longitude DECIMAL(10,7) NOT NULL,
  speed_kmh DECIMAL(8,2) NULL,
  heading_deg DECIMAL(6,2) NULL,
  recorded_at DATETIME NOT NULL,
  source VARCHAR(20) NOT NULL DEFAULT 'gps',
  notes TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_tracking_points_shipment_id (shipment_id),
  KEY idx_tracking_points_recorded_at (recorded_at),
  CONSTRAINT fk_tracking_points_shipment FOREIGN KEY (shipment_id) REFERENCES logistics_shipments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

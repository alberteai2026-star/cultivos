CREATE TABLE IF NOT EXISTS worker_tracking_points (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  worker_id BIGINT UNSIGNED NOT NULL,
  latitude DECIMAL(10,7) NOT NULL,
  longitude DECIMAL(10,7) NOT NULL,
  speed_kmh DECIMAL(8,2) NULL,
  recorded_at DATETIME NOT NULL,
  source VARCHAR(20) NOT NULL DEFAULT 'mobile',
  notes TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_worker_tracking_points_worker_id (worker_id),
  KEY idx_worker_tracking_points_recorded_at (recorded_at),
  CONSTRAINT fk_worker_tracking_points_worker FOREIGN KEY (worker_id) REFERENCES workers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

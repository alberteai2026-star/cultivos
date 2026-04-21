CREATE TABLE IF NOT EXISTS map_features (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NULL,
  feature_type VARCHAR(40) NOT NULL DEFAULT 'polygon',
  name VARCHAR(120) NOT NULL,
  geometry_geojson TEXT NOT NULL,
  properties_json TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_map_features_farm_id (farm_id),
  KEY idx_map_features_plot_id (plot_id),
  CONSTRAINT fk_map_features_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_map_features_plot FOREIGN KEY (plot_id) REFERENCES plots(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

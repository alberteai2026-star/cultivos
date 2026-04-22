CREATE TABLE IF NOT EXISTS map_feature_versions (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  feature_id BIGINT UNSIGNED NOT NULL,
  version_no INT NOT NULL,
  name TEXT NOT NULL,
  geometry_geojson LONGTEXT NOT NULL,
  properties_json LONGTEXT NULL,
  changed_by_user_id BIGINT UNSIGNED NULL,
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_map_feature_versions_feature_id (feature_id),
  KEY idx_map_feature_versions_version_no (version_no),
  CONSTRAINT fk_map_feature_versions_feature FOREIGN KEY (feature_id) REFERENCES map_features(id),
  CONSTRAINT fk_map_feature_versions_user FOREIGN KEY (changed_by_user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

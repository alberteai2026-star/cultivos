-- 008_weather.sql
-- Módulo 9 (Clima): observaciones climáticas por finca.

CREATE TABLE IF NOT EXISTS weather_observations (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  observed_at DATETIME NOT NULL,
  temperature_c DECIMAL(5,2) NULL,
  humidity_pct DECIMAL(5,2) NULL,
  rainfall_mm DECIMAL(6,2) NULL,
  wind_kmh DECIMAL(6,2) NULL,
  source VARCHAR(50) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_weather_farm_id (farm_id),
  KEY idx_weather_observed_at (observed_at),
  CONSTRAINT fk_weather_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

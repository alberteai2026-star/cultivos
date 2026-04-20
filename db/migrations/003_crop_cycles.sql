-- 003_crop_cycles.sql
-- Módulo 4 (Cultivos): ciclos de cultivo por lote.

CREATE TABLE IF NOT EXISTS crop_cycles (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NOT NULL,
  species VARCHAR(120) NOT NULL,
  variety VARCHAR(120) NULL,
  sowing_date DATETIME NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'activo',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_crop_cycles_farm_id (farm_id),
  KEY idx_crop_cycles_plot_id (plot_id),
  CONSTRAINT fk_crop_cycles_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_crop_cycles_plot FOREIGN KEY (plot_id) REFERENCES plots(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

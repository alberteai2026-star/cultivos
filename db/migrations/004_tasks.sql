-- 004_tasks.sql
-- Módulo 5 (Labores): tareas/labores por lote y ciclo.

CREATE TABLE IF NOT EXISTS tasks (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  plot_id BIGINT UNSIGNED NOT NULL,
  crop_cycle_id BIGINT UNSIGNED NULL,
  task_type VARCHAR(80) NOT NULL,
  title VARCHAR(180) NOT NULL,
  planned_date DATETIME NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'programada',
  notes VARCHAR(500) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_tasks_farm_id (farm_id),
  KEY idx_tasks_plot_id (plot_id),
  KEY idx_tasks_crop_cycle_id (crop_cycle_id),
  CONSTRAINT fk_tasks_farm FOREIGN KEY (farm_id) REFERENCES farms(id),
  CONSTRAINT fk_tasks_plot FOREIGN KEY (plot_id) REFERENCES plots(id),
  CONSTRAINT fk_tasks_crop_cycle FOREIGN KEY (crop_cycle_id) REFERENCES crop_cycles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS accounting_journal_entries (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  entry_date DATE NOT NULL,
  reference VARCHAR(80) NULL,
  description TEXT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'posted',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_accounting_journal_entries_farm_id (farm_id),
  KEY idx_accounting_journal_entries_entry_date (entry_date),
  CONSTRAINT fk_accounting_journal_entries_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS accounting_journal_lines (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  journal_entry_id BIGINT UNSIGNED NOT NULL,
  account_code VARCHAR(30) NOT NULL,
  account_name VARCHAR(120) NOT NULL,
  debit DECIMAL(14,2) NOT NULL DEFAULT 0,
  credit DECIMAL(14,2) NOT NULL DEFAULT 0,
  KEY idx_accounting_journal_lines_entry_id (journal_entry_id),
  KEY idx_accounting_journal_lines_account_code (account_code),
  CONSTRAINT fk_accounting_journal_lines_entry FOREIGN KEY (journal_entry_id) REFERENCES accounting_journal_entries(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

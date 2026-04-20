CREATE TABLE IF NOT EXISTS market_listings (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  farm_id BIGINT UNSIGNED NOT NULL,
  title VARCHAR(150) NOT NULL,
  product_name VARCHAR(120) NOT NULL,
  quantity DECIMAL(14,2) NOT NULL,
  unit VARCHAR(20) NOT NULL DEFAULT 'kg',
  unit_price DECIMAL(14,2) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'abierta',
  description TEXT NULL,
  published_at DATETIME NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_market_listings_farm_id (farm_id),
  KEY idx_market_listings_status (status),
  CONSTRAINT fk_market_listings_farm FOREIGN KEY (farm_id) REFERENCES farms(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS market_offers (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  listing_id BIGINT UNSIGNED NOT NULL,
  buyer_name VARCHAR(150) NOT NULL,
  buyer_contact VARCHAR(120) NULL,
  offered_price DECIMAL(14,2) NOT NULL,
  requested_quantity DECIMAL(14,2) NOT NULL,
  message TEXT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'nueva',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_market_offers_listing_id (listing_id),
  KEY idx_market_offers_status (status),
  CONSTRAINT fk_market_offers_listing FOREIGN KEY (listing_id) REFERENCES market_listings(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

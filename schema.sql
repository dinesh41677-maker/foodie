-- Foodie database schema (MySQL 8). Safe to run many times.

CREATE TABLE IF NOT EXISTS users (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(80)  NOT NULL,
  email         VARCHAR(120) NOT NULL UNIQUE,
  phone         VARCHAR(15)  NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('customer','admin') NOT NULL DEFAULT 'customer',
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS addresses (
  id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id      INT UNSIGNED NOT NULL,
  label        VARCHAR(30)  NOT NULL DEFAULT 'Home',
  address_line VARCHAR(255) NOT NULL,
  city         VARCHAR(60)  NOT NULL,
  pincode      CHAR(6)      NOT NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_addresses_user (user_id),
  CONSTRAINT fk_addresses_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS food_categories (
  id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(60) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS food_items (
  id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  category_id      INT UNSIGNED NOT NULL,
  name             VARCHAR(100) NOT NULL,
  description      VARCHAR(255) NOT NULL DEFAULT '',
  food_type        ENUM('veg','nonveg') NOT NULL,
  image            VARCHAR(255) NULL,
  original_price   DECIMAL(8,2) NOT NULL,
  discounted_price DECIMAL(8,2) NOT NULL,
  rating           DECIMAL(2,1) NOT NULL DEFAULT 4.0,
  is_bestseller    TINYINT(1) NOT NULL DEFAULT 0,
  is_available     TINYINT(1) NOT NULL DEFAULT 1,
  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_food_type (food_type),
  INDEX idx_food_category (category_id),
  INDEX idx_food_bestseller (is_bestseller),
  INDEX idx_food_name (name),
  CONSTRAINT fk_food_category FOREIGN KEY (category_id) REFERENCES food_categories(id) ON DELETE RESTRICT,
  CONSTRAINT chk_food_price CHECK (discounted_price <= original_price AND discounted_price > 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS addons (
  id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(80) NOT NULL,
  price        DECIMAL(8,2) NOT NULL,
  is_available TINYINT(1) NOT NULL DEFAULT 1,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS food_addons (
  food_id  INT UNSIGNED NOT NULL,
  addon_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (food_id, addon_id),
  CONSTRAINT fk_fa_food  FOREIGN KEY (food_id)  REFERENCES food_items(id) ON DELETE CASCADE,
  CONSTRAINT fk_fa_addon FOREIGN KEY (addon_id) REFERENCES addons(id)     ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cart_items (
  id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id    INT UNSIGNED NOT NULL,
  food_id    INT UNSIGNED NOT NULL,
  quantity   SMALLINT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_cart_user (user_id),
  CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES users(id)      ON DELETE CASCADE,
  CONSTRAINT fk_cart_food FOREIGN KEY (food_id) REFERENCES food_items(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cart_item_addons (
  cart_item_id INT UNSIGNED NOT NULL,
  addon_id     INT UNSIGNED NOT NULL,
  PRIMARY KEY (cart_item_id, addon_id),
  CONSTRAINT fk_cia_item  FOREIGN KEY (cart_item_id) REFERENCES cart_items(id) ON DELETE CASCADE,
  CONSTRAINT fk_cia_addon FOREIGN KEY (addon_id)     REFERENCES addons(id)     ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS orders (
  id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id          INT UNSIGNED NOT NULL,
  customer_name    VARCHAR(80)  NOT NULL,
  phone            VARCHAR(15)  NOT NULL,
  delivery_address VARCHAR(400) NOT NULL,
  payment_method   ENUM('cod','upi','card') NOT NULL DEFAULT 'cod',
  payment_status   ENUM('pending','paid') NOT NULL DEFAULT 'pending',
  mrp_total        DECIMAL(10,2) NOT NULL,
  discount_total   DECIMAL(10,2) NOT NULL,
  addon_total      DECIMAL(10,2) NOT NULL,
  delivery_fee     DECIMAL(10,2) NOT NULL,
  tax_amount       DECIMAL(10,2) NOT NULL,
  grand_total      DECIMAL(10,2) NOT NULL,
  status           ENUM('placed','confirmed','preparing','out_for_delivery','delivered','cancelled') NOT NULL DEFAULT 'placed',
  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_orders_user (user_id),
  INDEX idx_orders_status (status),
  INDEX idx_orders_created (created_at),
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_items (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_id       INT UNSIGNED NOT NULL,
  food_id        INT UNSIGNED NULL,
  food_name      VARCHAR(100) NOT NULL,
  food_type      ENUM('veg','nonveg') NOT NULL,
  unit_price     DECIMAL(8,2) NOT NULL,
  original_price DECIMAL(8,2) NOT NULL,
  quantity       SMALLINT UNSIGNED NOT NULL,
  line_total     DECIMAL(10,2) NOT NULL,
  INDEX idx_oi_order (order_id),
  CONSTRAINT fk_oi_order FOREIGN KEY (order_id) REFERENCES orders(id)     ON DELETE CASCADE,
  CONSTRAINT fk_oi_food  FOREIGN KEY (food_id)  REFERENCES food_items(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_addons (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_item_id INT UNSIGNED NOT NULL,
  addon_id      INT UNSIGNED NULL,
  addon_name    VARCHAR(80) NOT NULL,
  price         DECIMAL(8,2) NOT NULL,
  INDEX idx_oa_item (order_item_id),
  CONSTRAINT fk_oa_item  FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE CASCADE,
  CONSTRAINT fk_oa_addon FOREIGN KEY (addon_id)      REFERENCES addons(id)      ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_status_history (
  id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_id   INT UNSIGNED NOT NULL,
  status     ENUM('placed','confirmed','preparing','out_for_delivery','delivered','cancelled') NOT NULL,
  changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_osh_order (order_id),
  CONSTRAINT fk_osh_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- SmartDine V1.0 → V2.0 数据库迁移脚本
-- 在已有 V1.0 数据库上添加 V2.0 列和表
-- ============================================================

-- 1. 平台层新表
CREATE TABLE IF NOT EXISTS merchant (
  merchant_id    BIGINT PRIMARY KEY AUTO_INCREMENT,
  name           VARCHAR(64) NOT NULL,
  logo           VARCHAR(255),
  category       VARCHAR(32),
  address        VARCHAR(255),
  contact_name   VARCHAR(32),
  contact_phone  VARCHAR(20),
  business_hours VARCHAR(64),
  tables_count   INT NOT NULL DEFAULT 10,
  status         TINYINT NOT NULL DEFAULT 0,
  created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  approved_at    DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS platform_admin (
  admin_id      BIGINT PRIMARY KEY AUTO_INCREMENT,
  username      VARCHAR(32) NOT NULL UNIQUE,
  password_hash VARCHAR(128) NOT NULL,
  name          VARCHAR(32),
  status        TINYINT NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO merchant (merchant_id, name, status) VALUES (1, '默认商户', 1);
INSERT IGNORE INTO platform_admin (username, password_hash, name) VALUES ('admin', '$2b$12$LJ3m4ys3LkBCVxJGqOjPkuYVOYpGOKbHgEMoJxYzRqcMdFNP2sCuW', '超级管理员');

-- 2. dish
ALTER TABLE dish ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER dish_id;
ALTER TABLE dish ADD COLUMN cost_price DECIMAL(10,2) DEFAULT 0 AFTER price;
ALTER TABLE dish ADD COLUMN nutrition JSON AFTER allergens;
ALTER TABLE dish ADD COLUMN total_sales INT NOT NULL DEFAULT 0 AFTER weekly_sales;
ALTER TABLE dish ADD COLUMN recommended_weight INT DEFAULT 5 AFTER total_sales;
ALTER TABLE dish ADD INDEX idx_dish_merchant (merchant_id);

-- 3. ingredient
ALTER TABLE ingredient ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER ingredient_id;
ALTER TABLE ingredient ADD INDEX idx_ing_merchant (merchant_id);

-- 4. dish_ingredient
ALTER TABLE dish_ingredient ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER id;
ALTER TABLE dish_ingredient ADD INDEX idx_bom_merchant (merchant_id);

-- 5. stock_log
ALTER TABLE stock_log ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER log_id;
ALTER TABLE stock_log ADD INDEX idx_stock_log_merchant (merchant_id);

-- 6. order
ALTER TABLE `order` ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER order_id;
ALTER TABLE `order` ADD COLUMN discount_amount DECIMAL(10,2) DEFAULT 0 AFTER amount;
ALTER TABLE `order` ADD COLUMN actual_amount DECIMAL(10,2) DEFAULT 0 AFTER discount_amount;
ALTER TABLE `order` ADD COLUMN is_group_order TINYINT NOT NULL DEFAULT 0 AFTER source;
ALTER TABLE `order` ADD COLUMN member_count INT NOT NULL DEFAULT 1 AFTER is_group_order;
ALTER TABLE `order` ADD INDEX idx_order_merchant (merchant_id);

-- 7. order_item
ALTER TABLE order_item ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER item_id;
ALTER TABLE order_item ADD INDEX idx_item_merchant (merchant_id);

-- 8. dining_table
ALTER TABLE dining_table ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER table_id;
ALTER TABLE dining_table ADD COLUMN qr_code_url VARCHAR(255) AFTER current_order_id;
ALTER TABLE dining_table ADD INDEX idx_table_merchant (merchant_id);

-- 9. reservation
ALTER TABLE reservation ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER reservation_id;
ALTER TABLE reservation ADD INDEX idx_reservation_merchant (merchant_id);

-- 10. supplier
ALTER TABLE supplier ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER supplier_id;
ALTER TABLE supplier ADD COLUMN on_time_rate DECIMAL(3,2) DEFAULT 1.00 AFTER lead_time;
ALTER TABLE supplier ADD COLUMN quality_score DECIMAL(3,2) DEFAULT 1.00 AFTER on_time_rate;
ALTER TABLE supplier ADD COLUMN price_stability DECIMAL(3,2) DEFAULT 1.00 AFTER quality_score;
ALTER TABLE supplier ADD INDEX idx_supplier_merchant (merchant_id);

-- 11. member: 新增平台级字段
ALTER TABLE member ADD COLUMN wechat_openid VARCHAR(64) AFTER phone;
ALTER TABLE member ADD COLUMN allergies VARCHAR(255) AFTER preferences;
ALTER TABLE member ADD COLUMN health_goal VARCHAR(32) AFTER allergies;

-- 12. member_merchant: 新建商户级会员档案表
CREATE TABLE IF NOT EXISTS member_merchant (
  id               BIGINT PRIMARY KEY AUTO_INCREMENT,
  member_id        BIGINT NOT NULL,
  merchant_id      BIGINT NOT NULL DEFAULT 1,
  level            VARCHAR(8) NOT NULL DEFAULT '普通',
  points           INT NOT NULL DEFAULT 0,
  balance          DECIMAL(10,2) NOT NULL DEFAULT 0,
  visits           INT NOT NULL DEFAULT 0,
  total_spend      DECIMAL(10,2) NOT NULL DEFAULT 0,
  last_visit       DATETIME,
  churn_risk_score DECIMAL(4,3),
  UNIQUE KEY uk_member_merchant (member_id, merchant_id),
  INDEX idx_mm_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO member_merchant (member_id, merchant_id, level, points, balance, visits, total_spend, last_visit)
  SELECT member_id, 1, level, points, balance, visits, total_spend, last_visit FROM member;

-- 13. staff
ALTER TABLE staff ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER staff_id;
ALTER TABLE staff ADD INDEX idx_staff_merchant (merchant_id);

-- 14. schedule
ALTER TABLE schedule ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER id;
ALTER TABLE schedule ADD INDEX idx_schedule_merchant (merchant_id);

-- 15. campaign
ALTER TABLE campaign ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER campaign_id;
ALTER TABLE campaign ADD INDEX idx_campaign_merchant (merchant_id);

-- 16. coupon
ALTER TABLE coupon ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER coupon_id;
ALTER TABLE coupon ADD INDEX idx_coupon_merchant (merchant_id);

-- 17. service_ticket
ALTER TABLE service_ticket ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER ticket_id;
ALTER TABLE service_ticket ADD INDEX idx_ticket_merchant (merchant_id);

-- 18. review
ALTER TABLE review ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER review_id;
ALTER TABLE review ADD INDEX idx_review_merchant (merchant_id);

-- 19. agent_config: 改为自增主键 + merchant_id
ALTER TABLE agent_config ADD COLUMN config_id BIGINT AUTO_INCREMENT PRIMARY KEY FIRST;
ALTER TABLE agent_config ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER config_id;

-- 20. agent_log
ALTER TABLE agent_log ADD COLUMN merchant_id BIGINT NOT NULL DEFAULT 1 AFTER log_id;
ALTER TABLE agent_log ADD INDEX idx_agent_log_merchant (merchant_id);

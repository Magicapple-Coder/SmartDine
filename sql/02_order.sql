-- 订单与流水相关核心表（V2.0：全部表新增 merchant_id + 订单扩展字段）
-- 对应《系统设计说明书》4.3.3

CREATE TABLE `order` (
  order_id        BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id     BIGINT NOT NULL,
  member_id       BIGINT,
  table_id        BIGINT,
  source          VARCHAR(16) NOT NULL,   -- 堂食/外卖
  amount          DECIMAL(10,2) NOT NULL,
  discount_amount DECIMAL(10,2) DEFAULT 0,   -- V2.0 新增：优惠金额
  actual_amount   DECIMAL(10,2) DEFAULT 0,   -- V2.0 新增：实付金额
  is_group_order  TINYINT NOT NULL DEFAULT 0, -- V2.0 新增：是否群体点餐
  member_count    INT NOT NULL DEFAULT 1,     -- V2.0 新增：就餐人数
  pay_status      TINYINT NOT NULL DEFAULT 0,  -- 0待付 1已付 2退款
  cook_status     TINYINT NOT NULL DEFAULT 0,  -- 0待餐 1出餐 2完成
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_order_member (member_id),
  INDEX idx_order_created (created_at),
  INDEX idx_order_status (pay_status, cook_status),
  INDEX idx_order_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE order_item (
  item_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id BIGINT NOT NULL,
  order_id  BIGINT NOT NULL,
  dish_id   BIGINT NOT NULL,
  qty       INT NOT NULL,
  note      VARCHAR(128),
  subtotal  DECIMAL(10,2) NOT NULL,
  INDEX idx_item_order (order_id),
  INDEX idx_item_dish (dish_id),
  INDEX idx_item_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

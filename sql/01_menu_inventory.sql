-- 菜品与库存相关核心表（V2.0：全部表新增 merchant_id 租户隔离）
-- 对应《系统设计说明书》4.3.2

CREATE TABLE dish (
  dish_id       BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id   BIGINT NOT NULL,
  name          VARCHAR(64)  NOT NULL,
  category      VARCHAR(16)  NOT NULL,
  price         DECIMAL(10,2) NOT NULL,
  cost_price    DECIMAL(10,2) DEFAULT 0,
  tags          VARCHAR(128),
  allergens     VARCHAR(128),
  nutrition     JSON,                          -- V2.0 新增：{热量,蛋白质,碳水,脂肪}
  status        TINYINT NOT NULL DEFAULT 1,   -- 1 在售 0 停售
  weekly_sales  INT NOT NULL DEFAULT 0,
  total_sales   INT NOT NULL DEFAULT 0,        -- V2.0 新增：历史总销量
  recommended_weight INT DEFAULT 5,            -- V2.0 新增：推荐权重 1-10
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_dish_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE ingredient (
  ingredient_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id     BIGINT NOT NULL,
  supplier_id     BIGINT,
  name            VARCHAR(32) NOT NULL,
  unit            VARCHAR(8)  NOT NULL,
  stock           DECIMAL(10,3) NOT NULL,
  safe_threshold  DECIMAL(10,3) NOT NULL,
  INDEX idx_ing_supplier (supplier_id),
  INDEX idx_ing_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE dish_ingredient (   -- 菜品-食材 BOM
  id                BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id       BIGINT NOT NULL,
  dish_id           BIGINT NOT NULL,
  ingredient_id     BIGINT NOT NULL,
  qty_per_serving   DECIMAL(10,3) NOT NULL,
  unit              VARCHAR(8) NOT NULL,
  INDEX idx_bom_dish (dish_id),
  INDEX idx_bom_ing (ingredient_id),
  INDEX idx_bom_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE stock_log (   -- 出入库流水
  log_id        BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id   BIGINT NOT NULL,
  ingredient_id BIGINT NOT NULL,
  type          VARCHAR(8) NOT NULL,   -- 入库/出库/损耗
  qty           DECIMAL(10,3) NOT NULL,
  operator      VARCHAR(32) NOT NULL,  -- 操作人（含「系统」）
  time          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  remark        VARCHAR(128),
  INDEX idx_stock_log_ingredient (ingredient_id),
  INDEX idx_stock_log_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

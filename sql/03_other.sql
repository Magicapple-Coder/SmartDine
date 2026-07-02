-- 会员 / 桌台 / 员工 / 营销 / 客服评价 / 智能体配置与日志（V2.0：全部表新增 merchant_id + 扩展字段）
-- 对应《需求文档》6.1 主要数据实体、《系统设计说明书》4.3.4

CREATE TABLE dining_table (
  table_id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id       BIGINT NOT NULL,
  no                VARCHAR(16) NOT NULL,
  seats             INT NOT NULL,
  status            TINYINT NOT NULL DEFAULT 0,  -- 0空闲 1就餐中 2已预订 3待清理
  current_order_id  BIGINT,
  qr_code_url       VARCHAR(255),                 -- V2.0 新增：桌台二维码
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_table_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE reservation (   -- 桌台预订（用户端/客服智能体写入）
  reservation_id  BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id     BIGINT NOT NULL,
  table_id        BIGINT NOT NULL,
  member_id       BIGINT,
  contact_name    VARCHAR(32),
  contact_phone   VARCHAR(20),
  reserve_time    DATETIME NOT NULL,
  guests          INT NOT NULL DEFAULT 1,
  status          TINYINT NOT NULL DEFAULT 0,  -- 0待确认 1已确认 2已取消
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_reservation_table (table_id),
  INDEX idx_reservation_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE supplier (
  supplier_id     BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id     BIGINT NOT NULL,
  name            VARCHAR(64) NOT NULL,
  category        VARCHAR(32),
  contact         VARCHAR(32),
  phone           VARCHAR(20),
  status          TINYINT NOT NULL DEFAULT 1,
  lead_time       INT NOT NULL DEFAULT 1,        -- 采购周期（天）
  on_time_rate    DECIMAL(3,2) DEFAULT 1.00,     -- V2.0 新增：准时率
  quality_score   DECIMAL(3,2) DEFAULT 1.00,     -- V2.0 新增：品质评分
  price_stability DECIMAL(3,2) DEFAULT 1.00,     -- V2.0 新增：价格稳定性
  INDEX idx_supplier_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- 平台级会员（跨商户共享基本信息与偏好，V2.0 拆分设计）
CREATE TABLE member (
  member_id     BIGINT PRIMARY KEY AUTO_INCREMENT,
  name          VARCHAR(32),
  phone         VARCHAR(20) NOT NULL,
  wechat_openid VARCHAR(64),
  preferences   VARCHAR(255),    -- 偏好/忌口标签
  allergies     VARCHAR(255),    -- V2.0 新增：过敏原
  health_goal   VARCHAR(32),     -- V2.0 新增：健康目标（减脂/增肌/控糖等）
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_member_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- 商户级会员档案（每个商户独立积分/等级，V2.0 新增）
CREATE TABLE member_merchant (
  id               BIGINT PRIMARY KEY AUTO_INCREMENT,
  member_id        BIGINT NOT NULL,
  merchant_id      BIGINT NOT NULL,
  level            VARCHAR(8) NOT NULL DEFAULT '普通',  -- 黑卡/金卡/银卡/普通
  points           INT NOT NULL DEFAULT 0,
  balance          DECIMAL(10,2) NOT NULL DEFAULT 0,
  visits           INT NOT NULL DEFAULT 0,
  total_spend      DECIMAL(10,2) NOT NULL DEFAULT 0,
  last_visit       DATETIME,
  churn_risk_score DECIMAL(4,3),              -- V2.0 新增：流失风险评分
  UNIQUE KEY uk_member_merchant (member_id, merchant_id),
  INDEX idx_mm_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE staff (
  staff_id      BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id   BIGINT NOT NULL,
  name          VARCHAR(32) NOT NULL,
  role          VARCHAR(16) NOT NULL,   -- 店长/收银/后厨/服务员
  account       VARCHAR(32) NOT NULL,
  password_hash VARCHAR(128) NOT NULL,
  status        TINYINT NOT NULL DEFAULT 1,  -- 1在岗 0离职
  weekly_hours  DECIMAL(5,1) NOT NULL DEFAULT 0,
  UNIQUE KEY uk_staff_account (account),
  INDEX idx_staff_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE schedule (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id BIGINT NOT NULL,
  staff_id    BIGINT NOT NULL,
  date        DATE NOT NULL,
  shift       VARCHAR(8) NOT NULL,   -- 早/晚/休
  INDEX idx_schedule_staff (staff_id),
  INDEX idx_schedule_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE campaign (
  campaign_id  BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id  BIGINT NOT NULL,
  name         VARCHAR(64) NOT NULL,
  type         VARCHAR(16) NOT NULL,   -- 优惠券/套餐/限时促销
  rule         VARCHAR(255),
  period       VARCHAR(64),
  sold         INT NOT NULL DEFAULT 0,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_campaign_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE coupon (
  coupon_id    BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id  BIGINT NOT NULL,
  campaign_id  BIGINT NOT NULL,
  amount       DECIMAL(10,2) NOT NULL,
  threshold    DECIMAL(10,2) NOT NULL DEFAULT 0,
  claimed      INT NOT NULL DEFAULT 0,
  redeemed     INT NOT NULL DEFAULT 0,
  INDEX idx_coupon_campaign (campaign_id),
  INDEX idx_coupon_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE service_ticket (   -- 客服工单（系统设计说明书 6.3.5）
  ticket_id    BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id  BIGINT NOT NULL,
  member_id    BIGINT,
  channel      VARCHAR(16),
  content      TEXT NOT NULL,
  category     VARCHAR(8),   -- 咨询/投诉/建议/预订
  sentiment    VARCHAR(8),   -- 弱/中/强
  draft_reply  TEXT,
  status       TINYINT NOT NULL DEFAULT 0,  -- 0已自动 1待人工 2已记录
  to_human     TINYINT NOT NULL DEFAULT 0,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ticket_member (member_id),
  INDEX idx_ticket_status (status),
  INDEX idx_ticket_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE review (
  review_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id BIGINT NOT NULL,
  order_id    BIGINT NOT NULL,
  score       TINYINT NOT NULL,
  content     VARCHAR(500),
  sentiment   VARCHAR(8),   -- 好评/中评/差评
  cause       VARCHAR(64),  -- 差评归因
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_review_order (order_id),
  INDEX idx_review_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE agent_config (   -- 智能体参数配置（需求文档 3.9 / 5.5）
  merchant_id BIGINT NOT NULL,
  agent       VARCHAR(16),
  enabled     TINYINT NOT NULL DEFAULT 1,
  params      JSON,
  PRIMARY KEY (merchant_id, agent)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE agent_log (   -- 智能体运行日志（系统设计说明书 6.3.6）
  log_id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id     BIGINT NOT NULL,
  agent           VARCHAR(16) NOT NULL,
  action          VARCHAR(32) NOT NULL,
  input_summary   VARCHAR(255),
  output_summary  VARCHAR(255),
  result          VARCHAR(16),
  time            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_agent_log_agent (agent),
  INDEX idx_agent_log_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

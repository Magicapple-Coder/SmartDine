-- ============================================================
-- SmartDine V2.0 — 商户管理账号表
-- 每个商户拥有独立的管理账号，用于登录商户端后台
-- ============================================================

CREATE TABLE merchant_account (
  account_id      BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id     BIGINT NOT NULL,
  username        VARCHAR(32) NOT NULL UNIQUE,
  password_hash   VARCHAR(128) NOT NULL,
  name            VARCHAR(32),
  role            VARCHAR(16) NOT NULL DEFAULT '商家管理员',
  status          TINYINT NOT NULL DEFAULT 1,  -- 1正常 0停用
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ma_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 新增 3 家示例商户（对应不同餐厅品牌）
-- ============================================================
INSERT INTO merchant (merchant_id, name, category, address, contact_name, contact_phone, business_hours, tables_count, status)
VALUES
  (2, '湘味轩',   '湘菜', '深圳市南山区科技园路100号',   '刘老板', '13800001111', '10:00-22:00', 20, 1),
  (3, '粤海阁',   '粤菜', '深圳市福田区华强北路200号',   '黄老板', '13800002222', '09:00-23:00', 30, 1),
  (4, '蜀香园',   '川菜', '深圳市宝安区西乡大道300号',   '张老板', '13800003333', '11:00-21:00', 15, 1)
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- 更新默认商户名称
UPDATE merchant SET name = '味稻家', category = '中式快餐', address = '深圳市龙华区民治大道88号', contact_name = '陈老板', contact_phone = '13800000000' WHERE merchant_id = 1;

-- ============================================================
-- 为每个商户创建管理账号（密码均为 123456，bcrypt 加密）
-- ============================================================
INSERT INTO merchant_account (merchant_id, username, password_hash, name, role)
VALUES
  (1, 'weidaojia',    '$2b$12$ey/D8p5yrPavaqmcQPOHJ.4Q3rfq5fOjaOB8T5jftcwIGQCrwfo32', '陈老板', '商家管理员'),
  (2, 'xiangweixuan', '$2b$12$ey/D8p5yrPavaqmcQPOHJ.4Q3rfq5fOjaOB8T5jftcwIGQCrwfo32', '刘老板', '商家管理员'),
  (3, 'yuehaige',     '$2b$12$ey/D8p5yrPavaqmcQPOHJ.4Q3rfq5fOjaOB8T5jftcwIGQCrwfo32', '黄老板', '商家管理员'),
  (4, 'shuxiangyuan', '$2b$12$ey/D8p5yrPavaqmcQPOHJ.4Q3rfq5fOjaOB8T5jftcwIGQCrwfo32', '张老板', '商家管理员')
ON DUPLICATE KEY UPDATE username = VALUES(username);

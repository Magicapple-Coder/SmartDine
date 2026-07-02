-- 平台层表：商户信息 + 平台管理员
-- V2.0 新增，对应《系统设计说明书》4.3.1

CREATE TABLE merchant (
  merchant_id    BIGINT PRIMARY KEY AUTO_INCREMENT,
  name           VARCHAR(64) NOT NULL,
  logo           VARCHAR(255),
  category       VARCHAR(32),
  address        VARCHAR(255),
  location       POINT,                    -- 经纬度（LBS 附近商户查询）
  contact_name   VARCHAR(32),
  contact_phone  VARCHAR(20),
  business_hours VARCHAR(64),
  tables_count   INT NOT NULL DEFAULT 10,
  status         TINYINT NOT NULL DEFAULT 0,  -- 0待审核 1已开通 2已停用 3已注销
  created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  approved_at    DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE platform_admin (
  admin_id      BIGINT PRIMARY KEY AUTO_INCREMENT,
  username      VARCHAR(32) NOT NULL UNIQUE,
  password_hash VARCHAR(128) NOT NULL,
  name          VARCHAR(32),
  status        TINYINT NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- 初始化默认平台管理员（密码: admin123，上线后务必修改）
INSERT INTO platform_admin (username, password_hash, name) VALUES
  ('admin', '$2b$12$LJ3m4ys3LkBCVxJGqOjPkuYVOYpGOKbHgEMoJxYzRqcMdFNP2sCuW', '超级管理员');

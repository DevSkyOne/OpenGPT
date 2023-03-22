CREATE TABLE IF NOT EXISTS users
(
    user_id         VARCHAR(45) NOT NULL,
    credits         INTEGER     DEFAULT 100,
    model           VARCHAR(45) DEFAULT 'gpt-3.5-turbo',
    credits_spent   INTEGER     DEFAULT 0,
    prompt_amount   INTEGER     DEFAULT 0,
    last_used       DATETIME    DEFAULT CURRENT_TIMESTAMP,
    created         DATETIME    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY         KEY         (user_id)
) engine=InnoDB default charset=utf8mb4 collate=utf8mb4_unicode_ci comment 'users';

CREATE TABLE user_plans (
    id              INT         AUTO_INCREMENT,
    user_id         VARCHAR(45) NOT NULL,
    daily_credits   INT         DEFAULT 0,
    start_date      DATETIME    DEFAULT CURRENT_TIMESTAMP,
    end_date        DATETIME    DEFAULT (CURRENT_TIMESTAMP + INTERVAL 1 MONTH),
    PRIMARY         KEY         (id)
) engine=InnoDB default charset=utf8mb4 collate=utf8mb4_unicode_ci comment 'user_plans';
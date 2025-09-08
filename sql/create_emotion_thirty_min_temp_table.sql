CREATE TABLE IF NOT EXISTS `emotion_thirty_min_temp` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `character_id` varchar(64) NOT NULL,
  `event_id` varchar(64) NOT NULL,
  `event_type` varchar(50) NOT NULL,
  `processed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_character_event` (`character_id`,`event_id`),
  KEY `idx_processed_time` (`processed_at`),
  KEY `idx_character` (`character_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='情绪系统30分钟事件去重临时表';

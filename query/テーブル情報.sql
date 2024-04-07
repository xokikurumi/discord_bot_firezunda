CREATE TABLE `auto_send` (
  `guild_id` int NOT NULL,
  `channel_id` int NOT NULL,
  `url` text NOT NULL,
  `title` text NOT NULL,
  `mention` int DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='API/RSSëóêMèÓïÒ';

CREATE TABLE `auto_send_log` (
  `log_key_1` text,
  `log_key_2` text,
  `log_key_3` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='API/RSSëóêMÉçÉO';

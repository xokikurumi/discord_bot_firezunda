from sqlalchemy import text


async def run_schema_migrations(conn):
	"""Apply lightweight schema fixes needed by existing deployments."""
	# create_all() does not alter existing tables, so patch the small schema drift here.
	await _drop_unique_message_id_indexes(conn, "message_edit_log")
	await _drop_unique_message_id_indexes(conn, "message_delete_log")

	await _add_missing_columns(
		conn,
		"message_log",
		{
			"message_created_at": "DATETIME NULL",
			"has_stickers": "BOOLEAN NOT NULL DEFAULT FALSE",
			"stickers": "TEXT NULL",
		},
	)
	await _add_missing_columns(
		conn,
		"discord_user",
		{
			"guild_id": "BIGINT NOT NULL",
			"user_id": "BIGINT NOT NULL",
			"name": "VARCHAR(100) NULL",
			"display_name": "VARCHAR(100) NULL",
			"global_name": "VARCHAR(100) NULL",
			"discriminator": "VARCHAR(10) NULL",
			"bot_flg": "BOOLEAN NOT NULL DEFAULT FALSE",
			"avatar_url": "VARCHAR(500) NULL",
			"last_seen_at": "DATETIME NULL",
			"created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
		},
	)
	await _add_missing_columns(
		conn,
		"discord_channel",
		{
			"guild_id": "BIGINT NOT NULL",
			"channel_id": "BIGINT NOT NULL",
			"name": "VARCHAR(100) NULL",
			"channel_type": "VARCHAR(50) NULL",
			"category_id": "BIGINT NULL",
			"parent_channel_id": "BIGINT NULL",
			"position": "INT NULL",
			"last_seen_at": "DATETIME NULL",
			"created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
		},
	)
	await _add_missing_columns(
		conn,
		"message_edit_log",
		{
			"guild_id": "BIGINT NULL",
			"channel_id": "BIGINT NULL",
			"user_id": "BIGINT NULL",
		},
	)
	await _add_missing_columns(
		conn,
		"message_delete_log",
		{
			"guild_id": "BIGINT NULL",
			"channel_id": "BIGINT NULL",
			"user_id": "BIGINT NULL",
			"content": "TEXT NULL",
			"bot_flg": "BOOLEAN NULL",
			"has_attachments": "BOOLEAN NULL",
			"has_embeds": "BOOLEAN NULL",
		},
	)
	await _add_missing_columns(
		conn,
		"message_analysis_log",
		{
			"message_id": "BIGINT NOT NULL",
			"guild_id": "BIGINT NOT NULL",
			"channel_id": "BIGINT NOT NULL",
			"user_id": "BIGINT NOT NULL",
			"model": "VARCHAR(100) NOT NULL",
			"aggression": "INT NOT NULL DEFAULT 0",
			"intimidation": "INT NOT NULL DEFAULT 0",
			"insult": "INT NOT NULL DEFAULT 0",
			"sarcasm": "INT NOT NULL DEFAULT 0",
			"snide": "INT NOT NULL DEFAULT 0",
			"discomfort": "INT NOT NULL DEFAULT 0",
			"max_score": "INT NOT NULL DEFAULT 0",
			"targeted": "BOOLEAN NOT NULL DEFAULT TRUE",
			"confidence": "INT NOT NULL DEFAULT 100",
			"context_dependency": "BOOLEAN NOT NULL DEFAULT FALSE",
			"reason": "TEXT NULL",
			"raw_result": "TEXT NULL",
			"prompt_version": "VARCHAR(100) NULL",
			"prompt_hash": "VARCHAR(64) NULL",
			"retrieved_rag_cases": "TEXT NULL",
			"should_react": "BOOLEAN NOT NULL DEFAULT FALSE",
			"should_notify": "BOOLEAN NOT NULL DEFAULT FALSE",
			"created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
		},
	)
	await _add_missing_columns(
		conn,
		"message_analysis_feedback",
		{
			"message_id": "BIGINT NOT NULL",
			"guild_id": "BIGINT NOT NULL",
			"channel_id": "BIGINT NULL",
			"user_id": "BIGINT NULL",
			"reviewer_id": "BIGINT NOT NULL",
			"label": "VARCHAR(30) NOT NULL",
			"review_status": "VARCHAR(30) NOT NULL DEFAULT 'CONFIRMED'",
			"corrected_result_json": "TEXT NULL",
			"note": "TEXT NULL",
			"created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
		},
	)
	await _add_missing_columns(
		conn,
		"communication_trend_analysis",
		{
			"period_key": "VARCHAR(20) NOT NULL",
			"period_start": "DATETIME NOT NULL",
			"period_end": "DATETIME NOT NULL",
			"scope_type": "VARCHAR(20) NOT NULL",
			"guild_id": "BIGINT NOT NULL",
			"user_id": "BIGINT NULL",
			"model": "VARCHAR(100) NOT NULL",
			"message_count": "INT NOT NULL DEFAULT 0",
			"edit_count": "INT NOT NULL DEFAULT 0",
			"delete_count": "INT NOT NULL DEFAULT 0",
			"analysis_count": "INT NOT NULL DEFAULT 0",
			"max_score_avg": "INT NOT NULL DEFAULT 0",
			"metrics": "TEXT NULL",
			"summary": "TEXT NULL",
			"tendencies": "TEXT NULL",
			"risks": "TEXT NULL",
			"recommendations": "TEXT NULL",
			"raw_result": "TEXT NULL",
			"created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
		},
	)
	await _add_missing_columns(
		conn,
		"b_niconico_video_send_log",
		{
			"pub_date": "VARCHAR(100) NULL",
			"send_flg": "BOOLEAN NOT NULL DEFAULT FALSE",
			"delete_flg": "BOOLEAN NOT NULL DEFAULT FALSE",
			"created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
		},
	)
	await _add_missing_columns(
		conn,
		"b_m_niconico_video_infomation",
		{
			"delete_flg": "BOOLEAN NOT NULL DEFAULT FALSE",
		},
	)
	await _add_missing_columns(
		conn,
		"b_niconico_notify_cannel_config",
		{
			"enabled": "BOOLEAN NOT NULL DEFAULT TRUE",
			"mention": "TEXT NULL",
		},
	)
	await _add_missing_columns(
		conn,
		"niconico_info_event",
		{
			"source_key": "VARCHAR(255) NOT NULL",
			"title": "TEXT NOT NULL",
			"start_date": "DATE NULL",
			"end_date": "DATE NULL",
			"date_text": "TEXT NULL",
			"explanation": "TEXT NULL",
			"link": "TEXT NULL",
			"organizer_user": "TEXT NULL",
			"organizer_link": "TEXT NULL",
			"categories": "TEXT NULL",
			"source_url": "TEXT NULL",
			"send_flg": "BOOLEAN NOT NULL DEFAULT FALSE",
			"delete_flg": "BOOLEAN NOT NULL DEFAULT FALSE",
			"created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
		},
	)
	await _add_missing_columns(
		conn,
		"niconico_info_filter",
		{
			"guild_id": "BIGINT NOT NULL",
			"mode": "VARCHAR(20) NOT NULL DEFAULT 'include'",
			"keyword": "TEXT NOT NULL",
			"enabled": "BOOLEAN NOT NULL DEFAULT TRUE",
			"delete_flg": "BOOLEAN NOT NULL DEFAULT FALSE",
			"created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
		},
	)
	await _ensure_ics_guild_event_import_unique(conn)
	await _ensure_niconico_info_event_unique(conn)
	await _ensure_message_analysis_log_unique(conn)
	await _ensure_discord_user_unique(conn)
	await _ensure_discord_channel_unique(conn)


async def _drop_unique_message_id_indexes(conn, table_name):
	"""Drop legacy unique indexes on message_id for history tables."""
	# Edit/delete logs are event histories, so message_id must allow multiple rows.
	indexes = await conn.execute(
		text(
			"""
			SELECT INDEX_NAME
			FROM INFORMATION_SCHEMA.STATISTICS
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = :table_name
			  AND COLUMN_NAME = 'message_id'
			  AND NON_UNIQUE = 0
			  AND INDEX_NAME <> 'PRIMARY'
			"""
		),
		{"table_name": table_name},
	)

	for index_name in indexes.scalars().all():
		await conn.execute(text(f"ALTER TABLE `{table_name}` DROP INDEX `{index_name}`"))


async def _add_missing_columns(conn, table_name, columns):
	"""Add missing columns to a table if they are not already present."""
	# Add columns idempotently so startup is safe across fresh and existing databases.
	tables = await conn.execute(
		text(
			"""
			SELECT TABLE_NAME
			FROM INFORMATION_SCHEMA.TABLES
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = :table_name
			"""
		),
		{"table_name": table_name},
	)
	if tables.scalar_one_or_none() is None:
		return

	existing_columns = await conn.execute(
		text(
			"""
			SELECT COLUMN_NAME
			FROM INFORMATION_SCHEMA.COLUMNS
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = :table_name
			"""
		),
		{"table_name": table_name},
	)
	existing_column_names = set(existing_columns.scalars().all())

	for column_name, column_type in columns.items():
		if column_name not in existing_column_names:
			await conn.execute(
				text(f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {column_type}")
			)


async def _ensure_ics_guild_event_import_unique(conn):
	"""Create the ICS import duplicate-prevention index when the table exists."""
	tables = await conn.execute(
		text(
			"""
			SELECT TABLE_NAME
			FROM INFORMATION_SCHEMA.TABLES
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = 'ics_guild_event_import'
			"""
		)
	)
	if tables.scalar_one_or_none() is None:
		return

	indexes = await conn.execute(
		text(
			"""
			SELECT INDEX_NAME
			FROM INFORMATION_SCHEMA.STATISTICS
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = 'ics_guild_event_import'
			  AND INDEX_NAME = 'uq_ics_guild_event_import_guild_uid'
			"""
		)
	)
	if indexes.first() is None:
		await conn.execute(
			text(
				"ALTER TABLE `ics_guild_event_import` "
				"ADD UNIQUE INDEX `uq_ics_guild_event_import_guild_uid` (`guild_id`, `ics_uid`)"
			)
		)


async def _ensure_niconico_info_event_unique(conn):
	"""Create the Niconico info duplicate-prevention index when the table exists."""
	tables = await conn.execute(
		text(
			"""
			SELECT TABLE_NAME
			FROM INFORMATION_SCHEMA.TABLES
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = 'niconico_info_event'
			"""
		)
	)
	if tables.scalar_one_or_none() is None:
		return

	indexes = await conn.execute(
		text(
			"""
			SELECT INDEX_NAME
			FROM INFORMATION_SCHEMA.STATISTICS
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = 'niconico_info_event'
			  AND COLUMN_NAME = 'source_key'
			  AND NON_UNIQUE = 0
			"""
		)
	)
	if indexes.first() is None:
		await conn.execute(
			text(
				"ALTER TABLE `niconico_info_event` "
				"ADD UNIQUE INDEX `uq_niconico_info_event_source_key` (`source_key`)"
			)
		)


async def _ensure_message_analysis_log_unique(conn):
	"""Create the analysis duplicate-prevention index when the table exists."""
	tables = await conn.execute(
		text(
			"""
			SELECT TABLE_NAME
			FROM INFORMATION_SCHEMA.TABLES
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = 'message_analysis_log'
			"""
		)
	)
	if tables.scalar_one_or_none() is None:
		return

	indexes = await conn.execute(
		text(
			"""
			SELECT INDEX_NAME
			FROM INFORMATION_SCHEMA.STATISTICS
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = 'message_analysis_log'
			  AND COLUMN_NAME = 'message_id'
			  AND NON_UNIQUE = 0
			"""
		)
	)
	if indexes.first() is None:
		await conn.execute(
			text(
				"ALTER TABLE `message_analysis_log` "
				"ADD UNIQUE INDEX `uq_message_analysis_log_message_id` (`message_id`)"
			)
		)
async def _ensure_discord_user_unique(conn):
	"""Create the Discord user duplicate-prevention index when the table exists."""
	tables = await conn.execute(
		text(
			"""
			SELECT TABLE_NAME
			FROM INFORMATION_SCHEMA.TABLES
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = 'discord_user'
			"""
		)
	)
	if tables.scalar_one_or_none() is None:
		return

	indexes = await conn.execute(
		text(
			"""
			SELECT INDEX_NAME
			FROM INFORMATION_SCHEMA.STATISTICS
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = 'discord_user'
			  AND INDEX_NAME = 'uq_discord_user_guild_user'
			"""
		)
	)
	if indexes.first() is None:
		await conn.execute(
			text(
				"ALTER TABLE `discord_user` "
				"ADD UNIQUE INDEX `uq_discord_user_guild_user` (`guild_id`, `user_id`)"
			)
		)


async def _ensure_discord_channel_unique(conn):
	"""Create the Discord channel duplicate-prevention index when the table exists."""
	tables = await conn.execute(
		text(
			"""
			SELECT TABLE_NAME
			FROM INFORMATION_SCHEMA.TABLES
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = 'discord_channel'
			"""
		)
	)
	if tables.scalar_one_or_none() is None:
		return

	indexes = await conn.execute(
		text(
			"""
			SELECT INDEX_NAME
			FROM INFORMATION_SCHEMA.STATISTICS
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = 'discord_channel'
			  AND INDEX_NAME = 'uq_discord_channel_guild_channel'
			"""
		)
	)
	if indexes.first() is None:
		await conn.execute(
			text(
				"ALTER TABLE `discord_channel` "
				"ADD UNIQUE INDEX `uq_discord_channel_guild_channel` (`guild_id`, `channel_id`)"
			)
		)

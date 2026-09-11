# discord_bot_v3

Discord bot for server logging, notification settings, earthquake information, ICS scheduled event imports, message reactions, and Niconico notifications.

## Features

- Message create/edit/delete logging
- Ollama message analysis logging
- Semiannual communication trend analysis
- Voice channel status logging
- Reaction keyword automation
- Dice rolling
- P2PQuake notification delivery
- ICS calendar import into Discord scheduled events
- Niconico user upload notifications
- Niconico Info / niconews category notifications
- Prefix commands and slash commands via `discord.py` hybrid commands

## Requirements

- Python 3.10 or later
- MySQL
- Discord bot token

Install the main Python packages:

```bash
pip install discord.py sqlalchemy aiomysql aiohttp beautifulsoup4 d20
```

## Configuration

Settings are defined in `config.py`.

Important values:

- `TOKEN`: Discord bot token
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`: MySQL connection settings
- `SLASH_COMMAND_SYNC_TO_GUILDS`: Sync slash commands to joined guilds on startup for faster reflection, default `true`
- `OLLAMA_ANALYSIS_ENABLED`: Enable Ollama message analysis
- `OLLAMA_MODEL`: Ollama model used for message analysis
- `COMMUNICATION_TREND_ANALYSIS_ENABLED`: Enable semiannual communication trend analysis, default `true`
- `COMMUNICATION_TREND_GUILD_ANALYSIS_ENABLED`: Also create guild-level trend reports, default `false`
- `COMMUNICATION_TREND_CHECK_INTERVAL_SECONDS`: Check interval for semiannual trend analysis, default `86400`
- `COMMUNICATION_TREND_MIN_USER_MESSAGES`: Minimum half-year user messages required for user-level analysis, default `1`
- `COMMUNICATION_TREND_SAMPLE_LIMIT`: Number of recent sample messages included in each trend analysis prompt, default `30`
- `COMMUNICATION_TREND_NUM_PREDICT`: Ollama generation limit for trend reports, default `2048`
- `P2PQUAKE_ENABLED`: Enable P2PQuake WebSocket notifications
- `P2PQUAKE_MIN_NOTIFY_SCALE`: Minimum P2PQuake earthquake intensity code to notify, default `40` (震度4)
- `GSI_TILE_CACHE_DIR`: Local cache directory for GSI map tiles, default `cache/gsi_tiles`
- `ICS_GUILD_EVENT_ENABLED`: Enable ICS scheduled event imports
- `NICONICO_USER_VIDEO_ENABLED`: Enable Niconico user upload notifications
- Niconico user upload notifications run at `n:00` / `n:15` / `n:30` / `n:45`.
- `NICONICO_INFO_ENABLED`: Enable Niconico Info notifications
- `NICONICO_INFO_CHECK_INTERVAL_SECONDS`: Niconico Info check interval, default `3600`
- `NICONICO_INFO_TARGET_URLS`: Comma-separated Niconico Info category URLs

For GitLab CI/CD or production deployment, set secrets and environment-specific values with CI/CD Variables or server environment variables instead of committing them to the repository.

Minimum required variables for runtime:

- `DISCORD_TOKEN`: Discord bot token
- `DB_USER`: MySQL user
- `DB_PASSWORD`: MySQL password
- `DB_HOST`: MySQL host
- `DB_PORT`: MySQL port
- `DB_NAME`: MySQL database name

Additional variable for tag deployments:

- `DEPLOY_DIR`: Base directory where release tag contents are copied. Tagged pipelines deploy to `DEPLOY_DIR/<tag>`.

Set `DEPLOY_DIR` in GitLab `Settings > CI/CD > Variables`. Use an absolute path, for example `/opt/discord/releases`. If the variable is marked `Protected`, make sure the release tag is also protected or GitLab will not expose the variable to the job.

The GitLab pipeline is intended to run on a Shell executor runner tagged `shell`. Register a Shell runner with that tag when copying releases directly to a host directory. If the job runs on a Docker executor, it fails before copying because Docker writes to the container filesystem unless the host deploy directory is mounted. The release copy job uses the checked-out tag workspace and excludes `.git`, virtualenv, cache, and runtime file directories.

Current default Niconico Info URLs:

```text
https://blog.nicovideo.jp/niconews/category/ge_maintenance
https://blog.nicovideo.jp/niconews/category/ge_user/
```

## Message Analysis Evaluation

Confirmed administrator feedback can be used as an evaluation set for the current Ollama message analysis prompt and feedback RAG behavior.

```bash
python scripts/evaluate_message_analysis_feedback.py --limit 50
```

By default, exact-text feedback reuse is disabled during evaluation so the script does not trivially return the known correction for the same message. Feedback RAG remains enabled, but the current evaluation case is excluded from retrieved examples.

Useful options:

```bash
python scripts/evaluate_message_analysis_feedback.py --guild-id 123456789 --limit 100 --json
python scripts/evaluate_message_analysis_feedback.py --limit 50 --no-rag
python scripts/evaluate_message_analysis_feedback.py --limit 50 --dry-run
```

Feedback RAG can optionally use Ollama embeddings. Enable it after installing an embedding model such as `nomic-embed-text`.

```env
OLLAMA_ANALYSIS_FEEDBACK_EMBEDDING_RAG_ENABLED=true
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
```

Create embeddings for existing confirmed feedback rows before enabling or evaluating embedding RAG:

```bash
python scripts/backfill_message_analysis_feedback_embeddings.py --limit 0
```

Use `--force` when rebuilding embeddings after changing the embedding model or embedding text format.

## Start

```bash
python main.py
```

On startup, the bot creates missing tables, applies lightweight schema migrations, registers Cogs, and syncs slash commands once.

## systemd

CentOS などで systemd サービスとして起動する場合は、[deploy/systemd/README.md](deploy/systemd/README.md) を参照してください。

## Notification Settings

Notification channels are configured with `notify_config`.

Examples:

```text
!notify_config add #channel none NICONICO_INFO
!notify_config add #channel everyone QUAKE
!notify_config list
!notify_config category list
!notify_config enable <id>
!notify_config disable <id>
```

The same commands are also available as slash commands:

```text
/notify_config add
/notify_config list
/notify_config category list
/notify_config enable
/notify_config disable
```

Common categories:

- `QUAKE`: Earthquake/P2PQuake notifications
- `SALES_EVENT`: ICS scheduled event import notifications
- `NICONICO_INFO`: Niconico Info / niconews notifications

Niconico user upload notifications use per-user notification settings:

```text
!niconico_user_video_notify add <user_id> #channel none
!niconico_user_video_notify list
!niconico_user_video_notify enable <id>
!niconico_user_video_notify disable <id>
```

## Command Usage

Most commands are hybrid commands, so they can be used with either the `!` prefix or as slash commands.

Example:

```text
!roll 1d20+5
/roll expression: 1d20+5
```

Commands marked `Admin` require administrator permission.

### Message Logs

`backfill_message_logs` imports historical messages from all readable text channels in the current server into `message_log`.

```text
!backfill_message_logs [limit]
/backfill_message_logs limit:<count>
```

- Permission: Admin
- `limit`: Optional number of messages to read per channel. Use `0` or omit it to import all available history.

Examples:

```text
!backfill_message_logs 1000
/backfill_message_logs limit:1000
```

### Communication Trend Analysis

`communication_trend_analyze` manually analyzes the latest completed scheduled period for the current server.
The background task checks once per day and runs only on January 1 and June 1 in JST.
Trend analysis results are stored internally and are not posted to chat.

```text
!communication_trend_analyze
/communication_trend_analyze
```

- Permission: Admin
- Uses `message_log`, `message_delete_log`, `message_edit_log`, and `message_analysis_log`
- Stores user-level reports in `communication_trend_analysis`
- If the same user is active in multiple servers, a separate report is created for each `guild_id` and `user_id` pair
- Guild-level reports are created only when `COMMUNICATION_TREND_GUILD_ANALYSIS_ENABLED=true`
- User-level reports are created only when the user has at least `COMMUNICATION_TREND_MIN_USER_MESSAGES` messages in the period
- January 1 analyzes the period from June 1 of the previous year to January 1.
- June 1 analyzes the period from January 1 to June 1 of the same year.

### Dice Rolls

`roll` rolls a dice expression with the `d20` parser. Messages that consist only of a dice expression are also rolled automatically.

```text
<dice_expression>
!roll <dice_expression>
/roll expression:<dice_expression>
```

Examples:

```text
1d100
2d6+3
!roll 1d20+5
/roll expression:1d20+5
```

### Reaction Keywords

`reaction` manages automatic reactions for messages that contain registered keywords.

```text
!reaction add <keyword> <reaction> [ng_word]
/reaction add keyword:<keyword> reaction:<reaction> ng_word:<true|false>

!reaction remove <keyword>
/reaction remove keyword:<keyword>

!reaction list
/reaction list

!reaction check_emoji <emoji>
/reaction check_emoji emoji:<emoji>

!reaction seed_syukka
/reaction seed_syukka
```

- `add`: Admin. Registers a keyword and the emoji to add when it appears.
- `remove`: Admin. Soft-deletes keyword rules matching the keyword.
- `list`: Shows rules registered for the current server.
- `check_emoji`: Checks whether the bot can see and use a custom emoji.
- `seed_syukka`: Admin. Registers the legacy syukka reaction preset from `discord_bot_firezunda_v2`.
- `ng_word`: Optional. When true, matching this keyword suppresses automatic reactions.

Examples:

```text
!reaction add こんにちは 👋 false
!reaction add NGワード ✖ true
!reaction check_emoji <:name:123456789012345678>
!reaction seed_syukka
```

### Notification Settings

`notify_config` manages general notification destinations by category.

```text
!notify_config add [#channel] [mention] [category]
/notify_config add channel:<channel> mention:<mention> category:<category>

!notify_config list
/notify_config list

!notify_config category list
/notify_config category list

!notify_config enable <id>
/notify_config enable config_id:<id>

!notify_config disable <id>
/notify_config disable config_id:<id>
```

- `add`: Admin. Adds a notification destination for a category.
- `list`: Shows notification settings for the current server.
- `category list`: Shows available categories.
- `enable`: Admin. Enables one notification setting.
- `disable`: Admin. Disables one notification setting.
- `channel`: Optional. Defaults to the channel where the command is run.
- `mention`: Optional. Use `none` for no mention, `everyone`, `here`, a role id, or a mention string.
- `category`: Optional. Defaults to `QUAKE`.

Common categories:

- `QUAKE`: Earthquake/P2PQuake notifications
- `SALES_EVENT`: ICS scheduled event import notifications
- `NICONICO_INFO`: Niconico Info / niconews notifications
- `NICONICO_USER_VIDEO`: Listed for reference; user upload notifications normally use `niconico_user_video_notify`.

Examples:

```text
!notify_config add #earthquake everyone QUAKE
!notify_config add #nico-info none NICONICO_INFO
!notify_config category list
```

### ICS Scheduled Events

ICS commands manage calendar imports into Discord scheduled events for the current server.

```text
!ics_event_enable
/ics_event_enable

!ics_event_disable
/ics_event_disable

!ics_event_status
/ics_event_status

!ics_event_sync
/ics_event_sync
```

- Permission: Admin
- `ics_event_enable`: Enables periodic ICS import for this server.
- `ics_event_disable`: Disables periodic ICS import for this server.
- `ics_event_status`: Shows whether ICS import is enabled.
- `ics_event_sync`: Runs an import manually. The server must be enabled first.

### Niconico User Uploads

Niconico user upload commands manage monitored Niconico users and per-user notification destinations.
The latest uploaded video is fetched from `https://nvapi.nicovideo.jp/v2/users/{user_id}/videos`.
Short videos are also checked from `https://www.nicovideo.jp/user/{user_id}/shorts`.
Notification post times are shown in Japan time as `yyyy/mm/dd hh:mm:ss`.

```text
!niconico_user_video_check
/niconico_user_video_check
```

- Permission: Admin
- Manually checks monitored users for uploaded videos and sends unsent notifications.

```text
!niconico_user_video_user add <user_id>
/niconico_user_video_user add user_id:<user_id>

!niconico_user_video_user list
/niconico_user_video_user list

!niconico_user_video_user remove <id>
/niconico_user_video_user remove row_id:<id>
```

- Permission: Admin
- `add`: Adds a Niconico user id to the monitored list.
- `list`: Shows monitored Niconico user ids.
- `remove`: Disables a monitored user row by database id.

```text
!niconico_user_video_notify add <user_id> [#channel] [mention]
/niconico_user_video_notify add user_id:<user_id> channel:<channel> mention:<mention>

!niconico_user_video_notify list
/niconico_user_video_notify list

!niconico_user_video_notify enable <id>
/niconico_user_video_notify enable config_id:<id>

!niconico_user_video_notify disable <id>
/niconico_user_video_notify disable config_id:<id>
```

- Permission: Admin
- `add`: Adds a notification destination for one Niconico user.
- `list`: Shows per-user notification settings for this server.
- `enable`: Enables one notification setting.
- `disable`: Disables one notification setting.
- `channel`: Optional. Defaults to the command channel.
- `mention`: Optional. Use `none` for no mention.

Examples:

```text
!niconico_user_video_user add 141907929
!niconico_user_video_notify add 141907929 #nico-upload none
!niconico_user_video_check
```

### Niconico Info

Niconico Info commands manually run niconews checks and manage optional filters.

```text
!niconico_info_check
/niconico_info_check
```

- Permission: Admin
- Fetches configured Niconico Info pages and sends unsent notifications.
- Notifications show an about-500-character summary below the article link.

```text
!niconico_info_filter add <keyword> [include|exclude]
/niconico_info_filter add keyword:<keyword> mode:<include|exclude>

!niconico_info_filter list
/niconico_info_filter list

!niconico_info_filter enable <id>
/niconico_info_filter enable filter_id:<id>

!niconico_info_filter disable <id>
/niconico_info_filter disable filter_id:<id>

!niconico_info_filter remove <id>
/niconico_info_filter remove filter_id:<id>
```

- Permission: Admin
- `add`: Adds a keyword filter. Mode defaults to `include`.
- `list`: Shows filters for the current server.
- `enable`: Enables one filter.
- `disable`: Disables one filter.
- `remove`: Soft-deletes one filter.

Filter behavior:

- No filters: notify all Niconico Info items.
- `include`: notify only items containing at least one enabled include keyword.
- `exclude`: do not notify items containing an enabled exclude keyword.
- Exclude filters take priority over include filters.

Examples:

```text
!niconico_info_filter add メンテナンス include
!niconico_info_filter add 復旧 exclude
```

## Duplicate Prevention

Ollama message analysis results are stored in `message_analysis_log`.

- One row is stored per Discord `message_id`
- Scores are stored for `aggression`, `intimidation`, `insult`, `sarcasm`, `snide`, and `discomfort`
- `max_score`, `reason`, `raw_result`, `should_react`, and `should_notify` are also stored

Semiannual communication trend reports are stored in `communication_trend_analysis`.

- `scope_type = user`: report for one user within one Discord server
- `scope_type = guild`: report for an entire Discord server, only when enabled
- `period_key` uses values such as `2026-H1` and `2026-H2`
- Metrics and Ollama report text are stored together for later review

Niconico Info notifications are stored in `niconico_info_event`.

- Newly discovered articles are saved with `send_flg = False`
- Successfully notified rows are updated to `send_flg = True`
- Existing `source_key` values are not inserted again
- Failed sends remain unsent and are retried on later checks

Niconico user upload notifications use `b_niconico_video_send_log` in the same style.

## Notes

- Keep production tokens and database passwords out of committed source when possible.
- Slash command visibility can take time to update globally after sync.
- If Niconico Info page structure changes, update `NICONICO_INFO_TARGET_URLS` or the parser in `services/task/niconico_info_service.py`.

HELLO = "hello"
PONG = "pong"
MESSAGE = "message"
USER_TYPING = "user_typing"
CHANNEL_MARKED = "channel_marked"
CHANNEL_CREATED = "channel_created"
CHANNEL_JOINED = "channel_joined"
CHANNEL_LEFT = "channel_left"
CHANNEL_DELETED = "channel_deleted"
CHANNEL_RENAME = "channel_rename"
CHANNEL_ARCHIVE = "channel_archive"
CHANNEL_UNARCHIVE = "channel_unarchive"
CHANNEL_HISTORY_CHANGED = "channel_history_changed"
CHANNEL = frozenset([CHANNEL_MARKED, CHANNEL_CREATED, CHANNEL_JOINED,
                     CHANNEL_LEFT, CHANNEL_DELETED, CHANNEL_RENAME,
                     CHANNEL_ARCHIVE, CHANNEL_UNARCHIVE,
                     CHANNEL_HISTORY_CHANGED])
IM_CREATED = "im_created"
IM_OPEN = "im_open"
IM_CLOSE = "im_close"
IM_MARKED = "im_marked"
IM_HISTORY_CHANGED = "im_history_changed"
IM = frozenset([IM_CREATED, IM_OPEN, IM_CLOSE, IM_MARKED,
                IM_HISTORY_CHANGED])
GROUP_JOINED = "group_joined"
GROUP_LEFT = "group_left"
GROUP_OPEN = "group_open"
GROUP_CLOSE = "group_close"
GROUP_ARCHIVE = "group_archive"
GROUP_UNARCHIVE = "group_unarchive"
GROUP_RENAME = "group_rename"
GROUP_MARKED = "group_marked"
GROUP_HISTORY_CHANGED = "group_history_changed"
GROUP = frozenset([GROUP_JOINED, GROUP_LEFT, GROUP_OPEN, GROUP_CLOSE,
                   GROUP_ARCHIVE, GROUP_UNARCHIVE, GROUP_RENAME, GROUP_MARKED,
                   GROUP_HISTORY_CHANGED])
FILE_CREATED = "file_created"
FILE_SHARED = "file_shared"
FILE_UNSHARED = "file_unshared"
FILE_PUBLIC = "file_public"
FILE_PRIVATE = "file_private"
FILE_CHANGED = "file_changed"
FILE_DELETED = "file_deleted"
FILE_COMMENT_ADDED = "file_comment_added"
FILE_COMMENT_EDITED = "file_comment_edited"
FILE_COMMENT_DELETED = "file_comment_deleted"
FILE = frozenset([FILE_CREATED, FILE_SHARED, FILE_UNSHARED, FILE_PUBLIC,
                  FILE_PRIVATE, FILE_CHANGED, FILE_DELETED, FILE_COMMENT_ADDED,
                  FILE_COMMENT_EDITED, FILE_COMMENT_DELETED])
PIN_ADDED = "pin_added"
PIN_REMOVED = "pin_removed"
PIN = frozenset([PIN_ADDED, PIN_REMOVED])
PRESENCE_CHANGE = "presence_change"
MANUAL_PRESENCE_CHANGE = "manual_presence_change"
PREF_CHANGE = "pref_change"
USER_CHANGE = "user_change"
TEAM_JOIN = "team_join"
USER = frozenset([USER_CHANGE, TEAM_JOIN])
STAR_ADDED = "star_added"
STAR_REMOVED = "star_removed"
REACTION_ADDED = "reaction_added"
REACTION_REMOVED = "reaction_removed"
EMOJI_CHANGED = "emoji_changed"
COMMANDS_CHANGED = "commands_changed"
TEAM_PLAN_CHANGE = "team_plan_change"
TEAM_PREF_CHANGE = "team_pref_change"
TEAM_RENAME = "team_rename"
TEAM_DOMAIN_CHANGE = "team_domain_change"
EMAIL_DOMAIN_CHANGED = "email_domain_changed"
BOT_ADDED = "bot_added"
BOT_CHANGED = "bot_changed"
ACCOUNTS_CHANGED = "accounts_changed"
TEAM_MIGRATION_STARTED = "team_migration_started"
RECONNECT_URL = "reconnect_url"
SUBTEAM_CREATED = "subteam_created"
SUBTEAM_UPDATED = "subteam_updated"
SUBTEAM_SELF_ADDED = "subteam_self_added"
SUBTEAM_SELF_REMOVED = "subteam_self_removed"

# Internal Events
SETUP = "_setup"
TASK = "_task"
TEARDOWN = "_teardown"

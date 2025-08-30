USER_CREATE_CHANNEL_NAME = "user_create_changes"

USER_CREATE_NOTIFY_FUNCTION = f"""
CREATE OR REPLACE FUNCTION notify_user_create() RETURNS trigger AS $$
BEGIN
  IF (TG_OP = 'DELETE') THEN
    PERFORM pg_notify('{USER_CREATE_CHANNEL_NAME}', TG_OP || ':' || OLD.id::text);
    RETURN OLD;
  ELSE
    PERFORM pg_notify('{USER_CREATE_CHANNEL_NAME}', TG_OP || ':' || NEW.id::text);
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;

"""

USER_CREATE_DROP_TRIGGER = """
DROP TRIGGER IF EXISTS user_create_notify_trigger ON users;
"""


USER_CREATE_CREATE_TRIGGER = """
CREATE TRIGGER user_create_notify_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION notify_user_create();
"""

from utils.environment import APP_ENVIRONMENT


REQUEST_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
DOCS_URL = "" if APP_ENVIRONMENT.upper() in ["PRODUCTION", "PROD"] else "/openapi.json"
DATABASE_LOG_LEVEL = "WARNING" if APP_ENVIRONMENT.upper() in ["PRODUCTION", "PROD"] else "DEBUG"


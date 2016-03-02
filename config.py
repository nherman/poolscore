import os

class Config(object):
    # Statement for enabling the development environment
    DEBUG = False
    TESTING = False

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    DATABASE_NAME = 'app.db'
    SQLITE_DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_NAME)

    # Define the database - we are working with
    # SQLite for this example
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLITE_DATABASE_PATH
    #DATABASE = 'sqlite:///' + SQLITE_DATABASE_PATH
    DATABASE = os.path.join(BASE_DIR, '/tmp/poolscore.db')

    # Enable query monitoring
    # SQLALCHEMY_ECHO = True

    # The size of the database pool. Defaults to the engine's default (usually 5)
    # SQLALCHEMY_POOL_SIZE = 5

    # Specifies the connection timeout for the pool. Defaults to 10.
    # SQLALCHEMY_POOL_TIMEOUT = 10
    
    # Number of seconds after which a connection is automatically recycled. 
    # This is required for MySQL, which removes connections after 8 hours idle by default. 
    # Note that Flask-SQLAlchemy automatically sets this to 2 hours if MySQL is used.
    # SQLALCHEMY_POOL_RECYCLE = 3600
    
    # Controls the number of connections that can be created after the pool 
    # reached its maximum size. When those additional connections are 
    # returned to the pool, they are disconnected and discarded.
    # SQLALCHEMY_MAX_OVERFLOW = 10

    DATABASE_CONNECT_OPTIONS = {}

    # Application threads. A common general assumption is
    # using 2 per available processor cores - to handle
    # incoming requests using one and performing background
    # operations using the other.
    THREADS_PER_PAGE = 2

    # Enable protection against *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True

    # Use a secure, unique and absolutely secret key for signing the data. 
    CSRF_SESSION_KEY = "secret"

    # Secret key for signing cookies
    SECRET_KEY = "secret"

    # Session cookie name
    SESSION_COOKIE_NAME = "_poolscore_session_v1"
    PERMANENT_SESSION_LIFETIME = 86400 * 30

    DEFAULT_USER_TIMEZONE = 'US/Eastern'
    LOCALIZE_DATETIME_TO_USER_TIMEZONE = False

    PAGER_DEFAULT_ORDER_BY_FIELD = "date_created"
    PAGER_DEFAULT_PAGE = 1
    PAGER_DEFAULT_LIMIT = 50
    PAGER_DEFAULT_LIMIT_MAX = 150

    FORCE_SQLALCHEMY_CREATE_TABLES = False

    RESERVED_USERNAMES = (
        "about", "access", "account", "accounts", "add", "address", "adm", "adult", "administration", # "admin",
        "advertising", "affiliate", "affiliates", "ajax", "analytics", "android", "anon", "anonymous",
        "api", "app", "apps", "archive", "atom", "auth", "authentication", "avatar",
        "backup", "banner", "banners", "bin", "billing", "blog", "blogs", "board", "bot", "bots", "business"
        "chat", "cache", "cadastro", "calendar", "campaign", "careers", "cgi", "client", "cliente", "code", "comercial",
        "compare", "config", "connect", "contact", "contest", "create", "code", "compras", "css",
        "dashboard", "data", "db", "design", "delete", "demo", "design", "designer", "dev", "devel", "dir",
        "directory", "doc", "docs", "domain", "download", "downloads",
        "edit", "editor", "email", "ecommerce",
        "forum", "forums", "faq", "favorite", "feed", "feedback", "flog", "follow", "file", "files", "free", "ftp",
        "gadget", "gadgets", "games", "guest", "group", "groups",
        "help", "home", "homepage", "host", "hosting", "hostname", "html", "http", "httpd", "https", "hpg",
        "info", "information", "image", "img", "images", "imap", "index", "invite", "intranet", "indice",
        "ipad", "iphone", "irc",
        "java", "javascript", "job", "jobs", "js",
        "log", "login", "logs", "logout", "list", "lists",
        "mail", "mail1", "mail2", "mail3", "mail4", "mail5", "mailer", "mailing", "mx", "manager", "marketing",
        "master", "me", "media", "message", "microblog", "microblogs", "mine", "mp3", "msg", "msn", "mysql",
        "messenger", "mob", "mobile", "movie", "movies", "music", "musicas", "my",
        "name", "named", "net", "network", "new", "news", "newsletter", "nickname", "notes", "noticias",
        "ns", "ns1", "ns2", "ns3", "ns4",
        "old", "online", "operator", "order", "orders",
        "page", "pager", "pages", "panel", "password", "perl", "pic", "pics", "photo", "photos", "photoalbum",
        "php", "plugin", "plugins", "pop", "pop3", "post", "postmaster",
        "postfix", "posts", "profile", "project", "projects", "promo", "pub", "public", "python",
        "random", "register", "registration", "root", "ruby", "rss",
        "sale", "sales", "sample", "samples", "script", "scripts", "secure", "send", "service", "shop",
        "sql", "signup", "signin", "search", "security", "settings", "setting", "setup", "site",
        "sites", "sitemap", "smtp", "soporte", "ssh", "stage", "staging", "start", "subscribe",
        "subdomain", "suporte", "support", "stat", "static", "stats", "status", "store", "stores", # "system",
        "tablet", "tablets", "tech", "telnet", "test", "test1", "test2", "test3", "teste", "tests", "theme",
        "themes", "tmp", "todo", "task", "tasks", "tools", "tv", "talk",
        "update", "upload", "url", "user", "username", "usuario", "usage",
        "vendas", "video", "videos", "visitor",
        "win", "ww", "www", "www1", "www2", "www3", "www4", "www5", "www6", "www7", "wwww", "wws", "wwws", "web", "webmail",
        "website", "websites", "webmaster", "workshop",
        "xxx", "xpg",
        "you", "yourname", "yourusername", "yoursite", "yourdomain",)

class DevConfig(Config):
    DEBUG = True
    FORCE_SQLALCHEMY_CREATE_TABLES = True

class TestConfig(Config):
    TESTING = True
    DEBUG = True
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
    # Database is created inside of the unittest class setUpClass call.
    FORCE_SQLALCHEMY_CREATE_TABLES = False

    # SQLite tests
    # DATABASE_NAME = 'app-test.db'
    # SQLITE_DATABASE_PATH = os.path.join(Config.BASE_DIR, DATABASE_NAME)
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLITE_DATABASE_PATH

    # MySql tests (create empty db before running tests)
    DATABASE_NAME = ''
    SQLALCHEMY_POOL_SIZE = 1
    SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/' + DATABASE_NAME
    # DATABASE_CONNECT_OPTIONS = {'isolation_level': 'READ UNCOMMITTED'}

    RESERVED_USERNAMES = ("reserved", "test.reserved",)

class StageConfig(Config):
    DATABASE_NAME = ''
    SQLALCHEMY_DATABASE_URI = 'mysql://username:password@dbrw/' + DATABASE_NAME
    DATABASE_CONNECT_OPTIONS = {}

class ProdConfig(Config):
    DATABASE_NAME = ''
    SQLALCHEMY_DATABASE_URI = 'mysql://username:password/' + DATABASE_NAME
    DATABASE_CONNECT_OPTIONS = {}
    CSRF_SESSION_KEY = ''
    SECRET_KEY = ''
    SESSION_COOKIE_NAME = ""

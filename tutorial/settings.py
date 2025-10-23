# Scrapy settings for tutorial project

BOT_NAME = 'tutorial'

SPIDER_MODULES = ['tutorial.spiders']
NEWSPIDER_MODULE = 'tutorial.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure delays for requests
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# Configure user agent
USER_AGENT = 'tutorial (+http://www.yourdomain.com)'

# Configure pipelines
ITEM_PIPELINES = {
    'tutorial.pipelines.PostgresNoDuplicatesPipeline': 300,
}

# Enable autothrottling
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Logging
LOG_LEVEL = 'INFO'
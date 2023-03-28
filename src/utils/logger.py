import discord
import logging
import logging.handlers
import config

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)

class StreamFormatter(logging.Formatter):
    LEVEL_COLOURS = [
        (logging.DEBUG, '\x1b[40;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31m'),
        (logging.CRITICAL, '\x1b[41m'),
    ]

    FORMATS = {
        level: logging.Formatter(
            f'\x1b[30;1m%(asctime)s \x1b[0m{colour}%(levelname)s\x1b[0m \x1b[35m%(name)s [\x1b[35m%(filename)s:%(lineno)d]\x1b[0m %(message)s',
            '[%Y-%m-%d %H:%M:%S]',
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output
    
shandler = logging.StreamHandler()
shandler.setFormatter(StreamFormatter())
shandler.setLevel(logging.INFO)
logger.addHandler(shandler)

flog_format = logging.Formatter(
    '%(asctime)s %(levelname)s %(name)s '
    '%(message)s',
    datefmt="[%Y-%m-%d %H:%M:%S]")

fhandler = logging.handlers.RotatingFileHandler(
    filename = config.LOG_FILE,
    encoding = 'utf-8',
    maxBytes = 32 * 1024 * 1024,
    backupCount = 5,
)
fhandler.setFormatter(flog_format)
fhandler.setLevel(logging.INFO)
logger.addHandler(fhandler)


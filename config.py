from decouple import config

class DevelopmentConfig():
    DEBUG=True

d_config={
    'development':DevelopmentConfig,
    'secret_key':config('FLASH_SECRET_KEY')
} 
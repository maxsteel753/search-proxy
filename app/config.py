import os

class Settings:
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://adminUser:dfvjkn3msvmm0f3mcv@108.160.140.79:27017/admin")
    KAFKA_BROKER_URL: str = os.getenv("KAFKA_BROKER_URL", "45.76.208.187:9093")
    KAFKA_USERNAME: str = os.getenv("KAFKA_USERNAME","admin")
    KAFKA_PASSWORD: str = os.getenv("KAFKA_PASSWORD","NAVIgaze44##")
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://host.docker.internal:6379")  # Redis service URL (Docker)
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))  # Redis DB index (default 0)
    REDIS_CONNECTION_TIMEOUT: int = int(os.getenv("REDIS_CONNECTION_TIMEOUT", 5))  # Timeout in seconds
    REDIS_POOL_SIZE: int = int(os.getenv("REDIS_POOL_SIZE", 10))  # Connection pool size

settings = Settings()

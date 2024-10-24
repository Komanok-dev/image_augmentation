from app.settings import CelerySettings

# ======================= Test celery_settings_ur =====================


def test_celery_settings_url():
    settings = CelerySettings(
        DRIVER="redis", HOST="localhost", PORT="6379", NAME="celery_db"
    )
    result = settings.url
    assert result == "redis://localhost:6379/celery_db"

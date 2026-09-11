from packages.deployment.config import load_production_settings


if __name__ == "__main__":
    settings = load_production_settings()
    print(
        f"production configuration valid: code_version={settings.code_version} "
        f"queue={settings.queue_name}"
    )

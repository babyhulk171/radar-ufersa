import pytest

from radar_ufersa.cli import load_runtime_settings, parse_cli_options


def test_parse_cli_options_defaults_to_safe_bootstrap() -> None:
    options = parse_cli_options([])

    assert options.notify_existing is False


def test_parse_cli_options_can_notify_existing() -> None:
    options = parse_cli_options(["--notify-existing"])

    assert options.notify_existing is True


def test_load_runtime_settings_returns_trimmed_values() -> None:
    settings = load_runtime_settings(
        {"TELEGRAM_TOKEN": " token ", "TELEGRAM_CHAT_ID": " 123 "}
    )

    assert settings.telegram_token == "token"
    assert settings.telegram_chat_id == "123"


def test_load_runtime_settings_rejects_missing_token() -> None:
    with pytest.raises(ValueError, match="TELEGRAM_TOKEN=''.*non-empty"):
        load_runtime_settings({"TELEGRAM_CHAT_ID": "123"})


def test_load_runtime_settings_rejects_missing_chat_id() -> None:
    with pytest.raises(ValueError, match="TELEGRAM_CHAT_ID=''.*non-empty"):
        load_runtime_settings({"TELEGRAM_TOKEN": "token"})

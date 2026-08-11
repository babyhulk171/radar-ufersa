import argparse
from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class CliOptions:
    notify_existing: bool


@dataclass(frozen=True, slots=True)
class RuntimeSettings:
    telegram_token: str
    telegram_chat_id: str


def parse_cli_options(arguments: Sequence[str]) -> CliOptions:
    """Parses command-line flags without reading process-global argv.

    Example: ``parse_cli_options(['--notify-existing'])`` enables initial alerts.
    """
    parser = argparse.ArgumentParser(
        description="Radar diário de oportunidades da UFERSA"
    )
    parser.add_argument(
        "--notify-existing",
        action="store_true",
        help="Notifica oportunidades já existentes em vez de criar apenas a baseline.",
    )
    namespace = parser.parse_args(arguments)
    return CliOptions(notify_existing=namespace.notify_existing)


def load_runtime_settings(environment: Mapping[str, str]) -> RuntimeSettings:
    """Loads required Telegram settings from an injected environment mapping.

    Example: ``load_runtime_settings({'TELEGRAM_TOKEN': 'x', 'TELEGRAM_CHAT_ID': '1'})``.
    """
    token = environment.get("TELEGRAM_TOKEN", "").strip()
    chat_id = environment.get("TELEGRAM_CHAT_ID", "").strip()
    if not token:
        raise ValueError(
            f"Invalid TELEGRAM_TOKEN={token!r}; expected a non-empty bot token string."
        )
    if not chat_id:
        raise ValueError(
            f"Invalid TELEGRAM_CHAT_ID={chat_id!r}; expected a non-empty "
            "chat id string."
        )
    return RuntimeSettings(token, chat_id)

import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from radar_ufersa.adapters.filesystem import LocalTextFileGateway
from radar_ufersa.adapters.html_bs4 import BeautifulSoupAnchorExtractor
from radar_ufersa.adapters.http_requests import RequestsHttpClient
from radar_ufersa.adapters.text_sink import StreamTextSink
from radar_ufersa.cli import load_runtime_settings, parse_cli_options
from radar_ufersa.collector import OpportunityCollector
from radar_ufersa.logging_json import JsonLineLogger
from radar_ufersa.notification import TelegramOpportunityNotifier
from radar_ufersa.relevance import DEFAULT_MINIMUM_SCORE, DEFAULT_RELEVANCE_RULES
from radar_ufersa.service import RadarService
from radar_ufersa.sources import build_source_catalog
from radar_ufersa.state import JsonSeenStateStore

options = parse_cli_options(sys.argv[1:])
settings = load_runtime_settings(os.environ)
current_year = datetime.now(ZoneInfo("America/Fortaleza")).year
sources = build_source_catalog(current_year)

session = requests.Session()
http_client = RequestsHttpClient(session)
logger = JsonLineLogger(StreamTextSink(sys.stderr))
collector = OpportunityCollector(http_client, BeautifulSoupAnchorExtractor(), logger)
state_store = JsonSeenStateStore(LocalTextFileGateway(), Path("state.json"))
notifier = TelegramOpportunityNotifier(
    http_client, settings.telegram_token, settings.telegram_chat_id
)
service = RadarService(
    collector,
    state_store,
    notifier,
    logger,
    DEFAULT_RELEVANCE_RULES,
    DEFAULT_MINIMUM_SCORE,
)
summary = service.run(sources, options.notify_existing)

print(
    "Radar concluído: "
    f"{summary.scanned_candidates} links, "
    f"{summary.relevant_candidates} relevantes, "
    f"{summary.sent_notifications} notificações enviadas."
)
if summary.bootstrapped:
    print("Primeira execução: baseline criada sem alertar oportunidades antigas.")
if summary.failed_sources or summary.failed_notifications:
    raise SystemExit(1)

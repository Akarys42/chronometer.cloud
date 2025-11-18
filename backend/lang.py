import dataclasses
import json
from dataclasses import dataclass
from pathlib import Path

from starlette.requests import Request

from backend.utils import dataclass_shallow_dict

DEFAULT_LOCALE = "en"
LOCALE_PATH = Path("./i18n/locales")

_unset = object()


@dataclass
class Locale:
    """Represents all the translated strings for a specific locale."""

    default_page_name: str
    default_timer_name: str


def load_locales() -> dict[str, Locale]:
    """Load all locale files from the i18n/locales directory."""
    locales = {}

    for locale_file in LOCALE_PATH.glob("*.json"):
        locale_code = locale_file.stem
        locale_data = {}

        with open(locale_file, "r", encoding="utf-8") as f:
            data = json.load(f).get("backend", {})

        for key in dataclasses.fields(Locale):
            locale_data[key.name] = data.get(key.name, _unset)

        locales[locale_code] = Locale(**locale_data)
    return locales


LOCALES = load_locales()


def get_locale_from_request(request: Request) -> Locale:
    """Get the locale for the current request."""
    user_locale = request.headers.get("User-Locale", None)

    locale_data = dataclass_shallow_dict(LOCALES.get(DEFAULT_LOCALE))

    if user_locale and user_locale in LOCALES:
        user_locale_data = dataclass_shallow_dict(LOCALES[user_locale])

        for key, value in user_locale_data.items():
            if value is not _unset:
                locale_data[key] = value

    return Locale(**locale_data)

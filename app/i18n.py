from __future__ import annotations

from fastapi import Request

DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = frozenset({"en", "ru"})

MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        "file_missing": "No file provided",
        "unsupported_format": "Unsupported format. Allowed: {exts}",
        "empty_file": "Empty file",
        "file_too_large": "File is larger than 25 MB",
        "image_too_large": "Image is too large (max {max_side}px on the long side)",
        "upscale_failed": "Upscale failed. Check the server log for details.",
        "invalid_job_id": "Invalid job id",
        "result_not_found": "Result not found",
        "notice_not_found": "NOTICE not found",
        "license_not_found": "LICENSE not found",
    },
    "ru": {
        "file_missing": "Файл не передан",
        "unsupported_format": "Неподдерживаемый формат. Допустимо: {exts}",
        "empty_file": "Пустой файл",
        "file_too_large": "Файл больше 25 МБ",
        "image_too_large": "Изображение слишком большое (макс. {max_side}px по длинной стороне)",
        "upscale_failed": "Ошибка апскейла. Подробности — в логе сервера.",
        "invalid_job_id": "Некорректный идентификатор задачи",
        "result_not_found": "Результат не найден",
        "notice_not_found": "NOTICE не найден",
        "license_not_found": "LICENSE не найден",
    },
}


def resolve_locale(accept_language: str | None) -> str:
    """Pick the first supported language from Accept-Language, else English."""
    if not accept_language:
        return DEFAULT_LOCALE

    for part in accept_language.split(","):
        tag = part.split(";", 1)[0].strip().lower()
        if not tag:
            continue
        primary = tag.split("-", 1)[0]
        if primary in SUPPORTED_LOCALES:
            return primary
    return DEFAULT_LOCALE


def locale_from_request(request: Request) -> str:
    return resolve_locale(request.headers.get("accept-language"))


def t(key: str, locale: str, **kwargs: object) -> str:
    catalog = MESSAGES.get(locale) or MESSAGES[DEFAULT_LOCALE]
    template = catalog.get(key) or MESSAGES[DEFAULT_LOCALE][key]
    return template.format(**kwargs) if kwargs else template

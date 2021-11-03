# Internal
import ssl
import json
from pathlib import PurePath
from urllib.error import URLError, HTTPError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

# Project
from . import _constants
from .types import User
from ..http.multipart_form_data import MIME_JSON


def get_me(bot_token: str) -> User:
    """https://core.telegram.org/bots/api#deletewebhook

    Args:
        bot_token: Telegram bot token, for authentication with the Telegram API

    Raises:
        RuntimeError: Failure to communicate with Telegram API
    """
    try:
        with urlopen(
            Request(
                url=urljoin(_constants.TELEGRAM_API, (PurePath(bot_token) / "get_me").as_posix()),
                data="{}".encode(encoding="utf8"),
                method="POST",
                headers={"Content-Type": f"{MIME_JSON.main}/{MIME_JSON.sub}"},
            ),
            context=ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH),
        ) as req:
            try:
                res = json.loads(req.read().decode("utf-8"))
            except Exception as exc:
                raise RuntimeError("Failed to parse Telegram response for get_me") from exc

            if not res.get("ok", False):
                raise RuntimeError(
                    f"Telegram answered get_me with an error: {res.get('error_code', 'unknown')}\n{res.get('description', 'unknown')}"
                )

            result = res.get("result", None)
            if not isinstance(result, dict):
                raise RuntimeError("Telegram answered get_me with an invalid response")

            return User(**result)

    except HTTPError as exc:
        raise RuntimeError(f"ipify couldn't fulfill the request: {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"Failed to reach ipify due to: {exc.reason}") from exc


__all__ = ("get_me",)

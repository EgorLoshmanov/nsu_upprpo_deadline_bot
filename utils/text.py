# лимит длины одного сообщения в Telegram
TELEGRAM_LIMIT = 4096


def split_text(text: str, limit: int = TELEGRAM_LIMIT, sep: str = "\n\n") -> list[str]:
    """
    Разбивает длинный текст на части не длиннее limit символов.

    Старается резать по границам блоков (по sep, по умолчанию пустая строка
    между заданиями), чтобы не разрывать одно задание посередине. Если один
    блок сам по себе длиннее лимита — режет его жёстко по символам.
    """
    if len(text) <= limit:
        return [text]

    parts: list[str] = []
    current = ""

    for block in text.split(sep):
        candidate = block if not current else current + sep + block
        if len(candidate) <= limit:
            current = candidate
            continue

        if current:
            parts.append(current)
            current = ""

        # один блок длиннее лимита — режем по символам
        if len(block) > limit:
            for i in range(0, len(block), limit):
                parts.append(block[i:i + limit])
        else:
            current = block

    if current:
        parts.append(current)

    return parts


async def answer_long(target, text: str):
    """
    Отправляет text через target.answer(), при необходимости разбивая его
    на несколько сообщений, чтобы не упереться в лимит Telegram (4096).

    target — объект с методом answer() (Message или callback.message).
    """
    # Telegram отклоняет пустые сообщения — нечего отправлять
    if not text:
        return
    for part in split_text(text):
        await target.answer(part)

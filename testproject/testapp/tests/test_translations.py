from io import StringIO

from babel.messages.pofile import read_po
from django.utils.encoding import force_str
import pathlib

from djoser.constants import Messages


def test_constants_translations_are_up_to_date():
    messages = {force_str(v) for k, v in vars(Messages).items() if k.isupper()}
    ERROR_TEMPLATE = (
        "Error message '{message}' was found in "
        "locale {locale} but can't be found in the messages class"
    )

    root = pathlib.Path(__file__).parent.parent.parent.parent
    locale_dir = root / "djoser" / "locale"
    for specific_locale in locale_dir.iterdir():
        po_file = specific_locale / "LC_MESSAGES" / "django.po"
        po_contents = po_file.read_text()
        with StringIO() as buf:
            buf.write(po_contents)
            buf.seek(0)
            parsed_po = read_po(buf)
            for message in parsed_po:
                if not message.id:
                    continue
                if "djoser/constants.py" not in [loc[0] for loc in message.locations]:
                    continue
                if message.id not in messages:
                    raise ValueError(
                        ERROR_TEMPLATE.format(
                            message=message.id, locale=specific_locale.name
                        )
                    )

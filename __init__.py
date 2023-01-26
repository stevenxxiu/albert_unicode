import json
import subprocess
from pathlib import Path

from albert import Action, Item, Query, QueryHandler, setClipboardText  # pylint: disable=import-error


md_iid = '0.5'
md_version = '1.0'
md_name = 'Unicode'
md_description = 'Finds unicode'
md_url = 'https://github.com/stevenxxiu/albert_unicode'
md_maintainers = '@stevenxxiu'
md_bin_dependencies = ['uni']

TRIGGER = 'u'
ICON_PATH = str(Path(__file__).parent / 'icons/unicode.svg')
MAX_DISPLAYED = 20  # Can hang if this is too large


def find_unicode(query_str: str) -> list[dict]:
    try:
        output = subprocess.check_output(
            ['uni', 'search', '-format=all', '-as=json', query_str],
            stderr=subprocess.STDOUT,
            encoding='utf-8',
        )
    except subprocess.CalledProcessError as e:
        if e.returncode == 1 and e.output == 'uni: no matches\n':
            return []
        raise
    return json.loads(output)


def get_entry_clips(entry: dict) -> dict:
    return {
        'Copy Char': entry['char'],
        'Copy JSON': entry['json'],
        'Copy HTML': entry['html'],
        'Copy UTF-8 bytes': entry['utf8'],
        'Copy All': json.dumps(entry, indent=4, sort_keys=True),
    }


def create_all_clipboard_text(action_name: str, entries: list[dict]) -> str:
    match action_name:
        case 'Copy Char':
            return '\n'.join(entry['char'] for entry in entries) + '\n'
        case 'Copy JSON':
            return '\n'.join(f'{entry["char"]} {entry["json"]}' for entry in entries) + '\n'
        case 'Copy HTML':
            return '\n'.join(f'{entry["char"]} {entry["html"]}' for entry in entries) + '\n'
        case 'Copy UTF-8 bytes':
            return '\n'.join(f'{entry["char"]} {entry["utf8"]}' for entry in entries) + '\n'
        case 'Copy All':
            return '\n'.join(json.dumps(entry, indent=4, sort_keys=True) for entry in entries) + '\n'
    raise ValueError


class Plugin(QueryHandler):
    def id(self) -> str:
        return __name__

    def name(self) -> str:
        return md_name

    def description(self) -> str:
        return md_description

    def defaultTrigger(self) -> str:
        return f'{TRIGGER} '

    def synopsis(self) -> str:
        return 'query'

    def handleQuery(self, query: Query) -> None:
        query_str = query.string.strip()
        if not query_str:
            return

        all_entries = find_unicode(query_str)
        entries = all_entries[:MAX_DISPLAYED]

        for entry in entries:
            query.add(
                Item(
                    id=f'{md_name}/{entry["char"]}',
                    text=entry['char'],
                    subtext=f'{entry["cat"]}: {entry["name"]}',
                    icon=[ICON_PATH],
                    actions=[
                        Action(f'{md_name}/{entry["char"]}/{key}', key, lambda value_=value: setClipboardText(value_))
                        for key, value in get_entry_clips(entry).items()
                    ],
                )
            )

        if all_entries:
            query.add(
                Item(
                    id=f'{md_name}/All',
                    text='All',
                    subtext=f'{len(entries)}/{len(all_entries)} displayed',
                    icon=[ICON_PATH],
                    actions=[
                        Action(
                            f'{md_name}/all/{key}',
                            key,
                            lambda key_=key: setClipboardText(create_all_clipboard_text(key_, all_entries)),
                        )
                        for key, value in get_entry_clips(entries[0]).items()
                    ],
                )
            )

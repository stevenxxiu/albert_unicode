import json
import subprocess
from pathlib import Path

from albert import Action, Item, Query, QueryHandler, setClipboardText  # pylint: disable=import-error


md_iid = '0.5'
md_version = '1.0'
md_name = 'Unicode'
md_description = 'Finds unicode.'
md_url = 'https://github.com/stevenxxiu/albert_unicode'
md_maintainers = '@stevenxxiu'
md_bin_dependencies = ['uni']

TRIGGER = 'u'
ICON_PATH = str(Path(__file__).parent / 'icons/unicode.svg')

# Can crash if this is too large
MAX_DISPLAYED = 10


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

        entries = find_unicode(query_str)[:MAX_DISPLAYED]
        entries_clips = [
            {
                'Copy Char': entry['char'],
                'Copy JSON': entry['json'],
                'Copy HTML': entry['html'],
                'Copy UTF-8 bytes': entry['utf8'],
                'Copy All': json.dumps(entry, indent=4, sort_keys=True),
            }
            for entry in entries
        ]

        for entry, entry_clips in zip(entries, entries_clips):
            query.add(
                Item(
                    id=f'{md_name}/{entry["char"]}',
                    text=entry['char'],
                    subtext=f'{entry["cat"]}: {entry["name"]}',
                    icon=[ICON_PATH],
                    actions=[
                        Action(f'{md_name}/{entry["char"]}/{key}', key, lambda value_=value: setClipboardText(value_))
                        for key, value in entry_clips.items()
                    ],
                )
            )

        if entries:
            all_clips = {key: '' for key in entries_clips[0]}
            for entry, entry_clips in zip(entries, entries_clips):
                for key, value in entry_clips.items():
                    all_clips[key] += f'{entry["char"]}\n' if key == 'Copy Char' else f'{entry["char"]} {value}\n'
            query.add(
                Item(
                    id=f'{md_name}/All',
                    text='All',
                    icon=[ICON_PATH],
                    actions=[
                        Action(f'{md_name}/all/{key}', key, lambda value_=value: setClipboardText(value_))
                        for key, value in all_clips.items()
                    ],
                )
            )

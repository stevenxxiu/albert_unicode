import json
import subprocess
from pathlib import Path
from typing import Callable, TypedDict, override

from albert import setClipboardText  # pyright: ignore[reportUnknownVariableType]
from albert import (
    Action,
    Item,
    PluginInstance,
    Query,
    StandardItem,
    TriggerQueryHandler,
)

setClipboardText: Callable[[str], None]

md_iid = '3.0'
md_version = '1.4'
md_name = 'Unicode'
md_description = 'Finds Unicode'
md_license = 'MIT'
md_url = 'https://github.com/stevenxxiu/albert_unicode'
md_authors = ['@stevenxxiu']
md_bin_dependencies = ['uni']

ICON_URL = f'file:{Path(__file__).parent / "icons/unicode.svg"}'
MAX_DISPLAYED = 100


class UniEntry(TypedDict):
    name: str
    cat: str
    char: str
    json: str
    html: str
    utf8: str


def find_unicode(query_str: str) -> list[UniEntry]:
    try:
        output = subprocess.check_output(
            ['uni', 'search', '-format=all', '-as=json', query_str],
            stderr=subprocess.STDOUT,
            encoding='utf-8',
        )
    except subprocess.CalledProcessError as e:
        if e.returncode == 1 and e.output == 'uni: no matches\n':  # pyright: ignore[reportAny]
            return []
        raise
    return json.loads(output)  # pyright: ignore[reportAny]


def get_entry_clips(entry: UniEntry) -> dict[str, str]:
    return {
        'Copy Char': entry['char'],
        'Copy JSON': entry['json'],
        'Copy HTML': entry['html'],
        'Copy UTF-8 bytes': entry['utf8'],
        'Copy All': json.dumps(entry, indent=4, sort_keys=True),
    }


def create_all_clipboard_text(action_name: str, entries: list[UniEntry]) -> str:
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
        case _:
            raise ValueError


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

    @override
    def synopsis(self, _query: str) -> str:
        return 'query'

    @override
    def defaultTrigger(self):
        return 'u '

    @override
    def handleTriggerQuery(self, query: Query) -> None:
        query_str = query.string.strip()
        if not query_str:
            return

        all_entries = find_unicode(query_str)
        entries = all_entries[:MAX_DISPLAYED]

        items: list[Item] = []
        actions: list[Action]
        copy_call: Callable[[str], None]

        for entry in entries:
            actions = []
            for key, value in get_entry_clips(entry).items():
                copy_call = lambda value_=value: setClipboardText(value_)  # noqa: E731
                actions.append(Action(f'{md_name}/{entry["char"]}/{key}', key, copy_call))
            item = StandardItem(
                id=f'{md_name}/{entry["char"]}',
                text=entry['char'],
                subtext=f'{entry["cat"]}: {entry["name"]}',
                iconUrls=[ICON_URL],
                actions=actions,
            )
            items.append(item)

        if all_entries:
            actions = []
            for key, _value in get_entry_clips(entries[0]).items():
                copy_call = lambda key_=key: setClipboardText(create_all_clipboard_text(key_, all_entries))  # noqa: E731
                actions.append(Action(f'{md_name}/all/{key}', key, copy_call))
            item = StandardItem(
                id=f'{md_name}/All',
                text='All',
                subtext=f'{len(entries)}/{len(all_entries)} displayed',
                iconUrls=[ICON_URL],
                actions=actions,
            )
            items.append(item)

        query.add(items)  # pyright: ignore[reportUnknownMemberType]

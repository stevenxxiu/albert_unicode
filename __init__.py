'''Finds unicode.

Synopsis: <trigger> <query>'''
import json
import subprocess
from pathlib import Path

from albert import ClipAction, Item  # pylint: disable=import-error


__title__ = 'Unicode'
__version__ = '0.0.1'
__triggers__ = 'u '
__authors__ = ['Steven Xu']
__exec_deps__ = ['uni']

ICON_PATH = str(Path(__file__).parent / 'icons/unicode.svg')


def find_unicode(query_str):
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


def handleQuery(query):
    if not query.isTriggered or not query.string.strip():
        return None

    entries = find_unicode(query.string.strip())
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

    items = []
    for entry, entry_clips in zip(entries, entries_clips):
        items.append(
            Item(
                id=f'{__title__}/{entry["char"]}',
                icon=ICON_PATH,
                text=entry['char'],
                subtext=f'{entry["cat"]}: {entry["name"]}',
                actions=[ClipAction(text=key, clipboardText=value) for key, value in entry_clips.items()],
            )
        )

    if entries:
        all_clips = {key: '' for key in entries_clips[0]}
        for entry, entry_clips in zip(entries, entries_clips):
            for key, value in entry_clips.items():
                all_clips[key] += f'{entry["char"]}\n' if key == 'Copy Char' else f'{entry["char"]} {value}\n'
        items.append(
            Item(
                id=f'{__title__}/All',
                icon=ICON_PATH,
                text='All',
                actions=[ClipAction(text=key, clipboardText=value) for key, value in all_clips.items()],
            )
        )
    return items

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


def handleQuery(query):
    if not query.isTriggered or not query.string.strip():
        return None

    query.disableSort()
    stripped = query.string.strip()
    try:
        output = subprocess.check_output(
            ['uni', 'search', '-format=all', '-as=json', stripped],
            stderr=subprocess.STDOUT,
            encoding='utf-8',
        )
    except subprocess.CalledProcessError as e:
        if e.returncode == 1 and e.output == 'uni: no matches\n':
            return None
        raise
    entries = json.loads(output)
    for entry in entries:
        entry['utf8'] = '\\x' + '\\x'.join(entry['utf8'].split(' '))
    items = []
    for entry in entries:
        items.append(
            Item(
                id=__title__,
                icon=ICON_PATH,
                text=entry['char'],
                subtext=f'{entry["cat"]}: {entry["name"]}',
                actions=[
                    ClipAction(text='Copy Char', clipboardText=entry['char']),
                    ClipAction(text='Copy JSON', clipboardText=entry['json']),
                    ClipAction(text='Copy HTML', clipboardText=entry['html']),
                    ClipAction(text='Copy UTF-8 bytes', clipboardText=entry['utf8']),
                    ClipAction(text='Copy All', clipboardText=json.dumps(entry, indent=4, sort_keys=True)),
                ],
            )
        )

    items.append(
        Item(
            id=__title__,
            icon=ICON_PATH,
            text='All',
            actions=[
                ClipAction(text='Copy Char', clipboardText='\n'.join(entry['char'] for entry in entries)),
                ClipAction(
                    text='Copy JSON',
                    clipboardText='\n'.join(f'{entry["char"]} {entry["json"]}' for entry in entries),
                ),
                ClipAction(
                    text='Copy HTML',
                    clipboardText='\n'.join(f'{entry["char"]} {entry["html"]}' for entry in entries),
                ),
                ClipAction(
                    text='Copy UTF-8 bytes',
                    clipboardText='\n'.join(f'{entry["char"]} {entry["utf8"]}' for entry in entries),
                ),
                ClipAction(
                    text='Copy All',
                    clipboardText='\n'.join(
                        f'{entry["char"]} {json.dumps(entry, indent=4, sort_keys=True)}' for entry in entries
                    ),
                ),
            ],
        )
    )
    return items

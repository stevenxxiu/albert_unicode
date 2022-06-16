# -*- coding: utf-8 -*-

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
    res = json.loads(subprocess.check_output(['uni', 'search', '-format=all', '-as=json', stripped], encoding='utf-8'))
    items = []
    for entry in res:
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
                    ClipAction(text='Copy UTF-8 bytes', clipboardText='\\x' + '\\x'.join(entry['utf8'].split(' '))),
                    ClipAction(text='Copy All', clipboardText=json.dumps(entry, indent=4, sort_keys=True)),
                ],
            )
        )
    return items

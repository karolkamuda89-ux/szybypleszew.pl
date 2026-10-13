"""Filtr szablonu zamieniajacy tresc wpisu (prosty zapis z panelu) na HTML.

Zasady zapisu (opisane tez przy polu "Treść" w panelu):
  pusta linia          -> nowy akapit
  ## Tytul             -> srodtytul (h2),  ### Tytul -> mniejszy srodtytul (h3)
  - punkt              -> lista punktowana (kolejne linie zaczynajace sie od "- ")
  **tekst**            -> pogrubienie
  [tekst](https://...) -> link

Uzycie w szablonie: {% load blog_tags %} ... {{ post.content|render_post }}
"""
import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

BOLD = re.compile(r'\*\*(.+?)\*\*')
# Tylko linki http(s) i mailto – zadnych "javascript:" itp.
LINK = re.compile(r'\[([^\]]+)\]\(((?:https?://|mailto:)[^\s)]+)\)')


def _inline(text):
    """Formatowanie wewnatrz linii. Tekst jest juz zabezpieczony (escape) przed wywolaniem."""
    text = BOLD.sub(r'<strong>\1</strong>', text)

    def link(match):
        label, url = match.group(1), match.group(2)
        external = url.startswith('http')
        attrs = ' target="_blank" rel="noopener"' if external else ''
        return f'<a href="{url}"{attrs}>{label}</a>'
    return LINK.sub(link, text)


@register.filter
def render_post(value):
    html = []
    # Najpierw zabezpieczamy caly tekst – wpisany w panelu HTML nie zostanie wykonany na stronie
    blocks = re.split(r'\n\s*\n', escape(value or '').replace('\r\n', '\n').strip())
    for block in blocks:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if not lines:
            continue
        if len(lines) == 1 and lines[0].startswith('### '):
            html.append(f'<h3>{_inline(lines[0][4:])}</h3>')
        elif len(lines) == 1 and lines[0].startswith('## '):
            html.append(f'<h2>{_inline(lines[0][3:])}</h2>')
        elif all(line.startswith('- ') for line in lines):
            items = ''.join(f'<li>{_inline(line[2:])}</li>' for line in lines)
            html.append(f'<ul>{items}</ul>')
        else:
            html.append(f'<p>{"<br>".join(_inline(line) for line in lines)}</p>')
    return mark_safe('\n'.join(html))

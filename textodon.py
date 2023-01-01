''' Terminal Mastodon Public Feed Viewer '''

import argparse
from datetime import datetime
import requests
from html2text import html2text

from rich.markdown import Markdown
from textual.app import App, ComposeResult
from textual.widgets import Input, Static, Header, Footer, ListView, ListItem, Label


INSTANCE_URL = 'https://universeodon.com'
TIMELINE_URL = '/api/v1/timelines/public'
TAG_URL = '/api/v1/timelines/tag/'
LIMIT = 20


class TootHead(Static):
    ''' Toot Header with username, account name, and time '''
    def __init__(self, toot):
        self.toot = toot
        super().__init__()

    def compose(self) -> ComposeResult:
        ''' Compose the Toot Header '''
        username = self.toot['account']['display_name']
        acct = self.toot['account']['acct']
        timedelta = (datetime.utcnow() - datetime.fromisoformat(
            self.toot['created_at'].rstrip('Z')))
        minutesago = timedelta.seconds // 60
        hoursago = minutesago // 60
        if hoursago:
            timestr = f'{hoursago}h'
        else:
            timestr = f'{minutesago}m'

        yield Label(username, classes='username')
        yield Label(' • ', classes='dot')
        yield Label(acct, classes='acctname')
        yield Label(' • ', classes='dot')
        yield Label(timestr, classes='timestamp')


class Toot(Static):
    ''' A single toot '''
    def __init__(self, toot):
        super().__init__()
        self.toot = toot

    def compose(self) -> ComposeResult:
        ''' Compose the Toot Widget '''
        content = html2text(self.toot['content'], bodywidth=0)
        yield TootHead(self.toot)
        yield Label(Markdown(content))
        for media in self.toot['media_attachments']:
            if media['description']:
                yield Label(Markdown(f'{media["description"]} [[Link]]({media["url"]})'),
                            classes='media')


class Feed(ListView):
    ''' Feed of toots '''
    tag = None
    feed = None

    def on_mount(self) -> None:
        ''' Mount the Feed '''
        self.load_timeline()

    def dorefresh(self) -> None:
        ''' Refresh the feed '''
        if self.tag:
            self.load_tag(self.tag)
        else:
            self.load_timeline()

    def load_timeline(self):
        ''' Load public timeline into Feed '''
        self.tag = None
        response = requests.get(f'{INSTANCE_URL}{TIMELINE_URL}?limit={LIMIT}')
        self.feed = response.json()
        self.fill_feed()

    def load_tag(self, tag):
        ''' Load a tag search into Feed '''
        self.tag = tag
        response = requests.get(f'{INSTANCE_URL}{TAG_URL}{tag}?limit={LIMIT}')
        self.feed = response.json()
        self.fill_feed()

    def fill_feed(self):
        ''' Populate the list '''
        self.clear()
        for item in self.feed:
            self.append(ListItem(Toot(item)))


class Textodon(App):
    ''' Textodon App '''

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("r", "refresh_feed", "Refresh")]
    CSS_PATH = 'textodon.css'

    def compose(self) -> ComposeResult:
        ''' Add Widgets '''
        yield Header()
        yield Footer()
        yield Feed()
        yield Input(placeholder="Search for a tag")

    def action_toggle_dark(self) -> None:
        ''' Toggle dark mode '''
        self.dark = not self.dark

    async def action_refresh_feed(self) -> None:
        ''' Refresh the Feed '''
        feeds = self.query(Feed)
        if feeds:
            feeds.last().dorefresh()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        ''' Search form was submitted '''
        feed = self.query_one(Feed)
        if message.value:
            feed.load_tag(message.value)
        else:
            feed.load_timeline()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Terminal Mastodon Feed Viewer')
    parser.add_argument('instance', nargs='?', type=str, default='https://universeodon.com',
                        help='URL of the Mastodon Instance')
    parser.add_argument('-L', '--limit', type=int, default=20,
                        help='Limit the number of statuses to fetch')
    args = parser.parse_args()
    INSTANCE_URL = args.instance
    LIMIT = args.limit
    app = Textodon()
    app.run()

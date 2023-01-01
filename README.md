# Textodon #

View public Mastodon feeds in your terminal.

### Installation ###

Clone the repository, and install these dependencies:

- requests
- rich
- textual
- html2text

They may be installed by running:

    pip install -r requirements.txt

from the respository location.


### Usage ###

To start the feed viewer, run:

    python textodon.py

This uses the [universeodon.com](https://universeodon.com) instance by default. To change instances:

    python textodon.py [instanceurl]

To set the number of posts to fetch to 100:

    python textodon.py [instanceurl] -L 100

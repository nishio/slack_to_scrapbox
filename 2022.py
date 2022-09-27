import json
import os
import re
import html

INDIR = "slack_export"
TITLE_PREFIX = "Slack:"
OLD = 946652400.0  # 2000-01-01

user_names = {}
d = json.load(open(os.path.join(INDIR, "users.json")))
for x in d:
    user_names[x['id']] = x['name']


def id_to_name(m):
    return user_names[m.groups()[0]]


d = json.load(open(os.path.join(INDIR, "channels.json")))
channel_names = {}
channel_purposes = {}
for x in d:
    channel_names[x['id']] = x['name']
    channel_purposes[x['id']] = x['purpose']['value']
    # todo: support x['pins']['id'] (convert to link?)

dates = set()
pages = []
for cid in channel_names:
    cname = channel_names[cid]
    purpose = channel_purposes[cid]

    title = "{prefix}{}".format(cname, prefix=TITLE_PREFIX)
    lines = [title]
    lines.append(purpose)
    for f in sorted(os.listdir(os.path.join(INDIR, cname))):
        date, ext = f.split(".")
        assert ext == 'json'
        lines.append(f"")
        lines.append(f"[* {date}]")

        d = json.load(open(os.path.join(INDIR, cname, f)))
        for x in d:
            user = x.get('user', '')
            uname = user_names.get(user, user)
            line = u"({}) {}".format(uname, x['text'])
            line = html.unescape(line)
            # convert "<@U4SFL6V52|nishio>" to "nisiho"
            line = re.sub(r"<@[^|]+\|([^>]+)>", r"\1", line)
            # convert "<@U4SFL6V52>" to "nisiho"
            line = re.sub(r"<@([^|>]+)>", id_to_name, line)
            # convert "<#C4SH7J5HT|channel-name>" to [channel-name]
            line = re.sub(r"<#[^|]+\|([^>]+)>",
                          r"[{}\1]".format(TITLE_PREFIX), line)
            lines.extend(line.split("\n"))

    page = dict(title=title, lines=lines, updated=OLD)
    pages.append(page)

json.dump(dict(pages=pages), open('to_scrapbox.json', 'w'))

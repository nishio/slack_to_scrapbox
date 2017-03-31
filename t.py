import json
import os
import re

INDIR = "slack_export"
TITLE_PREFIX = "Slack:"

user_names = {}
d = json.load(file(os.path.join(INDIR, "users.json")))
for x in d:
    user_names[x['id']] = x['name']


d = json.load(file(os.path.join(INDIR, "channels.json")))
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
    for f in os.listdir(os.path.join(INDIR, cname)):
        date, ext = f.split(".")
        assert ext == 'json'
        dates.add(date)

        d = json.load(file(os.path.join(INDIR, cname, f)))
        lines = []
        title = "{prefix}{}({})".format(cname, date, prefix=TITLE_PREFIX)
        lines.append(u"{} ({})".format(cname, date))
        lines.append(purpose)
        for x in d:
            user = x.get('user', '')
            uname = user_names.get(user, user)
            line = u"({}) {}".format(uname, x['text'])
            # convert "<@U4SFL6V52|nishio>" to "nisiho"
            line = re.sub(r"<@[^|]+\|([^>]+)>", r"\1", line)
            # convert "<#C4SH7J5HT|channel-name>" to [channel-name]
            line = re.sub(r"<#[^|]+\|([^>]+)>", r"[{}\1]".format(TITLE_PREFIX), line)
            lines.append(line)

        lines.append(u"Tags: [{prefix}{}] [{prefix}{}]".format(cname, date, prefix=TITLE_PREFIX))
        page = dict(title=title, lines=lines)
        pages.append(page)

    cname = channel_names[cid]
    title = u"{prefix}{}".format(cname, prefix=TITLE_PREFIX)
    lines = []
    lines.append(title)
    lines.append(purpose)
    page = dict(title=title, lines=lines)
    pages.append(page)

for date in dates:
    title = u"{prefix}{}".format(date, prefix=TITLE_PREFIX)
    lines = []
    lines.append(title)
    page = dict(title=title, lines=lines)
    pages.append(page)


json.dump(dict(pages=pages), file('to_scrapbox.json', 'w'))

import asyncio
import re
import asyncio.subprocess
import logging
from datetime import timedelta, datetime
import shlex

def find_line(text, start):
    for i in text.split("\n"):
        if i.startswith(start):
            return i
    else:
        return ""

re_num = re.compile(r"[\.\d\,]+")
def first_num(text):
    found = re_num.search(text)
    if found:
        num = found.group().replace(",", "")
        if "." in num:
            return float(num)
        else:
            return int(num)

def parse_interval(s):
    if s.endswith("d"):
        return timedelta(days=int(s[:-1]))
    elif s.endswith("h"):
        return timedelta(hours=int(s[:-1]))
    elif s.endswith("m"):
        return timedelta(minutes=int(s[:-1]))

class Task():
    def __init__(self):
        pass

    def initialize(self):
        pass

    def start(self):
        pass

class RsyncTask(Task):
    command = ["rsync", "--relative", "--times", "--links", "--hard-links", "--verbose", "--delete", "--stats", "--whole-file"]
    re_stats = re.compile(r"Number\sof\sfiles[\s\S]+speedup is [.\d]+")

    def __init__(self, name, config):
        self.name = name
        self.target = config['target']
        self.source = config['source']
        self.interval = parse_interval(config.get("interval", "12h"))
        self.process = None
        self.last_run = datetime.now() - self.interval
        self.cmd = " ".join command + [self.target, self.source]
        self.logger = logging.getLogger("task:{}".format(name))
    def __str__(self):
        return "[RsyncTask {}]".format(self.name)

    def can_run(self):
        if self.process:
            return self.process.returncode != None and self.last_run + self.interval < datetime.now()
        else:
            return True
    def parse_stats(self, text):
        stats = self.re_stats.search(text)
        if not stats:
            self.logger.warn("fail finding the stats")
            return {}
        stats = stats.group()
        ret = {}
        ret["files"] = first_num(find_line(text, "Number of files"))
        ret["created"] = first_num(find_line(text, "Number of created"))
        ret["deleted"] = first_num(find_line(text, "Number of deleted"))
        ret["regular"] = first_num(find_line(text, "Number of regular"))
        ret["total_size"] = first_num(find_line(text, "Total file size"))
        ret["transfer"] = first_num(find_line(text, "Total transferred file size"))

        ret["speed"] = float(re_num.findall(find_line(text, "sent"))[2].replace(",", ""))

        return ret

    def start(self):
        asyncio.ensure_future(self.run())

    async def run(self):
        self.buffer = b''
        self.process = await asyncio.create_subprocess_shell(self.cmd, stdout=asyncio.subprocess.PIPE)
        self.logger.info("Started %s", self.name)
        while self.process.returncode == None and not self.process.stdout.at_eof():
            line = await self.process.stdout.readline()
            self.buffer += line
            # print(line)
            logging.info(line.decode("utf8").rstrip("\n"))
        self.logger.info("Finisheded %s, returncode %s", self.name, self.process.returncode)
        try:
            stats = self.parse_stats(self.buffer.decode("utf8"))
            # print(stats)
            # self.save_stats(stats)
        except Exception as e:
            self.logger.exception(e)
        self.last_run = datetime.now()

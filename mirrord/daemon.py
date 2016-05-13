import yaml
from task import RsyncTask
import asyncio
import logging
import argparse


class Application():
    def __init__(self):
        self.tasks = {}

    def load_config(self, config):
        with open(config) as fp:
            data = yaml.safe_load(fp)
            for i, j in data["task"].items():
                self.tasks[i] = RsyncTask(i, j)
        logging.info("loaded config")

    def find_to_update(self):
        for i in self.tasks.values():
            if i.can_run():
                return i

    async def run(self):
        while True:
            task = self.find_to_update()
            if task:
                logging.info("Schedule %s", task)
                task.start()
            await asyncio.sleep(1)  # emit no more than 1 task per minute

    def start(self):
        el = asyncio.get_event_loop()
        logging.info("Daemon Start >_<")
        el.run_until_complete(self.run())

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    a = Application()
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config")
    args = parser.parse_args()
    a.load_config(args.config)
    a.start()

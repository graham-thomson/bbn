import yaml
import requests
import pandas as pd
import datetime as dt
import sqlalchemy
from bs4 import BeautifulSoup, element
from random import choice

class GetData(object):

    def __init__(self, config):
        self.config = config
        self.user_agents = self.config["user_agents"]
        self.url = self.config["url"]

    def random_headers(self):
        return {
            'User-Agent': choice(self.user_agents),
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

    def make_request(self):
        r = requests.get(self.url, headers=self.random_headers())
        if r.status_code == 200:
            return r.content
        raise AttributeError("Problem with Request.")

    def parse_html(self):
        soup = BeautifulSoup(self.make_request(), "html.parser")
        blog_posts = []
        for post in soup.find_all("hr")[:10]:
            content = []
            not_end = True
            next_element = post.next_element
            while not_end:
                if isinstance(next_element, element.Tag) and next_element.get("class") == [u'p-entry-hr']:
                    not_end = False
                if isinstance(next_element, element.Tag) and next_element.name == "p":
                    content += [next_element.getText()]
                next_element = next_element.next_element
            blog_posts += [content]

        df = pd.DataFrame({dt.datetime.strptime(p[0], "%B %d, %Y"): [p[1:]] for p in blog_posts}).transpose()
        df = df[0].apply(pd.Series).stack().reset_index(level=1, drop=True).to_frame("story").reset_index()
        df.columns = ["date", "story"]

        return df

    def write_results(self):
        engine = sqlalchemy.create_engine("sqlite:///../beer.db", echo=False)
        stories = self.parse_html()
        try:
            stories.to_sql("news", con=engine, if_exists="fail", index=False)
        except ValueError:
            old_stories = pd.read_sql("SELECT * FROM news;", con=engine, parse_dates=["date"])
            pd.concat([stories, old_stories]).drop_duplicates()\
                .to_sql("news", con=engine, if_exists="replace", index=False)

    def run(self):
        self.write_results()

if __name__ == '__main__':

    with open("../config.yaml", "r") as cfg:
        cfg = yaml.load(cfg)

    data_getter = GetData(config=cfg)
    data_getter.run()
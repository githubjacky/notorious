import flair
from flair.data import Sentence
from flair.nn import Classifier
from flair.embeddings import TransformerDocumentEmbeddings
from googlesearch import search
import httpx
from loguru import logger
import logging
from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseTfidfVectorizer
import orjson
from pathlib import Path
from selectolax.parser import HTMLParser
from typing import List
from tqdm import tqdm



class NegativeKW_Collector():
    def __init__(self,
                 n_url: int,
                 sleep: int,
                 sentiment_model: str, 
                 extract_model: str
                 ):
        self.n_url = n_url
        self.tagger = Classifier.load(sentiment_model)
        flair_model = TransformerDocumentEmbeddings(model=extract_model)
        self.kw_model = KeyBERT(model=flair_model)
        self.sleep = sleep

    def setup(self, predator):
        output_dir = Path(f"data/preprocess/{predator}/negative_search")
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir

        url_path = output_dir / f"{self.n_url}_url.json"
        if url_path.exists():
            logger.info("negative search: url exists, fetch from file")
            urls = orjson.loads(url_path.read_text())["urls"]
        else:
            logger.info("negative search: fetch url")
            urls = []
            for i in search(
                predator, 
                num_results = self.n_url, 
                advanced = True,
                sleep_interval=self.sleep
            ):
                urls.append(i.url)

            with url_path.open('wb') as f:
                f.write(orjson.dumps({"urls": urls}, option=orjson.OPT_INDENT_2))

        self.urls = urls
        self.predator = predator


    def fetch_corpos(self) -> List[Sentence]:
        logger = logging.getLogger("httpx")
        logger.disables = True
        output_path = self.output_dir / f"{self.n_url}_corpus.json"

        if output_path.exists():
            logger.info("negative search: corpus exists, fetch from the file")
            corpus = [
                Sentence(i)
                for i in orjson.loads(output_path.read_text())["corpus"]
            ]
        else:
            logger.info("negative search: fetch corpus")
            _corpus = []
            with httpx.Client() as client:
                for url in tqdm(self.urls, position=1, leave=False):
                    try:
                        resp = client.get(url)
                        if resp.status_code == httpx.codes.OK:
                            tree = HTMLParser(resp.text)

                            for node in tree.css('title'):
                                item = node.text().replace("\n", "")
                                if item != "": _corpus.append(item)
                    except:
                        continue
            with output_path.open('wb') as f:
                f.write(orjson.dumps({"corpus": list(set(_corpus))}, option=orjson.OPT_INDENT_2))

            corpus = [Sentence(i) for i in set(_corpus)]

        return corpus

    def fetch_keywords(self, output_path):
        corpus = self.fetch_corpos()
        negative_sentence = []
        for i in corpus:
            self.tagger.predict(i)
            item = i.to_dict()
            res = item['all labels'][0]
            if res['value'] == 'NEGATIVE' and res['confidence'] > 0.7:
                negative_sentence.append(item['text'])

        __keywords = self.kw_model.extract_keywords(
            docs = "\n".join(negative_sentence)
        )

        logger.info("negative search: fetch negative keywords")
        _keywords = []
        for i in __keywords:
            if 0.7 < i[1]:
                _keywords += i[0].split(' ')

        keywords = [
            i 
            for i in list(set(_keywords)) 
            if i not in [j.lower() for j in self.predator.split(" ")]
        ]

        with output_path.open('wb') as f:
            f.write(orjson.dumps({"keywords": keywords}, option=orjson.OPT_INDENT_2))

        return keywords

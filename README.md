# notorious_cls
*This repo host my Research Assistant Work at NTU for Professor [Chih-Sheng Hsieh](https://sites.google.com/site/chihshenghsieh/)*


## File Structure
All the source code can be found under **ncls/** folder and this is the main
module of this repo. Besides, I modify some of the code
in original gtab [repo](https://github.com/epfl-dlab/GoogleTrendsAnchorBank) library and 
store it under **ncls/process/gtab**. **config** folder is the hydra configuration for 
collecting google trends records or web scrapping negative keywords. 
The **env/** folder simply store the meta-data after collect google trends records, 
such as the invalid keywords, keywords which need to be checked whether
it is actually "negative". **notebooks/** store the jupyter notebook that I use 
to prototype the module. In conclusion, the repo can be divided into main and
auxiliary category. For the main category, it contains three parts, which is
configuration, module, and test, all in similar structure. For the auxiliary
category, it involves notebooks and scripts.


## Reference Library
- collect google trends: [gtab](https://github.com/epfl-dlab/GoogleTrendsAnchorBank)
- search negative keyword: [keybert](https://github.com/MaartenGr/KeyBERT), [flair](https://github.com/flairNLP/flair)

*For more information about the dependencies of this repo, check the pyproject.toml file*


## DVC
To download the model in negative keyword searching task or the result of gtab,
use the dvc command:
```shell
dvc pull -r origin
```
Or you may only want to see the source of sheet "new_Ri_XXXX", "new_Rj_XXXX" 
```shell
dvc pull -r origin data/gtab_res
```
*Notice: DVC is a data version control utilities: [dvc](https://github.com/iterative/dvc)*


## docker container
To build the image you need to either modify the *$USERID*, *$GROUPID* and *$DOCKERUSER*
manually or crate an .env file and define those three environment variables. For more information, check out the compose file: docker-compose.yaml

To use the docker environment, build the the container first:
```shell
docker compose build
```

## Tests
for now, only test the functionality of the gtab API to detect the 429 error
```shell
make test

# docker
make dtest
```

## Collect Google Trends Records
1. edit the cofiguration: config/process/trend_search.yaml
2. before collecting the google trends records, one need to set up the region and the period which I define as creating anchorbanks
```shell
# poetry env
make create-anchorbanks

# docker
make dcreate-anchorbanks
```
3. run the command
```shell
make trend-search

# docker
make dtrend-search
```


## Data Processing(work in progress)
- create monthly google trends records from original weekly frequency
- adjust ait matrix to exclude the self-issue action
- from *new_ri_sum_smooth* to *new_ri_for_regression*:


## Collect Negative Google Trends
The way we filter out the "negative trends" is to add a custom negative keyword with the predator/victim name. For example, the negative keyword can be "Sexual harassment" and the input of gtab API should be {name} "{Sexual harassment}". In some cases, the name with the specific keyword can't get have valid result, due to too less of dicussion on the internet. In this case, I decide to collect the suitable keyword manually introduced in the next section. 

First, I collect the newest 100 URLs related to the predator/victim name. Second, I scrape the content and title of each website through the corresponding URL. It should be noted that some websites cannot be scraped for content. Finally, utilizing the Language Model to filter out keywords of the website and retain those containing negative words.

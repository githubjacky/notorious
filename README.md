# notorious_cls
*This repo host my Research Assistant Work at NTU*


## file structure
All the source code can be found under **src/** folder. I modify some of the code
in original gtab repoe and stored under **src/data/gtab**. **config** folder is
the hydra configuration for collecting google trends records or web scrapping 
negative keywords. The **env/** folder simply store the meta-data after collect google 
trends records, such as the invalid keywords, keywords which need to be checked whether
it is actually "negative." Basically, the raw data is hided, the accessible data is
the result of collecting google trends(gtab_res). **notebooks/** store the jupyter
notebook that I use to prototype the source code, might be helpful to quickly 
understand what I have done.


## package
- collect google trends: [gtab](https://github.com/epfl-dlab/GoogleTrendsAnchorBank)
- search negative keyword: [keybert](https://github.com/MaartenGr/KeyBERT), [flair](https://github.com/flairNLP/flair)

*For more information, check the pyproject.toml file*


## dvc
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
manually or crate an env file(ex: .env) and define those three variables.
For more information, check out the compose file: docker-compose.yaml


## data processing
- create monthly google trends records from original weekly frequency
```shell
python script/return_ri_rj.py --write
```
- adjust ait matrix to exclude the self-issue action
```shell
python script/adjust_ait.py --write
```
- from *new_ri_sum_smooth* to *new_ri_for_regression*: notebooks/create_ri_for_regression.ipynb
```shell
python script/create_ri_for_regression.py --write
```


## collect google trends records
1. edit the cofiguration: config/main.yaml
2. rund command
```shell
python src/data/collect_trend
```
Or use docker container:
```shell
docker compose run --rm collect_trend
```


## collect negative google trends
Use this gtab API to collect google trends of a METOO predator/victim. The way to
filter out the "negative trends" is to add a custom keyword with the name. For
example, the input of api should be {name} "{Sexual harassment}". In some cases,
the name with the specific keyword filter no result, hence, I decide to collect
the suitable keyword manually.

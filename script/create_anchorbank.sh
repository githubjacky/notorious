# 1. default period in gtab package: 2019-01-01 2020-12-31

# 2. if the following error is raised:
#    TypeError: Retry.__init__() got an unexpected keyword argument 'method_whitelist'
#    downgrade the version package urllib3 no more than 2(1.26.4)

# 3. pandas version should < 2(prevent warning message)
gtab-set-options --geo "" --timeframe "2016-01-01 2018-07-31"
gtab-create

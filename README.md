# Twitter Topic Detection for Bots

### Installation

Install the dependencies from requirements.txt

```sh
$ cp stopwords /home/<user>/nltk_data/corpora/
```


### Execution

For running weekly reports:
Make sure data is present in location `reports/InputData/week<week_no>/` with filename format as `week<week_no>.csv`

Execute:
```sh
$ python main.py reports <week_no>
```


For running coronavirus:
Make sure data is present in location `coronavirus/InputData/week<week_no>/` with filename format as `Week<week_no>.csv`

Execute:
```sh
$ python main.py reports <week_no>
```



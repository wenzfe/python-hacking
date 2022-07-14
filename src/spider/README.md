
<img src="spider.ico" width="64" height="64" style="margin-right: 20px; float:left;">

# Spider

</br>

A multi threaded web crawler / spider

```sh
# Demo
Spider.exe --urls http://wordpress:80/ -p Storage --log-output spider.log --log-lvl 10 --url-paths paths.txt

python main.py --urls http://wordpress:80/ -p C:/Temp/ --log-output C:/Temp/spider.log --log-lvl 0 --ur
--url-paths paths.txt
```

## Install

```sh
pip install -r requirements.txt
```

## Build a executable with pyinstaller

```sh
pyinstaller --clean --noconfirm --onefile --console --icon "spider.ico"  "main.py" -n Spider.exe
```

## Arguments

```sh
usage: main.py [-h] --urls URL [URL ...] [--url-paths PATH [PATH ...]] [--visit-ext | --no-visit-ext] [-w N] [-p [PATH]]
               [--store-data [{OTHER,HTML,JS,CSS,IMAGE,LINK} ...]] [--log-lvl LOG_LVL] [--log-output [LOG_OUTPUT]] [--request-timeout SEC] [--request-proxy JSON] [-v]

    A multithreaded Web Crawler / Spider



optional arguments:
  --urls URL [URL ...]  The URL's to be crawled, in the form http://example.com:80
  --url-paths PATH [PATH ...]
                        A file containing the paths to use when starting to performe the crawl.
  --visit-ext, --no-visit-ext
                        Set flag to visit external URLs (default: False) (default: False)
  -w N, --worker N      Number of workers / threads to use (default: 5)
  -p [PATH], --path [PATH]
                        The location on your system to store the data (default: ...)
  --store-data [{OTHER,HTML,JS,CSS,IMAGE,LINK} ...]
                        Select the data types to be stored (default: ['OTHER', 'HTML', 'JS', 'CSS', 'IMAGE', 'LINK'])
  --log-lvl LOG_LVL     The logging level of the script, control the verbosity of output (default: 20)
  --log-output [LOG_OUTPUT]
                        The logging output destination (default: stdout)
  --request-timeout SEC
                        Number of seconds before request timeout (default: 60)
  --request-proxy JSON  Specify a json file containing the proxy to use as a intermediate for requests
  -v, --version         show program's version number and exit

    Level     | Numeric value
    --------------------------
    CRITICAL  |   50
    ERROR     |   40
    WARNING   |   30
    INFO      |   20
    DEBUG     |   10
    NOTSET    |    0
```

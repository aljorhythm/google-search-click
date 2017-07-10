# google-search-click
automate clicking of link in google search results

## features

### random sleep

random sleep times are set to avoid google detecting botting

### preferences

As of now the maximum number of results per page can be set

### spelling correction

If google initiates a correction ("Including results for xxxx "), the original one will be clicked

## notes

### unable to click next
there are two cases where next cannot be pressed
1. all results have been displayed
2. google detects a bot

currently there is no support to detect which is the case, if the next button cannot be found program will just continue

# distribution

## windows

```
pyinstaller <entry-script-name>.py
copy chromedriver.exe dist\<entry-script-name>\
```
## mac

```
pyinstaller <entry-script-name>.py
cp chromedriver dist/<entry-script-name>/
```

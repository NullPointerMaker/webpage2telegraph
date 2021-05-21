# Webpage to Telegraph

Transfer webpage to Telegraph archive.

## Usage

```
import webpage2telegraph
webpage2telegraph.token = YOUR_TELEGRAPH_TOKEN
telegraph_url = webpage2telegraph.transfer(webpage_url)
```

If transfer failed, `telegraph_url` will be `None`.

## Install

`pip3 install webpage2telegraph`
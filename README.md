# Webpage to Telegraph

Library for transfer webpage to Telegraph archive.

## Usage

```
import webpage_to_telegraph
webpage_to_telegraph.token = YOUR_TELEGRAPH_TOKEN
telegraph_url = webpage_to_telegraph.transfer(webpage_url)
```

If transfer failed, `telegraph_url` will be None.

## How to Install

`pip3 install webpage_to_telegraph`
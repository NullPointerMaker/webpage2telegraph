# Webpage to Telegraph

Library for transfer webpage to Telegraph archive.

## usage

```
import webpage_to_telegraph
webpage_to_telegraph.token = YOUR_TELEGRAPH_TOKEN
telegraph_url = webpage_to_telegraph.transfer(webpage_url)
```

If transfer failed, `telegraph_url` will be None.

## how to install

`pip3 install webpage_to_telegraph`
# export_to_telegraph

Library for export webpage to Telegraph.

## usage

```
import export_to_telegraph
export_to_telegraph.TOKEN = YOUR_TELEGRAPH_TOKEN
telegraph_url = export_to_telegraph.export(webpage_url)
```

If export failed, `telegraph_url` will be None.

## how to install

`pip3 install export_to_telegraph`
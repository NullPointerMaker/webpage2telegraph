# Webpage to Telegraph

Transfer webpage to Telegraph archive.

Move to [Webpage to Telegraph Adapter](https://github.com/NullPointerMaker/webpage2telegraph.adapter).  
The new version is an adapter library to [Export to Telegraph](https://github.com/gaoyunzhi/export_to_telegraph), hacking with monkey patches.

Maintaining a separate library is too cumbersome, especially when the upstream does not cooperate.  
All commits are uncommented. The issues are ignored.

I just want to make some unacceptable fixes.

## Usage

```
import webpage2telegraph
webpage2telegraph.token = YOUR_TELEGRAPH_TOKEN
telegraph_url = webpage2telegraph.transfer(webpage_url)
```

If transfer failed, `telegraph_url` will be `None`.

## Install

`pip3 install webpage2telegraph`

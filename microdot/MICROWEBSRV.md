https://github.com/jczic/MicroWebSrv

TODO: We don't use the latest version from Github which has some patches

Using as captive portal :

```python
# To intercept all not found queries and redirect it,
mws.SetNotFoundPageUrl("http://my-device.wifi")
``` 
https://github.com/miguelgrinberg/microdot

https://microdot.readthedocs.io/en/latest/

## Setup

Download from https://github.com/miguelgrinberg/microdot/tree/main/src/microdot into lib/microdot:

- ___init___.py
- microdot.py
- utemplate.py

Download everything from https://github.com/miguelgrinberg/microdot/tree/main/libs/common/utemplate into lib/utemplate

memory free without utemplate: 122832
memory free with utemplate: 114784


app.run(port=80, debug=True)

## Template example

```python
@app.route('/')
async def index(request):
    gc.collect()
    mem_free = gc.mem_free()
    return Template('index.html').render(mem_free=mem_free)
```

```html
<!-- templates/index.html -->
 {% args mem_free %} <!-- this is mandatory! -->
<!DOCTYPE html>
<html>
<head>
    <title>Microdot Demo</title>
</head>
<body>
    <h1>Hello from Microdot!</h1>
    <p>Memory free: {{ mem_free }} bytes</p>
</body>
</html> 
```




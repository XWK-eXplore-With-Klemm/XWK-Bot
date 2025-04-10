https://github.com/miguelgrinberg/microdot

Download from https://github.com/miguelgrinberg/microdot/tree/main/src/microdot into lib/microdot:

- ___init___.py
- microdot.py
- utemplate.py

Download everything from https://github.com/miguelgrinberg/microdot/tree/main/libs/common/utemplate into lib/utemplate



memory free without utemplate: 122832


app.run(port=80, debug=True)








Changing the Default Response Content Type

Microdot uses a text/plain content type by default for responses that do not explicitly include the Content-Type header. The application can change this default by setting the desired content type in the default_content_type attribute of the Response class.

The example that follows configures the application to use text/html as default content type:

from microdot import Response

Response.default_content_type = 'text/html'


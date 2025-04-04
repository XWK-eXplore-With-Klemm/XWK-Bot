import os
import json
import sys
import network
import gc
from microWebSrv import MicroWebSrv


DEBUG_PRINT = True

def dprint(string):
    if not DEBUG_PRINT:
        return
    print("[--WEB DEBUG {}--]".format(string))

def get_memory_info():
    gc.collect()
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    total = free + alloc
    return {
        'free': free,
        'alloc': alloc,
        'total': total,
        'percent': alloc / total * 100
    }

def log_memory(prefix):
    mem = get_memory_info()
    dprint(f"{prefix} - Memory: free={mem['free']}, alloc={mem['alloc']}, total={mem['total']}, used={mem['percent']:.1f}%")

def _respond(httpResponse, content):
    httpResponse.WriteResponseOk(
        headers = {}, #"Access-Control-Allow-Origin": "*"
        contentType = "application/json",
        contentCharset = "UTF-8",
        content = json.dumps(content)
    )

@MicroWebSrv.route('/info')
def get_info(httpClient, httpResponse):
    args = httpClient.GetRequestQueryParams()
    wlan = network.WLAN()
    hostname = wlan.config('dhcp_hostname')
    ip = wlan.ifconfig()[0]
    name = hostname if hostname != 'espressif' else ip
    content = {"name": "MPY: {}".format(name), "ip": ip, "hostname": hostname}
    
    _respond(httpResponse, content)

@MicroWebSrv.route('/dir')
def get_dir(httpClient, httpResponse):
    args = httpClient.GetRequestQueryParams()
    path = args.get('path', '/')
    if path != "/" and path[-1] == "/":
        path = path[:len(path)-1]
    dprint("Listing dir {}".format(path))
    elements = list(os.ilistdir(path))
    files = [pt[0] for pt in elements if pt[1]==32768]
    dirs = [pt[0] for pt in elements if pt[1]==16384]
    content = {"files": files, "dirs": dirs}
    
    _respond(httpResponse, content)

@MicroWebSrv.route('/file')
def file_handler(httpClient, httpResponse):
    """Handle file read/write requests."""
    try:
        args = httpClient.GetRequestQueryParams()
        path = args.get('path', '')
        if not path:
            dprint("No path provided")
            httpResponse.WriteResponseBadRequest()
            return

        if httpClient.GetRequestMethod() == "GET":
            try:
                dprint("Loading file {} - starting".format(path))
                log_memory("Before file read")
                
                # Get file size first
                file_size = os.stat(path)[6]
                dprint("File size: {} bytes".format(file_size))
                
                # Set all required headers
                headers = {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                    "Cache-Control": "no-cache",
                    "Content-Type": "text/plain; charset=UTF-8",
                    "Content-Length": str(file_size)
                }
                
                # Send headers
                dprint("Sending headers")
                httpResponse._write('HTTP/1.1 200 OK\r\n')
                for k, v in headers.items():
                    httpResponse._write('{}: {}\r\n'.format(k, v))
                httpResponse._write('\r\n')
                
                # Send file content in chunks
                CHUNK_SIZE = 1024
                sent = 0
                with open(path, 'r') as f:
                    while sent < file_size:
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        httpResponse._write(chunk)
                        sent += len(chunk)
                        gc.collect()  # Force garbage collection after each chunk
                        dprint("Sent {} of {} bytes".format(sent, file_size))
                        log_memory("After sending chunk")
                
                dprint("File sending completed")
                log_memory("After sending complete file")
                return
                
            except Exception as e:
                import sys
                sys.print_exception(e)
                dprint("Error loading file: {}".format(str(e)))
                # Use WriteResponse instead of WriteResponseInternalServerError
                httpResponse.WriteResponse(
                    code=500,
                    headers={"Access-Control-Allow-Origin": "*"},
                    contentType="text/plain",
                    contentCharset="UTF-8",
                    content=str(e)
                )
                return

        elif httpClient.GetRequestMethod() == "OPTIONS":
            # Handle CORS preflight
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "86400"
            }
            httpResponse.WriteResponseOk(headers=headers)
            return
            
    except Exception as e:
        import sys
        sys.print_exception(e)
        dprint("Error in file handler: {}".format(str(e)))
        # Use WriteResponse instead of WriteResponseInternalServerError
        httpResponse.WriteResponse(
            code=500,
            headers={"Access-Control-Allow-Origin": "*"},
            contentType="text/plain",
            contentCharset="UTF-8",
            content=str(e)
        )
        return

@MicroWebSrv.route('/savefile', 'OPTIONS')
def save_file_OPTIONS(httpClient, httpResponse):
    dprint("received savefile OPTIONS request")
    httpResponse.WriteResponseOk(
        headers = {
            "Access-Control-Allow-Origin": "*", 
            "Access-Control-Allow-Methods": "OPTIONS, POST", 
            "Access-Control-Allow-Headers": "content-type"
        },
        contentType = "application/json",
        contentCharset = "UTF-8",
        content = ""
    )

@MicroWebSrv.route('/savefile', 'POST')
def save_file(httpClient, httpResponse):
    data = httpClient.ReadRequestContentAsJSON()
    fpath = data.get('path', None)
    if fpath:
        dprint("Got save file request for: {}".format(fpath))
        content = {"error": True}
        with open(fpath, "w") as f:
            f.write(data["lines"])
            content = {"saved": True}

    _respond(httpResponse, content)

@MicroWebSrv.route('/savefileb', 'POST')
def save_file(httpClient, httpResponse):
    try:
        headers = httpClient.GetRequestHeaders()
        fpath = headers.get('File-Path', None)
        
        if not fpath:
            dprint("No file path provided in headers")
            httpResponse.WriteResponse(
                code=400,
                headers={"Access-Control-Allow-Origin": "*"},
                contentType="application/json",
                contentCharset="UTF-8",
                content=json.dumps({"error": "No file path provided"})
            )
            return

        dprint("Starting save for file: {}".format(fpath))
        log_memory("Before save operation")

        # Read content in chunks and write directly to file
        CHUNK_SIZE = 1024
        total_written = 0
        
        with open(fpath, "w") as f:
            while True:
                chunk = httpClient.ReadRequestContent(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                total_written += len(chunk)
                gc.collect()  # Force garbage collection after each chunk
                dprint("Written {} bytes".format(total_written))
                log_memory("After writing chunk")

        dprint("File save completed, total bytes: {}".format(total_written))
        log_memory("After save complete")

        # Send success response
        httpResponse.WriteResponse(
            code=200,
            headers={"Access-Control-Allow-Origin": "*"},
            contentType="application/json",
            contentCharset="UTF-8",
            content=json.dumps({"saved": True, "bytes": total_written})
        )
        
    except Exception as e:
        import sys
        sys.print_exception(e)
        dprint("Error saving file: {}".format(str(e)))
        httpResponse.WriteResponse(
            code=500,
            headers={"Access-Control-Allow-Origin": "*"},
            contentType="application/json",
            contentCharset="UTF-8",
            content=json.dumps({"error": str(e)})
        )
        return

@MicroWebSrv.route('/savefileb', 'OPTIONS')
def save_file_options(httpClient, httpResponse):
    dprint("Received savefileb OPTIONS request")
    httpResponse.WriteResponse(
        code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400"
        },
        contentType="text/plain",
        contentCharset="UTF-8",
        content=""
    )

@MicroWebSrv.route('/run')
def run(httpClient, httpResponse):
    args = httpClient.GetRequestQueryParams()
    name = args.get('name', None)
    stop = args.get('stop', None)
    content = {}
    if stop:
        dprint("Stopping process")
        import weditor.pmanager
        weditor.pmanager.stop_process()
        # Stop all robot functions
        import bot
        bot.stop()  # Stop motors
        bot.shutup()  # Stop beeper
        bot.rgb_led(bot.BLACK)  # Turn off RGB LED
        content = {"stopped": True}
    elif name:
        dprint("Starting process {}".format(name))
        import weditor.pmanager
        weditor.pmanager.restart_process(name)
        content = {"started": True}

    _respond(httpResponse, content)

@MicroWebSrv.route('/newfile')
def new_file(httpClient, httpResponse):
    args = httpClient.GetRequestQueryParams()
    path = args.get('path', None)
    content = {"created": False}
    if path:
        dprint("Creating new file {}".format(path))
        with open(path, 'a') as f:
            content = {"created": True}

    _respond(httpResponse, content)

@MicroWebSrv.route('/newdir')
def new_file(httpClient, httpResponse):
    args = httpClient.GetRequestQueryParams()
    path = args.get('path', None)
    content = {"created": False}
    if path:
        dprint("Creating new directory {}".format(path))
        os.mkdir(path)
        content = {"created": True}

    _respond(httpResponse, content)

@MicroWebSrv.route('/deletefile')
def delete_file(httpClient, httpResponse):
    try:
        args = httpClient.GetRequestQueryParams()
        path = args.get('path', None)
        
        if not path:
            dprint("No file path provided")
            httpResponse.WriteResponse(
                code=400,
                headers={"Access-Control-Allow-Origin": "*"},
                contentType="application/json",
                contentCharset="UTF-8",
                content=json.dumps({"error": "No file path provided"})
            )
            return

        dprint("Deleting file: {}".format(path))
        
        # Check if file exists
        try:
            os.stat(path)
        except OSError:
            dprint("File not found: {}".format(path))
            httpResponse.WriteResponse(
                code=404,
                headers={"Access-Control-Allow-Origin": "*"},
                contentType="application/json",
                contentCharset="UTF-8",
                content=json.dumps({"error": "File not found"})
            )
            return

        # Delete the file
        os.remove(path)
        dprint("File deleted successfully")

        # Send success response
        httpResponse.WriteResponse(
            code=200,
            headers={"Access-Control-Allow-Origin": "*"},
            contentType="application/json",
            contentCharset="UTF-8",
            content=json.dumps({"deleted": True})
        )
        
    except Exception as e:
        import sys
        sys.print_exception(e)
        dprint("Error deleting file: {}".format(str(e)))
        httpResponse.WriteResponse(
            code=500,
            headers={"Access-Control-Allow-Origin": "*"},
            contentType="application/json",
            contentCharset="UTF-8",
            content=json.dumps({"error": str(e)})
        )
        return

@MicroWebSrv.route('/deletefile', 'OPTIONS')
def delete_file_options(httpClient, httpResponse):
    dprint("Received deletefile OPTIONS request")
    httpResponse.WriteResponse(
        code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400"
        },
        contentType="text/plain",
        contentCharset="UTF-8",
        content=""
    )

@MicroWebSrv.route('/renamefile')
def rename_file(httpClient, httpResponse):
    try:
        args = httpClient.GetRequestQueryParams()
        old_path = args.get('old_path', None)
        new_path = args.get('new_path', None)
        
        if not old_path or not new_path:
            dprint("Missing path parameters")
            httpResponse.WriteResponse(
                code=400,
                headers={"Access-Control-Allow-Origin": "*"},
                contentType="application/json",
                contentCharset="UTF-8",
                content=json.dumps({"error": "Missing path parameters"})
            )
            return

        dprint("Renaming file from {} to {}".format(old_path, new_path))
        
        # Check if source file exists
        try:
            os.stat(old_path)
        except OSError:
            dprint("Source file not found: {}".format(old_path))
            httpResponse.WriteResponse(
                code=404,
                headers={"Access-Control-Allow-Origin": "*"},
                contentType="application/json",
                contentCharset="UTF-8",
                content=json.dumps({"error": "Source file not found"})
            )
            return

        # Rename the file
        os.rename(old_path, new_path)
        dprint("File renamed successfully")

        # Send success response
        httpResponse.WriteResponse(
            code=200,
            headers={"Access-Control-Allow-Origin": "*"},
            contentType="application/json",
            contentCharset="UTF-8",
            content=json.dumps({"renamed": True})
        )
        
    except Exception as e:
        import sys
        sys.print_exception(e)
        dprint("Error renaming file: {}".format(str(e)))
        httpResponse.WriteResponse(
            code=500,
            headers={"Access-Control-Allow-Origin": "*"},
            contentType="application/json",
            contentCharset="UTF-8",
            content=json.dumps({"error": str(e)})
        )
        return

@MicroWebSrv.route('/reset')
def reset_device(httpClient, httpResponse):
    try:
        dprint("Resetting device")
        # Send success response before reset
        httpResponse.WriteResponse(
            code=200,
            headers={"Access-Control-Allow-Origin": "*"},
            contentType="application/json",
            contentCharset="UTF-8",
            content=json.dumps({"reset": True})
        )
        # Import machine for reset
        import machine
        # Schedule reset after response is sent
        machine.reset()
    except Exception as e:
        import sys
        sys.print_exception(e)
        dprint("Error resetting device: {}".format(str(e)))
        httpResponse.WriteResponse(
            code=500,
            headers={"Access-Control-Allow-Origin": "*"},
            contentType="application/json",
            contentCharset="UTF-8",
            content=json.dumps({"error": str(e)})
        )
        return

mws = MicroWebSrv(webPath="/weditor")

def start_debug():
    dprint("STARTING WEB SERVER")
    try:
        mws.Start(threaded=False)
    except KeyboardInterrupt:
        pass
    finally:
        dprint("STOPPING WEB SERVER")
        mws.Stop()
        mws._server.close()
        del sys.modules['microWebSrv']

def start():
    mws.Start(threaded=True)

start()


import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = "received_files"

class CustomHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.path = 'upload_form.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/upload':
            # Extract the length of the data
            content_length = int(self.headers['Content-Length'])
            
            print("content_length=",content_length)
            
            # Read the data
            post_data = self.rfile.read(content_length)

            # Parse the data to extract the file name
            content_type = self.headers['content-type']
            print("content_type=",content_type)
            
            if 'multipart/form-data;' in content_type:
                boundary = content_type.split("=")[1].encode()
                print("boundary=",boundary)
                parts = post_data.split(boundary)
                for part in parts:
                    if b'Content-Disposition: form-data;' in part:
                        disposition = part.split(b'\r\n')[1].decode()
                        # Find the filename
                        fn_idx = disposition.find('filename="')
                        if fn_idx >= 0:
                            fn_idx += 10
                            #print("part=",part)
                            print("disposition=",disposition)
                            print("fn_idx=",fn_idx)
                            filename = disposition[fn_idx:disposition.find('"', fn_idx)]
                            print("filename=",filename)
                            filepath = os.path.join(DIRECTORY, filename)
                            filedata = part.split(b'\r\n\r\n')[1].rstrip(b'\r\n--')
                            # Write the file data to a new file
                            with open(filepath, 'wb') as f:
                                f.write(filedata)
                            self.send_response(200)
                            self.end_headers()
                            self.wfile.write(f"File {filename} uploaded successfully.".encode())
                            return

            # If the file name is not found, send a 400 response
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"File not uploaded.")


if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

Handler = CustomHttpRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()

from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
import json
headers=json.load(open('web/public/vercel.json'))['headers'][0]['headers']
class Handler(SimpleHTTPRequestHandler):
 def end_headers(self):
  self.send_header('Access-Control-Allow-Origin','*')
  for h in headers:self.send_header(h['key'],h['value'])
  super().end_headers()
ThreadingHTTPServer(('127.0.0.1',4178),partial(Handler,directory='web/dist')).serve_forever()

#!/usr/bin/env python3
import json, time, urllib.request, urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

HOST='0.0.0.0'; PORT=8120
CLOUDANT_HOST='7d5f26cb-f87a-493c-b84f-7d1357a2f9b3-bluemix.cloudantnosqldb.appdomain.cloud'
CLOUDANT_APIKEY='JMnwCf-oFo6LB32UtJH7xSRAzr1240j_vZPyKGNpZMfZ'
DB='careroute_demo'
ROOT=Path(__file__).parent

def iam_token():
    data=urllib.parse.urlencode({'grant_type':'urn:ibm:params:oauth:grant-type:apikey','apikey':CLOUDANT_APIKEY}).encode()
    req=urllib.request.Request('https://iam.cloud.ibm.com/identity/token', data=data, method='POST', headers={'Content-Type':'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode()).get('access_token','')

def cloudant(method, path, body=None):
    tok=iam_token()
    req=urllib.request.Request(f'https://{CLOUDANT_HOST}{path}', method=method, headers={'Authorization':f'Bearer {tok}','Content-Type':'application/json'})
    if body is not None: req.data=json.dumps(body).encode()
    with urllib.request.urlopen(req, timeout=20) as r: return r.read().decode()

class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Headers','content-type')
        self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS')
    def do_OPTIONS(self): self.send_response(204); self._cors(); self.end_headers()
    def do_GET(self):
        if self.path in ('/','/index.html'):
            b=(ROOT/'index.html').read_bytes(); self.send_response(200); self._cors(); self.send_header('Content-Type','text/html'); self.end_headers(); self.wfile.write(b); return
        if self.path=='/monitor':
            b=(ROOT/'monitor.html').read_bytes(); self.send_response(200); self._cors(); self.send_header('Content-Type','text/html'); self.end_headers(); self.wfile.write(b); return
        if self.path=='/api/registrations':
            try:
                out=json.loads(cloudant('POST', f'/{DB}/_find', {"selector":{"type":"registration"},"limit":100}))
                rows=[{"timestamp":d.get('timestamp'),"firstName":d.get('firstName'),"lastName":d.get('lastName'),"email":d.get('email'),"insurance":d.get('insurance')} for d in out.get('docs',[])]
                b=json.dumps({"rows":rows}).encode(); self.send_response(200); self._cors(); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(b)
            except Exception as e:
                b=json.dumps({"rows":[],"error":str(e)}).encode(); self.send_response(500); self._cors(); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(b)
            return
        self.send_response(404); self._cors(); self.end_headers()
    def do_POST(self):
        if self.path=='/api/register':
            n=int(self.headers.get('Content-Length','0')); payload=json.loads(self.rfile.read(n).decode() or '{}')
            payload['type']='registration'; payload.setdefault('timestamp', int(time.time()*1000))
            try:
                out=cloudant('POST', f'/{DB}', payload)
                self.send_response(200); self._cors(); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(out.encode())
            except Exception as e:
                self.send_response(500); self._cors(); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(json.dumps({'ok':False,'error':str(e)}).encode())
            return
        self.send_response(404); self._cors(); self.end_headers()

if __name__=='__main__':
    print(f'live monitor on http://127.0.0.1:{PORT}')
    ThreadingHTTPServer((HOST,PORT),H).serve_forever()

import json

import requests
from pbx_gs_python_utils.utils.Misc import Misc


class Jupyter_API:
    def __init__(self,server=None, token=None):
        self.server =  server
        self.token  = token

    # this is not working
    # def create(self,target):
    #     data = {'ext': 'txt', 'type': 'Text File'}
    #     return self.http_post('api/contents/{0}'.format(target),data)

    def contents(self,target=None):
        path = 'api/contents'
        if target:
            path = '{0}/{1}'.format(path,target)
        return self.http_get(path)

    def http_get(self, path):
        url = self.url(path)
        headers = {'Authorization': 'Token {0}'.format(self.token)}
        response = requests.get(url,headers=headers)
        if response.status_code != 404:
            return response.json()

    def http_delete(self, path):
        url = self.url(path)
        headers = {
                'Authorization': 'Token {0}'.format(self.token)}
        response = requests.delete(url,headers=headers)
        if response.status_code != 404:
            if response.text != '':
                return response.json()
            return {}

    def http_patch(self, path, data):
        url = self.url(path)
        headers = {
                'Authorization': 'Token {0}'.format(self.token),
                'Content-Type' :  'application/json' }
        response = requests.patch(url,data=json.dumps(data), headers=headers)
        if response.status_code != 404:
            return response.json()

    def http_post(self, path, data):
        url = self.url(path)
        headers = {
                'Authorization': 'Token {0}'.format(self.token),
                'Content-Type' :  'application/json' }
        response = requests.post(url,data=json.dumps(data), headers=headers)
        if response.status_code != 404:
            return response.json()

    def kernels(self):
        items = {}
        for kernel in self.http_get('api/kernels'):
            items[kernel.get('id')] = kernel
        return items

    def notebook_content(self,path):
        return self.contents(path).get('content')

    def notebook_cells(self,path):
        return self.notebook_content(path).get('cells')

    def notebook_codes_source(self,path):
        codes_source = []
        for cell in self.notebook_content(path).get('cells'):
            if cell.get('cell_type') == 'code':
                codes_source.append(cell.get('source'))
        return codes_source

    def notebook_exists(self,path):
        return self.contents(path) is not None

    def session(self,session_id):
        return self.http_get('sessions/{0}'.format(session_id))

    def session_get(self, notebook_path):
        path = 'sessions'
        data = { 'path': notebook_path  ,
                 'type': 'python3' }
        return self.http_post(path, data)

    def session_delete(self,session_id):
        if self.session_exists(session_id) is False: return False
        self.http_delete('sessions/{0}'.format(session_id))
        return self.session_exists(session_id) is False

    def session_delete_all(self):
        for session_id in self.sessions_ids():
            self.session_delete(session_id)
        return self

    def session_exists(self, session_id):
        return self.session(session_id) is not None

    def session_rename(self, session_id, name):
        path = 'sessions/{0}'.format(session_id)
        data = { 'id': session_id, 'name': name}

        return self.http_patch(path, data)
        pass

    def status(self):
        return self.http_get('api/status')

    def url(self,path=None):
        if   path is None or len(path) == 0: path = '/'
        elif path[0] != '/'                : path = '/' + path

        if path.startswith('/api/') is False: path = '/api{0}'.format(path)

        return "{0}{1}".format(self.server,path)

    def version(self):
        return self.http_get('api')




    # experimental
    def kernel_code_execute(self,code_to_execute):

        from websocket import create_connection
        import uuid
        import datetime

        kernel_id = list(set(self.kernels())).pop()
        headers   = {'Authorization': 'Token {0}'.format(self.token)}
        url       = "ws://localhost:8888/api/kernels/{0}/channels".format(kernel_id)
        ws        = create_connection(url, header=headers)

        def send_execute_request(code):
            msg_type = 'execute_request';
            content = {'code': code, 'silent': False}


            hdr = {'msg_id': uuid.uuid1().hex,
                   'username': 'test',
                   'session': uuid.uuid1().hex,
                   'data': datetime.datetime.now().isoformat(),
                   'msg_type': msg_type,
                   'version': '5.0'}
            msg = {'header': hdr, 'parent_header': hdr,
                   'metadata': {},
                   'content': content}
            return msg

        ws.send(json.dumps(send_execute_request(code_to_execute)))
        messages = []
        msg_type = ''
        while msg_type != "execute_reply":
            rsp         = json.loads(ws.recv())
            content     = rsp.get("content")
            msg_type    = rsp.get("msg_type")
            messages.append({'msg_type': msg_type, 'content': content})
        ws.close()

        return messages
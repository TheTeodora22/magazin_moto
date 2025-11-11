from datetime import datetime

def get_ip(request):
    req_headers = request.META
    str_lista_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if str_lista_ip:
        return str_lista_ip.split(',')[-1].strip()
    else:
        return request.META.get('REMOTE_ADDR')


class Accesare:
    _next_id = 1
    _param_keys = ["data", "ultimele", "accesari", "iduri", "dubluri", "tabel"]

    def __init__(self, ip_client, url, data=None, pagina="/"):
        self.id = Accesare._next_id
        Accesare._next_id += 1
        self.ip_client = ip_client
        self._url = url
        self._pagina = pagina
        self._data = data or datetime.now()

    #a
    def lista_parametri(self, query_dict=None):
        if query_dict is None:
            return [(k, None) for k in self._param_keys]
        result = []
        lower_map = {k.lower(): v for k, v in query_dict.items()}
        for k in self._param_keys:
            v = lower_map.get(k, None)
            result.append((k, v))
        for k, v in query_dict.items():
            if k.lower() not in self._param_keys:
                result.append((k, v))
        return result
    #b
    def url(self):
        return self._url
    #c
    def data(self, fmt=None):
        return self._data if fmt is None else self._data.strftime(fmt)
    #d
    def pagina(self):
        return self._pagina

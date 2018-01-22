from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from dwapi.datawiz import DW


class DatawizMiddleware:
    """
    Instance of this class is used to associate DW instance with django session.
    This discard need in repeated authorization to datawiz api for every page that uses it.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self._dw_pool = set()

    def __call__(self, request):
        dw_api_key = request.session.get('dw_api_key', None)
        dw_api_secret = request.session.get('dw_api_secret', None)
        if dw_api_key and dw_api_secret:
            dw = self.get_dw_from_pool(dw_api_key, dw_api_secret)
            if dw:
                client = getattr(dw, 'client', None)
                if client:
                    setattr(client, 'info', dw.get_client_info())
                    # print(client.info['name'])
            setattr(request, 'dw', dw)

        response = self.get_response(request)

        return response

    def get_dw_from_pool(self, dw_api_key: str, dw_api_secret: str='', default=None):
        """
        Gets DW object from pool if it was there.

        If DW instance is not in pool and dw_api_secret was passed then
        creates DW object,
        adds it to pool and
        returns it.

        If DW object was not found in pool and dw_api_secret was not passed returns default's value.

        :param dw_api_key: DW API_KEY value of str type.
        :param dw_api_secret: DW API_SECRET value of str type.
        :param default: value to be returned if nothing better was found or done.
        :return: DW instance or default's value.
        """
        for element in self._dw_pool:
            if getattr(element, 'API_KEY', '') == dw_api_key:
                return element
        if dw_api_key and dw_api_secret:
            try:
                dw = DW(dw_api_key, dw_api_secret)
            except InvalidGrantError:
                return None
            else:
                self._dw_pool.add(dw)
                return dw
        return default

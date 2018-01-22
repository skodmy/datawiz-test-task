from django.urls import include


class DWClientSite:
    @property
    def urls(self):
        return include('dw_client.urls', namespace='dw-client')


site = DWClientSite()

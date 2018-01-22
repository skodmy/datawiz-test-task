from django.urls import path, include

from .views import sign_in, index, profile_info, sign_out, stats_page, sales_statistics
from .apps import DwClientConfig

app_name = DwClientConfig.name

sign_urlpatterns = [
    path('in/', sign_in, name='in'),
    path('out/', sign_out, name='out'),
]

auth_urlpatterns = [
    path('sign/', include((sign_urlpatterns, app_name), namespace='sign')),
]

profile_urlpatterns = [
    path('info/', profile_info, name='info'),
]

sales_urlpatterns = [
    path('', stats_page, name='stats-page'),
    path('statistics/<str:date_from>--<str:date_to>/<int:page_number>/', sales_statistics, name='statistics'),
]

urlpatterns = [
    # authorization urls group
    path('auth/', include((auth_urlpatterns, app_name), namespace='auth')),
    path('', index, name='index'),
    # profile urls group
    path('profile/', include((profile_urlpatterns, app_name), namespace='profile')),
    # sales urls group
    path('sales/', include((sales_urlpatterns, app_name), namespace='sales')),
]

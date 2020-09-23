from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from django.views.static import serve
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view

from apps.users.views import UpdateProfileViewSet
from apps.property.views import SalutariumViewSet, PaperViewSet, DeviceTokenViewSet

schema_view = get_swagger_view(title='Meal Paper API')

router = DefaultRouter()
router.register(r'update-profile', UpdateProfileViewSet, base_name='update_profile')
router.register(r'salutarium', SalutariumViewSet, base_name='salutarium')
router.register(r'paper', PaperViewSet, base_name='paper')
router.register(r'device-token', DeviceTokenViewSet, base_name='device_token')

urlpatterns = [
    url(r'^$', schema_view),
    url('auth-users/', include(('apps.users.urls', 'auth-users'), namespace='auth-users')),
    url(r'^api/', include(router.urls)),
    path('admin/', admin.site.urls),
    url(r'^api-auth/', include(('rest_framework.urls', 'rest_framework'), namespace='rest_framework')),
    url(r'^api/download/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT,}),
    url(r'^api/media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT,}),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]

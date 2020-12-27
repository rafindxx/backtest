from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from config.views import index


urlpatterns = [
    # django admin urls
    path('superadmin/', admin.site.urls),
    #home url
    path('', index, name='home'),
    path('calculation/', include('calculation.urls')),
]



if settings.DEBUG:
    # import debug_toolbar
    # urlpatterns += [
    #     path('__debug__/', include(debug_toolbar.urls)),
    # ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

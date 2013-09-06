from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'MSMaster.views.home', name='home'),
    # url(r'^MSMaster/', include('MSMaster.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'main.views.main'),
    url(r'^tree/$', 'main.views.tree'),
    url(r'^ms/([^/]+)/$', 'MS.views.get_ms_list'),
    url(r'^room/([^/]+)/$', 'room.views.get_room_list'),
    url(r'^task/([^/]+)/$', 'task.views.get_task_list'),
)

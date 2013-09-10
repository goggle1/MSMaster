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
    url(r'^get_ms_list/([^/]+)/$',      'MS.views.get_ms_list'),
    url(r'^show_ms_info/([^/]+)/$',     'MS.views.show_ms_list'),
    url(r'^sync_ms_db/([^/]+)/$',       'MS.views.sync_ms_db'),
    url(r'^get_room_list/([^/]+)/$',    'room.views.get_room_list'),
    url(r'^show_room_info/([^/]+)/$',   'room.views.show_room_list'),
    url(r'^sync_room_db/([^/]+)/$',     'room.views.sync_room_db'),
    url(r'^task/([^/]+)/$',             'task.views.get_task_list'),
)

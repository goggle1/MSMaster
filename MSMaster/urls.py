from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'MSMaster.views.home', name='home'),
    # url(r'^MSMaster/', include('MSMaster.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$',       'main.views.login'),
    url(r'^accounts/logout/$',      'main.views.logout'),
    url(r'^get_username/$',         'main.views.get_username'),
    url(r'^$',              'main.views.main'),
    url(r'^tree/$',         'main.views.tree'),
    url(r'^get_ms_list/([^/]+)/$',      'MS.views.get_ms_list'),
    url(r'^show_ms_info/([^/]+)/$',     'MS.views.show_ms_list'),
    url(r'^sync_ms_db/([^/]+)/$',       'MS.views.sync_ms_db'),
    url(r'^sync_ms_status/([^/]+)/$',   'MS.views.sync_ms_status'),
    url(r'^get_room_list/([^/]+)/$',    'room.views.get_room_list'),
    url(r'^show_room_info/([^/]+)/$',   'room.views.show_room_list'),
    url(r'^sync_room_db/([^/]+)/$',     'room.views.sync_room_db'),
    url(r'^sync_room_status/([^/]+)/$', 'room.views.sync_room_status'),
    url(r'^add_hot_tasks/([^/]+)/$',    'room.views.add_hot_tasks'),
    url(r'^delete_cold_tasks/([^/]+)/$','room.views.delete_cold_tasks'),
    url(r'^get_task_list/([^/]+)/$',    'task.views.get_task_list'),
    url(r'^sync_hash_db/([^/]+)/$',     'task.views.sync_hash_db'),
    url(r'^down_hot_tasks/([^/]+)/$',   'task.views.down_hot_tasks'),
    url(r'^down_cold_tasks/([^/]+)/$',  'task.views.down_cold_tasks'),
    url(r'^show_task_info/([^/]+)/$',   'task.views.show_task_list'),
    url(r'^upload_hits_num/([^/]+)/$',  'task.views.upload_hits_num'),
    url(r'^calc_cold/([^/]+)/$',        'task.views.calc_cold'),
    url(r'^get_operation_list/([^/]+)/$', 'operation.views.get_operation_list'),
    url(r'^show_operation_info/([^/]+)/$','operation.views.show_operation_list'),
)

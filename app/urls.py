from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^$', views.landing, name='landing'),
    url(r'^signup/$', views.signup_view, name='signup'),
    url(r'^userprofile/$', views.UserProfile.as_view(), name='userprofile'),
]

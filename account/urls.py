from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^signup/$', views.UserRegistrationView.as_view(), name='signup'),
    url(r'^user/email-verification/(?P<key>[\w]+)/$', views.UserEmailVerify.as_view()),
    url(r'^login/$', views.UserLoginView.as_view(), name='login'),
    url(r'^logout/$', views.UserLogoutView.as_view(), name='logout'),
    url(r'^$', views.HomePage.as_view(), name='index'),
]
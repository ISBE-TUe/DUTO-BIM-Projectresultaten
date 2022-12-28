"""validator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from validator.online import views
from django.views.generic.base import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer

##router = routers.DefaultRouter()
##router.register(r'users', views.UserViewSet)
##router.register(r'groups', views.GroupViewSet)

#router = routers.DefaultRouter()
#router.register(r'projects', views.ProjectViewSet)

schema_url_patterns = [    
    path('api/projects/', views.api.getProjects),
    path('api/checks/', views.api.getChecks),
    path('api/reports/', views.api.getReports),
    path('api/results/', views.api.getResults),
]

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(schema_url_patterns)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path("register/", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name= "logout"),
    path('settings/', views.settings, name='settings'),
    path('', views.getProjects, name='projects'),
    path('newproject/', views.createNewProject, name='newproject'),
    path('newifcproject/', views.createNewIfcProject, name='newifcproject'),  
    path('newilsproject/', views.createNewIlsProject, name='newilsproject'),   
    path('newilscheckproject/', views.createNewIlsCheckProject, name='newilscheckproject'),
    path('projects/', views.getProjects, name='projects'),
    path('projects/<int:projectId>/', views.getChecks, name='checks'),
    path('deleteproject/<int:projectId>/', views.deleteProject, name='deleteproject'),
    path('newcheck/<int:projectId>/', views.createNewCheck, name='newcheck'),
    path('downloadFile/<str:filename>', views.downloadFile, name='downloadFile'),
    path('deletecheck/<int:checkId>/', views.deleteCheck, name='deletecheck'),
    path('checks/', views.getAllChecks, name='allchecks'),
    path('reports/', views.getAllReports, name='allreports'),
    path('reports/<int:checkId>/<str:type>/', views.getReports, name='reports'), 
    path('deletereport/<int:reportId>/', views.deleteReport, name='deletereport'),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='swagger-ui'),
    path('openapi/', get_schema_view(
        title="BIMValidator DHRD project",
        description="The API for validating your BIM models",
        version="1.0.0",
        #renderer_classes=[JSONOpenAPIRenderer],
        #urlconf='validator.urls',
        patterns=schema_url_patterns,
    ), name='openapi-schema'),
]

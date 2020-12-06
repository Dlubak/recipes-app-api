from django.urls import path
from user import views
# from rest_framework.routers import DefaultRouter
# from snippets import views

# # Create a router and register our viewsets with it.
# router = DefaultRouter()
# router.register(r'snippets', views.SnippetViewSet)
# router.register(r'users', views.UserViewSet)

app_name = 'user'
urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name="create"),
    path('token/', views.CreateTokenView.as_view(), name="token"),
]

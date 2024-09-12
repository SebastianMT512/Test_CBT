from django.urls import path,include
from rest_framework import routers
import movies_api.views as v

router = routers.DefaultRouter()
router.register(r'movie', v.MoviesApiView, basename='movie')

urlpatterns = [
   path('', include(router.urls))
]

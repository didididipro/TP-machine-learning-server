from django.urls import path
from .views import PredictCancerView

urlpatterns = [
    path("predict/", PredictCancerView.as_view(), name="predict_cancer"),
]

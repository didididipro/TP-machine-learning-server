from django.urls import path
from .views import PredictCancerView, PredictionsView

urlpatterns = [
    path("predict/", PredictCancerView.as_view(), name="predict_cancer"),
    path("predictions/", PredictionsView.as_view(), name="predictions"),
]

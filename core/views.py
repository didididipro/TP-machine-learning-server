from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
import joblib
import numpy as np
from .serializers import PredictionInputSerializer, PredictionSerializer
import os
from . import serializers
from . import models


class PredictCancerView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load model
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "colon_cancer_model.pkl",
        )
        self.model = joblib.load(model_path)

    def post(self, request):
        # Handle prediction
        if isinstance(request.data, list):
            results = []
            for item in request.data:
                serializer = PredictionInputSerializer(data=item)
                if serializer.is_valid():
                    dao = serializer.validated_data["DAO"]
                    nom_patient = serializer.validated_data["nom_patient"]

                    # Make prediction
                    prediction = self.model.predict([[dao]])[0]
                    # Map prediction to class index
                    class_index = np.where(self.model.classes_ == prediction)[
                        0
                    ][0]
                    confidence = self.model.predict_proba([[dao]])[0][
                        class_index
                    ]

                    # Prepare result
                    result = {
                        "nom_patient": nom_patient,
                        "value": dao,
                        "pred": "Tumoral"
                        if prediction == "tumoral"
                        else "Normal",
                        "confidence": f"{confidence:.2f}",
                    }
                    pred_serializer = PredictionSerializer(data=result)
                    if pred_serializer.is_valid():
                        pred_serializer.save()
                        results.append(pred_serializer.data)
                    else:
                        return Response(
                            pred_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(results, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PredictionsView(ListAPIView):
    serializer_class = serializers.PredictionSerializer
    queryset = models.Prediction.objects.order_by("-id").all()

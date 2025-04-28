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
        # Load model and scaler
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_path, "colon_cancer_model.pkl")
        scaler_path = os.path.join(base_path, "scaler.pkl")
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

    def post(self, request):
        # Handle prediction
        if isinstance(request.data, list):
            results = []
            for item in request.data:
                serializer = PredictionInputSerializer(data=item)
                if serializer.is_valid():
                    UGP2 = serializer.validated_data["UGP2"]
                    nom_patient = serializer.validated_data["nom_patient"]

                    # Normalize input
                    UGP2_scaled = self.scaler.transform([[UGP2]])

                    # Make prediction
                    prediction = self.model.predict(UGP2_scaled)[0]
                    # Convert prediction to string
                    pred_label = "Tumoral" if prediction == 1 else "Normal"

                    # Get confidence if available
                    confidence = None
                    if hasattr(self.model, "predict_proba"):
                        class_index = 1 if prediction == 1 else 0
                        confidence = self.model.predict_proba(UGP2_scaled)[0][
                            class_index
                        ]
                    else:
                        confidence = 1.0  # Default to 1.0 if predict_proba is unavailable

                    # Prepare result
                    result = {
                        "nom_patient": nom_patient,
                        "value": UGP2,
                        "pred": pred_label,
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

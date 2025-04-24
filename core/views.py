from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import joblib
import numpy as np
from .serializers import PredictionInputSerializer, PredictionOutputSerializer
import os


class PredictCancerView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load model
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "colon_cancer_model.pkl",
        )
        self.model = joblib.load(model_path)
        # Ensure model has classes_ attribute
        if not hasattr(self.model, "classes_"):
            raise ValueError(
                "Model is not a classifier with classes_ attribute"
            )
        # Verify expected classes
        self.expected_classes = ["normal", "tumoral"]
        if not np.array_equal(
            self.model.classes_, np.array(self.expected_classes)
        ):
            raise ValueError(
                f"Model classes must be {self.expected_classes}, got {self.model.classes_}"
            )

    def post(self, request):
        # Handle bulk prediction
        if isinstance(request.data, list):
            results = []
            for item in request.data:
                serializer = PredictionInputSerializer(data=item)
                if serializer.is_valid():
                    dao = serializer.validated_data["DAO"]
                    id_sample = serializer.validated_data["id_sample"]

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
                        "id_sample": id_sample,
                        "prediction": "Tumoral"
                        if prediction == "tumoral"
                        else "Normal",
                        "confidence": f"{confidence:.2f}",
                    }
                    output_serializer = PredictionOutputSerializer(data=result)
                    if output_serializer.is_valid():
                        results.append(output_serializer.data)
                    else:
                        return Response(
                            output_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(results, status=status.HTTP_200_OK)

        # Handle single prediction
        serializer = PredictionInputSerializer(data=request.data)
        if serializer.is_valid():
            dao = serializer.validated_data["DAO"]
            id_sample = serializer.validated_data["id_sample"]

            # Make prediction
            prediction = self.model.predict([[dao]])[0]
            # Map prediction to class index
            class_index = np.where(self.model.classes_ == prediction)[0][0]
            confidence = self.model.predict_proba([[dao]])[0][class_index]

            # Prepare response
            result = {
                "id_sample": id_sample,
                "prediction": "Tumoral"
                if prediction == "tumoral"
                else "Normal",
                "confidence": f"{confidence:.2f}",
            }
            output_serializer = PredictionOutputSerializer(data=result)
            if output_serializer.is_valid():
                return Response(
                    output_serializer.data, status=status.HTTP_200_OK
                )
            return Response(
                output_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

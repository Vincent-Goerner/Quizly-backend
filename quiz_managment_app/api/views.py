import json

from django.db import DatabaseError
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from quiz_managment_app.models import Quiz
from .serializers import YTURLSerializer, QuizSerializer, QuizPatchSerializer
from .utils import QuizGenerator
from auth_app.api.permissions import CookieJWTAuthentication, IsOwner



class QuizCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        serializer = YTURLSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        url = serializer.validated_data["url"]
        processor = QuizGenerator()

        try:
            processor.fetch_audio_from_url(url)

            processor.transcribe_audio()

            processor.generate_quiz()

            final_text = processor.clean_quiz_text()

            import json
            try:
                generated_quiz = json.loads(final_text)
            except Exception:
                return Response(
                    {"detail": "Generated quiz is not valid JSON."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            quiz = serializer.save(generated_quiz=generated_quiz)
            return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)

        finally:
            processor.cleanup()


class QuizListView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, *args, **kwargs):
        try:
            quiz = Quiz.objects.filter(owner=self.request.user)
            serializer = QuizSerializer(
                quiz, many=True, context={"request": request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {"detail": {str(e)}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuizDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]
    authentication_classes = [CookieJWTAuthentication]

    def get_object(self, pk):
        quiz = get_object_or_404(Quiz, id=pk)
        if quiz.owner != self.request.user:
            raise PermissionDenied("You do not have permission to access this quiz.")
        return quiz

    def get(self, request, pk):
        quiz = self.get_object(pk)
        serializer = QuizSerializer(quiz, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        quiz = self.get_object(pk)
        serializer = QuizPatchSerializer(
            quiz, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            quiz = serializer.save()
            return Response(
                QuizSerializer(quiz, context={"request": request}).data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        quiz = self.get_object(pk)
        quiz.questions.all().delete()
        try:
            quiz.delete()
        except DatabaseError as e:
            return Response(
                {"error": f"An unexpected error occurred.: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
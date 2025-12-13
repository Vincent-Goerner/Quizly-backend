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
from .permissions import CookieJWTAuthentication, IsOwner



class QuizCreateView(APIView):
    """
    API view to create a Quiz from a YouTube URL. The process involves
    downloading audio, transcribing it, generating a quiz via AI, and
    saving it to the database.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        """
        Handles POST requests to create a quiz.

        Steps:
        1. Validates the provided YouTube URL using `YTURLSerializer`.
        2. Uses `QuizGenerator` to download audio, transcribe, and generate quiz JSON.
        3. Cleans the generated text and parses it as JSON.
        4. Saves the quiz and returns serialized data.

        Returns:
            Response: Serialized quiz data with HTTP 201 on success,
                      or an error response on failure.
        """
        serializer = YTURLSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        url = serializer.validated_data["url"]
        processor = QuizGenerator()

        try:
            processor.fetch_audio_from_url(url)

            processor.transcribe_audio()

            processor.generate_quiz()

            final_text = processor.clean_quiz_text()

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
    """
    API view to list all quizzes owned by the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve all quizzes for the authenticated user.

        Returns:
            Response: Serialized list of quizzes with HTTP 200 on success,
                      or an error response with HTTP 500 if an exception occurs.
        """
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
    """
    API view to retrieve, update, or delete a specific Quiz instance.
    Only the owner of the quiz is allowed to perform these actions.
    """
    permission_classes = [IsAuthenticated, IsOwner]
    authentication_classes = [CookieJWTAuthentication]

    def get_object(self, pk):
        """
        Retrieves the Quiz object by primary key and checks ownership.
        Raises PermissionDenied if the authenticated user is not the owner.
        """
        quiz = get_object_or_404(Quiz, id=pk)
        if quiz.owner != self.request.user:
            raise PermissionDenied("You do not have permission to access this quiz.")
        return quiz

    def get(self, request, pk):
        """
        Handles GET requests to retrieve a quiz's details.

        Returns:
            Response: Serialized quiz data with HTTP 200.
        """
        quiz = self.get_object(pk)
        serializer = QuizSerializer(quiz, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """
        Handles PATCH requests to update a quiz's title or description.
        Only these fields are editable.

        Returns:
            Response: Serialized updated quiz with HTTP 200 on success,
                      or validation errors with HTTP 400.
        """
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
        """
        Handles DELETE requests to remove a quiz and its associated questions.

        Returns:
            Response: HTTP 204 on success, or HTTP 500 if a database error occurs.
        """
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
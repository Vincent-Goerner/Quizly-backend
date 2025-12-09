from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    """
    Represents a quiz created by a user.

    Attributes:
        owner (ForeignKey): The user who created the quiz.
        title (CharField): Title of the quiz.
        description (CharField): Short description of the quiz.
        created_at (DateTimeField): Timestamp when the quiz was created.
        updated_at (DateTimeField): Timestamp when the quiz was last updated.
        video_url (CharField): URL of the YouTube video associated with the quiz.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz")
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video_url = models.CharField(max_length=255)

class Question(models.Model):
    """
    Represents a single question within a quiz.

    Attributes:
        quiz (ForeignKey): The quiz this question belongs to.
        question_title (CharField): The text of the question.
        question_options (JSONField): List of 4 possible answer options.
        answer (CharField): Correct answer for the question.
        created_at (DateTimeField): Timestamp when the question was created.
        updated_at (DateTimeField): Timestamp when the question was last updated.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_title = models.CharField(max_length=255)
    question_options = models.JSONField(default=list)
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
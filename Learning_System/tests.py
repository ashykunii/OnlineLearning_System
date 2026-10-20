from django.test import TestCase
from Learning_System.models import Lesson, Course, Instructor, User

class LessonYouTubeHelperTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='instructor1', password='password123', role='instructor')
        self.instructor = Instructor.objects.create(user=self.user)
        self.course = Course.objects.create(
            instructor=self.instructor,
            title='Test Course',
            description='A test course description.'
        )

    def test_extracts_youtube_video_id(self):
        url_formats = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=shared", "dQw4w9WgXcQ"),
            ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("", ""),
            ("https://example.com/some-other-video.mp4", ""),
        ]

        for url, expected_id in url_formats:
            lesson = Lesson(course=self.course, title='Test Lesson', video_url=url)
            self.assertEqual(lesson.youtube_video_id, expected_id, f"Failed for URL: {url}")

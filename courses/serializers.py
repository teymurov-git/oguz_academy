from rest_framework import serializers
from courses.models import Exam, ExamRegistration, CourseCategory, Course, Group, GroupStudent
from students.serializers import StudentListSerializer
from teachers.serializers import TeacherListSerializer


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class GroupStudentSerializer(serializers.ModelSerializer):
    student = StudentListSerializer(read_only=True)

    class Meta:
        model = GroupStudent
        fields = '__all__'


class GroupListSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('id', 'name', 'course_name', 'teacher_name', 'type', 'status', 'start_date', 'schedule_text', 'student_count', 'max_students', 'is_active')

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name() if obj.teacher else None

    def get_student_count(self, obj):
        return obj.group_students.count()


class GroupDetailSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    teacher = TeacherListSerializer(read_only=True)
    students = GroupStudentSerializer(many=True, read_only=True, source='group_students')

    class Meta:
        model = Group
        fields = '__all__'


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'


class ExamRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamRegistration
        fields = '__all__'

from rest_framework import serializers
from exam_system.models import (
    Exam, Question, Variant, StudentExam,
    StudentAnswer, MarkerConsensus, Competition
)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class QuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'question_type', 'text', 'difficulty', 'points', 'sort_order', 'is_active')


class VariantSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Variant
        fields = '__all__'

    def get_question_count(self, obj):
        return obj.questions.count()


class VariantDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Variant
        fields = '__all__'


class ExamListSerializer(serializers.ModelSerializer):
    registered_count = serializers.ReadOnlyField()
    is_registration_open = serializers.ReadOnlyField()
    is_active_now = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = (
            'id', 'title', 'slug', 'exam_type', 'status', 'subject',
            'total_questions', 'total_time_minutes', 'passing_score', 'max_score',
            'start_datetime', 'end_datetime', 'registration_deadline',
            'price', 'max_participants', 'location',
            'is_active', 'registered_count', 'is_registration_open', 'is_active_now',
            'created_by_name', 'created_at',
        )

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None


class ExamDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    variants = VariantSerializer(many=True, read_only=True)
    registered_count = serializers.ReadOnlyField()
    is_registration_open = serializers.ReadOnlyField()
    is_active_now = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = '__all__'

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = '__all__'


class StudentAnswerDetailSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = StudentAnswer
        fields = '__all__'


class MarkerConsensusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkerConsensus
        fields = '__all__'


class StudentExamListSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True, default=None)

    class Meta:
        model = StudentExam
        fields = (
            'id', 'student_name', 'exam', 'exam_title', 'variant', 'variant_name',
            'status', 'score', 'percentage', 'passed',
            'started_at', 'completed_at', 'time_spent_seconds', 'created_at',
        )

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() if obj.student else None


class StudentExamDetailSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    exam = ExamListSerializer(read_only=True)
    variant = VariantSerializer(read_only=True)
    answers = StudentAnswerDetailSerializer(many=True, read_only=True)

    class Meta:
        model = StudentExam
        fields = '__all__'

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() if obj.student else None


class CompetitionListSerializer(serializers.ModelSerializer):
    exam_count = serializers.SerializerMethodField()

    class Meta:
        model = Competition
        fields = (
            'id', 'title', 'slug', 'description', 'status',
            'start_datetime', 'end_datetime', 'is_active',
            'exam_count', 'created_at',
        )

    def get_exam_count(self, obj):
        return obj.exams.count()


class CompetitionDetailSerializer(serializers.ModelSerializer):
    exams = ExamListSerializer(many=True, read_only=True)
    exam_count = serializers.SerializerMethodField()

    class Meta:
        model = Competition
        fields = '__all__'

    def get_exam_count(self, obj):
        return obj.exams.count()

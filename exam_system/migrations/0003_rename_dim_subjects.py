from django.db import migrations


def rename_subjects(apps, schema_editor):
    """OTK konfiqurasiyasındakı yeni fənn adlarına uyğunlaşdır.

    Buraxılış: 'Azərbaycan dili' → 'Tədris dili'
    Blok III qrup: 'Azərbaycan dili' → 'Ana dili'
    """
    Question = apps.get_model('exam_system', 'Question')
    Question.objects.filter(
        exam__dim_type='buraxilis', subject='Azərbaycan dili'
    ).update(subject='Tədris dili')
    Question.objects.filter(
        exam__dim_type='blok', exam__exam_group='3', subject='Azərbaycan dili'
    ).update(subject='Ana dili')


class Migration(migrations.Migration):

    dependencies = [
        ('exam_system', '0002_exam_dim_type_exam_exam_group_exam_group_subtype_and_more'),
    ]

    operations = [
        migrations.RunPython(rename_subjects, migrations.RunPython.noop),
    ]

# Tələbə ID-sini 5 rəqəmli təsadüfi ədədə çevirir (köhnə STU-XXX formatından).
import random

from django.db import migrations


def convert_student_ids(apps, schema_editor):
    Student = apps.get_model('students', 'Student')
    students = list(Student.objects.all().order_by('created_at'))
    if not students:
        return

    used = set(
        s.student_id for s in students if s.student_id and s.student_id.isdigit()
    )
    used |= {str(s.work_number) for s in students if s.work_number}

    changed = []
    for s in students:
        if not s.student_id or not s.student_id.isdigit():
            for _ in range(100):
                num = random.randint(10000, 99999)
                if str(num) not in used:
                    break
            else:
                num = 10000
                while str(num) in used:
                    num += 1
            used.add(str(num))
            s.student_id = str(num)
            changed.append(s)

    if changed:
        Student.objects.bulk_update(changed, ['student_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_student_work_number'),
    ]

    operations = [
        migrations.RunPython(convert_student_ids, migrations.RunPython.noop),
    ]
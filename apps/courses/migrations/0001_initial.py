# Generated by Django 3.2 on 2021-11-15 23:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import recurrence.fields
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', tinymce.models.HTMLField()),
                ('due_date', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('section', models.CharField(max_length=10)),
                ('number', models.CharField(max_length=10)),
                ('description', tinymce.models.HTMLField()),
                ('private', models.BooleanField(blank=True, default=False)),
                ('credits', models.DecimalField(decimal_places=1, default='3.0', max_digits=3)),
                ('campus', models.CharField(choices=[('main', 'Main')], max_length=200)),
                ('location', models.CharField(max_length=200)),
                ('faculty', models.ManyToManyField(related_name='faculty', to=settings.AUTH_USER_MODEL, verbose_name='Faculty')),
                ('members', models.ManyToManyField(related_name='members', to=settings.AUTH_USER_MODEL, verbose_name='Members')),
            ],
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('year', models.IntegerField()),
                ('start', models.DateField()),
                ('end', models.DateField()),
            ],
            options={
                'verbose_name': 'Semester',
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', tinymce.models.HTMLField()),
                ('link', models.URLField(blank=True)),
                ('file', models.FileField(blank=True, upload_to='photos/%Y/%m/%d')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='CourseEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='For example: Lecture, Meeting, Lab', max_length=200)),
                ('start', models.TimeField()),
                ('end', models.TimeField()),
                ('recurrences', recurrence.fields.RecurrenceField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedule', to='courses.course')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.semester'),
        ),
        migrations.AddField(
            model_name='course',
            name='teaching_assistants',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Teaching Assistants'),
        ),
        migrations.CreateModel(
            name='AssignmentSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField(blank=True)),
                ('file', models.FileField(blank=True, upload_to='photos/%Y/%m/%d')),
                ('notes', models.TextField(blank=True)),
                ('submitted', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.assignment')),
                ('users', models.ManyToManyField(related_name='submitters', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='assignment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course'),
        ),
    ]

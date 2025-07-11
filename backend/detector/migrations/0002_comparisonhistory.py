# Generated by Django 5.2.3 on 2025-06-30 10:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detector', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComparisonHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plagiarism_percentage', models.FloatField()),
                ('compared_at', models.DateTimeField(auto_now_add=True)),
                ('doc1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comparisons_as_doc1', to='detector.document')),
                ('doc2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comparisons_as_doc2', to='detector.document')),
            ],
        ),
    ]

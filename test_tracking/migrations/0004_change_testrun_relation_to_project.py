# Generated by Django 5.1.6 on 2025-03-01 08:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("test_tracking", "0003_remove_testcase_expected_result_and_more"),
    ]

    def migrate_test_runs(apps, schema_editor):
        TestRun = apps.get_model("test_tracking", "TestRun")
        for test_run in TestRun.objects.all():
            test_run.project = test_run.suite.project
            test_run.save()

    def migrate_suites(apps, schema_editor):
        TestRun = apps.get_model("test_tracking", "TestRun")
        for test_run in TestRun.objects.all():
            test_run.available_suites.add(test_run.suite)

    operations = [
        migrations.AddField(
            model_name="testrun",
            name="project",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="test_runs",
                to="test_tracking.project",
            ),
        ),
        migrations.RunPython(migrate_test_runs),
        migrations.AddField(
            model_name="testrun",
            name="available_suites",
            field=models.ManyToManyField(
                help_text="このテスト実行で選択可能なテストスイート",
                related_name="available_test_runs",
                to="test_tracking.testsuite",
            ),
        ),
        migrations.RunPython(migrate_suites),
        migrations.AlterField(
            model_name="testrun",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="test_runs",
                to="test_tracking.project",
            ),
        ),
        migrations.RemoveField(
            model_name="testrun",
            name="suite",
        ),
    ]

from django.db import migrations

GROUPS = ("Faculty", "Students", "Admissions")


def create_groups(apps, schema_editor):
	Group = apps.get_model("auth", "Group")
	for name in GROUPS:
		Group.objects.get_or_create(name=name)


class Migration(migrations.Migration):
	dependencies = [
		("auth", "0012_alter_user_first_name_max_length"),
		("courses", "0002_alter_assignment_options_and_more"),
	]

	operations = [migrations.RunPython(create_groups, migrations.RunPython.noop)]

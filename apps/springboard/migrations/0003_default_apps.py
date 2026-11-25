from django.db import migrations

# (title, url, bootstrap icon, order, groups that see it — empty means everyone)
DEFAULT_APPS = (
	("Courses", "/courses/", "journal-bookmark", 10, ()),
	("My calendar", "/courses/user_calendar/", "calendar-week", 20, ()),
	("Alerts", "/alerts/", "bell", 30, ()),
	("API docs", "/api/docs/", "braces", 40, ("Faculty",)),
	("Admin", "/admin/", "gear", 50, ("Faculty", "Admissions")),
)


def create_apps(apps, schema_editor):
	IntranetApplication = apps.get_model("springboard", "IntranetApplication")
	Group = apps.get_model("auth", "Group")
	if IntranetApplication.objects.exists():
		return
	for title, url, icon_name, order, groups in DEFAULT_APPS:
		app = IntranetApplication.objects.create(title=title, url=url, icon_name=icon_name, order=order)
		app.groups.set(Group.objects.filter(name__in=groups))


class Migration(migrations.Migration):
	dependencies = [
		("courses", "0003_default_groups"),
		("springboard", "0002_alter_intranetapplication_options_and_more"),
	]

	operations = [migrations.RunPython(create_apps, migrations.RunPython.noop)]

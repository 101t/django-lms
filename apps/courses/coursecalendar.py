from calendar import HTMLCalendar
from datetime import date

from django.urls import reverse
from django.utils.html import escape


class HTMLCourseCalendar(HTMLCalendar):
	"""Month tables with each day's course events. `events` maps date -> [(occurrence, CourseEvent)]."""

	cssclass_month = "table table-bordered course-calendar mb-0"

	def __init__(self, events, user_cal=False):
		super().__init__(firstweekday=6)
		self.events = events
		self.user_cal = user_cal

	def formatmonth(self, year, month, withyear=True):
		self.year, self.month = year, month
		return super().formatmonth(year, month, withyear)

	def formatday(self, day, weekday):
		if day == 0:
			return '<td class="noday"></td>'
		current = date(self.year, self.month, day)
		classes = [self.cssclasses[weekday]] + (["today"] if current == date.today() else [])
		events = self.events.get(current)
		if not events:
			return f'<td class="{" ".join(classes)}"><span class="day-number">{day}</span></td>'

		name = "courses:user_calendar_day" if self.user_cal else "courses:calendar_day"
		url = reverse(name, kwargs={"year": self.year, "month": self.month, "day": day})
		items = "".join(
			f'<div class="event text-truncate"><span class="text-body-secondary">{event.start:%H:%M}</span> '
			f"{escape(event.course.full_title())}</div>"
			for _, event in events
		)
		return f'<td class="{" ".join(classes)} filled"><a class="day-number" href="{url}">{day}</a>{items}</td>'

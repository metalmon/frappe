import json


def extract(fileobj, *args, **kwargs):
	"""Extract messages from dashboard-related JSON fixtures.

	Supports the following doctypes:
	- Dashboard
	- Dashboard Chart
	- Number Card
	"""
	data = json.load(fileobj)

	if isinstance(data, list):
		return

	doctype = data.get("doctype")

	if doctype == "Dashboard":
		yield from _extract_dashboard(data)
	elif doctype == "Dashboard Chart":
		yield from _extract_dashboard_chart(data)
	elif doctype == "Number Card":
		yield from _extract_number_card(data)


def _extract_dashboard(data):
	dashboard_name = data.get("dashboard_name") or data.get("name")

	if dashboard_name:
		yield None, "_", dashboard_name, ["Name of a Dashboard"]

	for card in data.get("cards", []):
		label = card.get("card")
		if not label:
			continue

		comment = (
			f"Label of a Number Card in the {dashboard_name or 'Dashboard'} dashboard"
		)
		yield None, "_", label, [comment]

	for chart in data.get("charts", []):
		chart_name = chart.get("chart")
		if not chart_name:
			continue

		comment = (
			f"Label of a Dashboard Chart in the {dashboard_name or 'Dashboard'} dashboard"
		)
		yield None, "_", chart_name, [comment]


def _extract_dashboard_chart(data):
	chart_name = data.get("chart_name") or data.get("name")

	if chart_name:
		yield None, "_", chart_name, ["Name of a Dashboard Chart"]


def _extract_number_card(data):
	label = data.get("label") or data.get("name")

	if label:
		yield None, "_", label, ["Label of a Number Card"]



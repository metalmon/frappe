import orjson


def extract(fileobj, *args, **kwargs):
	"""Extract labels from Workspace Sidebar JSON fixtures."""
	data = orjson.loads(fileobj.read())

	if isinstance(data, list):
		return

	if data.get("doctype") != "Workspace Sidebar":
		return

	title = data.get("title") or data.get("name")
	if title:
		yield None, "_", title, ["Workspace Sidebar title"]

	for item in data.get("items", []):
		label = item.get("label")
		if not label:
			continue

		item_type = item.get("type") or "Item"
		yield (
			None,
			"_",
			label,
			[f"Workspace Sidebar {item_type} label under {title or 'Sidebar'}"],
		)


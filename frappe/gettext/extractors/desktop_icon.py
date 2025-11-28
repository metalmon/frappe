import orjson


def extract(fileobj, *args, **kwargs):
	"""Extract labels from Desktop Icon JSON fixtures."""
	data = orjson.loads(fileobj.read())

	if isinstance(data, list):
		return

	if data.get("doctype") != "Desktop Icon":
		return

	label = data.get("label")
	if label:
		context = data.get("parent_icon") or data.get("app") or "Desktop Icon"
		yield None, "_", label, [f"Desktop Icon label (parent: {context})"]


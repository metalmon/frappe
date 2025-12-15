import frappe


def execute():
    """Set default formats for Russian language."""
    if not frappe.db.exists("Language", "ru"):
        return

    frappe.db.set_value(
        "Language",
        "ru",
        {
            "date_format": "dd.mm.yyyy",
            "time_format": "HH:mm",
            "number_format": "# ###,##",
            "first_day_of_the_week": "Monday",
        },
    )



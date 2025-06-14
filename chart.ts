import json

def generate_line_chart_config(data):
    # Validate top-level input
    if not isinstance(data, list):
        return json.dumps({"error": "Input data must be a list of [date, value] pairs."})

    cleaned = []
    for entry in data:
        if (
            isinstance(entry, list) and
            len(entry) == 2 and
            isinstance(entry[0], str) and
            isinstance(entry[1], (int, float))
        ):
            cleaned.append({"date": entry[0], "value": round(entry[1], 4)})
        else:
            return json.dumps({
                "error": "Invalid entry format.",
                "details": f"Expected [str, number], but got: {entry}"
            })

    # Return JSON for Recharts config
    return json.dumps({
        "componentType": "Recharts.LineChart",
        "data": cleaned,
        "config": {
            "xKey": "date",
            "yKey": "value",
            "options": {
                "showGrid": True,
                "showTooltip": True,
                "strokeColor": "#8884d8"
            }
        }
    }, indent=2)
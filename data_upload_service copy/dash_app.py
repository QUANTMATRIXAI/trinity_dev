import base64
import io
import requests
import pandas as pd

import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc

# ------------------------------------------------------------------------------
# App & Server
# ------------------------------------------------------------------------------
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://use.fontawesome.com/releases/v5.8.1/css/all.css"
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# ------------------------------------------------------------------------------
# Layout
# ------------------------------------------------------------------------------
app.layout = dbc.Container(
    [
        html.H2("Data Validator", className="my-4 text-center"),

        # Pipeline selector
        dbc.Row(
            dbc.Col(
                dcc.Dropdown(
                    id="pipeline-dropdown",
                    options=[
                        {"label": "Category Forecasting", "value": "category_forecasting"},
                        {"label": "Promo Intensity",     "value": "promo_intensity"},
                        {"label": "MMM",                 "value": "mmm"},
                    ],
                    placeholder="Select pipeline...",
                    clearable=False,
                ),
                width=4,
            ),
            className="mb-3 justify-content-center"
        ),

        # Upload zone
        dcc.Upload(
            id="upload-data",
            children=html.Div(["📁 Drag & drop or click to upload file(s)"], className="text-center"),
            style={
                "width": "100%", "height": "120px",
                "borderWidth": "2px", "borderStyle": "dashed", "borderRadius": "5px",
                "textAlign": "center", "paddingTop": "40px",
                "marginBottom": "30px"
            },
            multiple=True,  # allow multiple for MMM
        ),

        # File card & Report panel
        dbc.Row(
            [
                dbc.Col(html.Div(id="file-card"), width=4),
                dbc.Col(html.Div(id="report-panel"), width=8),
            ],
            align="start",
            className="mb-4"
        ),

        html.Hr(),

        # Data preview
        html.Div(id="preview-container"),
    ],
    fluid=True,
)

# ------------------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------------------
@app.callback(
    Output("file-card", "children"),
    Output("report-panel", "children"),
    Output("preview-container", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("pipeline-dropdown", "value"),
    prevent_initial_call=True,
)
async def update_validation(contents, filenames, pipeline):
    # Only proceed if pipeline selected
    if not pipeline:
        return (
            dbc.Alert("Please select a pipeline first", color="warning"),
            "",
            "",
        )

    # Validate multiple files
    if not contents or not filenames:
        return "", "", ""

    # Decode & read each file
    dfs = {}
    for content, fname in zip(contents, filenames):
        header, data = content.split(",")
        raw = base64.b64decode(data)
        try:
            if fname.lower().endswith(".csv"):
                df = pd.read_csv(io.BytesIO(raw))
            else:
                df = pd.read_excel(io.BytesIO(raw))
        except Exception as e:
            alert = dbc.Alert(f"Error reading {fname}: {e}", color="danger")
            return alert, alert, ""
        # assign key
        if pipeline == "mmm":
            # first file=media, second=sales
            key = "media" if dfs == {} else "sales"
        else:
            key = "data"
        dfs[key] = (fname, raw)

    # Prepare files for request
    files_payload = []
    for key, (fname, raw) in dfs.items():
        files_payload.append(("files", (fname, raw, "text/csv")))

    data = {"pipeline": pipeline}
    if pipeline == "mmm":
        # map indices to keys
        data["file_keys"] = json.dumps({"0": "media", "1": "sales"})

    # Call API
    resp = requests.post(
        "http://localhost:8000/api/v1/validate/file",
        files=files_payload,
        data=data,
    )
    if resp.status_code != 200:
        err = dbc.Alert(f"API Error: {resp.status_code} - {resp.text}", color="danger")
        return err, err, ""

    result = resp.json()

    # Build file-card
    ok = result.get("ok", False)
    status = "Valid" if ok else "Invalid"
    color = "success" if ok else "danger"
    file_card = dbc.Card(
        dbc.CardBody([
            html.Div(html.I(className="fas fa-file fa-3x"), className="text-center"),
            html.H5(", ".join(filenames), className="mt-2 text-center"),
            html.P(f"File is {status}", className=f"text-center text-{color}"),
            html.I(className="fas fa-times float-end", style={"cursor": "pointer"}),
        ]),
        style={"height": "200px"},
    )

    # Build report-panel
    header = html.Div([
        html.H5("Validation Report", className="mb-0"),
        html.I(className="fas fa-times float-end", style={"cursor": "pointer"}),
    ], className="d-flex justify-content-between border-bottom pb-2 mb-2")

    icons = {
        "pass": "fas fa-check-circle text-success",
        "warn": "fas fa-exclamation-triangle text-warning",
        "fail": "fas fa-times-circle text-danger",
    }

    rows = []
    for r in result.get("rows", []):
        ic = icons.get(r["status"], "fas fa-info-circle text-secondary")
        lbl = r["check"].replace("_", " ").title()
        extra = html.Small(r.get("msg", ""), className="ms-2 text-muted") if r.get("msg") else None
        rows.append(
            html.Div([
                html.Span(lbl),
                html.Span(html.I(className=ic)),
                extra
            ], className="d-flex justify-content-between py-1")
        )

    report_panel = dbc.Card(
        dbc.CardBody([header] + rows),
        style={"height": "200px", "overflowY": "auto"},
    )

    # Build preview
    # show first loaded df
    first_df = pd.read_csv(io.BytesIO(dfs[next(iter(dfs))][1])) if filenames[0].lower().endswith(".csv") else pd.read_excel(io.BytesIO(dfs[next(iter(dfs))][1]))
    preview = html.Div([
        html.H5("Preview"),
        dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in first_df.columns],
            data=first_df.head(50).to_dict("records"),
            page_size=10,
            style_table={"overflowX": "auto"},
        )
    ])

    return file_card, report_panel, preview


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)

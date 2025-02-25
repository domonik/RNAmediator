from __future__ import annotations

import os
import sqlite3
from tempfile import TemporaryDirectory

import dash  # (version 1.12.0) pip install dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import numpy as np
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import plotly.io as pio
from dash import callback_context
from dash.dependencies import Input, Output, State, ALL

from RNAmediator import _version

__version__ = _version.get_versions()["version"]

from RNAmediator.Tweaks.RNAmediatorArgparsers import visualiziation_parser
from RNAmediator.vis.database_handling import (
    get_interesting,
    SearchSettings,
    csv_to_sqlite,
    insert_intersect,
    get_intersects,
)
from RNAmediator.vis.html_templates import (
    get_ingo,
    interesting_table,
    search_inputs,
    modal_image_download,
    data_upload,
    tables_table,
)


FILEDIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(FILEDIR, "vis/assets")
app = dash.Dash(
    "RNAmediator Dashboard",
    external_stylesheets=[dbc.themes.DARKLY],
    assets_folder=ASSETS_DIR,
    index_string=open(os.path.join(ASSETS_DIR, "index.html")).read(),
)

MODE = "db"
NUMBER_OF_INTERESTING = 10
PLOTLY_COLORS = px.colors.qualitative.Light24

pio.templates["plotly_white"].update(
    {
        "layout": {
            # e.g. you want to change the background to transparent
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": " rgba(0,0,0,0)",
            "font": dict(color="white"),
        }
    }
)


def get_app_layout(dash_app: dash.Dash, df: str):
    interesting = get_interesting(df, number_of_interesting=NUMBER_OF_INTERESTING)
    dash_app.layout = html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.Div(
                [
                    html.Div(
                        html.Div(
                            html.H3("RNAmediator Dashboard"),
                            className="databox",
                            style={"text-align": "center"},
                        ),
                        className="col-12 p-1 justify-content-center",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H4(
                                                id="header",
                                                children=[],
                                                style={"text-align": "center"},
                                                className="p-2",
                                            ),
                                            dcc.Graph(
                                                id="plotly_graph",
                                                style={"height": "375px"},
                                                className="col-12",
                                            ),
                                            dcc.Download(id="download-image"),
                                            html.Button(
                                                "Download",
                                                type="button",
                                                id="open",
                                                className="btn btn-primary m-2 col-5",
                                            ),
                                            modal_image_download(),
                                            data_upload(),
                                            dbc.Alert(
                                                "The File is not in the expected format. Please use RNAmediator output format",
                                                id="upload-alert-fade",
                                                dismissable=True,
                                                is_open=False,
                                                color="danger",
                                            ),
                                        ],
                                        className="row justify-content-center",
                                    ),
                                ],
                                className="databox",
                                id="graph-box",
                            ),
                        ],
                        className="col-12 p-1",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        html.Div(
                                            tables_table(),
                                            className="col-10 m-2 dash-bootstrap",
                                            id="select-table-dropdown",
                                        ),
                                        className="row justify-content-center",
                                    ),
                                    search_inputs(),
                                    html.Div(
                                        interesting_table(
                                            interesting,
                                            number_of_interesting=NUMBER_OF_INTERESTING,
                                        ),
                                        id="interesting-table-all",
                                        className="row justify-content-center m-1",
                                    ),
                                ],
                                className="databox",
                                id="interesting-table-div",
                                style={"height": "100%"},
                            ),
                        ],
                        className="col-12 p-1 justify-content-center",
                        style={"max-height": "50%"},
                    ),
                ],
                className="row justify-content-between",
                id="100-box",
            ),
            html.Div([], className="row", id="ingo"),
        ],
        id="wrapper",
        className="container-fluid",
    )


def update_graph_via_sql(slct_chrom, slct_goi, slct_start, slct_end):
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute(
        "SELECT Distance_to_constraint, Accessibility_difference, Accessibility_no_constraint, "
        "Accessibility_constraint, Zscore, Start, End, Strand FROM test WHERE Gene_of_interest=? AND Genomic_Start=? AND "
        "Genomic_End=? AND Chr=?",
        (slct_goi, slct_start, slct_end, slct_chrom),
    )
    rows = cur.fetchall()
    if len(rows) > 0:
        distance, acc_diff, acc_no_const, acc_cons, zscores, start, end, strand = zip(*rows)

    else:
        distance = acc_diff = acc_no_const = acc_cons = zscores = start = end = strand = []
    test = set(distance)
    distance = list(distance)
    acc_diff = list(acc_diff)
    acc_no_const = list(acc_no_const)
    acc_cons = list(acc_cons)
    zscores = list(zscores)
    if len(distance) > 0:
        for nuc in range(0, np.max(distance) + 1):
            if nuc not in test:
                distance.append(nuc)
                acc_diff.append("")
                acc_no_const.append("")
                acc_cons.append("")
                zscores.append(0)
        for nuc in range(np.min(distance), 0):
            if nuc not in test:
                distance.append(nuc)
                acc_diff.append("")
                acc_no_const.append("")
                acc_cons.append("")
                zscores.append(0)
    if len(test) > 0:
        sorted_data = sorted(zip(distance, acc_diff, acc_no_const, acc_cons))
        distance, acc_diff, acc_no_const, acc_cons = zip(*sorted_data)
    fig = go.Figure()
    if len(strand) > 0:
        start = min(start)
        end = max(end)
        strand = strand[0]
        tuples = get_intersects(database, start, end, strand)
        for entry in tuples:
            name, binding_sites = entry
            for bs in binding_sites:
                fig.add_trace(
                    go.Scatter(
                        x=[bs[0], bs[0], bs[-1], bs[-1]],
                        y=[2, -2, -2, 2],
                        fill="toself",
                        fillcolor="lightblue",
                        opacity=0.2,
                        line={"width": 0},
                        mode="lines",
                        name=f"{name}-binding site",
                    )
                )
    fig.add_trace(
        go.Scatter(
            x=distance,
            y=acc_diff,
            line={"width": 4, "color": PLOTLY_COLORS[7]},
            name="Accessibility Difference",
            visible="legendonly",
            connectgaps=False,
            hovertext=zscores,
            hovertemplate="<i>Distance</i>: %{x}"
            + "<br><b>Accessibility difference</b>: %{x:.2f}<br>"
            + "<b>Z-score</b>%{hovertext:.2f}",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=distance,
            y=acc_no_const,
            line={"width": 4, "color": PLOTLY_COLORS[1]},
            name="Accessibility no constraint",
            connectgaps=False,
            hovertext=zscores,
            hovertemplate="<i>Distance</i>: %{x}"
            + "<br><b>Accessibility</b>: %{x:.2f}<br>"
            + "<b>Z-score</b>%{hovertext:.2f}",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=distance,
            y=acc_cons,
            line={"width": 4, "color": PLOTLY_COLORS[0]},
            name="Accessibility with constraint",
            connectgaps=False,
            hovertext=zscores,
            hovertemplate="<i>Distance</i>: %{x}"
            + "<br><b>Accessibility</b>: %{y:.2f}<br>"
            + "<b>Z-score</b>%{hovertext:.2f}",
        )
    )

    fig.layout.template = "plotly_white"
    fig.update_yaxes(range=[-1, 1], title="Probability of being unpaired")
    x_range = np.max(np.abs(distance)) if len(distance) > 0 else 120
    fig.update_xaxes(range=[-x_range, x_range], title="Distance to constraint")

    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    conn.close()
    return fig


def update_graph_via_pandas(slct_chrom, slct_constraint):
    dff = database.copy()
    dff = dff[dff["Chr"] == slct_chrom]
    fig = go.Figure()
    if type(slct_constraint) == str:
        slct_constraint = [slct_constraint]
    for col_idx, element in enumerate(slct_constraint):
        pdf = dff[dff["Fold_Constraint"] == element]
        x = pdf["Distance_to_constraint"]
        y = pdf["Accessibility_difference"]
        fig.add_trace(go.Scatter(x=x, y=y, line={"width": 4, "color": PLOTLY_COLORS[col_idx]}))
    fig.layout.template = "plotly_white"
    fig.update_yaxes(range=[-1, 1])
    return fig


@app.callback(
    [
        Output(component_id="plotly_graph", component_property="figure"),
    ],
    [
        Input(component_id="header", component_property="children"),
    ],
)
def update_graph(header):
    slct_chrom, slct_goi, slct_start, slct_end = header.split(" ")
    if MODE == "db":
        fig = update_graph_via_sql(slct_chrom, slct_goi, slct_start, slct_end)
    else:
        raise NotImplementedError
    return [fig]


@app.callback(
    [
        Output(component_id="header", component_property="children"),
    ],
    [
        Input(
            {
                "type": "interesting-table-button",
                "index": ALL,
                "goi": ALL,
                "chrom": ALL,
                "start": ALL,
                "end": ALL,
            },
            "n_clicks",
        )
    ],
)
def table_click_callback(*click_args):
    assert click_args is not None
    callback_dict = callback_context.triggered[0]["prop_id"].split(".")[0]
    if callback_dict != "":
        callback_dict = eval(callback_dict)
        chrom = callback_dict["chrom"]
        goi = callback_dict["goi"]
        start = callback_dict["start"]
        end = callback_dict["end"]
    else:
        goi = start = end = chrom = ""
    return [f"{chrom} {goi} {start} {end}"]


@app.callback(
    [
        Output(component_id="interesting-table-all", component_property="children"),
        Output(component_id="url", component_property="pathname"),
        Output(component_id="ingo", component_property="children"),
        Output(component_id="prev-button", component_property="n_clicks"),
        Output(component_id="next-button", component_property="n_clicks"),
    ],
    [
        Input(component_id="prev-button", component_property="n_clicks"),
        Input(component_id="next-button", component_property="n_clicks"),
        Input(
            {"type": "interesting-table-header-button", "index": ALL, "name": ALL},
            "n_clicks",
        ),
        Input(component_id="search-chr-input", component_property="value"),
        Input(component_id="search-goi-input", component_property="value"),
        Input(component_id="search-span-start-input", component_property="value"),
        Input(component_id="search-span-end-input", component_property="value"),
        Input(component_id="intersect-dropdown", component_property="value"),
    ],
    [
        State(component_id="url", component_property="pathname"),
        State(
            component_id={"index": "sorting", "name": ALL, "type": ALL},
            component_property="n_clicks",
        ),
        State(component_id="intersect-dropdown", component_property="value"),
    ],
)
def table_switch_callback(
    prev_clicks,
    next_clicks,
    inputs,
    search_chr_input,
    search_goi,
    search_span_start,
    search_span_end,
    intersect_dropdown,
    url,
    last_sort,
    isd2,
):  # inputs is necessary for callback_context
    trigger = callback_context.triggered[0]["prop_id"].split(".")[0]
    sorting = "Max_Value" if len(os.path.basename(url)) == 0 else os.path.basename(url)
    if trigger in ["next-button", "prev-button", "", "url"]:
        page = next_clicks - prev_clicks
        if page < 0:
            next_clicks = prev_clicks = page = 0
        sorting_clicks = last_sort[0]
    elif trigger in [
        "search-input",
        "search-chr-input",
        "search-goi-input",
        "search-span-start-input",
        "search-span-end-input",
    ]:

        next_clicks = prev_clicks = page = 0
        sorting_clicks = 0

    elif trigger == "intersect-dropdown":
        sorting_clicks = 0
        next_clicks = prev_clicks = page = 0

    else:
        sorting_clicks = callback_context.triggered[0]["value"]
        trigger_dict = eval(trigger)
        next_clicks = prev_clicks = page = 0
        sorting = trigger_dict["name"]
    search_settings = SearchSettings(search_chr_input, search_goi, search_span_start, search_span_end)
    interesting = get_interesting(
        database,
        page,
        sorting,
        sorting_clicks,
        search_settings,
        number_of_interesting=NUMBER_OF_INTERESTING,
        intersect_filter=intersect_dropdown,
    )
    ingo = get_ingo(search_chr_input, search_goi, ASSETS_DIR)
    html_table = interesting_table(
        interesting,
        prev_clicks,
        next_clicks,
        sorting,
        sorting_clicks=sorting_clicks,
        number_of_interesting=NUMBER_OF_INTERESTING,
    )
    return [html_table, sorting, ingo, prev_clicks, next_clicks]


@app.callback(
    Output("download-image", "data"),
    [Input("svg-download", "n_clicks"), Input("png-download", "n_clicks")],
    [
        State(component_id="plotly_graph", component_property="figure"),
        State(component_id="header", component_property="children"),
    ],
    prevent_initial_call=True,
)
def download_image(svg, pdf, fig, header):
    trigger = callback_context.triggered[0]["prop_id"].split(".")[0]
    header = header.replace(" ", "_")
    image_format = trigger.split("-")[0]
    fig = go.Figure(fig)
    fig.layout.template = "plotly"
    if image_format == "png":
        with TemporaryDirectory() as handle:
            file_name = os.path.join(handle, f"{header}.{image_format}")
            fig.write_image(file_name, format="png", scale=3)
            return dcc.send_file(file_name)
    else:
        image = fig.to_image(format=image_format)
        image = image.decode()
        return dict(content=image, filename=f"{header}.{image_format}")


@app.callback(
    Output("modal", "is_open"),
    [
        Input("open", "n_clicks"),
        Input("close", "n_clicks"),
        Input("png-download", "n_clicks"),
    ],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open


@app.callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    try:
        if list_of_contents is not None:
            for x, element in enumerate(list_of_contents):
                insert_intersect(element, list_of_names[x], list_of_dates[x], database)
        return 1
    except sqlite3.DatabaseError:
        return 0


@app.callback(
    Output("upload-alert-fade", "is_open"),
    [Input("output-data-upload", "children")],
    [State("upload-alert-fade", "is_open")],
)
def toggle_alert(n, is_open):
    if not n and not is_open:
        return not is_open
    return is_open


@app.callback(Output("select-table-dropdown", "children"), Input("output-data-upload", "children"))
def change_dropdown(output_data_upload):
    con = sqlite3.connect(database)
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    names = [name[0] for name in cursor.fetchall()]
    names.remove("test")
    names.remove("importance")
    return tables_table(names)


def main():
    args = visualiziation_parser()
    if args.version:
        sys.exit("Running RNAmediator version " + __version__)

    bed_file = args.file
    global database
    if args.memory is True:
        database = ":memory:"
        tmpdir = None
        raise NotImplementedError("Might be implemented in following versions")
    elif args.tmp is True:
        tmpdir = TemporaryDirectory(
            prefix="RNAmediator_",
        )
        database = os.path.join(tmpdir.name, "rnamediator.db")
    else:
        database = args.database
        tmpdir = None

    if not os.path.exists(database):
        csv_to_sqlite(bed_file, database)
    get_app_layout(app, database)
    app.run_server(debug=False, port=8080, host="0.0.0.0")
    if tmpdir:
        tmpdir.cleanup()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
import dash
import werkzeug.utils
from dash import dcc, html, ctx
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import os
import urllib
import urllib.parse
import json
from flask import Flask, send_file, request

from flask_caching import Cache
from app import app

dash_app = dash.Dash(
    name="dashinterface",
    server=app,
    url_base_pathname="/microbiomemasst/",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

dash_app.title = 'microbiomeMASST'

cache = Cache(dash_app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'temp/flask-cache',
    'CACHE_DEFAULT_TIMEOUT': 0,
    'CACHE_THRESHOLD': 1000000
})


dash_app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Umami Analytics -->
        <script async defer data-website-id="a2c04f32-dca9-4fcd-b3f3-0f9aeeb2d74e" src="https://analytics.gnps2.org/umami.js"></script>
        <script async defer data-website-id="74bc9983-13c4-4da0-89ae-b78209c13aaf" src="https://analytics.gnps2.org/umami.js"></script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

NAVBAR = dbc.Navbar(
    children=[
        dbc.NavbarBrand(
            html.Img(src="https://gnps2.org/static/img/logo.png", width="120px"),
            href="https://www.cs.ucr.edu/~mingxunw/"
        ),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("microbiomeMASST Dashboard - Version 2025.09.29", href="/microbiomemasst")),
            ],
        navbar=True)
    ],
    color="light",
    dark=False,
    sticky="top",
)

DATASELECTION_CARD = [
    dbc.CardHeader(html.H5("Data Selection")),
    dbc.CardBody(
        [
            html.H5(children='GNPS Data Selection - Enter USI or Spectrum Peaks'),
            html.Br(),
            html.Br(),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Spectrum USI"),
                    dbc.Input(id='usi1', placeholder="Enter GNPS USI", value=""),
                ],
                className="mb-3",
            ),
            html.Hr(),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Spectrum Peaks"),
                    dbc.Textarea(id='peaks', placeholder="Enter one peak per line as follows:\n\nm/z1\tintensity1\nm/z2\tintensity2\nm/z3\tintensity3\n...", rows=10),
                ],
                className="mb-3"
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Precursor m/z"),
                    dbc.Input(id='precursor_mz', type='', placeholder="precursor m/z", min = 1, max=10000),
                    dbc.InputGroupText("Charge"),
                    dbc.Input(id='charge', type='number', placeholder="charge", min = 1, max=40),
                ],
                className="mb-3 no-margin-bottom"
            ),
            html.Hr(),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("PM Tolerance (Da)"),
                    dbc.Input(id='pm_tolerance', type='number', placeholder="pm tolerance", value=0.05, min = 0.01, max = 0.5, step=0.02),
                    dbc.InputGroupText("Fragment Tolerance (Da)"),
                    dbc.Input(id='fragment_tolerance', type='number', placeholder="fragment_tolerance", value=0.05,min = 0.01, max = 0.5, step=0.02),
                    dbc.InputGroupText("Cosine Threshold"),
                    dbc.Input(id='cosine_threshold', type='number', placeholder="cosine_threshold", value=0.7, min=0.5, max=1.0, step=0.05),
                    dbc.InputGroupText("Minimum Matched Peaks"),
                    dbc.Input(id='min_matched_peaks', type='number', placeholder="min_matched_peaks", value=4, min=1, max=100, step=1),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Analog Search"),
                    dbc.Select(
                        id="analog_select",
                        options=[
                            {"label": "Yes", "value": "Yes"},
                            {"label": "No", "value": "No"},
                        ],
                        value="No"
                    ),
                    dbc.InputGroupText("Delta Mass Below (Da)"),
                    dbc.Input(id='delta_mass_below', type='number', placeholder="delta_mass_below", value=130, min = 0, max = 300, step=1),
                    dbc.InputGroupText("Delta Mass Above (Da)"),
                    dbc.Input(id='delta_mass_above', type='number', placeholder="delta_mass_above", value=200, min = 0, max = 300, step=1),
                ],
                className="mb-3",
            ),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        dbc.Button("Search microbiomeMASST by USI", color="warning", id="search_button_usi", n_clicks=0),
                        className="d-grid gap-2",
                    )
                ]),
                dbc.Col([
                    html.Div(
                        dbc.Button("Search microbiomeMASST by Spectrum Peaks", color="warning", id="search_button_peaks", n_clicks=0),
                        className="d-grid gap-2",
                    )
                ]),
                dbc.Col([
                    html.Div(
                        dbc.Button("Copy Link", color="warning", id="copy_link_button", n_clicks=0),
                        className="d-grid gap-2",
                    )
                ]),
                dbc.Col([
                    html.A( html.Div(
                        dbc.Button("Open External MASST Search Results", color="warning", n_clicks=0),
                        className="d-grid gap-2"), id="link_to_masst", href="", target="_blank"),
                ])]
            ),
            html.Div(
                [
                    dcc.Link(id="query_link", href="#", target="_blank"),
                ],
                style={
                        "display" :"none"
                }
            )
        ]
    )
]

LEFT_DASHBOARD = [
    html.Div(
        [
            html.Div(DATASELECTION_CARD),
        ]
    )
]

MIDDLE_DASHBOARD = [
    dbc.CardHeader(html.H5("Data Exploration")),
    dbc.CardBody(
        [
            dcc.Loading(
                id="output",
                children=[html.Div([html.Div(id="loading-output-23")])],
                type="default",
            ),
            html.Br(),
            html.Hr(),
            html.Br(),
            dcc.Loading(
                id="spectrummirror",
                children=[html.Div([html.Div(id="loading-output-24")])],
                type="default",
            ),

        ]
    )
]

CONTRIBUTORS_DASHBOARD = [
    dbc.CardHeader(html.H5("Contributors")),
    dbc.CardBody(
        [
            "Mingxun Wang PhD - UC Riverside",
            html.Br(),
            "Shipei Xing PhD - UC San Diego",
            html.Br(),
            "Vincent Charron-Lamoureux PhD - UC San Diego",
            html.Br()
        ]
    )
]


def create_example(lib_id):
    return f"/microbiomemasst#%7B%22usi1%22%3A%20%22mzspec%3AGNPS%3AGNPS-LIBRARY%3Aaccession%3A{lib_id}%22%2C%20%22peaks%22%3A%20%5B%22%22%5D%2C%20%22precursor_mz%22%3A%20%5B%22%22%5D%7D"


EXAMPLES_DASHBOARD = [
    dbc.CardHeader(html.H5("Examples")),
    dbc.CardBody(
        [
            html.A("Phe-CA", id="example_molecule1", href=create_example("CCMSLIB00011432553")),
            html.Br(),
            html.A("Trp-CA", id="example_molecule2", href=create_example("CCMSLIB00011432558")),
            html.Br(),
            html.A("Arg-C18:1", id="example_molecule4", href=create_example("CCMSLIB00011436056")),
            html.Br(),
            # html.A("5-ASA-phenylpropionic acid", id="example_molecule5", href=create_example("CCMSLIB00016281670")),
            # html.Br(),
        ]
    )
]

BODY = dbc.Container(
    [
        dcc.Location(id='url', refresh=False),
        dbc.Row([
            dbc.Col(
                dbc.Card(LEFT_DASHBOARD),
                className="col-9"
            ),
            dbc.Col(
                [
                    dbc.Card(CONTRIBUTORS_DASHBOARD),
                    html.Br(),
                    dbc.Card(EXAMPLES_DASHBOARD)
                ],
                className="col-3"
            ),
        ], style={"marginTop": 30}),
        html.Br(),
        dbc.Row([
            dbc.Card(MIDDLE_DASHBOARD)
        ])
    ],
    fluid=True,
    className="",
)

dash_app.layout = html.Div(children=[NAVBAR, BODY])

def _get_url_param(param_dict, key, default):
    return param_dict.get(key, [default])

@dash_app.callback([
                Output('usi1', 'value'),
                Output('peaks', 'value'),
                Output('precursor_mz', 'value'),
              ],
              [
                  Input('url', 'hash')
              ])
def determine_task(search):

    try:
        query_dict = json.loads(urllib.parse.unquote(search[1:]))
    except:
        query_dict = {}

    usi1 = _get_url_param(query_dict, "usi1", 'mzspec:GNPS:GNPS-LIBRARY:accession:CCMSLIB00011432553')
    peaks = _get_url_param(query_dict, "peaks", '')
    precursor_mz = _get_url_param(query_dict, "precursor_mz", '')

    return [usi1, peaks, precursor_mz]




@dash_app.callback([
                Output('output', 'children')
              ],
              [
                Input('search_button_usi', 'n_clicks'),
                Input('search_button_peaks', 'n_clicks'),
              ],
              [
                State('usi1', 'value'),
                State('peaks', 'value'),
                State('precursor_mz', 'value'),
                State('pm_tolerance', 'value'),
                State('fragment_tolerance', 'value'),
                State('cosine_threshold', 'value'),
                State('min_matched_peaks', 'value'),
                State('analog_select', 'value'),
                State('delta_mass_below', 'value'),
                State('delta_mass_above', 'value')
              ])
def draw_output(
                search_button_usi,
                search_button_peaks,
                usi1,
                peaks,
                precursor_mz,
                prec_mz_tol,
                ms2_mz_tol,
                min_cos,
                min_matched_peaks,
                use_analog,
                analog_mass_below,
                analog_mass_above):

    button_id = ctx.triggered_id if not None else 'No clicks yet'

    import sys
    # print("HERE", search_button_usi, button_id, file=sys.stderr)

    # This is on load
    if search_button_usi == 0 and search_button_peaks == 0:
        return [dash.no_update]

    # For MicrobeMASST code from robin
    # import sys
    # sys.path.insert(0, "microbe_masst/code/")
    # import microbe_masst

    import uuid
    mangling = str(uuid.uuid4())
    output_temp = os.path.join("temp", "microbemasst", mangling)
    os.makedirs(output_temp, exist_ok=True)

    out_file = "../../{}/fastMASST".format(output_temp)

    # TODO seems to always run analog
    use_analog = use_analog == "Yes"

    # If USI is a list
    if len(usi1) == 1:
        usi1 = usi1[0]

    if button_id == "search_button_usi":
        cmd = 'cd microbe_masst/code/ && python masst_client.py \
        --usi_or_lib_id "{}" \
        --out_file "{}" \
        --precursor_mz_tol {} \
        --mz_tol {} \
        --min_cos {} \
        --min_matched_signals {} \
        --analog_mass_below {} \
        --analog_mass_above {} \
        --database metabolomicspanrepo_index_nightly \
        '.format(usi1,
                out_file,
                prec_mz_tol,
                ms2_mz_tol,
                min_cos,
                min_matched_peaks,
                analog_mass_below,
                analog_mass_above
                )

        # Tacking on the analog flag
        if use_analog:
            cmd += " --analog true"


    elif button_id == "search_button_peaks":
        # Writing out the MGF file if we are using peaks
        print("USING PEAKS")
        mgf_string = """BEGIN IONS
PEPMASS={}
MSLEVEL=2
CHARGE=1
{}
END IONS\n""".format(precursor_mz, peaks.replace(",", " ").replace("\t", " "))

        mgf_filename = os.path.join(output_temp, "input_spectra.mgf")
        with open(mgf_filename, "w") as o:
            o.write(mgf_string)

        cmd = 'cd microbe_masst/code/ && python masst_batch_client.py \
        --in_file "{}" \
        --out_file "{}" \
        --parallel_queries 1 \
        --precursor_mz_tol {} \
        --mz_tol {} \
        --min_cos {} \
        --min_matched_signals {} \
        --analog {} \
        --analog_mass_below {} \
        --analog_mass_above {} \
        --database metabolomicspanrepo_index_nightly \
        '.format(os.path.join("../..", mgf_filename),
                out_file,
                prec_mz_tol,
                ms2_mz_tol,
                min_cos,
                min_matched_peaks,
                use_analog,
                analog_mass_below,
                analog_mass_above
                )

    import sys
    print(cmd, file=sys.stderr, flush=True)
    os.system(cmd)
    response_list = [html.Iframe(src="/microbiomemasst/results?task={}&analog={}".format(mangling, use_analog), width="100%", height="900px")]

    # Creating download link for the results
    response_list.append(html.Br())
    response_list.append(html.A("Download Results", href="/microbiomemasst/results?task={}&analog={}".format(mangling, use_analog), download="mangling.html", target="_blank"))
    return [response_list]

@dash_app.callback([
                Output('spectrummirror', 'children')
              ],
              [
                  Input('usi1', 'value'),
                  Input('table', 'derived_virtual_data'),
                  Input('table', 'derived_virtual_selected_rows'),
              ]
)
def draw_spectrum(usi1, table_data, table_selected):
    try:
        selected_row = table_data[table_selected[0]]
    except:
        return ["Choose Match to Show Mirror Plot"]

    dataset_accession = selected_row["Accession"]
    dataset_scan = selected_row["DB Scan"]

    database_usi = "mzspec:MSV000084314:{}:scan:{}".format("updates/2020-11-18_mwang87_d115210a/other/MGF/{}.mgf".format(dataset_accession), dataset_scan)

    url_params_dict = {}
    url_params_dict["usi1"] = usi1
    url_params_dict["usi2"] = database_usi

    url_params = urllib.parse.urlencode(url_params_dict)

    link_url = "https://metabolomics-usi.gnps2.org/dashinterface"
    link = html.A("View Spectrum Mirror Plot in Metabolomics Resolver", href=link_url + "?" + url_params, target="_blank")
    svg_url = "https://metabolomics-usi.gnps2.org/svg/mirror/?{}".format(url_params)

    image_obj = html.Img(src=svg_url)

    return [[link, html.Br(), image_obj]]


@dash_app.callback([
                Output('query_link', 'href'),
              ],
                [
                    Input('usi1', 'value'),
                    Input('peaks', 'value'),
                    Input('precursor_mz', 'value'),
                ])
def draw_url(usi1, peaks, precursor_mz):
    params = {}
    params["usi1"] = usi1
    params["peaks"] = peaks
    params["precursor_mz"] = precursor_mz

    url_params = urllib.parse.quote(json.dumps(params))

    return [request.host_url + "/microbiomemasst#" + url_params]


@dash_app.callback([
                Output('link_to_masst', 'href'),
              ],
                [
                    Input('usi1', 'value'),
                ])
def draw_url(usi1):
    params = {}
    params["usi1"] = usi1

    try:
        params["usi1"] = usi1[0]
    except:
        pass

    url_params = urllib.parse.urlencode(params)

    return ["https://fasst.gnps2.org/fastsearch/?" + url_params]


dash_app.clientside_callback(
    """
    function(n_clicks, button_id, text_to_copy) {
        original_text = "Copy Link"
        if (n_clicks > 0) {
            const el = document.createElement('textarea');
            el.value = text_to_copy;
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            setTimeout(function(id_to_update, text_to_update){ 
                return function(){
                    document.getElementById(id_to_update).textContent = text_to_update
                }}(button_id, original_text), 1000);
            document.getElementById(button_id).textContent = "Copied!"
            return 'Copied!';
        } else {
            return original_text;
        }
    }
    """,
    Output('copy_link_button', 'children'),
    [
        Input('copy_link_button', 'n_clicks'),
        Input('copy_link_button', 'id'),
    ],
    [
        State('query_link', 'href'),
    ]
)

# API
@app.route("/microbiomemasst/results")
def microbiomeMASST_results():
    use_analog = request.args.get("analog") == "True"
    html_file = microbiome_masst_path(request.args.get("task"), use_analog)

    return send_file(html_file)

def microbiome_masst_path(task, use_analog):
    """
    actual file found - success and matches to microbiomeMASST,
    matches file found - success but no matches,
    no success - just placeholder to show error,
    :param task: taskid
    :param use_analog: whether to export the _analog html file or not.
    :return: the html file that matches the state
    """
    task_path = os.path.basename(task)
    output_folder = os.path.join("temp", "microbemasst", task_path)

    html_file = os.path.join(output_folder, "fastMASST_analog_microbiome.html") \
        if use_analog else os.path.join(output_folder, "fastMASST_microbiome.html")
    if os.path.isfile(html_file):
        return html_file
    elif os.path.isfile(os.path.join(output_folder, "fastMASST_matches.tsv")):
        return os.path.join("html_results", "success_no_matches_metadata.html")
    else:
        return os.path.join("html_results", "error_result.html")


if __name__ == "__main__":
    
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    dash_app.run(debug=True, port=8050, host="0.0.0.0")
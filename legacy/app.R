library(shiny)
library(bslib)
library(plotly)
library(dplyr)
library(tidyr)
library(DT)
library(echarts4r)

#  Toy Data ---------------------------------------------------------------
pipeline <- tibble::tibble(
  year = 2023:2030,
  Vaccines = c(120, 135, 150, 165, 175, 185, 195, 205),
  Drugs = c(80, 90, 95, 105, 115, 120, 128, 132),
  Devices = c(45, 52, 49, 55, 60, 66, 63, 61)
)

readiness <- tibble::tibble(
  status = c("Approved", "In Trials", "Under Review", "Early Stage"),
  pct = c(25, 38, 14, 23),
  colors = c("#10b981", "#3b82f6", "#f59e0b", "#ef4444")
)

# UI ---------------------------------------------------------------------
ui <- page_navbar(
  id = "main_nav",
  # Brand: logo + name (shows on every page)
  title = tags$div(
    class = "navbar-brand d-flex align-items-center me-4 pe-4",
    tags$img(
      src = "images/ALIGN_without_partners.png",
      alt = "ALIGN",
      class = "brand-logo"
    ),
    tags$span("Market Intelligence Hub", class = "brand-title ms-1")
  ),

  # Theme (brand colors)
  theme = bs_theme(
    version = 5,
    primary = "#1B457C", # blue accents
    secondary = "#BA5621", # orange (navbar)
    bg = "#FFFFFF",
    fg = "#111827", # general text color (black)
    base_font = bslib::font_google("Inter"),
    heading_font = bslib::font_google("Inter Tight")
  ),

  # Global styles that apply to all pages
  header = tags$head(
    tags$link(rel = "icon", type = "image/png", href = "images/ghic.png"),
    tags$style(HTML(
      "
  :root{
  --brand-primary:#1B457C;   /* blue */
  --brand-accent:#BA5621;    /* orange */
  --brand-light:#FFFFFF;
  --brand-gray:#E5E7EB;
  --text:#111827;            /* black-ish */
}

/* General text */
body { color: var(--text); }

/* Navbar */
.navbar { background-color: var(--brand-accent) !important; }
.navbar .navbar-brand, .navbar .nav-link { color:#fff !important; }
.navbar .nav-link.active, .navbar .nav-link:focus, .navbar .nav-link:hover {
  color:#fff !important; border-bottom:2px solid var(--brand-primary);
}
/* ===== Navbar brand + logo ===== */
.navbar .navbar-brand{
  display:flex; align-items:center; gap:.5rem;
  margin-right:1.25rem; padding-right:1.25rem;
  border-right: none;
}

/* Larger, crisp logo; remove baseline gap with display:block */
.brand-logo{
  height: 100px;       /* was 26px */
  width: auto;
  display: block;     /* avoids extra baseline space */
}

@media (min-width: 1200px){
  .brand-logo{ height: 70px; }
}

/* Title next to the logo */
.brand-title{
  color:#fff; font-weight: 600;
  font-size: 1.35rem; line-height: 1;   /* keep tight and vertically centered */
  letter-spacing: .2px;
}

/* ===== Navbar links — center vertically and match rhythm ===== */
.navbar{ background-color: var(--brand-accent) !important; }
.navbar-nav{ gap: 1rem; align-items: center; }   /* center the pill row */
.navbar .nav-link{
  color:#fff !important;
  padding: .5rem .75rem;                 /* balanced vertical padding */
}
.navbar .nav-link.active,
.navbar .nav-link:focus,
.navbar .nav-link:hover{
  color:#fff !important;
  border-bottom: 2px solid var(--brand-primary);
}

/* Optional: reduce the tall default navbar height on large screens */
@media (min-width: 992px){
  .navbar{ min-height: 56px; }
}

/* Accents */
.hero-gradient { background: linear-gradient(135deg, var(--brand-primary) 0%, var(--brand-primary) 100%); }
.card-title, .value-box .value { color: var(--brand-primary); }
.progress-bar, .mini-fill { background-color: var(--brand-primary); }
/* Make the 'Analytics' pill bar visible and responsive */
  /* Case 1: modern Shiny/bslib structure */
  ul.nav[data-tabsetid='impact_tabs'] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: .25rem .5rem;
    overflow: visible !important;
    align-items: center;
  }
  ul.nav[data-tabsetid='impact_tabs'] .nav-link { white-space: nowrap; }

  /* Case 2: older structure where the UL is a child of the container with the id */
  #impact_tabs > ul.nav.nav-pills {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: .25rem .5rem;
    overflow: visible !important;
    align-items: center;
  }
  #impact_tabs > ul.nav.nav-pills .nav-link { white-space: nowrap; }

  /* Safety: never hide the nav bar via overflow rules on the container */
  #impact_tabs { overflow: visible !important; }

  /* Optional: give the bar a bit of breathing room so it won't collapse visually */
  #impact_tabs > ul.nav.nav-pills,
  ul.nav[data-tabsetid='impact_tabs'] { min-height: 40px; }
analytics-row > [class*='col-'] { min-width: 0 !important; }

/* 2) Contain widget widths to their parent */
.card .html-widget,
.card .echarts4r,
.card .plotly,
.card canvas,
.card svg {
  max-width: 100% !important;
}

/* Optional: if the pills still act weird, keep the UL visible and wrapping */
#impact_tabs .nav.nav-pills,
ul.nav[data-tabsetid='impact_tabs'] {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: center;
  gap: .25rem .5rem;
}
.indicator-card{
  background:#fafafa;border:1px solid #e3e3e3;border-radius:12px;padding:12px 16px;
}
.indicator-row{display:flex;align-items:center;gap:.5rem;}
.indicator-row + .indicator-row{margin-top:10px;}
.indicator-row i{font-size:1.05rem;line-height:1;}
.indicator-row i.yes{color:#2e7d32;}   /* green */
.indicator-row i.no{color:#c62828;}    /* red   */
.indicator-label{font-size:.98rem;}

.subdomain-header { display:flex; align-items:center; gap:.75rem; margin: .25rem 0 .5rem; }

.badge-round {
  margin-left:auto;
  background:#f3f4f6; color:#111827; border-radius:9999px;
  padding:.25rem .55rem; font-weight:600; font-size:.85rem;
}
.subdomain-card { margin-bottom:1rem; }

/* tighter subdomain spacing */
.subdomain-block { margin: 8px 0 14px; }
.subdomain-title { margin: 2px 0 6px; }

/* compact badge */
.badge-round{
  background:#f3f4f6; color:#111827; border-radius:9999px;
  padding:.2rem .5rem; font-weight:600; font-size:.82rem; line-height:1;
}

/* tighten the checklist card and rows */
.indicator-card{ background:#f8f9fb; border:1px solid #e6e7eb;
  border-radius:12px; padding:10px 12px; }
.indicator-row + .indicator-row{ margin-top:6px; }
.indicator-row i{ font-size:.95rem; line-height:1; }
.indicator-label{ font-size:.97rem; line-height:1.2; }

/* remove extra space that h5 would add if used elsewhere */
#domain_bars h5{ margin:0; }


"
    ))
  ),

  # Overview Page -----------------------------------
  nav_panel(
    "Overview",

    # Hero
    div(
      class = "p-4 mb-4 text-white rounded",
      # style = "background: linear-gradient(135deg, #667eea 0%, #BA5621 100%);",
      style = "background:#1B457C;", # <- blue box
      div(
        class = "row align-items-center",
        div(
          class = "col-md-8",
          p(
            "Track and assess health technologies for policy implementation",
            class = "mb-1 fs-5"
          ),
          p("Innovations tracked", class = "mb-0 opacity-75")
        ),
        div(
          class = "col-md-4 text-end",
          div(
            class = "card bg-white bg-opacity-10 border-0",
            div(
              class = "card-body text-center",
              h4("47 of 60", class = "text-white mb-1"),
              tags$small("Policy Maker Access", class = "text-white-50"),
              div(
                class = "progress mt-2",
                style = "height: 6px;",
                div(class = "progress-bar bg-info", style = "width: 78%")
              )
            )
          )
        )
      )
    ),

    # KPI cards
    div(class = "row mb-4", {
      cards <- list(
        list(
          value = "624",
          label = "Active Innovations",
          sub = "+18% from last quarter",
          icon = "wave-square"
        ),
        list(
          value = "156",
          label = "Implementation Ready",
          sub = "+23% approved this quarter",
          icon = "circle-check"
        ),
        list(
          value = "89",
          label = "Maternal Health Focus",
          sub = "+12% new innovations",
          icon = "baby"
        ),
        list(
          value = "8.7/10",
          label = "Impact Score",
          sub = "+0.3 average improvement",
          icon = "star"
        )
      )
      lapply(cards, function(x) {
        div(
          class = "col-md-3",
          card(
            card_body(
              div(
                class = "d-flex justify-content-between align-items-center",
                div(
                  h3(x$value, class = "text-primary mb-1"),
                  p(x$label, class = "mb-1 fw-bold"),
                  tags$small(x$sub, class = "text-success")
                ),
                div(icon(x$icon, class = "fa-2x text-primary opacity-50"))
              )
            )
          )
        )
      })
    }),

    # Overview charts
    div(
      class = "row",
      div(
        class = "col-md-7",
        card(
          card_header("Recently and predicted approvals"),
          card_body(plotlyOutput("trend_chart", height = "300px"))
        )
      ),
      div(
        class = "col-md-5",
        card(
          card_header("Implementation Readiness"),
          card_body(plotlyOutput("pie_chart", height = "300px"))
        )
      )
    ),

    # High level value_boxes
    div(
      class = "row mt-3",
      div(
        class = "col-md-3",
        value_box(
          title = "Total Budget Impact",
          value = "$196M",
          showcase = icon("dollar-sign"),
          p(tags$small(
            "Savings projected over 5 years",
            class = "text-success"
          ))
        )
      ),
      div(
        class = "col-md-3",
        value_box(
          title = "Implementation Readiness",
          value = "75%",
          showcase = icon("gauge-simple"),
          p(tags$small(
            "Average across target countries",
            class = "text-success"
          ))
        )
      ),
      div(
        class = "col-md-3",
        value_box(
          title = "Population Coverage",
          value = "412M",
          showcase = icon("users"),
          p(tags$small("People potentially covered", class = "text-success"))
        )
      ),
      div(
        class = "col-md-3",
        value_box(
          title = "Risk Level",
          value = "Medium",
          showcase = icon("triangle-exclamation"),
          p(tags$small("Overall implementation risk", class = "text-warning"))
        )
      )
    ),

    ### Analytics tabs ---------------------------------------------------------
    card(
      min_height = "500px",
      card_header(
        div(
          class = "d-flex align-items-center justify-content-between flex-wrap gap-2",
          span("Analytics", class = "fw-semibold"),
          selectInput(
            "impact_country",
            NULL,
            # ADD: Global option, selected = global
            choices = c("Kenya", "Senegal", "South Africa"),
            selected = "Kenya",
            width = "220px"
          )
        )
      ),
      card_body(
        tabsetPanel(
          type = "pills",
          id = "impact_tabs",

          tabPanel(
            "Impact Analysis",
            div(
              class = "row mt-3 analytics-row",
              div(
                class = "col-md-7",
                card(
                  card_header(
                    "Innovation Impact by Category",
                    tags$div(
                      style = "font-weight:400; font-size:13px; color:#6b7280;",
                      "Potential population impact and cost effectiveness"
                    )
                  ),
                  card_body(echarts4rOutput("impact_combo", height = "300px"))
                )
              ),
              div(
                class = "col-md-5",
                card(
                  card_header(
                    "Implementation Readiness",
                    tags$div(
                      style = "font-weight:400; font-size:13px; color:#6b7280;",
                      "Innovations ready for policy implementation"
                    )
                  ),
                  card_body(echarts4rOutput("readiness_bar", height = "300px"))
                )
              )
            )
          ),

          tabPanel(
            "Budget Planning",
            p("Budget planning content coming soon.", class = "mt-3")
          ),
          tabPanel(
            "Implementation",
            p("Implementation content coming soon.", class = "mt-3")
          ),
          tabPanel(
            "Risk Assessment",
            p("Risk assessment content coming soon.", class = "mt-3")
          ),
          tabPanel(
            "Country Readiness",
            p("Country readiness content coming soon.", class = "mt-3")
          )
        )
      )
    ),

    ### Innovation table -------------------------------------------------------
    card(
      min_height = "500px",
      card_header(
        div(
          class = "d-flex align-items-center justify-content-between flex-wrap gap-2",
          span("Innovation Explorer", class = "fw-semibold"),
          selectInput(
            "impact_country_table",
            NULL,
            choices = c("Kenya", "Senegal", "South Africa"),
            selected = "Kenya",
            width = "220px"
          )
        )
      ),
      tabsetPanel(
        tabPanel(DT::DTOutput("pipeline_tbl"))
      )
    )
  ),

  # Other Pages --------------------------------
  nav_panel(
    "Vaccines",
    h4("Vaccines Dashboard"),
    p("Vaccine innovation tracking coming soon...")
  ),
  nav_panel(
    "Drugs",
    h4("Drugs Dashboard"),
    p("Drug development tracking coming soon...")
  ),
  nav_panel(
    "Devices",
    h4("Medical Devices"),
    p("Device innovation tracking coming soon...")
  ),
  nav_panel(
    "Policy",
    h4("Policy Implementation"),
    p("Policy analysis tools coming soon...")
  ),

  # Innovation Details Page ----------------------------
  nav_panel(
    "Innovation Details",
    value = "details",

    # Title & summary
    # Nao ta funcionando
    card(
      min_height = "400px",
      card_header(textOutput("detail_title")),
      card_body(uiOutput("detail_summary"))
    ),
    # Overall domain readiness (full width)
    # tags$hr(),
    # h4("Overall Domain Readiness"),
    # uiOutput("domain_summary_bars"),
    # Two-column: details (left) + summary (right) ----
    div(
      class = "row g-4 align-items-start",

      # LEFT: overall domain readiness summar
      div(
        class = "col-12 col-lg-4 position-sticky",
        style = "top: 1rem;", # keeps the summary visible while scrolling
        card(
          card_header("Overall Domain Readiness"),
          card_body(uiOutput("domain_summary_bars"))
        )
      ),
      # RIGHT: the tabset + detailed progress
      div(
        class = "col-12 col-lg-8",
        card(
          card_header("Scores within selected domain"),
          card_body(
            tabsetPanel(
              type = "pills",
              id = "domain_tabs",
              tabPanel("Impact potential", value = "impact"),
              tabPanel("Introduction readiness", value = "intro_readiness")
            ),
            div(class = "mt-3", uiOutput("domain_bars"))
          )
        )
      )
    ),
    tags$head(tags$style(HTML(
      "
        .readiness-row { margin-bottom: 14px; }
        .readiness-row .lbl { font-weight: 600; }
        .progress { height: 8px; border-radius: 8px; background-color:#e5e7eb; }
        .progress-bar { border-radius: 8px; background-color:#0f172a; }
        .overall .progress { height: 10px; }
      "
    ))),

    # KPIs ----------
    tags$hr(),
    # h4("Key Indicators"),
    card(
      min_height = "600px",
      card_header(
        div(
          class = "d-flex align-items-center justify-content-between flex-wrap gap-2",
          span("Key Indicators", class = "fw-semibold"),
          selectInput(
            "impact_country_KPIs",
            NULL,
            # ADD: Global option, selected = global
            choices = c("Kenya", "Senegal", "South Africa"),
            selected = "Kenya",
            width = "220px"
          )
        )
      ),
      card_body(
        div(
          class = "btn-group mb-3 visually-hidden",
          role = "group",
          actionButton(
            "metric_pop",
            "Population impact potential",
            class = "btn btn-outline-primary"
          ),
          actionButton(
            "metric_ce",
            "Cost-effectiveness",
            class = "btn btn-outline-primary"
          ),
          actionButton(
            "metric_impl",
            "Implementation readiness",
            class = "btn btn-outline-primary"
          ),
          actionButton(
            "metric_dev",
            "Development score",
            class = "btn btn-outline-primary"
          )
        ),
        div(
          class = "row g-3",
          div(class = "col-12", uiOutput("kpi_box")), # shows all four KPIs at once
        )
      )
    )
  )
)

server <- function(input, output, session) {
  horizon_path <- file.path("www", "horizon.csv")

  # auto-reload every 2s if the file changes
  horizon_read <- reactiveFileReader(
    intervalMillis = 2000,
    session = session,
    filePath = horizon_path,
    readFunc = function(path) {
      readr::read_csv(path, show_col_types = FALSE)
    }
  )
  # Shared data ------
  pipeline_df <- reactive({
    df <- horizon_read()
    # Ensure required columns exist / are named as the table expects

    # Countries: if not present, or you want a per-innovation count, compute it
    if (!"Countries" %in% names(df)) {
      df <- df |>
        dplyr::group_by(.data$Innovation) |>
        dplyr::mutate(
          Countries = dplyr::n_distinct(.data$Country %||% NA_character_)
        ) |>
        dplyr::ungroup()
    }

    # Minimal set that the table/details use
    need <- c(
      "Innovation",
      "Disease",
      "Category",
      "Stage",
      "Readiness",
      "LeadOrg",
      "Impact Score",
      "Countries",
      "Country"
    )
    for (nm in need) {
      if (!nm %in% names(df)) df[[nm]] <- NA
    }

    # Add a stable id if none
    if (!"id" %in% names(df)) {
      df <- dplyr::arrange(df, .data$Innovation, .data$Country %||% "") |>
        dplyr::mutate(id = paste0("INV-", sprintf("%03d", dplyr::row_number())))
    }

    # Order columns and return
    dplyr::select(
      df,
      id,
      Innovation,
      Disease,
      Category,
      Stage,
      `Introduction Readiness`,
      LeadOrg,
      `Impact Potential`,
      Countries,
      dplyr::everything()
    )
  })

  observeEvent(pipeline_df(), {
    df <- pipeline_df()
    if ("Country" %in% names(df)) {
      countries <- sort(unique(stats::na.omit(df$Country)))
      if (length(countries)) {
        updateSelectInput(
          session,
          "impact_country_table",
          choices = countries,
          selected = countries[[1]]
        )
      }
    }
  })

  # Overview charts ------
  brand <- list(primary = "#1B457C", accent = "#BA5621", gray = "#E5E7EB")
  # plotly trend
  output$trend_chart <- renderPlotly({
    pipeline |>
      tidyr::pivot_longer(
        cols = c(Vaccines, Drugs, Devices),
        names_to = "category",
        values_to = "count"
      ) |>
      plot_ly(
        x = ~year,
        y = ~count,
        color = ~category,
        colors = c(brand$primary, brand$accent, "#94A3B8"), # third is a neutral
        type = "scatter",
        mode = "lines+markers",
        line = list(width = 3),
        marker = list(size = 6)
      ) |>
      layout(
        hovermode = "x unified",
        legend = list(orientation = "h", y = 1.02)
      ) |>
      config(displayModeBar = FALSE)
  })
  readiness$colors <- c(brand$primary, brand$accent, "#CBD5E1", "#E5E7EB")

  output$pie_chart <- renderPlotly({
    plot_ly(
      data = readiness,
      labels = ~status,
      values = ~pct,
      type = "pie",
      hole = 0.4,
      marker = list(
        colors = readiness$colors,
        line = list(color = "#FFFFFF", width = 2)
      ),
      textinfo = "label+percent",
      textposition = "outside"
    ) |>
      layout(showlegend = TRUE) |>
      config(displayModeBar = FALSE)
  })

  # Impact tabs data (Kenya / Senegal / South Africa) -----------------------
  impact_dat_all <- tibble::tribble(
    ~country,
    ~category,
    ~impact,
    ~cost_eff,
    "Kenya",
    "Vaccines",
    100,
    11.4,
    "Kenya",
    "Drugs",
    150,
    10.9,
    "Kenya",
    "Medical Devices",
    90,
    10.5,
    "Kenya",
    "Diagnostics",
    70,
    11.6,
    "Kenya",
    "Nutrition",
    40,
    10.8,

    "Senegal",
    "Vaccines",
    80,
    11.1,
    "Senegal",
    "Drugs",
    130,
    10.4,
    "Senegal",
    "Medical Devices",
    85,
    10.2,
    "Senegal",
    "Diagnostics",
    65,
    11.3,
    "Senegal",
    "Nutrition",
    30,
    10.6,

    "South Africa",
    "Vaccines",
    120,
    11.6,
    "South Africa",
    "Drugs",
    170,
    11.1,
    "South Africa",
    "Medical Devices",
    110,
    10.7,
    "South Africa",
    "Diagnostics",
    90,
    11.7,
    "South Africa",
    "Nutrition",
    55,
    11.0
  )

  readiness_cat_all <- tibble::tribble(
    ~country,
    ~category,
    ~ready,
    ~total,
    "Kenya",
    "Vaccines",
    12,
    45,
    "Kenya",
    "Drugs",
    33,
    130,
    "Kenya",
    "Medical Devices",
    17,
    58,
    "Kenya",
    "Diagnostics",
    14,
    52,
    "Kenya",
    "Nutrition",
    6,
    24,

    "Senegal",
    "Vaccines",
    10,
    40,
    "Senegal",
    "Drugs",
    29,
    120,
    "Senegal",
    "Medical Devices",
    14,
    55,
    "Senegal",
    "Diagnostics",
    12,
    50,
    "Senegal",
    "Nutrition",
    5,
    22,

    "South Africa",
    "Vaccines",
    16,
    50,
    "South Africa",
    "Drugs",
    38,
    150,
    "South Africa",
    "Medical Devices",
    20,
    65,
    "South Africa",
    "Diagnostics",
    18,
    60,
    "South Africa",
    "Nutrition",
    8,
    28
  )

  # Impact tabs reactives (scoped to the tabset via input$impact_country) ---
  sel_impact_country <- reactive({
    req(input$impact_country)
    input$impact_country
  })

  impact_dat_country <- reactive({
    dplyr::filter(impact_dat_all, country == sel_impact_country())
  })

  readiness_country <- reactive({
    dplyr::filter(readiness_cat_all, country == sel_impact_country())
  })

  # Impact tabs renders (replace your existing ones) ------------------------
  output$impact_combo <- renderEcharts4r({
    impact_dat_country() |>
      e_charts(category) |>
      e_bar(impact, name = "Impact") |>
      e_line(
        cost_eff,
        name = "Cost effectiveness",
        y_index = 1,
        smooth = TRUE
      ) |>
      e_y_axis(name = "Impact index") |>
      e_y_axis(index = 1, name = "Cost effectiveness") |>
      e_grid(left = "8%", right = "6%", top = 30, bottom = 20) |>
      e_tooltip(trigger = "axis") |>
      e_legend(right = 10)
  })

  output$readiness_bar <- renderEcharts4r({
    readiness_country() |>
      e_charts(category) |>
      e_bar(
        total,
        name = "Total in pipeline",
        itemStyle = list(color = "#d1d5db")
      ) |>
      e_bar(ready, name = "Ready", z = 10) |>
      e_grid(left = "8%", right = "6%", top = 30, bottom = 20) |>
      e_tooltip() |>
      e_legend(right = 10)
  })

  # Pipeline table and navigation ------
  pipe_filtered <- reactive({
    df <- pipeline_df() # from horizon.csv
    req(nrow(df) > 0, input$impact_country_table)

    # keep only the selected country
    if ("Country" %in% names(df)) {
      df <- dplyr::filter(df, .data$Country == input$impact_country_table)
    }

    s <- input$pipe_search
    if (!is.null(s) && nzchar(s)) {
      s <- tolower(s)
      df <- dplyr::filter(
        df,
        grepl(s, tolower(.data$Innovation)) |
          grepl(s, tolower(.data$Disease)) |
          grepl(s, tolower(.data$LeadOrg))
      )
    }
    if (!is.null(input$pipe_cat) && input$pipe_cat != "All Categories") {
      df <- dplyr::filter(df, .data$Category == input$pipe_cat)
    }
    if (!is.null(input$pipe_stage) && input$pipe_stage != "All Stages") {
      df <- dplyr::filter(df, .data$Stage == input$pipe_stage)
    }
    df
  })

  output$pipeline_tbl <- DT::renderDT(
    {
      df <- pipe_filtered() |>
        dplyr::mutate(
          Countries = sprintf("%s countries", Countries),
          `Introduction Readiness` = paste0(`Introduction Readiness`, "%")
        ) |>
        dplyr::select(
          Innovation,
          Disease,
          Category,
          Stage,
          `Introduction Readiness`,
          LeadOrg,
          `Impact Potential`,
          Countries
        )

      DT::datatable(
        df,
        escape = FALSE,
        rownames = FALSE,
        selection = "single",
        filter = "top",
        options = list(dom = "ftip", pageLength = 5, autoWidth = TRUE)
      )
    },
    server = TRUE
  )

  # Innovation Page --------------------------------------------------------
  ## Innovation details selection state ------
  .selected_id <- reactiveVal(NULL)

  observeEvent(input$pipeline_tbl_rows_selected, {
    sel <- input$pipeline_tbl_rows_selected
    req(length(sel) == 1)

    cur <- input$pipeline_tbl_rows_current
    ridx <- if (length(cur)) cur[sel] else sel

    row <- pipe_filtered()[ridx, , drop = FALSE]
    req(nrow(row) == 1, !is.na(row$id))

    .selected_id(row$id)
    bslib::nav_select("main_nav", "details")
  })

  ## Innovation details data bindings ------
  detail_row <- reactive({
    req(.selected_id())
    dplyr::filter(pipeline_df(), id == .selected_id())
  })

  output$detail_title <- renderText({
    req(detail_row())
    detail_row()$Innovation
  })

  output$detail_summary <- renderUI({
    d <- detail_row()
    req(nrow(d) == 1) # Add explicit requirement

    tagList(
      tags$p(tags$b("ID: "), d$id),
      tags$p(tags$b("Disease(s): "), d$Disease),
      tags$p(tags$b("Target Population: "), d$TargetPop),
      tags$p(tags$b("Lead Organization: "), d$LeadOrg)
    )
  })

  ## Domain scores and helpers ------
  domain_types <- c(
    impact = "binary",
    intro_readiness = "binary"
    # add others as needed
  )

  # domain and subscores
  domain_scores_template <- list(
    impact = tibble::tibble(
      metric = c(
        "Disease burden",
        "Epidemiological impact",
        "Alignment with goals",
        "Cost-effectiveness",
        "Budget impact",
        "Resource optimization"
      ),
      value = c(0, 1, 1, 1, 1, 1)
    ),
    intro_readiness = tibble::tibble(
      subdomain = c(
        rep("Financing", 2),
        rep("Policy", 5),
        rep("Uptake/Delivery", 4)
      ),
      metric = c(
        # Financing
        "Probability of technical and regulatory success",
        "Procurement model",
        # Policy
        "Regulatory approvals",
        "Policy readiness",
        "Social context",
        "Guidelines and training",
        "Policy implemented",
        # Uptake/Delivery
        "Advance launch and planing/timeline",
        "Demand forecasting and generation",
        "Potential supply chain",
        "Delivery model"
      ),
      value = c(
        # <- set your 0/1 values here
        0,
        1, # Financing
        0,
        0,
        1,
        0,
        1, # Policy
        0,
        0,
        1,
        1 # Uptake/Delivery
      )
    )
  )

  ## No offsets anymore — return the template for the selected innovation
  domain_scores <- reactive({
    req(.selected_id()) # keeps details page logic intact
    domain_scores_template
  })

  # ## Per-innovation domain adjustments (Temporary) -----------------
  # domain_offsets <- list(
  #   "INV-001" = c(
  #     impact = +6,
  #     intro_readiness = +2
  #   ),
  #   "INV-002" = c(
  #     impact = -8,
  #     intro_readiness = +7
  #   ),
  #   "INV-003" = c(
  #     impact = +2,
  #     intro_readiness = -6
  #   )
  # )

  progress_row <- function(label, value) {
    tags$div(
      class = "readiness-row",
      tags$div(
        class = "d-flex justify-content-between",
        tags$span(class = "lbl", label),
        tags$span(sprintf("%d%%", round(value)))
      ),
      tags$div(
        class = "progress",
        tags$div(
          class = "progress-bar",
          role = "progressbar",
          style = sprintf("width:%d%%", round(value)),
          `aria-valuenow` = round(value),
          `aria-valuemin` = "0",
          `aria-valuemax` = "100"
        )
      )
    )
  }

  # one row with an icon + label
  indicator_row <- function(label, value) {
    yes <- isTRUE(value) ||
      identical(value, 1L) ||
      (is.numeric(value) && value >= 1)
    icon_class <- if (yes) {
      "fa-solid fa-circle-check yes"
    } else {
      "fa-solid fa-circle-xmark no"
    }
    tags$div(
      class = "indicator-row",
      tags$i(class = icon_class),
      tags$span(class = "indicator-label", label)
    )
  }

  # tally UI: n_yes blue boxes out of n_total
  tally_ui <- function(n_yes, n_total) {
    boxes <- lapply(seq_len(n_total), function(i) {
      cls <- if (i <= n_yes) "box filled" else "box"
      tags$div(class = cls)
    })
    tags$div(class = "tally", boxes)
  }

  # one subdomain section: heading (with tally + 2/5) + checklist card
  intro_subdomain_section <- function(title, df) {
    n_yes <- sum(df$value %in% 1, na.rm = TRUE)
    n_total <- nrow(df)

    tags$div(
      class = "subdomain-block",
      tags$div(
        class = "subdomain-title d-flex align-items-center justify-content-between",
        tags$h5(class = "mb-0 fw-bold", title),
        tags$span(class = "badge-round", sprintf("%d/%d", n_yes, n_total))
      ),
      # your indicator_list already returns the rounded card
      indicator_list(df$metric, df$value)
    )
  }

  # a small rounded “card” of rows
  indicator_list <- function(labels, values) {
    tags$div(
      class = "indicator-card",
      mapply(
        function(l, v) indicator_row(l, v),
        labels,
        values,
        SIMPLIFY = FALSE
      ) |>
        tagList()
    )
  }

  # convenience: detect whether a vector is binary {0,1}
  is_binary01 <- function(x) {
    is.numeric(x) && all(x %in% c(0, 1)) && length(x) > 0
  }

  ## Domain summary chart ------
  domain_labels <- c(
    impact = "Impact potential",
    intro_readiness = "Introduction readiness",
    regulatory = "Regulatory",
    policy = "Policy",
    guidelines = "Guidelines & training",
    demand = "Demand forecasting & generation"
  )

  ## Domain summary progress bars ------
  output$domain_summary_bars <- renderUI({
    ds <- domain_scores()

    labels <- c(
      impact = "Impact Potential",
      intro_readiness = "Introduction Readiness",
      regulatory = "Regulatory",
      policy = "Policy",
      guidelines = "Guidelines & training",
      demand = "Demand forecasting & generation"
    )
    vals <- vapply(
      ds,
      function(t) {
        v <- t$value
        if (all(v %in% c(0, 1))) {
          100 * mean(v, na.rm = TRUE) # percent “yes”
        } else if (max(v, na.rm = TRUE) <= 1.1) {
          # handles 0–1 scaled data just in case
          100 * mean(v, na.rm = TRUE)
        } else {
          mean(v, na.rm = TRUE) # already 0–100
        }
      },
      numeric(1)
    )

    df <- tibble::tibble(
      label = unname(labels[names(ds)]),
      value = pmax(0, pmin(100, round(vals)))
    )

    # small progress row
    mini_bar <- function(label, value) {
      tags$div(
        class = "mini-row",
        tags$div(
          class = "d-flex justify-content-between align-items-center mb-1",
          tags$span(class = "mini-label", label),
          tags$span(class = "mini-pct", sprintf("%d%%", value))
        ),
        tags$div(
          class = "mini-track",
          role = "progressbar",
          `aria-valuenow` = value,
          `aria-valuemin` = "0",
          `aria-valuemax` = "100",
          tags$div(class = "mini-fill", style = sprintf("width:%d%%", value))
        )
      )
    }

    tagList(
      # single column stack
      tags$div(
        class = "domain-summary-vertical",
        lapply(seq_len(nrow(df)), function(i) {
          mini_bar(df$label[i], df$value[i])
        })
      ),

      # styling for the compact bars
      tags$head(tags$style(HTML(
        "
      .domain-summary-vertical .mini-row { margin-bottom: 12px; }
      .domain-summary-vertical .mini-label { font-weight: 600; color:#111827; }
      .domain-summary-vertical .mini-pct   { font-weight: 600; color:#111827; }
      .domain-summary-vertical .mini-track {
        height: 8px; border-radius: 9999px; background:#e5e7eb; overflow:hidden;
      }
      .domain-summary-vertical .mini-fill  {
        height: 100%; border-radius: 9999px; background: var(--brand-primary);
      }

      #impact_tabs.nav-pills {
      flex-wrap: wrap !important;
      }
      #impact_tabs .nav-link {
      white-space: nowrap;
      }
    "
      )))
    )
  })

  # Domain per-metric progress UI ------
  # output$domain_bars <- renderUI({
  #   dom <- input$domain_tabs %||% "impact"
  #   scores <- domain_scores()[[dom]]
  #   req(!is.null(scores), nrow(scores) > 0)

  #   # if values are 0/1 -> show icon list; otherwise keep progress bars
  #   if (is_binary01(scores$value)) {
  #     indicator_list(scores$metric, scores$value)
  #   } else {
  #     tagList(lapply(seq_len(nrow(scores)), function(i) {
  #       progress_row(scores$metric[i], scores$value[i])
  #     }))
  #   }
  # })

  output$domain_bars <- renderUI({
    dom <- input$domain_tabs %||% "impact"
    ds <- domain_scores()
    scores <- ds[[dom]]
    req(!is.null(scores))

    if (dom == "intro_readiness") {
      # group and render each subdomain in order
      split(scores, scores$subdomain) |>
        lapply(function(df) {
          intro_subdomain_section(unique(df$subdomain), df)
        }) |>
        tagList()
    } else if (is_binary01(scores$value)) {
      indicator_list(scores$metric, scores$value)
    } else {
      tagList(lapply(seq_len(nrow(scores)), function(i) {
        progress_row(scores$metric[i], scores$value[i])
      }))
    }
  })

  # Fictional data ------
  usage_all <- tibble::tribble(
    ~id,
    ~country,
    ~status,
    ~lat,
    ~lon,
    "INV-001",
    "Kenya",
    "Approved",
    -0.02,
    37.9,
    "INV-001",
    "Senegal",
    "In Market",
    14.5,
    -14.4,
    "INV-001",
    "South Africa",
    "Approved",
    -30.6,
    22.9,
    "INV-001",
    "Brazil",
    "Approved",
    -10.8,
    -52.9,
    "INV-001",
    "India",
    "In Market",
    21.0,
    78.0,
    "INV-002",
    "Kenya",
    "Approved",
    -0.02,
    37.9,
    "INV-002",
    "Nigeria",
    "Approved",
    9.1,
    8.7,
    "INV-002",
    "Tanzania",
    "In Market",
    -6.4,
    35.0,
    "INV-003",
    "South Africa",
    "Approved",
    -30.6,
    22.9,
    "INV-003",
    "Ghana",
    "In Use",
    7.9,
    -1.0
  )

  ce_all <- tibble::tribble(
    # fictitious USD per DALY averted
    ~id,
    ~country,
    ~ce_usd_per_daly,
    "INV-001",
    "Kenya",
    210,
    "INV-001",
    "Senegal",
    260,
    "INV-001",
    "South Africa",
    320,
    "INV-001",
    "Brazil",
    290,
    "INV-001",
    "India",
    180,
    "INV-002",
    "Kenya",
    410,
    "INV-002",
    "Nigeria",
    380,
    "INV-002",
    "Tanzania",
    430,
    "INV-003",
    "South Africa",
    270,
    "INV-003",
    "Ghana",
    240
  )

  # Optional: fictional population impact (millions)
  pop_impact_all <- tibble::tribble(
    ~id,
    ~pop_millions,
    "INV-001",
    62,
    "INV-002",
    28,
    "INV-003",
    35
  )

  # Helpers reusing your existing state ----------
  # Normalize status and palette
  status_levels <- c("In Use", "In Market", "Approved")
  status_palette <- c(
    "In Use" = "#3b82f6",
    "In Market" = "#f59e0b",
    "Approved" = "#10b981"
  )

  normalize_status <- function(x) {
    dplyr::case_when(
      is.na(x) | trimws(x) == "" ~ NA_character_,
      grepl("^in\\s*use$", x, ignore.case = TRUE) ~ "In Use",
      grepl("^aplicad", x, ignore.case = TRUE) ~ "In Use",
      grepl("market|com[eé]rcio", x, ignore.case = TRUE) ~ "In Market",
      grepl("approved|aprovad", x, ignore.case = TRUE) ~ "Approved",
      TRUE ~ "In Use" # fallback
    )
  }

  sel_usage <- reactive({
    req(.selected_id())
    usage_all |>
      dplyr::filter(id == .selected_id()) |>
      dplyr::mutate(
        status = normalize_status(status),
        status = factor(status, levels = status_levels)
      ) |>
      dplyr::filter(!is.na(status))
  })

  sel_ce <- reactive({
    req(.selected_id())
    dplyr::filter(ce_all, id == .selected_id())
  })

  sel_pop <- reactive({
    req(.selected_id())
    pop_impact_all |>
      dplyr::filter(id == .selected_id()) |>
      dplyr::pull(pop_millions) %||%
      NA_real_
  })

  # Average implementation readiness across your domain_scores()
  impl_readiness_avg <- reactive({
    ds <- domain_scores()
    vals <- unlist(lapply(ds, function(t) t$value))
    round(mean(vals, na.rm = TRUE))
  })

  # R&D score from Stage
  rd_score_from_stage <- function(stage) {
    dplyr::case_when(
      grepl("Implementation Ready", stage, ignore.case = TRUE) ~ 95,
      grepl("Post-Market Surveillance", stage, ignore.case = TRUE) ~ 90,
      grepl("Phase\\s*III", stage, ignore.case = TRUE) ~ 85,
      grepl("Phase\\s*II", stage, ignore.case = TRUE) ~ 65,
      grepl("Phase\\s*I", stage, ignore.case = TRUE) ~ 45,
      TRUE ~ 50
    )
  }

  # Delivery & Scale score from selected domains
  delivery_scale_score <- reactive({
    ds <- domain_scores()
    target <- c("intro_readiness", "policy", "guidelines", "demand")
    have <- intersect(names(ds), target)
    round(mean(unlist(lapply(ds[have], function(t) t$value)), na.rm = TRUE))
  })

  # Plots ----------
  output$usage_map <- renderPlotly({
    df <- sel_usage()
    req(nrow(df) > 0)

    # keep stable trace order by status factor levels
    df <- df |>
      dplyr::arrange(status) # ensures trace order matches status_levels

    p <- plot_ly(
      df,
      type = "scattergeo",
      mode = "markers",
      lat = ~lat,
      lon = ~lon,
      text = ~ paste0(country, "<br>Status: ", status),
      split = ~status, # one trace per status
      marker = list(size = 9, line = list(width = 0.5, color = "#ffffff"))
    ) |>
      layout(
        geo = list(
          projection = list(type = "natural earth"),
          showcountries = TRUE,
          showland = TRUE,
          landcolor = "#f8fafc"
        ),
        legend = list(orientation = "h")
      ) |>
      config(displayModeBar = FALSE)

    # Apply palette in the same order as levels
    trace_idx <- seq_along(status_levels[status_levels %in% unique(df$status)])
    p <- plotly::style(
      p,
      traces = trace_idx,
      marker = list(
        color = unname(status_palette[levels(df$status)][trace_idx])
      )
    )
    p
  })

  output$ce_by_country <- renderPlotly({
    df <- sel_ce()
    req(nrow(df) > 0)
    df <- dplyr::arrange(df, ce_usd_per_daly)

    plot_ly(
      df,
      x = ~country,
      y = ~ce_usd_per_daly,
      type = "bar",
      hovertemplate = "%{x}<br>$%{y:.0f} per DALY<extra></extra>"
    ) |>
      layout(
        yaxis = list(title = "USD per DALY averted"),
        xaxis = list(title = "")
      ) |>
      config(displayModeBar = FALSE)
  })

  # Keep original inputs; show all KPIs at once ----------
  # preserve your reactive, though buttons are hidden in the UI
  metric_selected <- reactiveVal("pop")
  observeEvent(input$metric_pop, {
    metric_selected("pop")
  })
  observeEvent(input$metric_ce, {
    metric_selected("ce")
  })
  observeEvent(input$metric_impl, {
    metric_selected("impl")
  })
  observeEvent(input$metric_dev, {
    metric_selected("dev")
  })

  output$kpi_box <- renderUI({
    req(.selected_id())
    d <- detail_row()
    stage <- d$Stage

    rd <- rd_score_from_stage(stage)
    del <- delivery_scale_score()
    impl <- impl_readiness_avg()
    ce_mean <- sel_ce() |>
      dplyr::summarise(v = mean(ce_usd_per_daly, na.rm = TRUE)) |>
      dplyr::pull(v)
    pop_m <- sel_pop()

    tagList(
      div(
        class = "row g-3",
        div(
          class = "col-md-3",
          value_box(
            title = "Population Impact Potential",
            value = if (is.na(pop_m)) "—" else paste0(pop_m, " M"),
            showcase = icon("users"),
            p(tags$small("Estimated potential beneficiaries"))
          )
        ),
        div(
          class = "col-md-3",
          value_box(
            title = "Cost-effectiveness (mean)",
            value = if (is.na(ce_mean)) {
              "—"
            } else {
              paste0("$", format(round(ce_mean), big.mark = ","), " /DALY")
            },
            showcase = icon("scale-balanced"),
            p(tags$small("Mean across countries with data"))
          )
        ),
        div(
          class = "col-md-3",
          value_box(
            title = "Implementation Readiness",
            value = paste0(impl, "%"),
            showcase = icon("gauge-simple-high"),
            p(tags$small("Average of implementation domains"))
          )
        ),
        div(
          class = "col-md-3",
          value_box(
            title = "Development Score",
            value = paste0(round(0.6 * rd + 0.4 * del), "%"),
            showcase = icon("flask"),
            p(tags$small("Blend of R&D trial phase and Delivery & Scale"))
          )
        )
      )
    )
  })

  output$dev_subscores <- renderUI({
    req(.selected_id())
    d <- detail_row()
    stage <- d$Stage
    rd <- rd_score_from_stage(stage)
    del <- delivery_scale_score()

    tiny_row <- function(label, value) {
      tags$div(
        class = "mb-2",
        tags$div(
          class = "d-flex justify-content-between",
          tags$span(tags$b(label)),
          tags$span(paste0(value, "%"))
        ),
        tags$div(
          class = "progress",
          style = "height: 8px;",
          tags$div(class = "progress-bar", style = sprintf("width:%d%%", value))
        )
      )
    }
  })
}

shinyApp(ui, server)

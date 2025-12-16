# innovation_details_progress_only.R
# Focused Innovation Details page with progress bars only
# deps: shiny, bslib, dplyr, tibble, tidyr

library(shiny)
library(bslib)
library(dplyr)
library(tibble)
library(tidyr)

# ---------------------------
# Reusable UI bits
# ---------------------------
progress_row_with_icon <- function(label, value, passed = TRUE) {
  icon_html <- if (passed) {
    '<i class="fa fa-check text-success me-2"></i>'
  } else {
    '<i class="fa fa-times text-danger me-2"></i>'
  }

  tags$div(
    class = "readiness-row",
    tags$div(
      class = "d-flex justify-content-between align-items-center",
      tags$div(
        class = "d-flex align-items-center",
        HTML(icon_html),
        tags$span(class = "lbl", label)
      ),
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

mini_bar <- function(label, value) {
  tags$div(
    class = "mini-row",
    tags$div(
      class = "d-flex justify-content-between align-items-center mb-1",
      tags$span(class = "mini-label", label),
      tags$span(class = "mini-pct", sprintf("%d%%", round(value)))
    ),
    tags$div(
      class = "mini-track",
      role = "progressbar",
      `aria-valuenow` = round(value),
      `aria-valuemin` = "0",
      `aria-valuemax` = "100",
      tags$div(class = "mini-fill", style = sprintf("width:%d%%", round(value)))
    )
  )
}

# ---------------------------
# Module UI
# ---------------------------
innovation_details_ui <- function(id) {
  ns <- NS(id)
  tagList(
    layout_sidebar(
      sidebar = sidebar(
        # demo selector; hide if you control selection upstream
        selectInput(
          ns("selected_id"),
          "Select innovation",
          choices = c("INV-001", "INV-002", "INV-003"),
          selected = "INV-001"
        ),
        width = 260
      ),
      tagList(
        # Header card: title + characteristics
        card(
          card_header(textOutput(ns("detail_title"))),
          card_body(uiOutput(ns("detail_summary")))
        ),

        # Domain roll-ups
        card(
          card_header("Domain roll-ups"),
          card_body(
            div(
              class = "row g-3",
              div(
                class = "col-md-6",
                value_box(
                  title = "Impact potential (avg.)",
                  value = textOutput(ns("impact_avg"), inline = TRUE),
                  showcase = icon("bullseye")
                )
              ),
              div(
                class = "col-md-6",
                value_box(
                  title = "Introduction readiness (avg.)",
                  value = textOutput(ns("intro_avg"), inline = TRUE),
                  showcase = icon("clipboard-check")
                )
              )
            )
          )
        ),

        # Impact potential: flat list of metric scores
        card(
          card_header("Impact potential"),
          card_body(uiOutput(ns("impact_list")))
        ),

        # Introduction readiness: subdomains with per-metric bars + subdomain roll-ups
        card(
          card_header("Introduction readiness"),
          card_body(
            # Subdomain roll-ups
            div(class = "mb-3", uiOutput(ns("intro_sub_rollups"))),

            # Per-subdomain details
            uiOutput(ns("intro_subdomains"))
          )
        )
      )
    ),

    # Styles for bars
    tags$head(tags$style(HTML(
      "
      .readiness-row{ margin-bottom:14px; }
      .readiness-row .lbl{ font-weight:600; }
      .progress{ height:8px; border-radius:8px; background:#e5e7eb; }
      .progress-bar{ border-radius:8px; background:#1B457C; }

      .mini-row { margin-bottom: 10px; }
      .mini-label { font-weight: 600; color:#111827; }
      .mini-pct   { font-weight: 600; color:#111827; }
      .mini-track { height: 8px; border-radius:9999px; background:#e5e7eb; overflow:hidden; }
      .mini-fill  { height: 100%; border-radius:9999px; background:#1B457C; }

      .subdomain-card + .subdomain-card { margin-top: 1rem; }
    "
    )))
  )
}

# ---------------------------
# Module Server
# ---------------------------
innovation_details_server <- function(
  id,
  details_df,
  impact_template = NULL,
  intro_template = NULL,
  id_offsets = NULL
) {
  moduleServer(id, function(input, output, session) {
    ns <- session$ns

    # --------- Default templates you can override ----------
    # Impact potential metrics (flat)
    if (is.null(impact_template)) {
      impact_template <- tibble::tibble(
        metric = c(
          "Disease burden",
          "Epidemiological impact",
          "Alignment with goals",
          "Cost-effectiveness",
          "Budget impact",
          "Resource Optimization"
        ),
        value = c(72, 68, 63, 74, 58, 61),
        passed = c(TRUE, TRUE, FALSE, TRUE, FALSE, TRUE) # Set based on your criteria
      )
    }

    # Introduction readiness: subdomain + metric + value
    if (is.null(intro_template)) {
      intro_template <- tibble::tribble(
        ~subdomain,
        ~metric,
        ~value,
        "Financing",
        "Probability of technical and regulatory success",
        65,
        "Financing",
        "Procurement model",
        60,
        "Policy",
        "Regulatory Approvals",
        62,
        "Policy",
        "Policy Readiness",
        58,
        "Policy",
        "Social context",
        55,
        "Policy",
        "Guidelines and training",
        57,
        "Policy",
        "Policy Implemented",
        50,
        "Uptake/Delivery",
        "Advance launch and planning / timeline",
        63,
        "Uptake/Delivery",
        "Demand Forecasting and generation",
        59,
        "Uptake/Delivery",
        "Potential supply chain",
        61,
        "Uptake/Delivery",
        "Delivery model",
        60
        # If you truly want a second "Potential supply chain" entry, add it here
      )
    }

    # Optional per-ID offsets (additive deltas, clipped to 0–100)
    if (is.null(id_offsets)) {
      id_offsets <- list(
        "INV-001" = list(
          impact = c(+4, +2, +3, 0, +5, +2),
          impact_passed = c(TRUE, TRUE, TRUE, TRUE, FALSE, TRUE),
          intro = intro_template %>%
            mutate(delta = c(+2, 0, +3, +2, -1, +1, 0, +2, +1, 0, +1))
        ),
        "INV-002" = list(
          impact = c(-6, +5, 0, +3, -2, +1),
          impact_passed = c(FALSE, TRUE, FALSE, TRUE, TRUE, TRUE),
          intro = intro_template %>%
            mutate(delta = c(+1, +3, +4, 0, +1, +2, +2, 0, -2, +1, 0))
        ),
        "INV-003" = list(
          impact = c(+1, -2, +4, +2, +3, +2),
          impact_passed = c(TRUE, FALSE, TRUE, TRUE, TRUE, FALSE),
          intro = intro_template %>%
            mutate(delta = c(0, +2, +6, -1, +2, +3, +4, +1, +2, +2, +2))
        )
      )
    }

    # --------- Selection & header ----------
    detail_row <- reactive({
      req(input$selected_id)
      dplyr::filter(details_df, id == input$selected_id)
    })

    output$detail_title <- renderText({
      d <- detail_row()
      req(nrow(d) == 1)
      d$Innovation
    })
    output$detail_summary <- renderUI({
      d <- detail_row()
      req(nrow(d) == 1)
      tagList(
        p(tags$strong("ID: "), d$id),
        p(tags$strong("Disease(s): "), d$Disease),
        p(tags$strong("Target Population: "), d$TargetPop),
        p(tags$strong("Lead Organization: "), d$LeadOrg),
        p(tags$strong("Stage: "), d$Stage)
      )
    })

    # --------- Build scores for selected ID ----------
    scores_for_id <- reactive({
      sel <- req(input$selected_id)

      # Impact
      imp <- impact_template
      offs_imp <- id_offsets[[sel]]$impact
      offs_passed <- id_offsets[[sel]]$impact_passed

      if (!is.null(offs_imp)) {
        imp$value <- pmax(0, pmin(100, imp$value + offs_imp))
      }
      if (!is.null(offs_passed)) {
        imp$passed <- offs_passed
      }

      # Intro (unchanged)
      intro <- intro_template
      offs_intro <- id_offsets[[sel]]$intro
      if (!is.null(offs_intro)) {
        intro <- intro %>%
          left_join(
            offs_intro %>% select(subdomain, metric, delta),
            by = c("subdomain", "metric")
          ) %>%
          mutate(
            delta = tidyr::replace_na(delta, 0),
            value = pmax(0, pmin(100, value + delta))
          ) %>%
          select(subdomain, metric, value)
      }

      list(impact = imp, intro = intro)
    })

    # --------- Roll-ups ----------
    output$impact_avg <- renderText({
      s <- scores_for_id()$impact
      paste0(round(mean(s$value, na.rm = TRUE)), "%")
    })
    output$intro_avg <- renderText({
      s <- scores_for_id()$intro
      paste0(round(mean(s$value, na.rm = TRUE)), "%")
    })

    # --------- Impact potential: flat list of progress bars ----------
    output$impact_list <- renderUI({
      df <- scores_for_id()$impact
      tagList(lapply(seq_len(nrow(df)), function(i) {
        progress_row_with_icon(df$metric[i], df$value[i], df$passed[i])
      }))
    })

    # --------- Introduction readiness ----------
    # Subdomain roll-ups (mini bars)
    output$intro_sub_rollups <- renderUI({
      df <- scores_for_id()$intro %>%
        group_by(subdomain) %>%
        summarise(avg = round(mean(value, na.rm = TRUE)), .groups = "drop")

      tags$div(
        class = "row g-3",
        lapply(seq_len(nrow(df)), function(i) {
          tags$div(class = "col-md-4", mini_bar(df$subdomain[i], df$avg[i]))
        })
      )
    })

    # Per-subdomain detailed progress bars
    output$intro_subdomains <- renderUI({
      df <- scores_for_id()$intro
      subs <- unique(df$subdomain)

      tagList(lapply(subs, function(sd) {
        dsd <- dplyr::filter(df, subdomain == sd)

        card(
          class = "subdomain-card",
          card_header(sd),
          card_body(
            tagList(lapply(seq_len(nrow(dsd)), function(i) {
              progress_row(dsd$metric[i], dsd$value[i])
            }))
          )
        )
      }))
    })
  })
}

# ---------------------------
# Standalone demo app
# ---------------------------
details_demo <- tibble(
  id = c("INV-001", "INV-002", "INV-003"),
  Innovation = c(
    "mRNA Malaria Vaccine BNT165",
    "AI-Powered Diagnostic Platform",
    "Maternal Health Monitoring Kit"
  ),
  Disease = c(
    "Malaria",
    "Tuberculosis, Pneumonia, COVID-19",
    "Pregnancy complications, Preeclampsia"
  ),
  TargetPop = c(
    "Children 6 months to 5 years",
    "Primary healthcare settings",
    "Pregnant women in rural areas"
  ),
  LeadOrg = c("BioNTech", "HealthAI Labs", "MaternalCare Inc"),
  Stage = c("Phase III", "Post-Market Surveillance", "Implementation Ready")
)

ui <- page_fixed(
  theme = bs_theme(
    version = 5,
    primary = "#1B457C",
    base_font = font_google("Inter"),
    heading_font = font_google("Inter Tight")
  ),
  # Add Font Awesome CSS
  tags$head(
    tags$link(
      rel = "stylesheet",
      href = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    )
  ),
  h3("Innovation Details — Progress Bars"),
  innovation_details_ui("details")
)

server <- function(input, output, session) {
  innovation_details_server("details", details_df = details_demo)
}

shinyApp(ui, server)

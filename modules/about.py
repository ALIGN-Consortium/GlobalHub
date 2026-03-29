import os
from shiny import ui


# =========================================================
# UTIL
# =========================================================
def load_html(path):
    with open(path, "r") as f:
        html = f.read()

    # Extract only the content within the main tag to avoid including
    # full <html>, <head>, and <body> tags which break host page styling.
    start_tag = '<main class="content" id="quarto-document-content">'
    end_tag = "</main>"

    start_idx = html.find(start_tag)
    end_idx = html.find(end_tag)

    if start_idx != -1 and end_idx != -1:
        content = html[start_idx : end_idx + len(end_tag)]

        # Clean up unrendered Quarto/R artifacts if they exist
        content = content.replace("<code>r params$last_updated</code>", "2026-03-27")
        content = content.replace("`r params$last_updated`", "2026-03-27")

        return content

    return html


# =========================================================
# LOAD CONTENT (CACHE AT IMPORT)
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ABOUT_PATH = os.path.join(BASE_DIR, "dist", "content", "about.html")

ABOUT_HTML = load_html(ABOUT_PATH)


# =========================================================
# UI
# =========================================================

def about_ui(id):

    return ui.div(
        ui.div(
            ui.HTML(ABOUT_HTML),
            class_="about-body",
            # FULL WIDTH
            style="""
                width: 100%;
            """,
        ),
        class_="container-fluid px-4 py-4",
    )


######
# from shiny import ui


# def about_ui(id):

#     return ui.div(
#         # =====================================================
#         # HERO — PLATFORM VISION
#         # =====================================================
#         ui.div(
#             ui.div(
#                 ui.h1("ALIGN Global Hub", class_="fw-bold mb-3"),
#                 ui.p(
#                     "A structured intelligence platform for tracking, classifying, "
#                     "and comparing health products across diseases, "
#                     "development phases, and geographic contexts.",
#                     class_="lead",
#                 ),
#                 ui.p(
#                     "ALIGN transforms fragmented R&D, regulatory, and policy data "
#                     "into standardized, interpretable records that support strategic prioritization and introduction decision-making in global health.",
#                     class_="text-muted",
#                 ),
#                 class_="container text-center",
#             ),
#             class_="py-5 border-bottom",
#         ),
#         # =====================================================
#         # WHY IT EXISTS
#         # =====================================================
#         ui.div(
#             ui.div(
#                 ui.h2("Why ALIGN exists", class_="fw-bold mb-4"),
#                 ui.p(
#                     "Health product data is fragmented across trial registries, "
#                     "regulatory agencies, procurement systems, and essential medicine lists. "
#                     "Definitions vary, timelines are inconsistent, and geographic context "
#                     "fundamentally alters interpretation."
#                 ),
#                 ui.p(
#                     "ALIGN GlobalHub was designed to create conceptual unity across "
#                     "products while preserving contextual specificity. "
#                     "It enables comparability without oversimplification."
#                 ),
#                 class_="container py-5",
#             ),
#             class_="bg-light border-bottom",
#         ),
#         # =====================================================
#         # ARCHITECTURE PRINCIPLES
#         # =====================================================
#         ui.div(
#             ui.div(
#                 ui.h2("Architecture principles", class_="fw-bold mb-4"),
#                 ui.div(
#                     ui.div(
#                         ui.tags.i(
#                             class_="fa-solid fa-layer-group fa-2x mb-3 text-primary"
#                         ),
#                         ui.h5(
#                             "Conceptual unity, contextual multiplicity",
#                             class_="fw-semibold",
#                         ),
#                         ui.p(
#                             "Each product is defined once at the identity level "
#                             "but represented across multiple geographic scopes to "
#                             "reflect regulatory, trial, and policy variation.",
#                             class_="text-muted",
#                         ),
#                         class_="col-md-6 mb-4",
#                     ),
#                     ui.div(
#                         ui.tags.i(
#                             class_="fa-solid fa-diagram-project fa-2x mb-3 text-primary"
#                         ),
#                         ui.h5("Decoupled identity and scope", class_="fw-semibold"),
#                         ui.p(
#                             "Core product attributes remain stable, while scope-specific "
#                             "fields capture contextual differences such as approval status, "
#                             "trial activity, and policy inclusion.",
#                             class_="text-muted",
#                         ),
#                         class_="col-md-6 mb-4",
#                     ),
#                     ui.div(
#                         ui.tags.i(
#                             class_="fa-solid fa-table-cells fa-2x mb-3 text-primary"
#                         ),
#                         ui.h5(
#                             "Controlled vocabularies by default", class_="fw-semibold"
#                         ),
#                         ui.p(
#                             "Structured classifications are prioritized to ensure "
#                             "interoperability and analytic consistency. Free text "
#                             "is reserved for clinically nuanced descriptions.",
#                             class_="text-muted",
#                         ),
#                         class_="col-md-6 mb-4",
#                     ),
#                     ui.div(
#                         ui.tags.i(
#                             class_="fa-solid fa-check-double fa-2x mb-3 text-primary"
#                         ),
#                         ui.h5("Row-level interpretability", class_="fw-semibold"),
#                         ui.p(
#                             "Each record is independently interpretable without "
#                             "requiring joins or external reconstruction of context.",
#                             class_="text-muted",
#                         ),
#                         class_="col-md-6 mb-4",
#                     ),
#                     class_="row",
#                 ),
#                 class_="container py-5",
#             ),
#             class_="border-bottom",
#         ),
#         # =====================================================
#         # DATA MODEL
#         # =====================================================
#         # =====================================================
#         # DATA MODEL
#         # =====================================================
#         ui.div(
#             ui.div(
#                 ui.h2("The data model", class_="fw-bold mb-4"),
#                 ui.p(
#                     "Each row represents one Product × Geographic Scope. "
#                     "This structure enables cross-country comparison while preserving "
#                     "local regulatory and implementation context."
#                 ),
#                 ui.p(
#                     "The model separates three conceptual layers: "
#                     "Identity (what the product is), Scope (where it applies), "
#                     "and Evidence (what signals support its development or adoption).",
#                     class_="text-muted mb-4",
#                 ),
#                 ui.p(
#                     "ALIGN is maintained as a living registry. Each release documents "
#                     "the date of last structured data extraction from integrated sources "
#                     "(e.g., trial registries, regulatory databases, and procurement systems)."
#                 ),
#                 ui.p(
#                     "Scope-specific regulatory and trial fields reflect the most recent "
#                     "available signal at the time of data collection. Historical updates "
#                     "are versioned to preserve interpretability over time."
#                 ),
#                 ui.p(
#                     "The current dataset reflects data collected through "
#                     "February, 2026.",
#                     class_="text-muted",
#                 ),
#                 class_="container py-5",
#             ),
#             class_="bg-light border-bottom",
#         ),
#         # =====================================================
#         # QUANTITATIVE FRAMEWORK
#         # =====================================================
#         ui.div(
#             ui.div(
#                 ui.h2("Quantitative reference framework", class_="fw-bold mb-4"),
#                 ui.p(
#                     "ALIGN applies standardized quantitative reference measures to enable cross-product prioritization and introduction, including using a portfolio-based approach."
#                 ),
#                 ui.h4("Disease Burden (DALYs)", class_="fw-semibold mt-4"),
#                 ui.p(
#                     "Disability-Adjusted Life Years (DALYs) are used as global "
#                     "reference measures of disease burden based on the Global Burden "
#                     "of Disease (GBD) study coordinated by IHME."
#                 ),
#                 ui.h4("Global prevalence references", class_="fw-semibold mt-4"),
#                 ui.p(
#                     "Prevalence estimates are derived from UNAIDS, WHO global reports, "
#                     "and IHME maternal disorder analyses to provide order-of-magnitude "
#                     "comparative baselines."
#                 ),
#                 ui.h4("Development archetypes (P2I model)", class_="fw-semibold mt-4"),
#                 ui.p(
#                     "Products are classified using the Portfolio-to-Impact (P2I) "
#                     "framework to estimate development timelines, costs, and "
#                     "probabilities of success. Archetypes are assigned using "
#                     "rule-based inference aligned with published definitions."
#                 ),
#                 class_="container py-5",
#             ),
#             class_="border-bottom",
#         ),
#         # ====        # =====================================================
#         # HORIZON SCANNING INFRASTRUCTURE
#         # =====================================================
#         ui.div(
#             ui.div(
#                 ui.h2("Integrated horizon scanning system", class_="fw-bold mb-4"),
#                 ui.p(
#                     "ALIGN continuously integrates structured signals from global "
#                     "R&D trackers, regulatory authorities, procurement databases, "
#                     "investment trackers, and national registries to maintain a "
#                     "living product registry.",
#                     class_="mb-3",
#                 ),
#                 ui.p(
#                     "These sources provide complementary visibility into clinical "
#                     "development activity, regulatory approvals, financing flows, "
#                     "procurement signals, and policy inclusion across geographic scopes.",
#                     class_="text-muted mb-4",
#                 ),
#                 ui.tags.table(
#                     ui.tags.thead(
#                         ui.tags.tr(
#                             ui.tags.th("Database"),
#                             ui.tags.th("Function"),
#                             ui.tags.th("Coverage"),
#                         )
#                     ),
#                     ui.tags.tbody(
#                         ui.tags.tr(
#                             ui.tags.td("WHO ICTRP"),
#                             ui.tags.td("Global Clinical Trial Registry Aggregator"),
#                             ui.tags.td("Global"),
#                         ),
#                         ui.tags.tr(
#                             ui.tags.td("ClinicalTrials.gov"),
#                             ui.tags.td("Clinical Trial Registry"),
#                             ui.tags.td("Global"),
#                         ),
#                         ui.tags.tr(
#                             ui.tags.td("WHO Prequalification (PQ)"),
#                             ui.tags.td("Regulatory Signal & Quality Assessment"),
#                             ui.tags.td("Global / LMIC"),
#                         ),
#                         ui.tags.tr(
#                             ui.tags.td(
#                                 "National Regulatory Authorities (e.g., FDA, EMA, SAHPRA, PPB)"
#                             ),
#                             ui.tags.td("Country-Level Regulatory Approval"),
#                             ui.tags.td("Country-Specific"),
#                         ),
#                         ui.tags.tr(
#                             ui.tags.td("Impact Global Health R&D Tracker"),
#                             ui.tags.td("Investment & Development Funding Tracking"),
#                             ui.tags.td("Global"),
#                         ),
#                         ui.tags.tr(
#                             ui.tags.td("WHO Essential Medicines Lists (EML)"),
#                             ui.tags.td("Policy & Adoption Signal"),
#                             ui.tags.td("Global / Country"),
#                         ),
#                         ui.tags.tr(
#                             ui.tags.td("UNICEF Supply & Procurement Data"),
#                             ui.tags.td("Procurement & Market Uptake Signal"),
#                             ui.tags.td("Global / LMIC"),
#                         ),
#                     ),
#                     class_="table table-sm table-striped mb-4",
#                 ),
#                 ui.p(
#                     "A complete and regularly updated list of integrated databases "
#                     "is available in the public repository:",
#                     class_="mb-2",
#                 ),
#                 ui.p(
#                     ui.a(
#                         "View Full Horizon Scan Database List (GitHub)",
#                         href="https://github.com/ALIGN-Consortium/GlobalHub/blob/main/docs/Databases%20Used%20in%20The%20Horizon%20Scan.csv",
#                         target="_blank",
#                         class_="fw-semibold",
#                     )
#                 ),
#                 class_="container py-5",
#             ),
#             class_="bg-light",
#         ),
#         id=id,
#     )
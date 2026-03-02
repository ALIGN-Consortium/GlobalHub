from shiny import ui


def about_ui(id):

    return ui.div(
        # =====================================================
        # HERO — PLATFORM VISION
        # =====================================================
        ui.div(
            ui.div(
                ui.h1("ALIGN GlobalHub", class_="fw-bold mb-3"),
                ui.p(
                    "A structured intelligence platform for tracking, classifying, "
                    "and comparing global health products across diseases, "
                    "development phases, and geographic contexts.",
                    class_="lead",
                ),
                ui.p(
                    "ALIGN transforms fragmented R&D, regulatory, and policy data "
                    "into standardized, interpretable records that support strategic "
                    "decision-making in global health.",
                    class_="text-muted",
                ),
                class_="container text-center",
            ),
            class_="py-5 border-bottom",
        ),
        # =====================================================
        # WHY IT EXISTS
        # =====================================================
        ui.div(
            ui.div(
                ui.h2("Why ALIGN Exists", class_="fw-bold mb-4"),
                ui.p(
                    "Health product data is fragmented across trial registries, "
                    "regulatory agencies, procurement systems, and essential medicine lists. "
                    "Definitions vary, timelines are inconsistent, and geographic context "
                    "fundamentally alters interpretation."
                ),
                ui.p(
                    "ALIGN GlobalHub was designed to create conceptual unity across "
                    "products while preserving contextual specificity. "
                    "It enables comparability without oversimplification."
                ),
                class_="container py-5",
            ),
            class_="bg-light border-bottom",
        ),
        # =====================================================
        # ARCHITECTURE PRINCIPLES
        # =====================================================
        ui.div(
            ui.div(
                ui.h2("Architecture Principles", class_="fw-bold mb-4"),
                ui.div(
                    ui.div(
                        ui.tags.i(
                            class_="fa-solid fa-layer-group fa-2x mb-3 text-primary"
                        ),
                        ui.h5(
                            "Conceptual Unity, Contextual Multiplicity",
                            class_="fw-semibold",
                        ),
                        ui.p(
                            "Each product is defined once at the identity level "
                            "but represented across multiple geographic scopes to "
                            "reflect regulatory, trial, and policy variation.",
                            class_="text-muted",
                        ),
                        class_="col-md-6 mb-4",
                    ),
                    ui.div(
                        ui.tags.i(
                            class_="fa-solid fa-diagram-project fa-2x mb-3 text-primary"
                        ),
                        ui.h5("Decoupled Identity and Scope", class_="fw-semibold"),
                        ui.p(
                            "Core product attributes remain stable, while scope-specific "
                            "fields capture contextual differences such as approval status, "
                            "trial activity, and policy inclusion.",
                            class_="text-muted",
                        ),
                        class_="col-md-6 mb-4",
                    ),
                    ui.div(
                        ui.tags.i(
                            class_="fa-solid fa-table-cells fa-2x mb-3 text-primary"
                        ),
                        ui.h5(
                            "Controlled Vocabularies by Default", class_="fw-semibold"
                        ),
                        ui.p(
                            "Structured classifications are prioritized to ensure "
                            "interoperability and analytic consistency. Free text "
                            "is reserved for clinically nuanced descriptions.",
                            class_="text-muted",
                        ),
                        class_="col-md-6 mb-4",
                    ),
                    ui.div(
                        ui.tags.i(
                            class_="fa-solid fa-check-double fa-2x mb-3 text-primary"
                        ),
                        ui.h5("Row-Level Interpretability", class_="fw-semibold"),
                        ui.p(
                            "Each record is independently interpretable without "
                            "requiring joins or external reconstruction of context.",
                            class_="text-muted",
                        ),
                        class_="col-md-6 mb-4",
                    ),
                    class_="row",
                ),
                class_="container py-5",
            ),
            class_="border-bottom",
        ),
        # =====================================================
        # DATA MODEL
        # =====================================================
        # =====================================================
        # DATA MODEL
        # =====================================================
        ui.div(
            ui.div(
                ui.h2("The Data Model", class_="fw-bold mb-4"),
                ui.p(
                    "Each row represents one Product × Geographic Scope. "
                    "This structure enables cross-country comparison while preserving "
                    "local regulatory and implementation context."
                ),
                ui.p(
                    "The model separates three conceptual layers: "
                    "Identity (what the product is), Scope (where it applies), "
                    "and Evidence (what signals support its development or adoption).",
                    class_="text-muted mb-4",
                ),
                ui.p(
                    "ALIGN is maintained as a living registry. Each release documents "
                    "the date of last structured data extraction from integrated sources "
                    "(e.g., trial registries, regulatory databases, and procurement systems)."
                ),
                ui.p(
                    "Scope-specific regulatory and trial fields reflect the most recent "
                    "available signal at the time of data collection. Historical updates "
                    "are versioned to preserve interpretability over time."
                ),
                ui.p(
                    "The current dataset reflects data collected through "
                    "February, 2026.",
                    class_="text-muted",
                ),
                class_="container py-5",
            ),
            class_="bg-light border-bottom",
        ),
        # =====================================================
        # QUANTITATIVE FRAMEWORK
        # =====================================================
        ui.div(
            ui.div(
                ui.h2("Quantitative Reference Framework", class_="fw-bold mb-4"),
                ui.p(
                    "ALIGN applies standardized quantitative reference measures "
                    "to enable cross-product prioritization and portfolio analysis."
                ),
                ui.h4("Disease Burden (DALYs)", class_="fw-semibold mt-4"),
                ui.p(
                    "Disability-Adjusted Life Years (DALYs) are used as global "
                    "reference measures of disease burden based on the Global Burden "
                    "of Disease (GBD) study coordinated by IHME."
                ),
                ui.h4("Global Prevalence References", class_="fw-semibold mt-4"),
                ui.p(
                    "Prevalence estimates are derived from UNAIDS, WHO global reports, "
                    "and IHME maternal disorder analyses to provide order-of-magnitude "
                    "comparative baselines."
                ),
                ui.h4("Development Archetypes (P2I Model)", class_="fw-semibold mt-4"),
                ui.p(
                    "Products are classified using the Portfolio-to-Impact (P2I) "
                    "framework to estimate development timelines, costs, and "
                    "probabilities of success. Archetypes are assigned using "
                    "rule-based inference aligned with published definitions."
                ),
                class_="container py-5",
            ),
            class_="border-bottom",
        ),
        # ====        # =====================================================
        # HORIZON SCANNING INFRASTRUCTURE
        # =====================================================
        ui.div(
            ui.div(
                ui.h2("Integrated Horizon Scanning System", class_="fw-bold mb-4"),
                ui.p(
                    "ALIGN continuously integrates structured signals from global "
                    "R&D trackers, regulatory authorities, procurement databases, "
                    "investment trackers, and national registries to maintain a "
                    "living product registry.",
                    class_="mb-3",
                ),
                ui.p(
                    "These sources provide complementary visibility into clinical "
                    "development activity, regulatory approvals, financing flows, "
                    "procurement signals, and policy inclusion across geographic scopes.",
                    class_="text-muted mb-4",
                ),
                ui.tags.table(
                    ui.tags.thead(
                        ui.tags.tr(
                            ui.tags.th("Database"),
                            ui.tags.th("Function"),
                            ui.tags.th("Coverage"),
                        )
                    ),
                    ui.tags.tbody(
                        ui.tags.tr(
                            ui.tags.td("WHO ICTRP"),
                            ui.tags.td("Global Clinical Trial Registry Aggregator"),
                            ui.tags.td("Global"),
                        ),
                        ui.tags.tr(
                            ui.tags.td("ClinicalTrials.gov"),
                            ui.tags.td("Clinical Trial Registry"),
                            ui.tags.td("Global"),
                        ),
                        ui.tags.tr(
                            ui.tags.td("WHO Prequalification (PQ)"),
                            ui.tags.td("Regulatory Signal & Quality Assessment"),
                            ui.tags.td("Global / LMIC"),
                        ),
                        ui.tags.tr(
                            ui.tags.td(
                                "National Regulatory Authorities (e.g., FDA, EMA, SAHPRA, PPB)"
                            ),
                            ui.tags.td("Country-Level Regulatory Approval"),
                            ui.tags.td("Country-Specific"),
                        ),
                        ui.tags.tr(
                            ui.tags.td("Impact Global Health R&D Tracker"),
                            ui.tags.td("Investment & Development Funding Tracking"),
                            ui.tags.td("Global"),
                        ),
                        ui.tags.tr(
                            ui.tags.td("WHO Essential Medicines Lists (EML)"),
                            ui.tags.td("Policy & Adoption Signal"),
                            ui.tags.td("Global / Country"),
                        ),
                        ui.tags.tr(
                            ui.tags.td("UNICEF Supply & Procurement Data"),
                            ui.tags.td("Procurement & Market Uptake Signal"),
                            ui.tags.td("Global / LMIC"),
                        ),
                    ),
                    class_="table table-sm table-striped mb-4",
                ),
                ui.p(
                    "A complete and regularly updated list of integrated databases "
                    "is available in the public repository:",
                    class_="mb-2",
                ),
                ui.p(
                    ui.a(
                        "View Full Horizon Scan Database List (GitHub)",
                        href="https://github.com/ALIGN-Consortium/GlobalHub/blob/main/docs/Databases%20Used%20in%20The%20Horizon%20Scan.csv",
                        target="_blank",
                        class_="fw-semibold",
                    )
                ),
                class_="container py-5",
            ),
            class_="bg-light",
        ),
        id=id,
    )
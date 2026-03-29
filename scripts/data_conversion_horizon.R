library(tidyverse)
library(lubridate)

path <- "/Users/jps89/Projects/dashboard_template/www/ALIGN_health_product_data V2.csv"
data <- read_csv(path)

yrs_to_days <- function(x) round(x * 365.25)

data <- data |>
  mutate(
    gra = recode(gra, "yes" = "Yes", "no" = "No"),
    category = recode(category, "Drugs" = "Therapeutics"),
    # enforce consistent date format
    gra_date = as.Date(gra_date, format = "%m/%d/%y"),
    # fixed times to milestones. Since in this data we only have dates for GRA, we need to ignore other possible
    # milestone dates
    time_to_regulatory_approval = ifelse(!is.na(gra_date), 2.62, NA_integer_),
    time_approval_to_first_launch = ifelse(!is.na(gra_date), 0.32, NA_integer_),
    time_launch_to_20lmic = ifelse(!is.na(gra_date), 5.0, NA_integer_),

    # --- Expected milestone dates
    expected_date_of_regulatory_approval = gra_date,

    expected_date_of_first_launch = expected_date_of_regulatory_approval +
      days(yrs_to_days(time_approval_to_first_launch)),

    expected_date_of_market = expected_date_of_first_launch +
      days(yrs_to_days(time_launch_to_20lmic)),

    country = rep(c("Kenya", "South Africa", "Senegal"), nrow(data) / 3),
    nra = ifelse(
      !is.na(nra_Kenya) | !is.na(nra_Senegal) | !is.na(nra_South_Africa),
      "Yes",
      "No"
    ),
    eml = ifelse(
      !is.na(eml_Kenya) | !is.na(eml_Senegal) | !is.na(eml_South_Africa),
      "Yes",
      "No"
    ),
    readiness = NA,
    financing = NA,
    trial_status = case_when(
      trial_status %in%
        c(
          "Approved",
          "Post-marketing surveillance",
          "Registration and access",
          "Registration and Access",
          "Under review"
        ) ~ "Approved / Marketed",
      trial_status %in%
        c("Phase 4") ~ "Phase 4 / Post-marketing",
      trial_status %in%
        c(
          "Phase 3",
          "Phase 3 (Complete)",
          "Phase 3 (Completed)",
          "Phase 2 & 3",
          "Phase 2, 3",
          "Phase 2 and 3",
          "Phase 2 and 4",
          "Phase 2, 3, 4, Approved, Marketed"
        ) ~ "Phase 3",
      trial_status %in%
        c(
          "Phase 2",
          "Phase 2a",
          "Phase 2b",
          "Phase 2 (complete)",
          "Phase 2 (completed)",
          "Late development",
          "PK/PD bridging study (active)"
        ) ~ "Phase 2",
      is.na(trial_status) ~ NA_character_,
    ),
    disease_group = ifelse(
      disease_group == "TB",
      "Tuberculosis",
      disease_group
    ),
    impact_potential = runif(n = nrow(data), min = 15, max = 100),
    introduction_readiness = runif(n = nrow(data), min = 13, max = 97),
    efficacy = NA,
  ) |>
  rename(disease = disease_group)


data |>
  write_csv(
    "/Users/jps89/Projects/dashboard_template/www/ALIGN_health_product_data_horizon.csv"
  )

# Something else - reading horizon data and concatenating
# read data
files <- c(
  "~/Projects/tool_universe_horizon/Data/processed/HorizonScan_Child_Health_20260111_Silver.csv",
  "~/Projects/tool_universe_horizon/Data/processed/HorizonScan_Neonatal_Disorders_20260111_Silver.csv",
  "~/Projects/tool_universe_horizon/Data/processed/HorizonScan_Perinatal_Conditions_20260111_Silver.csv",
  "~/Projects/tool_universe_horizon/Data/processed/HorizonScan_Maternal_Mortality_20260111_Silver.csv",
  "~/Projects/tool_universe_horizon/Data/processed/HorizonScan_Pregnancy_Complications_20260111_Silver.csv",
  "~/Projects/tool_universe_horizon/Data/processed/HorizonScan_maternal_and_child_health_20260111_Silver.csv",
  "~/Projects/tool_universe_horizon/Data/processed/HorizonScan_HIV_20260111_Silver.csv",
  "~/Projects/tool_universe_horizon/Data/processed/HorizonScan_Malaria_20260111_Silver.csv",
  "~/Projects/tool_universe_horizon/Data/processed/HorizonScan_Tuberculosis_20260111_Silver.csv"
)
concatenated <- data.frame()
for (file in files) {
  temp_file <- read_csv(file) |>
    mutate(StartDate = as.Date(StartDate))
  concatenated <- concatenated |>
    bind_rows(temp_file)
}

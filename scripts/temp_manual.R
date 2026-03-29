library(tidyverse)
horizon <- read_csv(
  "www/ALIGN_health_product_data_horizon.csv",
  n_max = 300,
  na = c("", "NA", "na", "Unknown", "unknown"),
)

gra_body_issues <- c(
  "Center for Drug standard control organization (CDSCO), India",
  "China Medical Products Administration (NMPA)",
  "Drug Regulatory Authority of Pakistan",
  "European Medical Agency",
  "Japan",
  "Korea MFDS;CE-IVDD;WHO recommended",
  "Korean Ministry of Food and Drug Safety",
  "Medicines and Healthcare products Regulatory Agency (MHRA) of the United Kingdom (UK)"
)
horizon <- horizon |>
  mutate(
    # for cases where the gra_body variable had data referring to national level not from
    other_nra = case_when(
      gra_body %in% gra_body_issues ~ gra_body,
      TRUE ~ other_nra
    ),
    gra_body = case_when(
      gra_body %in% gra_body_issues ~ NA_character_,
      (is.na(gra_body) | gra_body == "No") & startsWith(gra_note, "CE") ~ "CE", # european
      # trial status misscollected as PQ or CE
      trial_status == "WHO_PQ" & is.na(gra_body) ~ "WHO PQ",
      trial_status == "CE Marked" & is.na(gra) ~ "CE",
      TRUE ~ gra_body
    ),
    # If there is something in gra_note, gra should be Yes - unless if it starts with "Phase 2 was terminated"
    gra = case_when(
      startsWith(gra_note, "Phase 2 was t") ~ gra,
      !is.na(gra_note) & gra == "No" ~ "Yes",
      !is.na(gra_note) & is.na(gra) ~ "Yes",
      !is.na(gra_body) & is.na(gra) ~ "Yes",
      !is.na(gra_body) & gra == "No" ~ "Yes",
      trial_status == "WHO_PQ" & (is.na(gra) | gra == "No") ~ "Yes",
      trial_status == "CE Marked" & (is.na(gra) | gra == "No") ~ "Yes",
      TRUE ~ gra
    ),
    # Trial status fix categories
    trial_status = case_when(
      trial_status %in%
        c(
          "CE Marked",
          "WHO_PQ"
        ) ~ "Phase 4",
      TRUE ~ trial_status
    ),
    phase_1_status = ifelse(!is.na(phase_1_date), "Completed", phase_1_status),
    phase_3_status = ifelse(
      !is.na(phase_3_date) | phase_3_status %in% c('Yes', 'Yes_Completed'),
      "Completed",
      phase_3_status
    ),
    phase_4_status = ifelse(
      !is.na(phase_4_date) | phase_4_status == "Yes",
      "Completed",
      phase_4_status
    )
  )

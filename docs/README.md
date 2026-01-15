# ALIGN GlobalHub – Documentation

## Overview

The **ALIGN GlobalHub data model** provides a standardized structure for describing health innovations across their **technical characteristics**, **clinical purpose**, and ** scope**. The model is designed to support horizon scanning, regulatory tracking, policy readiness assessment, and cross-country comparison for innovations relevant to global health.

## Core Design Principles

The ALIGN data model follows four key principles:

1. **One innovation, many scopes**  
   Innovations are described once conceptually, but **represented across multiple rows** to reflect differences by country, region, or global scope.

2. **Explicit separation of identity and context**  
   Fields such as *innovation name*, *technology*, and *indication* describe the product itself, while *scope-specific fields* (e.g., regulatory status, trials, policy readiness) vary by geography.

3. **Controlled vocabularies with meaningful free text**  
   Wherever possible, fields use controlled categories (e.g., `Diagnostic`, `Medical Device`). Free-text fields are used only where nuance is required (e.g., clinical indication).

4. **Row-level interpretability**  
   Each row should be interpretable on its own, without requiring joins or external context.

## Row Structure: Innovation × Scope

Each row in the dataset represents:

> **One innovation in one geographic scope**

This means that the same innovation **will appear in multiple rows** if it is relevant to multiple countries or to both national and global contexts.

## Core Identity Fields

The following columns define the **identity and purpose** of the innovation. These fields are typically **identical across scopes** for the same innovation.

| Column | Description |
|------|------------|
| `innovation` | Canonical name of the innovation |
| `alternative_names` | Common aliases, product codes, or prior names |
| `category` | High-level classification (e.g., Diagnostic, Medical Device) |
| `technology` | Specific technology subtype |
| `disease` | Primary disease or domain addressed |
| `indication` | Clinical use case, population, and setting |


## Example: How Data Are Organized

The table below illustrates how innovations are represented in the data model.  
Note how **innovations are repeated across rows** while maintaining consistent identity fields.

| innovation | alternative_names | category | technology | disease | indication |
|----------|------------------|----------|------------|---------|------------|
| UltraDetect Malaria RDT | UD-Mal RDT; UltraDetect HRP2/pLDH | Diagnostic | Diagnostics: RDT | Malaria | Point-of-care diagnosis of uncomplicated malaria in febrile patients (all ages) presenting to primary care facilities in endemic settings. |
| UltraDetect Malaria RDT | UD-Mal RDT; UltraDetect HRP2/pLDH | Diagnostic | Diagnostics: RDT | Malaria | Point-of-care diagnosis of uncomplicated malaria in febrile patients (all ages) presenting to primary care facilities in endemic settings. |
| UltraDetect Malaria RDT | UD-Mal RDT; UltraDetect HRP2/pLDH | Diagnostic | Diagnostics: RDT | Malaria | Point-of-care diagnosis of uncomplicated malaria in febrile patients (all ages) presenting to primary care facilities in endemic settings. |
| NeoWatch AI Fetal Monitor | NeoWatch; NeoWatch AI Monitor | Medical Device | Devices: wearable | MNCH | Intrapartum fetal heart rate monitoring with AI-assisted risk alerts for laboring mothers in district hospitals to enable earlier intervention for fetal distress. |
| NeoWatch AI Fetal Monitor | NeoWatch; NeoWatch AI Monitor | Medical Device | Devices: wearable | MNCH | Intrapartum fetal heart rate monitoring with AI-assisted risk alerts for laboring mothers in district hospitals to enable earlier intervention for fetal distress. |

## Data Dictionary

Authoritative definitions, allowable values, formats, and constraints for every variable are defined in:

```
docs/ALIGNDataModel.csv
```

All contributions to the GlobalHub **must conform to this dictionary**.
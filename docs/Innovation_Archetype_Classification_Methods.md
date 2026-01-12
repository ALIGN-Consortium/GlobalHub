# Methodological Description: Innovation Archetype Classification

## Overview

This analysis classified health products into **innovation archetypes** to support portfolio-level assessment of development risk, cost, and likelihood of success. Archetypes were defined following the **Portfolio-to-Impact (P2I) model** described by Terry et al. (2018), which was developed to estimate costs, timelines, and probabilities of success for global health product research and development.

The P2I framework groups products into standardized **intervention archetypes** based on technological approach, prior knowledge, and development complexity. These archetypes are widely used in global health R&D portfolio modeling and are appropriate for comparative analyses across heterogeneous product pipelines.

> Terry RF, Gardner CA, Dieleman JL, et al. *Funding global health product R&D: the Portfolio-to-Impact (P2I) model.* Health Policy Plan. 2018.  
> Available at: https://pmc.ncbi.nlm.nih.gov/articles/PMC6139376/

---

## Archetype Taxonomy (P2I Model)

Products were classified into one of the following P2I archetypes:

- Vaccine — Simple  
- Vaccine — Complex  
- New Chemical Entity (NCE) — Simple  
- New Chemical Entity (NCE) — Innovative  
- New Chemical Entity (NCE) — Complex  
- Repurposed Drug — Simple  
- Repurposed Drug — Complex  
- Biologic — Simple  
- Biologic — Complex  
- Diagnostics — Assay development  
- Diagnostics — Simple technical platform development  

These categories correspond to the archetypes defined in **Table 1** of the P2I publication and reflect increasing levels of scientific uncertainty, technical novelty, and development risk.

---

## Classification Logic

Archetypes were assigned using **rule-based inference** aligned with the P2I definitions. The following hierarchical logic was applied:

### 1. Diagnostics
Products were classified as diagnostics if the text included terms such as:
- *diagnostic, test, assay, screening, PCR, RT-PCR, RDT, lateral flow*

Diagnostics were further divided into:
- **Diagnostics — Assay development**: standard or incremental diagnostic tests
- **Diagnostics — Simple technical platform**: enhancements to existing platforms (e.g., hypersensitive or next-generation tests)

### 2. Vaccines
Products explicitly described as vaccines were classified as:
- **Vaccine — Simple** if based on established platforms
- **Vaccine — Complex** if described as novel, first-in-class, or using new platforms (e.g., mRNA, viral vectors)

### 3. Biologics
Products described as:
- *antibody, monoclonal antibody, biologic, protein therapeutic*
were classified as biologics, with complexity determined by whether the target or mechanism was well-established.

### 4. Repurposed Drugs
Products identified as existing or previously approved drugs used for a new indication were classified as:
- **Repurposed Drug — Simple** if prior safety data allowed skipping early development phases
- **Repurposed Drug — Complex** if additional safety or dosing studies were required

### 5. New Chemical Entities (NCEs)
Small-molecule drugs or novel compounds were classified as NCEs:
- **NCE — Simple**: validated target and mechanism
- **NCE — Innovative**: novel application with known pathogenesis
- **NCE — Complex**: novel target or mechanism with high scientific uncertainty

### 6. Unclassified
If insufficient information was available in either field to reliably infer the archetype, products were labeled:
- **Unclassified / Insufficient information**

---

## Consistency With P2I Assumptions

Each assigned archetype was subsequently linked to:
- Expected **development costs by phase**: Defined as USD Millions for each phase as defind by Terry et al. 2018
- **Phase-specific probabilities of success** as estimated by archetype by Terry et al. 2018.

These parameters were taken directly from **Tables 3 and 4** of the P2I publication and applied uniformly to all products within the same archetype.

---

## Strengths and Limitations

**Strengths**
- Transparent, reproducible classification logic
- Direct alignment with a published and widely cited R&D portfolio model
- Enables comparison across heterogeneous product types

**Limitations**
- Classification relies on textual descriptions and may not capture all technical nuances
- Archetypes represent average assumptions and may not reflect product-specific deviations
- Intended for portfolio-level analysis rather than regulatory decision-making

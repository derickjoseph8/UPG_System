# UPG Household Eligibility Tool - XLSForm Design

## Overview
This document describes the XLSForm structure for the UPG HH Eligibility Tool,
designed to work with KoBoToolbox offline validation using data from UPG MIS.

## Required CSV Files (from UPG MIS)
Upload these to KoBoToolbox Settings > Media Files:
- `households.csv` - For validating existing household IDs
- `bm_cycles.csv` - For BM Cycle dropdown selection
- `villages.csv` - For cascading location selection

---

## XLSForm Structure

### SURVEY SHEET

| type | name | label | required | constraint | constraint_message | relevant | calculation | appearance |
|------|------|-------|----------|------------|-------------------|----------|-------------|------------|
| **begin_group** | identification | **Section 1: Identification** | | | | | | field-list |
| select_one bm_cycle_list | bm_cycle | Select BM Cycle | yes | | | | | |
| text | household_id | Enter Household ID | yes | regex(., '^[A-Z0-9-]+$') | Invalid ID format | | | |
| calculate | hh_exists | | | | | | pulldata('households', 'hh_id', 'hh_id', ${household_id}) | |
| calculate | hh_name_lookup | | | | | | pulldata('households', 'hh_name', 'hh_id', ${household_id}) | |
| calculate | hh_village_lookup | | | | | | pulldata('households', 'village_name', 'hh_id', ${household_id}) | |
| calculate | hh_ppi_lookup | | | | | | pulldata('households', 'ppi_score', 'hh_id', ${household_id}) | |
| calculate | hh_eligible_lookup | | | | | | pulldata('households', 'is_eligible', 'hh_id', ${household_id}) | |
| note | hh_info_display | **Household Found:**<br>Name: ${hh_name_lookup}<br>Village: ${hh_village_lookup}<br>PPI Score: ${hh_ppi_lookup} | | | | ${hh_exists} != '' | | |
| note | hh_not_found_warning | **WARNING: Household ID not found in system!** Please verify the ID. | | | | ${hh_exists} = '' and ${household_id} != '' | | |
| text | household_name | Household Head Name | yes | | | | | |
| **end_group** | | | | | | | | |
| **begin_group** | consent | **Section 2: Consent** | | | | | | field-list |
| select_one yes_no | respondent_consent | Does the respondent give consent to participate? | yes | | | | | |
| **end_group** | | | | | | | | |
| **begin_group** | area_of_operation | **Section 3: Area of Operation** | | | | ${respondent_consent} = 'yes' | | field-list |
| select_one county_list | county | Select County | yes | | | | | |
| select_one subcounty_list | subcounty | Select Sub-County | yes | | | | | |
| select_one village_list | village | Select Village | yes | | | | | |
| calculate | village_valid | | | | | | pulldata('villages', 'village_id', 'village_name', ${village}) | |
| geopoint | household_gps | Capture Household GPS Location | yes | | | | | |
| **end_group** | | | | | | | | |
| **begin_group** | participant_info | **Section 4: Participant Basic Information** | | | | ${respondent_consent} = 'yes' | | field-list |
| select_one record_type | record_type | Is this a new or existing household? | yes | | | | | |
| text | national_id_number | National ID Number | yes | regex(., '^[0-9]{8}$') | ID must be 8 digits | | | |
| select_one gender | gender_displayed | Gender (from system) | | | | ${hh_exists} != '' | | |
| select_one yes_no | is_gender_correct | Is the gender correct? | yes | | | | | |
| select_one gender | correct_gender | Select correct gender | yes | | | ${is_gender_correct} = 'no' | | |
| date | date_of_birth_displayed | Date of Birth (from system) | | | | ${hh_exists} != '' | | |
| select_one yes_no | is_dob_correct | Is the date of birth correct? | yes | | | | | |
| date | correct_dob | Enter correct date of birth | yes | . <= today() | Date cannot be in future | ${is_dob_correct} = 'no' | | |
| select_one yes_no | owns_phone | Does participant own a phone/SIM card? | yes | | | | | |
| text | phone_number | Phone Number | yes | regex(., '^(07|01)[0-9]{8}$') | Invalid Kenya phone number | ${owns_phone} = 'yes' | | |
| select_one education_level | highest_education | Highest level of education in household | yes | | | | | |
| select_one education_level | participant_education | Participant's highest education level | yes | | | | | |
| select_one relationship | relationship_to_head | Relationship to household head | yes | | | | | |
| text | other_relationship | Specify other relationship | yes | | | ${relationship_to_head} = 'other' | | |
| **end_group** | | | | | | | | |
| **begin_group** | pwd_ovc | **Section 5: PWD and OVC** | | | | ${respondent_consent} = 'yes' | | field-list |
| select_one yes_no | has_disability | Does participant have any disability? | yes | | | | | |
| text | disability_type | Describe the disability | yes | | | ${has_disability} = 'yes' | | |
| select_one yes_no | family_disability | Does any family member have disability? | yes | | | | | |
| select_one yes_no | has_ovc | Are there OVC (orphans/vulnerable children) in household? | yes | | | | | |
| calculate | pwd_score | PWD Score | | | | | if(${has_disability} = 'yes', 10, 0) + if(${family_disability} = 'yes', 5, 0) + if(${has_ovc} = 'yes', 5, 0) | |
| **end_group** | | | | | | | | |
| **begin_group** | chronic_illness | **Section 6: Chronic Illness** | | | | ${respondent_consent} = 'yes' | | field-list |
| select_one yes_no | on_long_term_medication | Is participant on long-term medication? | yes | | | | | |
| select_one yes_no | family_on_medication | Is any family member on long-term medication? | yes | | | | | |
| calculate | chronic_score | Chronic Illness Score | | | | | if(${on_long_term_medication} = 'yes', 5, 0) + if(${family_on_medication} = 'yes', 5, 0) | |
| **end_group** | | | | | | | | |
| **begin_group** | household_details | **Section 7: Household Details** | | | | ${respondent_consent} = 'yes' | | field-list |
| integer | total_hh_members | Total number of household members | yes | . > 0 and . <= 30 | Must be between 1 and 30 | | | |
| integer | children_under_5 | Number of children under 5 years | yes | . >= 0 and . <= ${total_hh_members} | Cannot exceed total members | | | |
| integer | working_age_members | Number of working age members (16-64) | yes | . >= 0 and . <= ${total_hh_members} | Cannot exceed total members | | | |
| select_one yes_no | single_parent | Is this a single-parent household? | yes | | | | | |
| **end_group** | | | | | | | | |
| **begin_group** | savings | **Section 8: Savings** | | | | ${respondent_consent} = 'yes' | | field-list |
| select_one savings_location | savings_location | Where do you keep savings? | yes | | | | | |
| integer | savings_amount | Approximate savings amount (KES) | yes | . >= 0 | Cannot be negative | | | |
| select_one yes_no | member_of_savings_group | Are you a member of any savings group? | yes | | | | | |
| calculate | savings_score | Savings Score | | | | | if(${savings_amount} < 1000, 10, if(${savings_amount} < 5000, 5, 0)) | |
| **end_group** | | | | | | | | |
| **begin_group** | loans | **Section 9: Loans** | | | | ${respondent_consent} = 'yes' | | field-list |
| select_one yes_no | has_outstanding_loan | Do you have any outstanding loans? | yes | | | | | |
| integer | loan_amount | Outstanding loan amount (KES) | yes | . >= 0 | Cannot be negative | ${has_outstanding_loan} = 'yes' | | |
| select_one loan_source | loan_source | Source of loan | yes | | | ${has_outstanding_loan} = 'yes' | | |
| **end_group** | | | | | | | | |
| **begin_group** | income | **Section 10: Household Income** | | | | ${respondent_consent} = 'yes' | | field-list |
| integer | monthly_income | Estimated monthly household income (KES) | yes | . >= 0 | Cannot be negative | | | |
| select_multiple income_sources | income_sources | Sources of income (select all that apply) | yes | | | | | |
| calculate | income_score | Income Score | | | | | if(${monthly_income} < 3000, 15, if(${monthly_income} < 6000, 10, if(${monthly_income} < 10000, 5, 0))) | |
| **end_group** | | | | | | | | |
| **begin_group** | food_security | **Section 11: Food Security** | | | | ${respondent_consent} = 'yes' | | field-list |
| select_one meals_per_day | meals_per_day | How many meals does household eat per day? | yes | | | | | |
| select_one yes_no | skipped_meals_last_week | Did household skip any meals in the last 7 days? | yes | | | | | |
| select_one yes_no | worried_about_food | Were you worried about having enough food last month? | yes | | | | | |
| calculate | food_score | Food Security Score | | | | | if(${meals_per_day} = '1', 15, if(${meals_per_day} = '2', 10, 5)) + if(${skipped_meals_last_week} = 'yes', 5, 0) + if(${worried_about_food} = 'yes', 5, 0) | |
| **end_group** | | | | | | | | |
| **begin_group** | other_programs | **Section 12: Other Programs** | | | | ${respondent_consent} = 'yes' | | field-list |
| select_one yes_no | in_other_graduation_program | Is participant in another graduation program? | yes | | | | | |
| text | other_program_name | Name of other program | yes | | | ${in_other_graduation_program} = 'yes' | | |
| select_one participation_status | current_participation | Current participation status | yes | | | ${in_other_graduation_program} = 'yes' | | |
| calculate | program_score | Program Participation Score | | | | | if(${in_other_graduation_program} = 'yes', -20, 0) | |
| **end_group** | | | | | | | | |
| **begin_group** | willingness | **Section 13: Willingness to Participate** | | | | ${respondent_consent} = 'yes' | | field-list |
| select_one yes_no | willing_to_participate | Is participant willing to join UPG program? | yes | | | | | |
| select_one yes_no | can_attend_training | Can participant attend weekly training sessions? | yes | | | ${willing_to_participate} = 'yes' | | |
| select_one yes_no | willing_to_form_group | Is participant willing to form a business group? | yes | | | ${willing_to_participate} = 'yes' | | |
| **end_group** | | | | | | | | |
| **begin_group** | scoring | **Section 14: Eligibility Score** | | | | ${respondent_consent} = 'yes' | | field-list |
| calculate | total_eligibility_score | Total Eligibility Score | | | | | ${pwd_score} + ${chronic_score} + ${savings_score} + ${income_score} + ${food_score} + ${program_score} | |
| note | score_display | **ELIGIBILITY SCORE: ${total_eligibility_score}** | | | | | | |
| calculate | is_eligible | Eligibility Status | | | | | if(${total_eligibility_score} >= 40 and ${willing_to_participate} = 'yes' and ${in_other_graduation_program} = 'no', 'eligible', 'not_eligible') | |
| note | eligible_note | **STATUS: ELIGIBLE FOR UPG PROGRAM** | | | | ${is_eligible} = 'eligible' | | |
| note | not_eligible_note | **STATUS: NOT ELIGIBLE FOR UPG PROGRAM** | | | | ${is_eligible} = 'not_eligible' | | |
| **end_group** | | | | | | | | |
| **begin_group** | signature | **Section 15: Confirmation** | | | | ${respondent_consent} = 'yes' | | |
| image | participant_signature | Capture participant signature | yes | | | | | signature |
| text | surveyor_name | Surveyor Name | yes | | | | | |
| date | survey_date | Survey Date | yes | | | | | |
| **end_group** | | | | | | | | |


### CHOICES SHEET

| list_name | name | label |
|-----------|------|-------|
| yes_no | yes | Yes |
| yes_no | no | No |
| gender | male | Male |
| gender | female | Female |
| record_type | new | New Household |
| record_type | existing | Existing Household |
| education_level | none | No formal education |
| education_level | primary | Primary |
| education_level | secondary | Secondary |
| education_level | tertiary | Tertiary/University |
| relationship | head | Household Head |
| relationship | spouse | Spouse |
| relationship | child | Child |
| relationship | parent | Parent |
| relationship | sibling | Sibling |
| relationship | other | Other |
| savings_location | home | At home |
| savings_location | bank | Bank account |
| savings_location | mobile | Mobile money (M-Pesa) |
| savings_location | sacco | SACCO |
| savings_location | group | Savings group |
| savings_location | none | No savings |
| loan_source | bank | Bank |
| loan_source | mobile | Mobile loan (Fuliza, etc.) |
| loan_source | sacco | SACCO |
| loan_source | group | Savings group |
| loan_source | family | Family/Friends |
| loan_source | shylock | Shylock/Money lender |
| income_sources | farming | Farming |
| income_sources | casual_labor | Casual labor |
| income_sources | small_business | Small business |
| income_sources | formal_employment | Formal employment |
| income_sources | remittances | Remittances |
| income_sources | pension | Pension |
| income_sources | none | None |
| meals_per_day | 1 | One meal |
| meals_per_day | 2 | Two meals |
| meals_per_day | 3 | Three or more meals |
| participation_status | active | Currently active |
| participation_status | graduated | Graduated |
| participation_status | dropped | Dropped out |


### SETTINGS SHEET

| form_title | form_id | version | style |
|------------|---------|---------|-------|
| UPG HH Eligibility Tool | upg_hh_eligibility | 2025.1 | pages |


---

## Notes for Implementation

### Offline Validation with pulldata()
1. Upload CSV files to KoBoToolbox before deploying the form
2. The `pulldata()` function works offline once CSVs are synced to devices
3. CSV files must be re-uploaded when data changes in UPG MIS

### Scoring Logic
- Total score is calculated from multiple components
- Threshold of 40+ points = Eligible
- Participation in other programs disqualifies (-20 points)

### Data Flow
```
UPG MIS → Export CSVs → KoBoToolbox Media Files → Mobile Device (Offline)
                                                        ↓
                                                 Form Submission
                                                        ↓
                                         KoBoToolbox → UPG MIS (via API)
```

### Recommended Update Frequency
- Households CSV: Weekly
- BM Cycles CSV: Monthly
- Villages CSV: As needed (rarely changes)

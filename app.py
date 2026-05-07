from extract_schema import extract_schema
from extract_findings import extract_core_findings
import json
JSON = {
    "abstract":{
            "Objective":"""To assess and compare the diagnostic accuracy of the Pediatric Risk of Mortality (PRISM) III score
and Pediatric Sequential Organ Failure Assessment (p-SOFA) for the prediction of mortality in critically ill
children.""",
    "Methodology":"""This was a cross-validation study conducted at the Pediatric Intensive Care Unit (PICU) of the
National Institute of Child Health Karachi from February 2021 to July 2021. Two hundred eighty-six critically
ill children of age one month to 15 years of either gender staying in PICU for more than 24 hours were
included. Within 24 hours of admission, the p-SOFA and PRISM III 24 scores were calculated for all eligible
children. The outcome of the study was mortality within 30 days of PICU admitted children. Data were
analyzed using Statistical Package for the Social Sciences (SPSS) version 23.
""",
"Results":"""The median age was 24 months (range: 1-144 months). The 30-day mortality was estimated as 57%.
The p-SOFA and PRISM scores were significantly greater in children who did not survive than survivors. The
maximum p-SOFA score (area under the curve (AUC)=0.81, 95% CI=0.76-0.86, p=0.001) and PRISM III 24
score (AUC=0.75, 95% CI=0.69-0.81, p=0.001) had good discrimination for 30-day mortality. For the
prediction of 30-day mortality at the cut-off value of p-SOFA>2, the sensitivity was 93.87%, specificity was
38.21%, and accuracy was 69.93%. Whereas at the cut-off value of PRISM III 24 score>8, the sensitivity was
55.83%, specificity was 77.24%, and accuracy was 65.03%."""
    },
    "Materials And Methods":"""From February to July 2021, cross-validation research was done in the PICU of the National Institute of Child
Health (NICH) in Karachi. This study was carried out with the approval of NICH Karachi's Institutional
Ethical Review Board, approval number 42/2020, and with the signed informed consent of the children's
parents. The sample size was calculated using the diagnostic accuracy sample size calculator by Dr. Lin
Naing, with PRISM sensitivity of 70.6%, specificity of 82.3%, a margin of error of 5.2%, 30-day mortality
prevalence of 28.1%, and a confidence level of 95%. The sample size was calculated to be 286 [2]. A nonprobability consecutive sampling approach was used to include critically ill children aged one month to 15
years of either gender who had been in the PICU for more than 24 hours. Patients with an underlying
congenital deformity who were hospitalized for routine treatment before planned procedures such as
intravenous immunoglobulin (IVIG) and hemodialysis, cardiopulmonary resuscitation (CPR) before
admission, and children who died within 12 hours of admission were excluded from the research. Within 24
hours of admission, the p-SOFA score was calculated for all eligible children. p-SOFA score of higher than 2
is considered as a predictor of mortality. We calculated PRISM III score within 24 hours after admission, in
addition to p-SOFA. A score of higher than 8 on the PRISM III 24 was deemed a predictor of mortality. On a
pre-designed proforma, demographic data such as age, weight, type of admission (clinical or medical cases
and surgical (post-surgical recovery cases)), length of stay in PICU, need for ventilator support, and
inotropic support was also noted by the researcher himself. All of the children were followed up from
admission till discharged from the PICU. Mortality within 30 days was the outcome of the study.
After collecting data the analyses were conducted by using Statistical Package for Social Sciences (SPSS)
version 23 (IBM Corp., Armonk, NY, USA). We presented our numeric data with median and range as they
were non-normally distributed. We presented our categorical variables with frequencies and percentages.
We compared numeric data with the Mann-Whitney U test and categorical data with the chi-square test to
assess the association with mortality. PRISM III 24 and p-SOFA scores were categorized according to the
25th, 50th, and 75th percentiles of these scores. Comparison between categories of PRISM III 24 score and
p-SOFA with 30-day mortality were done using Pearson’s chi-square test. Two by two tables were used to
calculate the specificity (Sp), sensitivity (Sn), negative predictive value (NPV), positive predictive value
(PPV), and accuracy of PRISM III 24 and p-SOFA scores by taking 30-day mortality as the gold standard.
Spearmen’s correlation was applied to assess the relationship between the duration of PICU stay and both
scores (PRISM III 24 score and p-SOFA score). A p-value of ≤0.05 was taken as statistically significant.""",
"Results":"""We included 286 children in the study. The median age was 24 months (range: 1-144 months). The 30-day
mortality was estimated as 57%. The median age of 163 non-survivors was 24 months (range: 2-144
months). Table 1 displays the other information of non-survivors and survivors.""",
"Introduction":"""The pediatric intensive care unit (PICU) plays an important role in delivering demanding and required care
to seriously ill children. In both developing and developed countries, PICU children have a considerably
higher risk of morbidity and death [1,2]. Quality and quantities of PICUs are improving in developing
countries like Pakistan, but it is an uphill process, as the units need modern, expensive equipment and a
large highly trained staff. So there is a need for time to employ methods, techniques, and scoring systems
that are predictive of mortality and morbidity risk in these patients, thus allowing these systems to assist in
timely and focused decisions regarding the deployment of different expertise and resources, to produce
highly productive results [3,4].
Several prognostic scoring systems like Pediatric Index of Mortality (PIM and PIM2), Pediatric Risk of
Mortality (PRISM, PRISM III), Sequential Organ Failure Assessment (SOFA), Pediatric Sequential Organ
Failure Assessment Score (p-SOFA), and the Paediatric Logistic Organ Dysfunction (PELOD) score have been
developed to predict PICU children's morbidity and death, which can be extremely helpful in treatment
planning [1,2,5-9]. The PRISM III 24 score is a commonly used system that is used to evaluate various
scoring systems. PRISM III 24 score helps us in predicting institutional performance [10,11]. Models like the
PRISM III 24 score provide one of the best ways to organize an intensive care unit. PRISM III 24 score takes
24 hours to complete and cannot be used in regulating admissions to the PICU but only to assess illness
severity and length of stay [3,12]. The p-SOFA has been developed recently and so far only validated
retrospectively in critically ill children [13,14]. Whereas only a few studies have been conducted for
validation of p-SOFA and PRISM III in developing countries like Pakistan. An ideal scoring system would be
accurate, easy to use, and simple, as well as minimally intrusive and low-cost. However, no scoring system is
flawless, and each one has its own set of limitations, which is why studies are being conducted to enhance
"""
}
core_findings = extract_core_findings(JSON)
# print(core_findings)
print(
    json.dumps(
        extract_schema(core_findings, JSON),
        indent=2,
        ensure_ascii=False
    )
)
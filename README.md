# NexaMove: AI-Powered Reskilling and Internal Talent Mobility Platform

NexaMove is an AI-supported internal talent mobility and reskilling prototype developed as part of the MSc Business Analytics project at the University of Greenwich.

The project investigates how predictive analytics, internal-role recommendation, skill-gap identification and personalised learning recommendations can be integrated into a single decision-support workflow for employees and HR teams.

## Project Objectives

The project was developed to:

- analyse employee skill profiles and internal role requirements;
- identify potential internal career opportunities;
- evaluate employee readiness for selected roles;
- identify skill gaps;
- recommend relevant learning and reskilling pathways;
- support HR review through transparent analytical outputs.

## Project Components

NexaMove consists of two connected interfaces:

### Employee Career Portal

The employee portal enables users to:

- retrieve an employee profile;
- select a target internal role;
- review role requirements;
- update skills and certifications;
- upload supporting information;
- complete a role-specific assessment;
- view career-readiness results;
- identify missing skills;
- access recommended learning pathways;
- apply or express interest in an internal opportunity.

### HR Dashboard

The HR dashboard provides:

- internal candidate information;
- readiness analytics;
- skill-match results;
- assessment performance;
- experience and salary alignment;
- identified skill gaps;
- candidate-review information for human decision-making.

NexaMove is designed as a decision-support system rather than an automated employment-selection system.

## Dataset

The project uses an original synthetic HR feasibility dataset containing:

- 1,200 employee profiles;
- 1,200 linked internal applications;
- 22 internal roles;
- 62 skill-to-learning mappings;
- 110 role-related assessment questions.

Synthetic data were used to avoid processing identifiable or confidential employee information.

The `transition_success` target was synthetically constructed for feasibility testing. The associated `transition_success_probability` generation field was excluded from the predictive feature set to prevent direct target leakage.

Therefore, the machine-learning results should be interpreted as evidence of analytical workflow feasibility rather than proof of predictive performance in a real organisational workforce.

## Machine-Learning Workflow

Five classification algorithms were evaluated:

- Logistic Regression
- Support Vector Machine
- Gradient Boosting
- Random Forest
- Decision Tree

The modelling workflow included:

- data validation;
- preprocessing;
- stratified train-test splitting;
- model comparison;
- five-fold cross-validation;
- hyperparameter optimisation;
- majority-class baseline comparison;
- precision-recall and decision-threshold analysis.

The final tuned Logistic Regression model achieved:

- Accuracy: 65.83%
- Precision: 50.40%
- Recall: 75.90%
- F1-score: 60.58%
- ROC-AUC: 74.95%

The majority-class baseline achieved 65.42% accuracy. The model is therefore interpreted primarily in terms of discriminatory and ranking information rather than overall accuracy alone.

## Internal Role Recommendation

The recommendation component evaluates internal roles using:

- skill match;
- experience suitability;
- role-level suitability.

The prototype recommendation score uses the following weighting:

- 60% Skill Match
- 25% Experience Suitability
- 15% Role-Level Suitability

Sensitivity analysis was also conducted using alternative weighting configurations to assess whether the highest-ranked recommendation was dependent on the selected weighting structure.

## Reskilling Recommendation Logic

Identified missing skills are mapped to relevant learning resources using the course-mapping dataset.

The reskilling analysis is scenario-based. Projected post-learning outcomes assume that mapped skills are successfully acquired after course completion.

These results are intended to demonstrate the internal consistency of the recommendation workflow and should not be interpreted as evidence of causal reskilling effectiveness.

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Streamlit
- Microsoft Excel
- Jupyter Notebook

## Repository Contents

This repository contains the main project materials, including:

- final Jupyter Notebook;
- synthetic HR dataset;
- machine-learning analysis;
- recommendation and skill-gap logic;
- validation outputs;
- project documentation.

## Live Prototype

NexaMove is deployed as an interactive Streamlit application.

Live prototype:

https://ai-app-talent-mobility-platform-57nsdls2va2fn2kzv8phop.streamlit.app/

## Limitations

The project has several important limitations:

- employee records and transition outcomes are synthetic;
- predictive performance has not been validated using real organisational HR data;
- the reskilling evaluation is scenario-based rather than causal;
- formal employee and HR usability testing has not yet been conducted;
- the Streamlit application is a research prototype rather than an enterprise production system.

Future development should include organisational pilot testing, real-world data validation, fairness assessment, user testing, model monitoring and secure integration with HRIS and learning-management systems.

## Academic Project

**Project Title:** AI-Powered Reskilling and Internal Talent Mobility Platform: Development and Evaluation of NexaMove

**Programme:** MSc Business Analytics

**Module:** Business Analytics Project – BUSI 1783

**University:** University of Greenwich

**Student:** Pavithra Jada

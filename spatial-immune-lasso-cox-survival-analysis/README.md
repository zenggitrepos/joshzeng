
# Spatial Immune-cell LASSO Cox Survival Analysis

## Overview

This project focuses on a survival-analysis workflow using spatial immune-cell features. The goal is to identify immune-cell spatial parameters associated with patient survival and build an interpretable prognostic model.

The analysis applies **LASSO Cox regression** to select survival-associated spatial immune features and evaluate their relationship with clinical outcome.

## Goal of the Analysis

The main goal is to use spatial immune-cell measurements to:

- identify prognostic immune microenvironment features
- reduce high-dimensional spatial variables using LASSO regularization
- build a Cox survival model for outcome association
- support biomarker discovery in the tumor microenvironment

## Machine-learning / Statistical Method

- **LASSO Cox regression**
- **Cox proportional hazards modeling**
- **Regularized feature selection**
- **Survival-risk modeling**

LASSO Cox regression is used because it can shrink less informative variables toward zero while retaining features most associated with survival outcome.

## Workflow

1. Load spatial immune-cell parameters and survival metadata
2. Preprocess clinical and spatial feature data
3. Fit a LASSO Cox regression model
4. Select survival-associated spatial immune features
5. Estimate patient risk scores
6. Evaluate prognostic separation between risk groups
7. Interpret selected immune spatial features in the tumor microenvironment context

## Tools

- R / Python
- Jupyter Notebook
- Survival-analysis packages
- LASSO / regularized regression packages
- Data visualization packages


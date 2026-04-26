# Contributing Guidelines

Thank you for your interest in contributing to this project.

This repository was developed as an end-to-end supplier risk intelligence platform focused on operational KPI scoring, FinBERT-based sentiment analysis, LLM-generated risk narratives, and interactive dashboarding for procurement teams. Contributions, suggestions, and improvements are welcome.

## How to Contribute

If you would like to contribute, please follow these guidelines:

1. Fork the repository
2. Create a dedicated feature branch
3. Make your changes
4. Test your changes locally
5. Submit a pull request with a clear and concise description

## Contribution Areas

Potential contribution areas include:

- synthetic data generation improvements
- KPI engine enhancements
- sentiment analysis pipeline improvements
- risk scoring model refinement
- LLM prompt and brief-generation enhancements
- alert logic and threshold improvements
- DuckDB persistence and data model improvements
- Plotly Dash dashboard features and usability enhancements
- testing, reproducibility, and project structure improvements
- documentation and usage examples

## Coding Standards

Please follow these basic rules:

- Write clear, readable, and modular Python code
- Prefer reusable functions and source modules over duplicated logic
- Use meaningful names for files, variables, functions, and classes
- Add comments where the logic is not immediately obvious
- Keep ingestion, features, intelligence, database, dashboard, scripts, and tests well organized
- Maintain consistency with the existing project structure and naming conventions
- Validate structured data carefully when working with scoring logic, generated outputs, and schema-based models

## Testing

Before submitting changes, make sure that:

- scripts and application modules run correctly from the project root
- file paths, imports, and configuration values remain consistent
- outputs are reproducible where applicable
- no API keys, local environment files, or unnecessary generated artifacts are committed
- relevant documentation is updated
- changes do not break the KPI, sentiment, risk scoring, intelligence, dashboard, or persistence workflow
- tests pass successfully using `pytest tests/ -v`

## Data Usage

This project uses synthetically generated supply chain transaction data, country risk lookup data, and generated supplier news headlines for experimentation and demonstration purposes.

To keep the repository clean and safe:

- do not commit secrets such as `.env` files or API keys
- do not push unnecessary generated files, caches, or temporary artifacts
- keep synthetic data generation reproducible and well documented
- document any assumptions introduced into the data generation or scoring logic
- ensure any example data used for testing remains non-sensitive and appropriate for public sharing

## Project Scope

This repository is primarily focused on:

- supplier KPI computation
- sentiment-based supplier risk signals
- weighted risk scoring and tier classification
- LLM-generated procurement risk narratives
- alert generation and supplier risk monitoring
- DuckDB-based analytical persistence
- dashboard-based supplier risk intelligence

Please keep contributions aligned with the core purpose of the project.

## Pull Request Notes

When opening a pull request, please include:

- a short summary of the change
- why the change improves the project
- any impact on KPI calculations, sentiment outputs, risk scores, alerts, dashboard behaviour, or generated briefs
- any new dependencies, assumptions, configuration changes, or setup steps

## Questions or Suggestions

If you would like to suggest an improvement, feel free to open an issue or submit a pull request.
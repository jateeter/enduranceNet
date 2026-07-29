# Preserve legacy URLs and redirects

## Goal

Ensure public legacy URLs continue to work after the React/Scala deployment.

## Scope

- Build a legacy URL table from source paths and public crawl evidence.
- Add Scala redirect/resolve endpoint or Nginx rules as appropriate.
- Preserve anchors where practical for Current News and Featured Stories.
- Route immutable raw archive pages when structured migration is not warranted.
- Add link-checking verification.

## Acceptance Criteria

- A representative crawl of legacy URLs returns either 200 or intentional 301/302.
- Static `.html` legacy URLs are not assumed static; they are resolved through
  the migration model.
- Redirect behavior is covered by automated tests.


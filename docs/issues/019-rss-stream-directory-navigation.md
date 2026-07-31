# RSS stream directory navigation

## Problem

The RSS corpus spans active news, long-lived community streams, event/team
archives, photo journals, and resource channels. The new website needs a uniform
navigation surface that lets readers scan the corpus without learning legacy
folder structure.

## Scope

- Add a `/streams` route to the React app.
- Group streams by editorial purpose: Active News, Community, Event & Team
  Archives, News Archives, Photo & Travel Journals, Resources, and Archive.
- Use the current Endurance.Net palette, masthead rhythm, compact cards, and
  list/card styling.
- Show source freshness, stream type, legacy source, and canonical RSS action.
- Add the stream directory to primary navigation.

## Acceptance Criteria

- The stream directory renders from `/api/streams`.
- Active streams appear first.
- Stream grouping works on desktop and mobile.
- The page uses the same visual language as the current landing page.

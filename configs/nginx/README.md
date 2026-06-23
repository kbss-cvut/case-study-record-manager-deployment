# Gateway Dashboard

This directory contains the static dashboard for the Record Manager gateway.
The dashboard is a lightweight landing page served by Nginx. It shows available applications and services exposed through the gateway.

## Main files

| File / Directory | Purpose                                                                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `index.html`     | Main dashboard page. Defines the page structure and includes the header, footer, services section, stylesheet, and JavaScript. |
| `services.json`  | Configuration file for service cards shown on the dashboard.                                                                   |
| `dashboard.js`   | JavaScript that loads `services.json` and renders service cards into the page.                                                 |
| `partials/`      | Directory with reusable HTML fragments included into dashboard pages, such as shared header and footer markup.                 |
| `styles/`        | Directory with separated CSS files for the dashboard layout and responsive behavior.    |
| `images/`        | Directory with static images used by the dashboard, service cards, logos, icons, and favicon.                                  |
| `styles.css`     | Main stylesheet entry file loaded by `index.html`.                                                                             |
| `error.html`     | Static Nginx error page used for backend, proxy, or gateway errors.                                                            |


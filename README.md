# CareRoute Prototype Web

Web parity prototype for the Android CareRoute demo flow.

## Live URLs
- Web app (Try Demo): `https://watsoncsulahack.github.io/careroute-prototype-web/`
- Live monitor: `https://watsoncsulahack.github.io/careroute-prototype-web/monitor.html`
- Landing page: `https://watsoncsulahack.github.io/careroute-landing-page/`

## Included parity flow
- O01 Welcome/Auth
- O02 Sign In
- O03 Register Identity
- O04 Register Insurance
- O05 Medical + Consent (**merged screen 5+6**)
- M01 Big round CALL FOR HELP
- M02 Auto loading (2s)
- M03 Route found summary
- M04 Merged map + dispatch summary (screen 7 removed)

## Online registration writes
Web app writes registrations to Cloudant via update-handler form POST fallback, and monitor reads records using online fetch/JSONP paths.

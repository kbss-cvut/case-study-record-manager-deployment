#!/usr/bin/env bash
#
# Fix the exported vita-form.ttl so it works in the deployment.
#
# Two post-export fixups are applied:
#
#   1. The form is exported with a developer-local RDF4J endpoint baked into
#      every `form:has-possible-values-query`. This rewrites it to the
#      in-cluster GraphDB endpoint used by the deployment so the queries
#      resolve at runtime.
#
#   2. The root `form:form-template` label is exported with an `@en` language
#      tag, which leaks into the UI. This strips the language tag from it.
#
set -euo pipefail

OLD_URL='http://localhost:58080/rdf4j-server/repositories/vita-study-formgen'
NEW_URL='http://db-server:7200/repositories/record-manager-formgen'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORM_FILE="${1:-$SCRIPT_DIR/../configs/db-server/import/record-manager-formgen/forms/vita-form.ttl}"

if [[ ! -f "$FORM_FILE" ]]; then
    echo "Form file not found: $FORM_FILE" >&2
    exit 1
fi

# 1. Rewrite the local possible-values query endpoint to the GraphDB endpoint.
count=$(grep -c "$OLD_URL" "$FORM_FILE" || true)
if [[ "$count" -eq 0 ]]; then
    echo "No occurrences of the local endpoint in $FORM_FILE — nothing to do."
else
    sed -i "s#${OLD_URL}#${NEW_URL}#g" "$FORM_FILE"
    echo "Replaced $count occurrence(s) of the local endpoint with the GraphDB endpoint in $FORM_FILE"
fi

# 2. Strip the language tag from the form-template label.
lang_removed=$(perl -0777 -i -pe \
    '$c += s/(form:form-template\b.*?rdfs:label\s+"[^"]*")\@[A-Za-z-]+/$1/s; END { print STDERR $c }' \
    "$FORM_FILE" 2>&1)
if [[ "$lang_removed" -eq 0 ]]; then
    echo "No language tag on the form-template label in $FORM_FILE — nothing to do."
else
    echo "Removed the language tag from the form-template label in $FORM_FILE"
fi

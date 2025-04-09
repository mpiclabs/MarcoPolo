#!/bin/bash
# Authenticator script for Certbot with precise challenge handling
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "running auth script"

mkdir -p $SCRIPT_DIR/webroot/.well-known/acme-challenge
echo "created webroot at $SCRIPT_DIR/webroot/.well-known/acme-challenge"

# Write the validation string to the specified file, so that the challenge can be validated
echo "$CERTBOT_VALIDATION" > $SCRIPT_DIR/webroot/.well-known/acme-challenge/"$CERTBOT_TOKEN"
echo "wrote validation string $CERTBOT_VALIDATION to $SCRIPT_DIR/webroot/.well-known/acme-challenge/$CERTBOT_TOKEN"

# Write the token to the token file, so that it can be read by Marco-Polo
echo "$CERTBOT_TOKEN" > $SCRIPT_DIR/token
echo "wrote token $CERTBOT_TOKEN to $SCRIPT_DIR/token"

# Exit the script
exit 0

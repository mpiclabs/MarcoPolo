#!/bin/bash
# Cleanup script for Certbot to destroy the temporary HTTP server
echo "about to run cleanup"
rm -f "~/certbot_tools/webroot/.well-known/acme-challenge/$CERTBOT_TOKEN"
echo "ran cleanup"

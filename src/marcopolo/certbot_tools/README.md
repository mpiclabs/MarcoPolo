authenticator script-- 
-this allows us to extract the token used by certbot. without that we wouldn't be able to query the nodes by token, meaning we won't be able to identify which ips contacted each test node during this attack.
-cerbot uses the authenticator script to place the validation token in the correct place and pass DCV-- since we're replacing that script, we need to include that step as well. Why do we need the challenge to pass if we only care about the DCV requests? Because some CA's (including Let's Encrypt) use a preflight request-- if the first doesn't pass, it doesn't bother with the rest. 

cleanup script--
we just delete the acme-challenge file to avoid wasting space

token-- we right to and read from this file to keep track of the token for each Turn

config, work, logs-- 
Certbot defaults to using:
/etc/letsencrypt (for --config-dir)
/var/lib/letsencrypt (for --work-dir)
/var/log/letsencrypt (for --logs-dir)
these are all system-level-directories, meaning certbot needs to be run from root. To avoid running wild with permissions, we manually provide local folders to write to instead.

webroot-- this is where the validation tokens will be stored in '.well-known/acme-challenge' in order to pass validation. Webroot needs to be served for this to work.
webroot_server.py-- functions to control the server serving webroot.

IMPORTANT: For any of this to work, you need to be running a basic python server pointing to webroot. Why? Because each node forwards any acme requests to the central server (an ip that is hardcoded, which means as of now you can only run marcopolo with let's encrypt on that one server). This request will automatically go to port 80, which means not only does something need to listen on that port, but that something needs to have the challenge ready to be returned. We do that by spinning up a basic python server that points to webroot. That is the equivalent of what 
```bash
certbot certonly --standalone
```
does-- it temporarily spins up a basic webserver at webroot, then writes the tokens to it so that DCV requests will pass.

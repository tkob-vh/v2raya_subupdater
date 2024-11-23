# v2raya subscription updater

Update the subscription automatically according to the provided `config.yaml`.

There is a systemd service file and corresponding timer to help me update the rules regularly.

## Example

`config.yaml`
```yaml
subscription: "AABB.com"
server_name: "ADBC.com:1145"
```

Then when executing the script, it will update the subscription `AABB.com` and connect to the server `ADBC.com:1145`, regardless of whether or not you are connecting to a server, or the server you previously connected became invalid.




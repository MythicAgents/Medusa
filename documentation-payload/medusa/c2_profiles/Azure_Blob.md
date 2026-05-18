+++
title = "Azure Blob"
chapter = false
weight = 103
+++

## Summary
The `medusa` agent supports Azure Blob Storage as a transport profile.

Tasking and responses are exchanged through blobs in the provisioned container:

- Agent uploads request blobs to `ats/<message_id>.blob`
- Agent polls and downloads response blobs from `sta/<message_id>.blob`
- Agent deletes processed response blobs after retrieval

At build time, Medusa calls the `azure_blob` service to provision scoped configuration and stamps the generated values into the payload.

### Profile Option Deviations

#### Callback Interval / Jitter
The Azure Blob transport uses callback interval and jitter to control polling cadence for `sta/` response blobs.

#### HTTPS Verification
If Medusa build parameter `https_check` is set to `No`, TLS certificate verification is disabled for blob operations.

### Build-Time Notes

When `azure_blob` is selected, Medusa:

1. Requests configuration from the `azure_blob` service (`generate_config` RPC)
2. Embeds:
   - blob endpoint
   - container name
   - scoped SAS token
3. Uses the core+transport template assembly process to generate the final payload

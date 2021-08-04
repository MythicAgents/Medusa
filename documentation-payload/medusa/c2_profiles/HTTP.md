+++
title = "HTTP"
chapter = false
weight = 102
+++

## Summary
The `medusa` agent uses a series of `POST` web requests to send responses for tasking and a series of `GET` requests to get tasking from the Mythic server. 

### Profile Option Deviations

#### Callback Host
The URL for the redirector or Mythic server. This must include the protocol to use (e.g. `http://` or `https://`).

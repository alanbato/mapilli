# Protocol Types

The protocol module contains the request and response types.

## FingerRequest

::: mapilli.protocol.request.FingerRequest
    options:
      show_root_heading: true
      members:
        - parse
        - to_wire
        - wire_query
        - target_host

## FingerResponse

::: mapilli.protocol.response.FingerResponse
    options:
      show_root_heading: true
      members:
        - body
        - host
        - port
        - query
        - lines

## QueryType

::: mapilli.protocol.request.QueryType
    options:
      show_root_heading: true

## Constants

::: mapilli.protocol.constants
    options:
      show_root_heading: true
      members:
        - DEFAULT_PORT
        - DEFAULT_TIMEOUT
        - MAX_RESPONSE_SIZE
        - CRLF
        - VERBOSE_PREFIX

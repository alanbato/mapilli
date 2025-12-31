# CLI Reference

Complete reference for the `mapilli` command-line interface.

## Synopsis

```
mapilli [OPTIONS] [QUERY]
```

## Description

Query Finger servers from the command line.

## Arguments

### QUERY

The query string to send to the Finger server.

**Formats:**

| Format | Description | Example |
|--------|-------------|---------|
| `user@host` | Query user at host | `alice@example.com` |
| `user` | Query user (requires `-h`) | `alice -h example.com` |
| `@host` | Forward to host | `@remote.com` |
| `/W user` | Verbose query | `/W alice@example.com` |

## Options

### `-h, --host TEXT`

Target host. Required if not specified in the query.

```bash
mapilli alice -h example.com
```

### `-p, --port INTEGER`

Target port. Default: `79`

```bash
mapilli alice@example.com -p 1079
```

### `-t, --timeout FLOAT`

Request timeout in seconds. Default: `30.0`

```bash
mapilli alice@example.com -t 10
```

### `-W, --whois`

Request verbose/whois output from the server. Adds the `/W` prefix to the query.

```bash
mapilli -W alice@example.com
```

### `-V, --version`

Show version and exit.

```bash
mapilli --version
```

### `--help`

Show help message and exit.

```bash
mapilli --help
```

## Examples

### Query a User

```bash
mapilli alice@example.com
```

### List All Users

```bash
mapilli -h example.com
```

### Verbose Output

```bash
mapilli -W alice@example.com
# Equivalent to:
mapilli "/W alice@example.com"
```

### Custom Timeout

```bash
mapilli alice@example.com -t 5
```

### Custom Port

```bash
mapilli alice@example.com -p 1079
```

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (timeout, connection, invalid query) |

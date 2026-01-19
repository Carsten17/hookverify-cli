# HookVerify CLI

Receive webhooks on your local machine during development. No need for ngrok or tunneling services.

## Installation

Download the latest release for your platform from the [Releases page](https://github.com/Carsten17/hookverify-cli/releases).

### Windows
```powershell
# Download hookverify.exe and add to your PATH
```

### macOS / Linux
```bash
# Download, make executable, and move to PATH
chmod +x hookverify
sudo mv hookverify /usr/local/bin/
```

## Usage

### Login
```bash
hookverify login --api-key YOUR_API_KEY
```

### Listen for webhooks
```bash
# Forward webhooks to localhost:3000
hookverify listen 3000

# Forward to a specific path
hookverify listen 8080 --path /webhooks/stripe
```

### Check status
```bash
hookverify status
```

### Logout
```bash
hookverify logout
```

## How It Works

1. Configure your webhook source (Stripe, Shopify, etc.) to send to your HookVerify endpoint
2. Run `hookverify listen 3000` on your local machine
3. Webhooks are received by HookVerify and forwarded to your localhost in real-time

## Commands

| Command | Description |
|---------|-------------|
| `hookverify login` | Authenticate with your API key |
| `hookverify listen <port>` | Forward webhooks to localhost |
| `hookverify status` | Check connection status |
| `hookverify logout` | Remove stored credentials |
| `hookverify version` | Show CLI version |

## Requirements

- A [HookVerify](https://hookverify.com) account
- Your HookVerify API key (found in Dashboard → API Keys)

## License

MIT License - see [LICENSE](LICENSE) file.

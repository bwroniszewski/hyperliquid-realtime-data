# Security Guidelines

## ⚠️ Important Security Notice

This application requires your **private key** to access Hyperliquid APIs. This is a sensitive credential that provides full access to your wallet.

## Security Best Practices

### 1. **Never Commit Credentials**
- ✅ The `config.json` file is already in `.gitignore`
- ✅ Never commit private keys to version control
- ✅ Use environment variables when possible

### 2. **Use Environment Variables (Recommended)**
```bash
export HYPERLIQUID_ACCOUNT_ADDRESS="your_wallet_address"
export HYPERLIQUID_SECRET_KEY="your_private_key"
export HYPERLIQUID_IS_MAINNET="true"
```

### 3. **File Permissions**
Set restrictive permissions on configuration files:
```bash
chmod 600 config.json
chmod 600 .env
```

### 4. **Use Dedicated Wallets**
- Create a separate wallet for API access
- Don't use your main trading wallet
- Only fund the dedicated wallet with necessary amounts

### 5. **Monitor Usage**
- Regularly check your wallet activity
- Monitor API usage
- Set up alerts for unusual activity

### 6. **Network Security**
- Use secure networks (avoid public WiFi)
- Consider using VPN
- Keep your system updated

### 7. **Backup Security**
- Encrypt backup files containing credentials
- Use secure cloud storage with 2FA
- Never share backup files

## Risk Mitigation

### What Could Go Wrong
1. **Private key exposure**: Full wallet access
2. **Unauthorized trading**: Malicious actors could trade on your behalf
3. **Fund theft**: Complete loss of wallet funds
4. **API abuse**: Excessive API usage leading to rate limits

### Mitigation Strategies
1. **Minimal funding**: Only keep necessary funds in API wallet
2. **Regular rotation**: Change private keys periodically
3. **Monitoring**: Set up alerts for wallet activity
4. **Isolation**: Use separate wallets for different purposes

## Emergency Procedures

### If Credentials Are Compromised
1. **Immediately transfer funds** to a secure wallet
2. **Revoke API access** if possible
3. **Generate new wallet** for future use
4. **Review logs** for unauthorized activity
5. **Report incident** to relevant authorities if necessary

### Recovery Steps
1. Create new wallet
2. Update configuration with new credentials
3. Test with small amounts first
4. Monitor for any issues

## Compliance

### Regulatory Considerations
- Check local regulations regarding crypto trading
- Ensure compliance with financial regulations
- Consider tax implications of automated trading

### Data Protection
- Be aware of data retention policies
- Consider GDPR compliance if applicable
- Protect user data appropriately

## Support

If you suspect a security issue:
1. **Don't panic** - follow emergency procedures
2. **Document everything** - keep records of the incident
3. **Seek professional help** - consider consulting security experts
4. **Report responsibly** - follow responsible disclosure practices

## Disclaimer

This document provides general security guidance. Security is your responsibility. The authors are not liable for any security incidents or financial losses. 
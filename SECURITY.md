# Security Guidelines

## 🔐 API Key Management

### Never Commit API Keys
- **NEVER** put API keys directly in code
- **NEVER** put API keys in documentation files
- **NEVER** commit `.env` files to git

### Proper Way to Handle API Keys

#### Local Development
1. Copy `.env.example` to `.env`
2. Fill in your actual API keys in `.env`
3. The `.env` file is gitignored and won't be committed

#### Production Deployment (Render/Vercel)
1. Go to your hosting dashboard
2. Add environment variables in the UI
3. Never hardcode them in your code

### Environment Variables Checklist

✅ **DO:**
- Use `.env` files locally
- Add secrets via hosting platform UI
- Use `.env.example` as a template (without real values)
- Rotate keys regularly
- Use different keys for dev/staging/production

❌ **DON'T:**
- Commit `.env` files
- Put keys in documentation
- Share keys in chat/email
- Use the same key across environments
- Hardcode keys in source code

## 🚨 If You Accidentally Expose a Key

1. **Revoke the key immediately**
   - Google Gemini: https://aistudio.google.com/app/apikey
   
2. **Generate a new key**

3. **Update your environment variables**
   - Locally: Update `.env`
   - Render: Dashboard → Environment → Update variable
   - Vercel: Dashboard → Settings → Environment Variables

4. **Remove from git history** (if committed)
   ```bash
   # Option 1: Use BFG Repo-Cleaner
   java -jar bfg.jar --replace-text passwords.txt
   
   # Option 2: Use git filter-repo
   pip install git-filter-repo
   git filter-repo --replace-text passwords.txt
   ```

5. **Close GitHub security alert** once key is revoked

## 🛡️ Additional Security Best Practices

### Database
- Use strong passwords
- Never commit database credentials
- Use environment variables for connection strings

### Authentication
- Use strong JWT secrets
- Rotate secrets periodically
- Never log sensitive data

### CORS
- Configure allowed origins properly
- Don't use `*` in production

### File Uploads
- Validate file types
- Limit file sizes
- Scan for malware if possible

## 📋 Security Checklist Before Deployment

- [ ] All API keys in environment variables
- [ ] `.env` files gitignored
- [ ] No hardcoded secrets in code
- [ ] Strong SECRET_KEY and JWT_SECRET_KEY
- [ ] CORS properly configured
- [ ] Database credentials secure
- [ ] HTTPS enabled in production
- [ ] Error messages don't leak sensitive info

## 🔍 Regular Security Audits

Run these checks periodically:

```bash
# Check for accidentally committed secrets
git log -p | grep -i "api_key\|secret\|password"

# Scan for exposed secrets (install gitleaks)
gitleaks detect --source . --verbose

# Check dependencies for vulnerabilities
pip-audit  # Python
npm audit  # Node.js
```

## 📞 Reporting Security Issues

If you find a security vulnerability, please:
1. Don't open a public issue
2. Contact the maintainer directly
3. Provide details about the vulnerability
4. Allow time for a fix before public disclosure

---

**Remember:** Security is everyone's responsibility. When in doubt, ask!

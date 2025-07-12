# 🔐 How to Get Your Splinterlands Posting Key

## ⚠️ **IMPORTANT: Use Posting Key, NOT Login Password!**

The bot requires your **posting key** (also called private key), not your regular login password. This is a security feature that gives the bot limited access to your account.

---

## 📋 **Step-by-Step Guide**

### **1. Log into Splinterlands**
- Go to [splinterlands.com](https://splinterlands.com)
- Log in with your regular username and password

### **2. Access the Menu**
- Click on the **menu icon** (☰) in the top right corner
- Or look for your profile picture/username

### **3. Request Keys**
- Look for **"Request Keys"** or **"Private Keys"** option
- Click on it (this will open a new tab/window)

### **4. Get Your Keys**
- You'll be redirected to a Hive blockchain page
- This page will show your various private keys
- **Look for the "Posting Key"** - this is what you need!

### **5. Copy the Posting Key**
- Copy the entire posting key (starts with "5...")
- It's usually a long string of letters and numbers
- **Keep this key SECRET and SECURE!**

---

## 🛡️ **Security Tips**

### **✅ Do:**
- Keep your posting key private
- Store it in a secure password manager
- Use the posting key for the bot
- Test with a small amount first

### **❌ Don't:**
- Share your posting key with anyone
- Post it in public forums or Discord
- Use your login password for the bot
- Store it in plain text files

---

## 🔍 **What is a Posting Key?**

The posting key is a **limited access key** that allows:
- ✅ Playing battles
- ✅ Claiming rewards
- ✅ Basic game operations

It does **NOT** allow:
- ❌ Transferring assets
- ❌ Selling cards
- ❌ Major account changes

This makes it safer to use with bots!

---

## 🆘 **Troubleshooting**

### **"I can't find Request Keys"**
- Make sure you're logged into Splinterlands
- Try refreshing the page
- Look under Profile > Settings
- Check the main menu dropdown

### **"The key doesn't work"**
- Make sure you copied the entire key
- Check for extra spaces at the beginning/end
- Verify you're using the POSTING key, not active/owner key
- Try logging out and back in to Splinterlands

### **"I'm getting authentication errors"**
- Double-check your username (not email)
- Ensure the posting key is correct
- Try generating new keys if the old ones don't work
- Contact Splinterlands support if issues persist

---

## 🎯 **Quick Setup**

Once you have your posting key:

1. **Run the setup script:**
   ```bash
   python setup_credentials.py
   ```

2. **Enter your credentials:**
   - Username: `your_username` (not email)
   - Posting key: `5K...` (the long key you copied)

3. **Start the bot:**
   ```bash
   python main.py
   ```

---

## 💡 **Pro Tips**

- **Test first**: Try the bot with a small account before using your main account
- **Monitor regularly**: Check logs to ensure everything is working
- **Keep keys updated**: If you change your keys, update the bot configuration
- **Use environment variables**: Store keys in `.env` file for security

---

## 🔗 **Additional Resources**

- [Splinterlands Official Guide](https://splinterlands.com)
- [Hive Blockchain Documentation](https://hive.io)
- [Bot Documentation](README-Python.md)

---

## 🛡️ **Final Security Reminder**

Your posting key is like a **limited access pass** to your account. While it's safer than your main password, still keep it secure:

1. **Never share it publicly**
2. **Don't store it in unsecured files**
3. **Use a password manager**
4. **Monitor your account regularly**

---

*Need help? Join our Discord community or open a GitHub issue!*
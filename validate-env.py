#!/usr/bin/env python3
"""
Environment validation script for IoT Project
Checks if all required environment variables are properly configured
"""
import os
import sys
from typing import List, Tuple


def load_env_file(env_file: str = ".env"):
    """Load environment variables from a file"""
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    env_vars[key] = value
    return env_vars


def validate_env_vars() -> Tuple[bool, List[str]]:
    """Validate required environment variables"""
    required_vars = [
        'SECRET_KEY',
        'CORS_ORIGINS'
    ]
    
    # Default values that indicate configuration is needed
    default_values = [
        'your_secure_password_here',
        'your_secret_key_here_change_for_production',
        'CHANGE_THIS_SECURE_PASSWORD',
        'CHANGE_THIS_SECRET_KEY_FOR_PRODUCTION',
        'your_email@example.com',
        'your_email_password'
    ]
    
    warnings = []
    errors = []
    
    # Load environment variables
    env_vars = load_env_file()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        errors.append("❌ .env file not found! Please create one using setup-env.bat or copy from .env.production")
        return False, errors
    
    # Check required variables
    for var in required_vars:
        if var not in env_vars:
            errors.append(f"❌ Missing required variable: {var}")
        elif env_vars[var] in default_values or not env_vars[var]:
            warnings.append(f"⚠️  {var} is using default/empty value - please update for production")
        elif var == 'SECRET_KEY' and len(env_vars[var]) < 32:
            warnings.append(f"⚠️  {var} should be at least 32 characters long")
    
    # Print results
    if not errors and not warnings:
        print("✅ All environment variables are properly configured!")
        return True, []
    
    if warnings:
        print("⚠️  Configuration warnings:")
        for warning in warnings:
            print(f"   {warning}")
        print()
    
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   {error}")
        return False, errors + warnings
    
    return len(errors) == 0, warnings


def main():
    """Main validation function"""
    print("🔍 Validating IoT Project Environment Configuration")
    print("=" * 50)
    
    is_valid, messages = validate_env_vars()
    
    if messages:
        print("\n📋 Next Steps:")
        if not is_valid:
            print("   1. Create or fix your .env file")
            print("   2. Run this script again to verify")
        else:
            print("   1. Review and update the warnings above")
            print("   2. Your application should work, but consider the security recommendations")
    
    print("\n" + "=" * 50)
    
    if is_valid:
        print("✅ Environment validation passed!")
        sys.exit(0)
    else:
        print("❌ Environment validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_project.settings')

try:
    django.setup()
    from library_app.models import *
    print("✅ Models imported successfully!")
except Exception as e:
    print(f"❌ Error importing models: {e}")
    import traceback
    traceback.print_exc()
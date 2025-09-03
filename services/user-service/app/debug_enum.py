#!/usr/bin/env python3
"""
Debug script to understand the enum issue
"""
import sys
sys.path.append('/app')

from models.user import UserRole as ModelUserRole
from schemas.user import UserRole as SchemaUserRole

print("Model UserRole enum:")
for role in ModelUserRole:
    print(f"  {role.name} = {role.value}")

print("\nSchema UserRole enum:")
for role in SchemaUserRole:
    print(f"  {role.name} = {role.value}")

print(f"\nDefault role from schema: {SchemaUserRole.CLIENT}")
print(f"Default role value: {SchemaUserRole.CLIENT.value}")

# Test conversion
schema_role = SchemaUserRole.CLIENT
model_role = ModelUserRole(schema_role.value)
print(f"\nConversion test:")
print(f"Schema role: {schema_role} (value: {schema_role.value})")
print(f"Model role: {model_role} (value: {model_role.value})")

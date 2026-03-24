# Templates Directory

This directory contains document templates for mail-merge operations.

## Template Format

Templates should be `.doc` or `.docx` files with placeholders in the format `{{variable_name}}`.

### Example Template

A rental contract template might include placeholders like:

- `{{tenant_name}}` - Name of the tenant
- `{{landlord_name}}` - Name of the landlord
- `{{property_address}}` - Address of the property
- `{{monthly_rent}}` - Monthly rent amount
- `{{contract_date}}` - Date of the contract
- `{{contract_duration}}` - Duration of the contract

## Usage

Place your `.doc` or `.docx` template files in this directory. When calling the `/api/v1/generate-contract` endpoint, use the template filename (without extension) as the `template_name` parameter.

Example:
- Template file: `rental_contract.docx`
- API call: `{"template_name": "rental_contract", "merge_data": {...}}`

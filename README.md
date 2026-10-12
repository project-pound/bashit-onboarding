# BashIt Onboarding

This repo manages onboarding for new vendors and captains. It stores their master data, compliance information, service history, ratings, and contract records so the operations team can review and approve candidates before they are assigned to work.

## Included onboarding data

### Vendors
- Name, address, and contact information
- PAN, Aadhaar, GSTIN, TIN, and tax details
- Category and service specialization
- Document references and compliance status
- Service history and rating summary
- Partner contract and onboarding state

### Captains
- Name, address, and contact information
- PAN and Aadhaar references
- Police verification and background check status
- Service history and rating summary
- Partner contract and onboarding state

## Local demo

```bash
pip install -r requirements.txt
python app.py
```

Open:
- http://localhost:8005/ — onboarding dashboard with KPI cards and recent records
- http://localhost:8005/records — full vendor and captain record overview
- http://localhost:8005/vendor — vendor onboarding form
- http://localhost:8005/captain — captain onboarding form

## Notes

This is a local-first workflow and demo repository designed to track vendor/captain onboarding in a structured way before full production integration with a CRM or HR system.

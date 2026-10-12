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
- http://localhost:8005/
- http://localhost:8005/vendor
- http://localhost:8005/captain

## Notes

This is a local-first workflow and demo repository designed to track vendor/captain onboarding in a structured way before full production integration with a CRM or HR system.

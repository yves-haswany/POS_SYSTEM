from app.modules.accounting.models import LedgerEntry
from app.extensions import db
class AccountingService:

    @staticmethod
    def record_entry(entry_type, amount, currency, ref_type, ref_id):
        entry = LedgerEntry(
            type=entry_type,
            amount=amount,
            currency=currency,
            reference_type=ref_type,
            reference_id=ref_id
        )

        db.session.add(entry)
        db.session.commit()
        return entry
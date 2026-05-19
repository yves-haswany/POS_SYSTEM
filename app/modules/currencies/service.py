from app.modules.currencies.models import CurrencyRate
class CurrencyService:

    @staticmethod
    def convert(amount, from_cur, to_cur, rate):
        return amount * rate

    @staticmethod
    def get_latest_rate(from_cur, to_cur):
        return CurrencyRate.query.filter_by(
            from_currency=from_cur,
            to_currency=to_cur
        ).order_by(CurrencyRate.date.desc()).first()
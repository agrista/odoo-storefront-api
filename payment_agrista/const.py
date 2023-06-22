# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Mapping of payment status on Authorize side to transaction statuses.
# See https://developer.authorize.net/api/reference/index.html#transaction-reporting-get-transaction-details.
TRANSACTION_STATUS_MAPPING = {
    'authorized': ['authorizedPendingCapture', 'capturedPendingSettlement'],
    'captured': ['settledSuccessfully'],
    'voided': ['voided'],
    'refunded': ['refundPendingSettlement', 'refundSettledSuccessfully'],
}

# Adyen-specific mapping of currency codes in ISO 4217 format to the number of decimals.
# Only currencies for which Adyen does not follow the ISO 4217 norm are listed here.
# See https://docs.adyen.com/development-resources/currency-codes
CURRENCY_DECIMALS = {
    'CLP': 2,
    'CVE': 0,
    'IDR': 0,
    'ISK': 2,
}
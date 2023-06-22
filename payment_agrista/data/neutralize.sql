-- disable agrista payment provider
UPDATE payment_provider
   SET agrista_login = NULL,
       agrista_transaction_key = NULL,
       agrista_signature_key = NULL,
       agrista_client_key = NULL;

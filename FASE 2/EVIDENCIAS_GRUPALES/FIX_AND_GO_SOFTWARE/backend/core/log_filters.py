"""Payment capability tokens must never appear in HTTP access logs."""
import logging
import re

class PaymentTokenFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        record.msg = re.sub(r'((?:token_ws|TBK_TOKEN|token)=)[^\s&"\']+', r'\1[redacted]', message)
        record.args = ()
        return True

"""
🛡️ WEB APPLICATION FIREWALL
- Detect SQL Injection
- Detect XSS
- Detect Path Traversal
- Detect Command Injection
"""

import re
from django.http import HttpResponseForbidden
from django.conf import settings
from django.utils import timezone
from apps.accounts.models import SecurityLogs
from apps.accounts.security import get_client_ip
import logging

logger = logging.getLogger('apps.security')


class WAFMiddleware:
    """
    Web Application Firewall Middleware
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.patterns = getattr(settings, 'WAF_BLOCK_PATTERNS', {})

    def __call__(self, request):
        if getattr(settings, 'WAF_ENABLED', False):
            # Check all input
            attack_type = self._check_request(request)

            if attack_type:
                ip_address = get_client_ip(request)

                # Log attack
                try:
                    SecurityLogs.objects.create(
                        action_type='waf_blocked',
                        ip_address=ip_address,
                        matk_id=request.session.get('matk'),
                        details=f"attack_type={attack_type}, path={request.path}, method={request.method}"
                    )
                except Exception as e:
                    logger.error(f"Error logging WAF block: {e}")

                logger.warning(f"WAF blocked {attack_type} from {ip_address} on {request.path}")

                return HttpResponseForbidden('Request blocked by security policy.')

        response = self.get_response(request)
        return response

    def _check_request(self, request):
        """Kiểm tra request có chứa payload tấn công không"""

        # Combine all input
        all_input = []

        # GET parameters
        all_input.extend(request.GET.values())

        # POST parameters
        if request.method == 'POST':
            all_input.extend(request.POST.values())

        # Check each input
        for value in all_input:
            if not isinstance(value, str):
                continue

            # Check SQL Injection
            for pattern in self.patterns.get('sql_injection', []):
                if re.search(pattern, value, re.IGNORECASE):
                    return 'sql_injection'

            # Check XSS
            for pattern in self.patterns.get('xss', []):
                if re.search(pattern, value, re.IGNORECASE):
                    return 'xss'

            # Check Path Traversal
            for pattern in self.patterns.get('path_traversal', []):
                if re.search(pattern, value, re.IGNORECASE):
                    return 'path_traversal'

            # Check Command Injection
            for pattern in self.patterns.get('command_injection', []):
                if re.search(pattern, value, re.IGNORECASE):
                    return 'command_injection'

        return None
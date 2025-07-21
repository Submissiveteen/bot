from jinja2 import Template

import logging

from core.signature import get_signature_strategy



logger = logging.getLogger("deeplink")



class DeeplinkBuilder:

    def __init__(self, template: str):

        self.template = Template(template)



    def render(self, params: dict) -> str:

        try:

            return self.template.render(**params)

        except Exception as e:

            logger.error(f"Failed rendering deeplink: {e}", exc_info=True)

            return ""





def validate_deeplink_params(params: dict, required: list) -> bool:

    missing = [k for k in required if k not in params]

    if missing:

        logger.warning(f"Missing required keys in params: {missing}")

        return False

    return True





def inject_signature(aggregator: str, params: dict, secret: str) -> dict:

    strat = get_signature_strategy(aggregator)

    if strat and secret:

        params["signature"] = strat.sign(params, secret)

    return params

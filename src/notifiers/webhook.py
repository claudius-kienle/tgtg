import logging
import requests
from models import Item, Config, WebHookConfigurationError

log = logging.getLogger('tgtg')


class WebHook():
    def __init__(self, config: Config):
        self.enabled = config.webhook["enabled"]
        self.method = config.webhook["method"]
        self.url = config.webhook["url"]
        self.body = config.webhook["body"]
        self.type = config.webhook["type"]
        self.timeout = config.webhook["timeout"]
        if self.enabled and (not self.method or not self.url):
            raise WebHookConfigurationError()
        if self.enabled:
            Item.check_mask(self.body)
            Item.check_mask(self.url)

    def send(self, item: Item):
        if self.enabled:
            log.debug("Sending WebHook Notification")
            try:
                url = item.unmask(self.url)
                log.debug("Webhook url: %s", url)
                body = None
                headers = {
                    "Content-Type": self.type
                }
                log.debug("Webhook headers: %s", headers)
                if self.body:
                    body = item.unmask(self.body)
                    headers["Content-Length"] = str(len(body))
                    log.debug("Webhook body: %s", body)
                res = requests.request(method=self.method, url=url,
                                       timeout=self.timeout, data=body, headers=headers)
                if not res.ok:
                    log.error(
                        "WebHook Request failed with status code %s", res.status_code)
            except Exception as err:
                log.error(err)
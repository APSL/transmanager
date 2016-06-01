# -*- encoding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)


# gestió de les senyals #
def object_on_pre_save(sender, instance, **kwargs):
    from .manager import Manager
    man = Manager()
    man.start(sender, instance, **kwargs)


class SignalBlocker(object):
    """
    Class used to block the models signals in certains cases
    """
    def __init__(self, signal):
        self.signal = signal
        self.receivers = signal.receivers

    def __enter__(self, *args, **kwargs):
        self.signal.receivers = []

    def __exit__(self, *args, **kwargs):
        self.signal.receivers = self.receivers


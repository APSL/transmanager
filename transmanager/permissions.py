# -*- encoding: utf-8 -*-

import logging
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy

logger = logging.getLogger(__name__)


class AuthenticationMixin(object):

    """
    Mixin to check that the user has the translator profile
    """
    translator_user = None

    # def dispatch(self, request, *args, **kwargs):
    #
    #     if request.user.is_superuser:
    #         authorized = True
    #     else:
    #         try:
    #             self.translator_user = request.user.translator_user
    #             authorized = True
    #         except ObjectDoesNotExist:
    #             authorized = False
    #
    #     if not authorized:
    #         return redirect(reverse_lazy('index'))
    #
    #     return super(AuthenticationMixin, self).dispatch(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_superuser:
            authorized = True
        else:
            try:
                self.translator_user = request.user.translator_user
                authorized = True
            except ObjectDoesNotExist:
                authorized = False

        if not authorized:
            return redirect(reverse_lazy('index'))

        return super(AuthenticationMixin, self).dispatch(request, *args, **kwargs)


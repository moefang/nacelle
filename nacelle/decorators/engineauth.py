"""
A collection of decorators used for applying access
control to a handler method when using engineauth
"""


def login_required(providers=None):

    def real_decorator(function):

        def wrapper(self, *args, **kwargs):

            # url to redirect to after login
            next = self.request.path_qs

            # check if user is currently logged in
            user = self.request.user if self.request.user else None

            # if only a single provider is specified then make
            # sure it's in a list
            if isinstance(providers, basestring):
                provider = providers
                auth_providers = [provider]
            else:
                auth_providers = providers

            if auth_providers is None:

                # if auth_providers is None we don't care how the
                # user is logged in, just that they are
                if user:
                    function(self, *args, **kwargs)
                # send the user off to the default password login portal
                else:
                    self.redirect('/auth/password?next=%s' % next)

            else:

                # loop over all auth_providers in turn and make sure the user has that auth
                for provider in auth_providers:
                    if user:
                        # get required auth_providers for this handler
                        auth_ids = [x.split(':')[0] for x in user.auth_ids]
                        # if user already has this auth then we can skip it and
                        # check the next one
                        if provider in auth_ids:
                            continue
                        # force the user to login via the specified provider if
                        # they haven't already authed
                        else:
                            self.redirect('/auth/%s?next=%s' % (provider, next))
                    # force user to log in via provider if not logged in at all
                    else:
                        self.redirect('/auth/%s?next=%s' % (provider, next))
                # return the decorated function once all auths have been acquired
                else:
                    function(self, *args, **kwargs)

        return wrapper

    return real_decorator

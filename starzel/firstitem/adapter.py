import logging
from zope.annotation.interfaces import IAnnotations
from zope.i18n import translate
from Products.statusmessages import adapter
from Products.statusmessages import STATUSMESSAGEKEY
from htmllaundry import cleaners
from htmllaundry.utils import sanitize


msgcleaner = \
    cleaners.LaundryCleaner(
            page_structure = True,
            safe_attrs_only = True,
            remove_unknown_tags = False,
            allow_tags = ["blockquote", "a", "em", "strong", "span"],
            add_nofollow = True,
            scripts = True,
            javascript = False,
            comments = True,
            style = False,
            processing_instructions = True,
            frames = True,
            annoying_tags = False,
            link_target = "_blank")


class StatusMessage(adapter.StatusMessage):
    """ Overrides the standard IStatusMessage adapter to provide literal string
        support (i.e strings with the '__html__' class).

        This allows us to send html as statusmessages, without it being escaped
        by Chameleon.
    """

    def show(self):
        """ Removes all status messages (including HTML) and returns them
            for display.
        """
        context = self.context
        annotations = IAnnotations(context)
        value = annotations.get(STATUSMESSAGEKEY,
                                context.cookies.get(STATUSMESSAGEKEY))
        if value is None:
            return []
        value = adapter._decodeCookieValue(value)
        for msg in value:
            msg.message = sanitize(msg.message, cleaner=msgcleaner, wrap=None)

        # clear the existing cookie entries, except on responses that don't
        # actually render in the browser (really, these shouldn't render
        # anything so we shouldn't get to this message, but some templates
        # are sloppy).
        if self.context.response.getStatus() not in (301, 302, 304):
            context.cookies[STATUSMESSAGEKEY] = None
            context.response.expireCookie(STATUSMESSAGEKEY, path='/')
            annotations[STATUSMESSAGEKEY] = None

        return value

    showStatusMessages = show

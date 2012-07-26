from AccessControl import getSecurityManager
from Acquisition import aq_base, aq_inner
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from starzel.firstitem import FirstItemMessageFactory as _


class FirstItemView(BrowserView):
    """Custom view for the Folders forwarding to the first item inside
    """
    template = ViewPageTemplateFile('templates/folder_listing.pt')

    def __call__(self):
        context = self.context
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal_catalog = getToolByName(context, 'portal_catalog')
        currentpath = '/'.join(context.getPhysicalPath())
        folder_contents = portal_catalog(path=dict(query=currentpath, depth=1), sort_on='getObjPositionInParent')
        if folder_contents:
            first_item = folder_contents[0]
            if getSecurityManager().checkPermission(permissions.ModifyPortalContent, context):
                messages = IStatusMessage(self.request)
                msg = _(u'redirect_info', 
                      default=_(u'You have been forwarded from "${title}". Use the menu "Manage redirect" to change this.'),
                      mapping={'title': context.title})
                messages.addStatusMessage(msg, type="info")
            self.request.response.redirect(first_item.getURL())
        else:
            return self.template()


class FirstItemView_Helper(BrowserView):

    def redirect_source(self):
        """ url of the parent if context is the target of a 'firstitem_view'
        """
        obj = self.context
        parent = obj.__parent__
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request), name=u'plone_context_state')
        if context_state.is_default_page():
            obj = parent
            parent = parent.__parent__
        if getattr(aq_base(parent), 'layout', None) == 'firstitem_view':
            position = parent.getObjectPosition(obj.id)
            if position == 0:
                return parent.absolute_url()
        return False

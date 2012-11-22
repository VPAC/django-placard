from tldap.schemas import rfc, ad, helpers
import tldap.manager
import django.conf
import time
import datetime
import smbpasswd

import placard.ldap_passwd

##########
# person #
##########

class person(ad.person, rfc.organizationalPerson, rfc.inetOrgPerson, ad.user):

    class Meta:
        base_dn = django.conf.settings.LDAP_USER_BASE
        object_classes = { 'top', }
        search_classes = { 'person', }
        pk = 'cn'

    def __unicode__(self):
        return u"P:%s"%(self.displayName or self.cn)

    def check_password(self, password):
        return tldap.connection.check_password(self.dn, password)

    def change_password(self, password):
        if isinstance(password, unicode):
            password = password.encode()

        up = placard.ldap_passwd.UserPassword()
        self.userPassword = up.encodePassword(password, "ssha")

    def set_defaults(self):
        self.userAccountControl = 512

    def save(self, *args, **kwargs):
        if self.uid is not None:
            self.cn = '%s' % (self.uid)
        self.displayName = '%s %s' % (self.givenName, self.sn)
        super(person, self).save(*args, **kwargs)

    def is_locked(self):
        return self.userAccountControl & 0x2

    def lock(self):
        if not self.loginShell.startswith("/locked"):
            self.loginShell = '/locked' + self.loginShell
        self.userAccountControl = self.userAccountControl | 0x2

    def unlock(self):
        if self.loginShell.startswith("!"):
            self.loginShell = self.loginShell[1:]
        if self.loginShell.startswith("/locked"):
            self.loginShell = self.loginShell[7:]
        self.userAccountControl = self.userAccountControl & 0xFFFFFFFD

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'demo.ad_models.person', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'demo.ad_models.person', 'manager')

###########
# account #
###########

class account(person, ad.posixAccount, helpers.accountMixin):

    class Meta:
        base_dn = django.conf.settings.LDAP_USER_BASE
        object_classes = { 'top', }
        search_classes = { 'user', }
        pk = 'cn'

    def __unicode__(self):
        return u"A:%s"%(self.displayName or self.cn)

    secondary_groups = tldap.manager.ManyToManyDescriptor('dn', 'demo.ad_models.group', 'member', True)
    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'demo.ad_models.account', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'demo.ad_models.account', 'manager')

    def set_defaults(self):
        super(account, self).set_defaults()

        self.set_free_uidNumber()

        self.secondary_groups.add(group.objects.get(cn="Domain Users"))

        self.o = 'VPAC'
        self.loginShell = '/bin/bash'
        self.shadowInactive = 10
        self.shadowLastChange = 13600
        self.shadowMax = 365
        self.shadowMin = 1
        self.shadowWarning = 10
        self.objectSid = "S-1-5-" + django.conf.settings.SAMBA_DOMAIN_SID + "-" + str(int(self.uidNumber)*2)

    def delete(self, using=None):
        for u in self.manager_of.all():
            self.manager_of.remove(u)
        super(account, self).delete(using)

    def save(self, *args, **kwargs):
        self.gecos = '%s %s' % (self.givenName, self.sn)
        if self.uid is not None:
            self.unixHomeDirectory =  '/home/%s' % self.uid

        super(account, self).save(*args, **kwargs)

#########
# group #
#########

class group(rfc.posixGroup, ad.group, helpers.groupMixin):
    class Meta:
        base_dn = django.conf.settings.LDAP_GROUP_BASE
        object_classes = { 'top', }
        search_classes = { 'group', }
        pk = 'cn'

    def __unicode__(self):
        return u"G:%s"%(self.displayName or self.cn)

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor('gidNumber', account, 'gidNumber', "primary_group")
#    secondary_accounts = tldap.manager.ManyToManyDescriptor('memberUid', account, 'uid', False, "secondary_groups")
#    secondary_accounts = tldap.manager.ManyToManyDescriptor('member', account, 'dn', False, "secondary_groups")
    secondary_accounts = tldap.manager.ManyToManyDescriptor('dn', account, 'memberOf', True)

    def set_defaults(self):
        self.set_free_gidNumber()
        self.objectSid = "S-1-5-" + django.conf.settings.SAMBA_DOMAIN_SID + "-" + str(int(self.uidNumber)*2 + 1001)

    def save(self, *args, **kwargs):
        if self.displayName is None:
            self.displayName = self.cn
        if self.description is None:
            self.description = self.displayName
        super(group, self).save(*args, **kwargs)

    def delete(self, using=None):
        super(group, self).delete(using)

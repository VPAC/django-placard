from tldap.schemas import rfc, helpers
import tldap.manager
import django.conf
import time
import datetime
import smbpasswd

import placard.ldap_passwd

##########
# person #
##########

class person(rfc.person, rfc.organizationalPerson, rfc.inetOrgPerson, rfc.pwdPolicy):

    class Meta:
        base_dn = django.conf.settings.LDAP_USER_BASE
        object_classes = { 'top', }
        search_classes = { 'person', }
        pk = 'uid'

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
        self.pwdAttribute = 'userPassword'

    def save(self, *args, **kwargs):
        if self.cn is None:
            self.cn = '%s %s' % (self.givenName, self.sn)
        self.displayName = '%s %s' % (self.givenName, self.sn)
        if self.pwdAttribute is None:
            self.pwdAttribute = 'userPassword'
        super(person, self).save(*args, **kwargs)

    def is_locked(self):
        return self.pwdAccountLockedTime is not None

    def lock(self):
        if not self.loginShell.startswith("/locked"):
            self.loginShell = '/locked' + self.loginShell
        self.eduPersonAffiliation = 'affiliate'
        self.pwdAccountLockedTime='000001010000Z'
        self.primary_group = placard.models.group.objects.get(cn="visitor")
        self.secondary_groups.clear()

    def unlock(self):
        if self.loginShell.startswith("/locked"):
            self.loginShell = self.loginShell[7:]
        self.pwdAccountLockedTime=None

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'vpac_ldap.models.person', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'vpac_ldap.models.person', 'manager')

###########
# account #
###########

class account(person, rfc.posixAccount, rfc.shadowAccount, helpers.AccountMixin)

    class Meta:
        base_dn = django.conf.settings.LDAP_USER_BASE
        object_classes = { 'top', }
        search_classes = { 'posixAccount', }
        pk = 'uid'

    def __unicode__(self):
        return u"A:%s"%(self.displayName or self.cn)

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'vpac_ldap.models.account', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'vpac_ldap.models.account', 'manager')



    def _generate_shared_token(self):
        try:
            from hashlib import sha
        except:
            from sha import sha
        import base64
        uid = self.uid
        mail = self.mail
        entityID = 'https://idp.vpac.org/idp/shibboleth'
        salt = 'bvFVFz+T6t15uGP16QkUy7GHE2QMFHmziLehUGg3QX8MFeI9'
        return base64.urlsafe_b64encode(sha(uid + mail + entityID + salt).digest())[:-1]

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

    def delete(self, using=None):
        for u in self.manager_of.all():
            self.manager_of.remove(u)
        super(account, self).delete(using)

    def save(self, *args, **kwargs):
        self.gecos = '%s %s' % (self.givenName, self.sn)
        self.homeDirectory =  '/home/%s' % self.uid

        super(account, self).save(*args, **kwargs)

#########
# group #
#########

class group(rfc.posixGroup, helpers.groupMixin):
    class Meta:
        base_dn = django.conf.settings.LDAP_GROUP_BASE
        object_classes = { 'top', }
        search_classes = { 'posixGroup', }
        pk = 'cn'

    def __unicode__(self):
        return u"G:%s"%(self.displayName or self.cn)

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor('gidNumber', account, 'gidNumber', "primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor('memberUid', account, 'uid', False, "secondary_groups")

    def set_defaults(self):
        self.set_free_gidNumber()

    def save(self, *args, **kwargs):
        if self.displayName is None:
            self.displayName = self.cn
        if self.description is None:
            self.description = self.displayName
        super(group, self).save(*args, **kwargs)

    def delete(self, using=None):
        super(group, self).delete(using)


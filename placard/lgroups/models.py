from django.db import models


class LDAPGroup(object):

    def __init__(self, data):
        self.dn = data[0]
        data_dict = data[1]
        for k, v in data_dict.items():
            if len(v) == 1 and k != 'memberUid':
                setattr(self, k, v[0])
            else:
                setattr(self, k, v)
        
    def __unicode__(self):
        return u'%s' % self.__str__()

    def __str__(self):
        return self.name()

    def __repr__(self):
        return self.__str__()

    @models.permalink
    def get_absolute_url(self):
        return ('plac_grp_detail', [self.gidNumber])

    def name(self):
        try:
            return self.description
        except AttributeError:
            return self.cn


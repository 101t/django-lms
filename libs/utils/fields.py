from django.db import models

#TODO Make this non-mongo specific
from bson.objectid import ObjectId, InvalidId

class ForeignKey(models.ForeignKey):
    __metaclass__ = models.fields.subclassing.SubfieldBase

    def db_type(self, connection):
        super_type = super(ForeignKey, self).db_type(connection=connection)

        if not super_type:
            if 'django_mongodb_engine' in connection.settings_dict['ENGINE']:
                return 'objectid'

        return super_type
    
    def to_python(self, value):
        if issubclass(type(value), unicode):
            return self.rel.to.objects.get(pk = value)
        return value

    def get_db_prep_save(self, value, **kwargs):
        if isinstance(type(value), type(self.rel.to)):
            return unicode(value.pk)
        else:
            return value

    def get_db_prep_lookup(self, *args, **kwargs):
        look_up = args[0]
        value = args[1]

        if type(value) == self.rel.to:
            # Got a single value
            try:
                return ObjectId(value.pk)
            except InvalidId:
                # Provide a better message for invalid IDs
                assert isinstance(value, unicode)
                if len(value) > 13:
                    value = value[:10] + '...'
                msg = "AutoField (default primary key) values must be strings " \
                    "representing an ObjectId on MongoDB (got %r instead)" % value
                raise InvalidId(msg)
        else:
            return super(ForeignKey, self).get_db_prep_lookup(*args, **kwargs)
            
    def get_db_prep_value(self, value, connection, prepared=False):
        raise NotImplimentedError

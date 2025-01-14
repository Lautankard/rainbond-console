# -*- coding: utf-8 -*-
from datetime import datetime

from console.models.main import ConsoleSysConfig


class ConfigRepository(object):
    def list_by_keys(self, keys):
        return ConsoleSysConfig.objects.filter(enable=True, key__in=keys)

    def delete_by_key(self, key):
        cfg = ConsoleSysConfig.objects.get(key=key)
        cfg.delete()

    def update_by_key(self, key, value):
        return ConsoleSysConfig.objects.filter(key=key).update(value=value)

    def update_or_create_by_key(self, key, value):
        try:
            obj = ConsoleSysConfig.objects.get(key=key)
            setattr(obj, "value", value)
            obj.save()
        except ConsoleSysConfig.DoesNotExist:
            ConsoleSysConfig.objects.create(
                key=key,
                value=value,
                type="json",
                desc="git配置",
                enable=True,
                create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

    def get_by_key(self, key):
        return ConsoleSysConfig.objects.get(key=key, enable=True)


cfg_repo = ConfigRepository()

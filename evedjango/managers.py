from django.db import models
from evedjango.models import *
import eveapi

class APIKeyInfoManager(models.Manager):

    def corporations(self):
        return self.get_query_set().filter(key_type='CO')

    def characters(self):
        return self.get_query_set().filter(key_type='CH')

    def accounts(self):
        return self.get_query_set().filter(key_type='AC')

class EveEntityManager(models.Manager):

    def create_simple(self, id, name):
        return self.get_query_set().get_or_create(pk=id, name=name)

class KillReportManager(models.Manager):

    def bulk_create_from_auth(self, api_key, max_pages=5, before_id=None):

        def _proc_info(auth_base, before_id):
            if before_id:
                if before_id != 0:
                    resultset = auth_base.KillLog(beforeKillID=before_id)
            else:
                resultset = auth_base.KillLog()

            kill_ids = []

            for kill in resultset.kills:
                kill_ids.append(kill.killID)
                kill_report, drops = self.model.create_from_kill_row(kill, api_key)

            before_id = kill_id[-1]

            return before_id, (kill_report, drops)

        page_count = 0
        processed_kills = []

        access_mask = api_key.info.access_mask
        if access_mask & 256 == 256:
            auth_obj = api_key.get_api_object()
            while page_count < max_pages:
                if api_key.info.key_type == 'CO':
                    corp_auth = auth_obj.corp
                    before_id, param_set = _proc_info(corp_auth, before_id)
                elif api_key.info.key_type in ['AC', 'CH']:
                    char_auth = auth_obj.char
                    before_id, param_set = _proc_info(char_auth, before_id)

                processed_kills.append(param_set)
                page_count += 1

            return {'count': len(processed_kills), 'kills': processed_kills}

        else:
            return False


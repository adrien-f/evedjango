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

class KillReportManager(models.Manager):

    def bulk_create_from_auth(self, apikey, max_pages=5, before_id=None):

        def _proc_info(auth_base, before_id):
            if before_id:
                if before_id != 0:
                    resultset = auth_base.KillLog(beforeKillID=before_id)
                else:
                    resultset = auth_base.KillLog()
            else:
                resultset = auth_base.KillLog()

            params = []
            kill_ids = []

            for kill in resultset.kills:
                kill_id = kill.killID
                kill_ids.append(kill_id)
                solar_system_id = kill.solarSystemID
                kill_time = kill.killTime
                victim = {
                        'id': kill.victim.characterID,
                        'name': kill.victim.characterName,
                        'corp_id': kill.victim.corporationID,
                        'alliance_id': kill.victim.allianceID,
                        'alliance_name': kill.victim.allianceName,
                        'faction_id': kill.victim.factionID,
                        'damage_taken': kill.victim.damageTaken,
                        'ship_id': kill.victim.shipTypeID,
                        }

                attackers = [{
                                    'id': attacker.characterID,
                                    'name': attacker.characterName,
                                    'corp_id': attacker.corporationID,
                                    'alliance_id': attacker.allianceID,
                                    'faction_id': attacker.factionID,
                                    'sec_status': attacker.securityStatus,
                                    'damage_done': attacker.damageDone,
                                    'final_blow': bool(attacker.finalBlow),
                                    'weapon_type': attacker.weaponTypeID,
                                    'ship_type': attacker.shipTypeID,
                                } for attacker in kill.attackers]

                def _proc_items(items):
                    output = []
                    for item in items:
                        item_info = {
                                        'type_id': item.typeID,
                                        'flag': item.flag,
                                        'qty_dropped': item.qtyDropped,
                                        'qty_destroyed': item.qtyDestroyed,
                                        'singleton': item.singleton,
                                        'contains': [],
                                    }

                        if hasattr(item, 'items'):
                            item_info['contains'] = _proc_items(item.items)

                        output.append(item_info)

                    return output

                kill_items = _proc_items(kill.items)

                params.append({
                                'id': kill_id,
                                'solar_system_id': solar_system_id,
                                'kill_time': kill_time,
                                'victim': victim,
                                'attackers': attackers,
                                'items': kill_items,
                              })

            return kill_ids[-1], params

        page_count = 0

        processed_params = []

        access_mask = apikey.info.get().access_mask
        if access_mask & 256 == 256:
            auth_obj = apikey.get_api_object()
            while page_count < max_pages:
                if apikey.info.get().key_type == 'CO':
                    corp_auth = auth_obj.corp
                    before_id, param_set = _proc_info(corp_auth, before_id)
                elif apikey.info.get().key_type in ['AC', 'CH']:
                    char_auth = auth_obj.char
                    before_id, param_set = _proc_info(char_auth, before_id)

                processed_params += param_set
                page_count += 1

        else:
            return False

        api = eveapi.EVEAPIConnection()
        for param_dict in processed_params:
            victim = param_dict['victim']
            attackers = param_dict['attackers']
            items = param_dict['items']
            solar_system_id = param_dict['solar_system_id']
            kill_report = self.create(pk=param_dict['kill_id'])

            vic_char = Victim.objects.get_or_create(pk=victim['id'])
            if not vic_char.name:
                vic_char.name = victim['name']
                corporation = Corporation.objects.get_or_create(pk=victim['corp_id'])
                if not corporation.name:
                    corporation.fetch_and_save()
                vic_char.corporation = corporation

                if victim['alliance_id'] != 0:
                    alliance = Alliance.objects.get_or_create(pk=victim['alliance_id'])
                    if not alliance.name:
                        alliance.name = victim['alliance_name']
                    vic_char.alliance = alliance

                if victim['faction_id'] != 0:
                    vic_char.faction = ChrFaction.objects.get(pk=victim['faction_id'])
                vic_char.save()

            kill_report.victim = vic_char
            kill_report.kill_time = param_dict['kill_time']

            attacker_chars = []
            for attacker in attackers:
                att_char = Attacker.get_or_create(pk=attacker['id'])
                if not att_char.name:
                    att_char.sec_status = attacker['sec_status']
                    att_char.damage_done = attacker['damage_done']
                    att_char.final_blow = attacker['final_blow']
                    att_char.weapon_type = InvType.objects(pk=attacker['weapon_type'])
                    att_char.ship_type = InvType.objects(pk=attacker['ship_type'])
                    att_char.fetch_and_save()

                kill_report.attackers.add(att_char)

            kill_report.attackers.add(attacker_chars)

            def _db_proc_items(items, container=None):
                for item in items:
                    item_drop = ItemDrop.objects.create(item_type=InvType.objects.get(pk=item['type_id']))
                    item_drop.location_flag = item['flag']
                    if container:
                        item_drop.container = container
                    item_drop.qty_dropped = item['qty_dropped']
                    item_drop.qty_destroyed = item['qty_destroyed']
                    item_drop.singleton = item['singleton']
                    item_drop.save()
                    kill_report.items.add(item_drop)
                    if item['contains']:
                        _db_proc_items(items, item_drop)

            solar_system = MapSolarSystem.objects.get(pk=solar_system_id)
            kill_report.solar_system = solar_system

            kill_report.save()
